"""PHX-G343 CN issue ↔ RMA link gateway contracts."""

from __future__ import annotations

from dataclasses import replace
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
from noventi.crm.credit_note import CRMReturnAuthorizationCreditNoteLinkAdapter
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
        self, ctx: ExecutionContext, **kwargs: object
    ) -> KernelResult[UUID]:
        result = self._finance.create_credit_note(ctx, **kwargs)
        if not result.ok:
            return result
        assert result.data is not None
        return KernelResult.success(result.data.id, audit_id=result.audit_id)


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g343",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g343-http",
    }


def _client() -> tuple[TestClient, InMemoryCRMRepository, str, str]:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    assert permission.grant(
        _ctx(),
        principal_subject_id=SUBJECT,
        resource_type=RETURN_AUTHORIZATION_RESOURCE,
        actions={"read", "restock", "create_credit_note"},
        scope_level=ScopeLevel.TENANT,
    ).ok
    assert permission.grant(
        _ctx(),
        principal_subject_id=SUBJECT,
        resource_type=AR_CREDIT_NOTE_RESOURCE,
        actions={"create", "read", "issue"},
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
            code="INV-G343",
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
        code="RA-G343",
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
        rma_credit_note_link_port=CRMReturnAuthorizationCreditNoteLinkAdapter(
            crm_repo
        ),
    )
    crm = CRMService(
        permission,
        repository=crm_repo,
        audit_log=audit,
        return_restock_port=_RestockPort(),
        credit_note_create_port=_CreditNotePort(finance),
    )
    return (
        TestClient(create_app(crm_service=crm, finance_service=finance)),
        crm_repo,
        str(rma.id),
        str(invoice_id),
    )


def _restock(client: TestClient, rma_id: str) -> None:
    response = client.post(
        f"/v1/crm/return-authorizations/{rma_id}/restock",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert response.status_code == 200


def _create_from_rma(client: TestClient, rma_id: str) -> dict:
    response = client.post(
        f"/v1/crm/return-authorizations/{rma_id}/credit-notes",
        headers=_headers(),
        json={"amount": "5.00", "idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert response.status_code == 201
    return response.json()["data"]


def _issue(client: TestClient, credit_note_id: str):
    return client.post(
        f"/v1/finance/credit-notes/{credit_note_id}/issue",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )


def test_g343_issues_restocked_rma_credit_note_and_stamps_trace() -> None:
    client, _repo, rma_id, _invoice_id = _client()
    _restock(client, rma_id)
    rma = _create_from_rma(client, rma_id)

    issued = _issue(client, rma["credit_note_id"])

    assert issued.status_code == 200
    traced = client.get(
        f"/v1/crm/return-authorizations/{rma_id}", headers=_headers()
    ).json()["data"]
    assert traced["credit_note_issued_at"] is not None


def test_g343_rejects_broken_rma_invoice_lineage() -> None:
    client, repo, rma_id, _invoice_id = _client()
    _restock(client, rma_id)
    rma = _create_from_rma(client, rma_id)
    current = repo.get_return_authorization(UUID(rma_id))
    assert current is not None
    repo.save_return_authorization(
        replace(current, invoice_id=uuid4(), version=current.version + 1),
        expected_version=current.version,
    )

    rejected = _issue(client, rma["credit_note_id"])

    assert rejected.status_code == 409


def test_g343_allows_unlinked_credit_note_issue() -> None:
    client, _repo, _rma_id, invoice_id = _client()
    created = client.post(
        "/v1/finance/credit-notes",
        headers=_headers(),
        json={"invoice_id": invoice_id, "amount": "5.00", "idempotency_key": str(uuid4())},
    )
    assert created.status_code == 201

    issued = _issue(client, created.json()["data"]["id"])

    assert issued.status_code == 200
    assert issued.json()["data"]["status"] == "issued"


def test_g343_restock_does_not_auto_issue_credit_note() -> None:
    client, _repo, rma_id, _invoice_id = _client()
    _restock(client, rma_id)
    rma = _create_from_rma(client, rma_id)

    credit_note = client.get(
        f"/v1/finance/credit-notes/{rma['credit_note_id']}", headers=_headers()
    )

    assert credit_note.status_code == 200
    assert credit_note.json()["data"]["status"] == "draft"
