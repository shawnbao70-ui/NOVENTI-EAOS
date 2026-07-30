"""PHX-G337 RET → Credit Note gateway contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
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
from noventi.crm.service import (
    RETURN_AUTHORIZATION_RESOURCE,
    CRMService,
)
from noventi.finance.repository import InMemoryFinanceRepository
from noventi.finance.service import (
    AR_CREDIT_NOTE_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
)

SUBJECT, TENANT = uuid4(), uuid4()


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


class _RestockPort:
    def shipped_line_quantities(
        self, delivery_order_id: UUID
    ) -> tuple[tuple[UUID, Decimal], ...]:
        return ((uuid4(), Decimal("1.000")),)

    def atomic_rma_restock(self, **_kwargs: object) -> None:
        return None


class _InvoiceReader:
    def __init__(self, repo: InMemoryCRMRepository) -> None:
        self._repo = repo

    def get_ar_invoice_snapshot(
        self, invoice_id: UUID
    ) -> ARInvoiceSnapshot | None:
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
        self,
        ctx: ExecutionContext,
        *,
        invoice_id: UUID,
        amount: Decimal,
        idempotency_key: UUID,
    ) -> KernelResult[UUID]:
        result = self._finance.create_credit_note(
            ctx,
            invoice_id=invoice_id,
            amount=amount,
            idempotency_key=idempotency_key,
        )
        if not result.ok:
            return result
        assert result.data is not None
        return KernelResult.success(result.data.id, audit_id=result.audit_id)


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g337",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g337-http",
    }


def _client(*, grant_credit: bool = True) -> tuple[TestClient, str]:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    rma_actions = {"read", "restock"}
    if grant_credit:
        rma_actions.add("create_credit_note")
    assert permission.grant(
        _ctx(),
        principal_subject_id=SUBJECT,
        resource_type=RETURN_AUTHORIZATION_RESOURCE,
        actions=rma_actions,
        scope_level=ScopeLevel.TENANT,
    ).ok
    assert permission.grant(
        _ctx(),
        principal_subject_id=SUBJECT,
        resource_type=AR_CREDIT_NOTE_RESOURCE,
        actions={"create", "read"},
        scope_level=ScopeLevel.TENANT,
    ).ok
    crm_repo = InMemoryCRMRepository(tenant_id=TENANT)
    invoice_id, delivery_order_id = uuid4(), uuid4()
    now = datetime.now(timezone.utc)
    crm_repo.add_ar_invoice(
        ARInvoice(
            id=invoice_id,
            tenant_id=TENANT,
            delivery_order_id=delivery_order_id,
            delivery_order_version=1,
            sales_order_id=uuid4(),
            sales_order_version=1,
            customer_id=uuid4(),
            code="INV-G337",
            currency="USD",
            total_amount=Decimal("10.00"),
            idempotency_key=uuid4(),
            status=ARInvoiceStatus.ISSUED,
            created_at=now,
            issued_at=now,
        )
    )
    rma = ReturnAuthorization(
        id=uuid4(),
        tenant_id=TENANT,
        delivery_order_id=delivery_order_id,
        invoice_id=invoice_id,
        code="RA-G337",
        reason="return",
        idempotency_key=uuid4(),
        status=ReturnAuthorizationStatus.DRAFT,
        created_at=now,
    )
    crm_repo.add_return_authorization(rma)
    finance = FinanceService(
        permission,
        repository=InMemoryFinanceRepository(tenant_id=TENANT),
        audit_log=audit,
        ar_invoice_reader=_InvoiceReader(crm_repo),
    )
    crm = CRMService(
        permission,
        repository=crm_repo,
        audit_log=audit,
        return_restock_port=_RestockPort(),
        credit_note_create_port=_CreditNotePort(finance),
    )
    return TestClient(create_app(crm_service=crm, finance_service=finance)), str(rma.id)


def _restock(client: TestClient, rma_id: str) -> None:
    response = client.post(
        f"/v1/crm/return-authorizations/{rma_id}/restock",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert response.status_code == 200


def test_g337_denies_credit_note_without_rma_grant() -> None:
    client, rma_id = _client(grant_credit=False)
    response = client.post(
        f"/v1/crm/return-authorizations/{rma_id}/credit-notes",
        headers=_headers(),
        json={
            "amount": "5.00",
            "idempotency_key": str(uuid4()),
            "human_confirm": True,
        },
    )
    assert response.status_code == 403


def test_g337_restock_then_creates_draft_credit_note_and_link() -> None:
    client, rma_id = _client()
    _restock(client, rma_id)
    created = client.post(
        f"/v1/crm/return-authorizations/{rma_id}/credit-notes",
        headers=_headers(),
        json={
            "amount": "5.00",
            "idempotency_key": str(uuid4()),
            "human_confirm": True,
        },
    )
    assert created.status_code == 201
    rma = created.json()["data"]
    assert rma["credit_note_id"] is not None
    credit_note = client.get(
        f"/v1/finance/credit-notes/{rma['credit_note_id']}", headers=_headers()
    )
    assert credit_note.status_code == 200
    assert credit_note.json()["data"]["status"] == "draft"
    assert credit_note.json()["data"]["ar_invoice_id"] == rma["invoice_id"]


def test_g337_restock_alone_does_not_create_credit_note() -> None:
    client, rma_id = _client()
    _restock(client, rma_id)
    rma = client.get(
        f"/v1/crm/return-authorizations/{rma_id}", headers=_headers()
    )
    assert rma.status_code == 200
    assert rma.json()["data"]["credit_note_id"] is None


def test_g337_rejects_credit_note_for_draft_rma() -> None:
    client, rma_id = _client()
    response = client.post(
        f"/v1/crm/return-authorizations/{rma_id}/credit-notes",
        headers=_headers(),
        json={
            "amount": "5.00",
            "idempotency_key": str(uuid4()),
            "human_confirm": True,
        },
    )
    assert response.status_code == 409


def test_g337_is_idempotent_and_exposes_openapi_path() -> None:
    client, rma_id = _client()
    _restock(client, rma_id)
    key = str(uuid4())
    payload = {"amount": "5.00", "idempotency_key": key, "human_confirm": True}
    first = client.post(
        f"/v1/crm/return-authorizations/{rma_id}/credit-notes",
        headers=_headers(),
        json=payload,
    )
    second = client.post(
        f"/v1/crm/return-authorizations/{rma_id}/credit-notes",
        headers=_headers(),
        json=payload,
    )
    assert first.status_code == second.status_code == 201
    assert first.json()["data"]["credit_note_id"] == second.json()["data"][
        "credit_note_id"
    ]
    assert (
        "/v1/crm/return-authorizations/{return_authorization_id}/credit-notes"
        in client.get("/openapi.json").json()["paths"]
    )
