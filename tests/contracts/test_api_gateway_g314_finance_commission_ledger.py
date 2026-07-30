"""PHX-G314 Finance Commission Ledger HTTP contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import (
    AR_INVOICE_RESOURCE,
    CONVERSION_RESOURCE,
    CUSTOMER_RESOURCE,
    DELIVERY_ORDER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    QUOTE_LINE_RESOURCE,
    QUOTE_RESOURCE,
    REQUIREMENT_RESOURCE,
    SALES_ORDER_RESOURCE,
    CRMService,
)
from noventi.finance.repository import InMemoryFinanceRepository
from noventi.finance.service import (
    AR_CREDIT_NOTE_RESOURCE,
    AR_RECEIPT_RESOURCE,
    ARInvoiceSnapshot,
    COMMISSION_RESOURCE,
    FinanceService,
)
from tests.contracts.test_finance_z2_commission_ledger import _issued_invoice

SUBJECT, TENANT = uuid4(), uuid4()


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


class _CRMInvoiceReader:
    def __init__(self, crm_repo: InMemoryCRMRepository) -> None:
        self._crm = crm_repo

    def get_ar_invoice_snapshot(
        self, invoice_id: UUID
    ) -> ARInvoiceSnapshot | None:
        invoice = self._crm.get_ar_invoice(invoice_id)
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


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g314",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g314-http",
    }


def _client() -> tuple[TestClient, CRMService]:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    for resource in (
        CUSTOMER_RESOURCE,
        OPPORTUNITY_RESOURCE,
        REQUIREMENT_RESOURCE,
        QUOTE_RESOURCE,
        QUOTE_LINE_RESOURCE,
        CONVERSION_RESOURCE,
        SALES_ORDER_RESOURCE,
        DELIVERY_ORDER_RESOURCE,
        AR_INVOICE_RESOURCE,
        AR_RECEIPT_RESOURCE,
        AR_CREDIT_NOTE_RESOURCE,
        COMMISSION_RESOURCE,
    ):
        assert permission.grant(
            _ctx(),
            principal_subject_id=SUBJECT,
            resource_type=resource,
            actions={
                "create",
                "read",
                "update",
                "archive",
                "convert",
                "issue",
                "confirm",
                "release",
                "void",
                "apply",
            },
            scope_level=ScopeLevel.TENANT,
        ).ok
    crm_repo = InMemoryCRMRepository(tenant_id=TENANT)
    crm = CRMService(permission, repository=crm_repo, audit_log=audit)
    finance = FinanceService(
        permission,
        repository=InMemoryFinanceRepository(tenant_id=TENANT),
        audit_log=audit,
        ar_invoice_reader=_CRMInvoiceReader(crm_repo),
        beneficiary_eligibility=_Eligibility(),
    )
    return (
        TestClient(create_app(crm_service=crm, finance_service=finance)),
        crm,
    )


def test_g314_commission_round_trip_and_context_override() -> None:
    client, crm = _client()
    invoice = _issued_invoice(crm, _ctx())
    response = client.post(
        "/v1/finance/commissions",
        headers=_headers(),
        json={
            "invoice_id": str(invoice.id),
            "beneficiary_subject_id": str(SUBJECT),
            "amount": "3.00",
            "currency": invoice.currency,
            "idempotency_key": str(uuid4()),
        },
    )
    assert response.status_code == 201
    body = response.json()["data"]
    assert body["status"] == "accrued"
    assert body["source_invoice_id"] == str(invoice.id)
    fetched = client.get(
        f"/v1/finance/commissions/{body['id']}", headers=_headers()
    )
    assert fetched.status_code == 200
    rejected = client.post(
        "/v1/finance/commissions",
        headers=_headers(),
        json={
            "invoice_id": str(invoice.id),
            "beneficiary_subject_id": str(SUBJECT),
            "amount": "1.00",
            "currency": invoice.currency,
            "idempotency_key": str(uuid4()),
            "tenant_id": str(uuid4()),
        },
    )
    assert rejected.status_code == 422


def test_g314_openapi_forbids_payout_surfaces() -> None:
    client, _ = _client()
    spec = client.get("/openapi.json").json()
    assert "/v1/finance/commissions" in spec["paths"]
    surface = str(spec["paths"]["/v1/finance/commissions"]).casefold()
    for forbidden in ("payout", "payroll", "psp", "clawback", "brain", "twin"):
        assert forbidden not in surface
