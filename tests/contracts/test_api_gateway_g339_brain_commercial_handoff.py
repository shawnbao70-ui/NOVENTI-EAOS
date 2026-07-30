"""PHX-G339 explicit Brain/Twin → draft credit-note handoff contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from eaos_platform.brain.service import BrainService
from eaos_platform.twin.service import TwinService
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.results import KernelResult
from noventi.crm.models import (
    ARInvoice,
    ARInvoiceStatus,
    ReturnAuthorization,
    ReturnAuthorizationStatus,
)
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import CRMService, RETURN_AUTHORIZATION_RESOURCE
from noventi.finance.repository import InMemoryFinanceRepository
from noventi.finance.service import (
    AR_CREDIT_NOTE_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
)

SUBJECT, ADMIN, TENANT = uuid4(), uuid4(), uuid4()


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


class _RestockPort:
    def shipped_line_quantities(self, delivery_order_id: UUID) -> tuple[tuple[UUID, Decimal], ...]:
        return ((uuid4(), Decimal("1.000")),)

    def atomic_rma_restock(self, **_kwargs: object) -> None:
        return None


class _InvoiceReader:
    def __init__(self, repo: InMemoryCRMRepository) -> None:
        self._repo = repo

    def get_ar_invoice_snapshot(self, invoice_id: UUID) -> ARInvoiceSnapshot | None:
        invoice = self._repo.get_ar_invoice(invoice_id)
        if invoice is None:
            return None
        return ARInvoiceSnapshot(
            id=invoice.id,
            tenant_id=invoice.tenant_id,
            customer_id=invoice.customer_id,
            currency=invoice.currency,
            total_amount=invoice.total_amount,
            status=invoice.status.value,
            version=invoice.version,
        )


class _CreditNotePort:
    def __init__(self, finance: FinanceService) -> None:
        self._finance = finance

    def create_credit_note(
        self, ctx: ExecutionContext, *, invoice_id: UUID, amount: Decimal, idempotency_key: UUID
    ) -> KernelResult[UUID]:
        result = self._finance.create_credit_note(
            ctx, invoice_id=invoice_id, amount=amount, idempotency_key=idempotency_key
        )
        if not result.ok:
            return result
        assert result.data is not None
        return KernelResult.success(result.data.id, audit_id=result.audit_id)


def _ctx(subject_id: UUID = SUBJECT) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g339",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g339-http",
    }


def _client(*, handoff: bool = True, brain_execute: bool = True, twin_authorize: bool = True) -> tuple[TestClient, str]:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit, grant_administrators={ADMIN}, principal_eligibility=_Eligibility()
    )
    for resource, actions in (
        (RETURN_AUTHORIZATION_RESOURCE, {"read", "restock", "create_credit_note"}),
        (AR_CREDIT_NOTE_RESOURCE, {"create", "read"}),
        ("brain_insight", {"publish", "read"} | ({"execute"} if brain_execute else set())),
        ("twin_snapshot", {"write", "read"} | ({"authorize"} if twin_authorize else set())),
        (
            "pkg.platform.commercial_handoff",
            {"handoff_rma_credit_note"} if handoff else set(),
        ),
    ):
        if not actions:
            continue
        assert permission.grant(
            _ctx(ADMIN),
            principal_subject_id=SUBJECT,
            resource_type=resource,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok

    crm_repo = InMemoryCRMRepository(tenant_id=TENANT)
    invoice_id, delivery_order_id = uuid4(), uuid4()
    now = datetime.now(timezone.utc)
    crm_repo.add_ar_invoice(
        ARInvoice(
            id=invoice_id, tenant_id=TENANT, delivery_order_id=delivery_order_id,
            delivery_order_version=1, sales_order_id=uuid4(), sales_order_version=1,
            customer_id=uuid4(), code="INV-G339", currency="USD",
            total_amount=Decimal("10.00"), idempotency_key=uuid4(),
            status=ARInvoiceStatus.ISSUED, created_at=now, issued_at=now,
        )
    )
    rma = ReturnAuthorization(
        id=uuid4(), tenant_id=TENANT, delivery_order_id=delivery_order_id,
        invoice_id=invoice_id, code="RA-G339", reason="return",
        idempotency_key=uuid4(), status=ReturnAuthorizationStatus.DRAFT, created_at=now,
    )
    crm_repo.add_return_authorization(rma)
    finance = FinanceService(
        permission, repository=InMemoryFinanceRepository(tenant_id=TENANT),
        audit_log=audit, ar_invoice_reader=_InvoiceReader(crm_repo),
    )
    crm = CRMService(
        permission, repository=crm_repo, audit_log=audit, return_restock_port=_RestockPort(),
        credit_note_create_port=_CreditNotePort(finance),
    )
    twin = TwinService(permission, audit_log=audit)
    brain = BrainService(permission, audit_log=audit, twin_reader=twin)
    return TestClient(
        create_app(
            permission_service=permission, twin_service=twin, brain_service=brain,
            crm_service=crm, finance_service=finance,
        )
    ), str(rma.id)


def _seed(client: TestClient) -> tuple[str, str]:
    snapshot = client.post("/v1/twin/snapshots", headers=_headers(), json={
        "entity_ref": "rma:g339", "state": {"restocked": True},
        "source_ref": "test:g339", "reason": "seed", "confidence": 0.9,
    })
    assert snapshot.status_code == 201, snapshot.text
    insight = client.post("/v1/brain/insights", headers=_headers(), json={
        "kind": "recommendation", "summary": "create draft credit note",
        "confidence": 0.9, "source_ref": "test:g339", "reason": "seed",
        "twin_ref": snapshot.json()["data"],
    })
    assert insight.status_code == 201, insight.text
    return snapshot.json()["data"], insight.json()["data"]


def _restock(client: TestClient, rma_id: str) -> None:
    response = client.post(
        f"/v1/crm/return-authorizations/{rma_id}/restock", headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert response.status_code == 200, response.text


def _handoff(client: TestClient, rma_id: str, insight_id: str, *, key: str | None = None):
    return client.post(
        "/v1/platform/commercial-handoffs/rma-credit-note", headers=_headers(),
        json={
            "authorization_source": "brain", "insight_id": insight_id,
            "return_authorization_id": rma_id, "amount": "5.00",
            "idempotency_key": key or str(uuid4()), "human_confirm": True,
        },
    )


def test_g339_denies_without_handoff_grant() -> None:
    client, rma_id = _client(handoff=False)
    _restock(client, rma_id)
    _snapshot_id, insight_id = _seed(client)
    response = _handoff(client, rma_id, insight_id)
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "COMMERCIAL_HANDOFF_FORBIDDEN"


def test_g339_denies_without_brain_execution_grant() -> None:
    client, rma_id = _client(brain_execute=False)
    _restock(client, rma_id)
    _snapshot_id, insight_id = _seed(client)
    response = _handoff(client, rma_id, insight_id)
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "BRAIN_EXECUTION_FORBIDDEN"


def test_g339_creates_draft_credit_note_and_is_idempotent() -> None:
    client, rma_id = _client()
    _restock(client, rma_id)
    _snapshot_id, insight_id = _seed(client)
    key = str(uuid4())
    first = _handoff(client, rma_id, insight_id, key=key)
    second = _handoff(client, rma_id, insight_id, key=key)
    assert first.status_code == second.status_code == 201
    assert first.json()["data"]["credit_note_id"] == second.json()["data"]["credit_note_id"]
    credit_note = client.get(
        f"/v1/finance/credit-notes/{first.json()['data']['credit_note_id']}", headers=_headers()
    )
    assert credit_note.status_code == 200
    assert credit_note.json()["data"]["status"] == "draft"


def test_g339_g335_execute_alone_does_not_create_credit_note() -> None:
    client, rma_id = _client()
    _restock(client, rma_id)
    _snapshot_id, insight_id = _seed(client)
    assert client.post(f"/v1/brain/insights/{insight_id}/execute", headers=_headers()).status_code == 200
    rma = client.get(f"/v1/crm/return-authorizations/{rma_id}", headers=_headers())
    assert rma.status_code == 200
    assert rma.json()["data"]["credit_note_id"] is None


def test_g339_twin_handoff_and_openapi_path_present() -> None:
    client, rma_id = _client()
    _restock(client, rma_id)
    snapshot_id, _insight_id = _seed(client)
    response = client.post(
        "/v1/platform/commercial-handoffs/rma-credit-note", headers=_headers(),
        json={
            "authorization_source": "twin", "snapshot_id": snapshot_id,
            "return_authorization_id": rma_id, "amount": "5.00",
            "idempotency_key": str(uuid4()), "human_confirm": True,
        },
    )
    assert response.status_code == 201, response.text
    assert "/v1/platform/commercial-handoffs/rma-credit-note" in client.get("/openapi.json").json()["paths"]
