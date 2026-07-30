"""PHX-G312 Finance AR Credit Note HTTP contracts."""

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
    AR_REFUND_RESOURCE,
    AR_RECEIPT_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
)

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
        correlation_id="corr-g312",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g312-http",
    }


def _client() -> TestClient:
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
        AR_REFUND_RESOURCE,
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
                "post",
            },
            scope_level=ScopeLevel.TENANT,
        ).ok
    crm_repo = InMemoryCRMRepository(tenant_id=TENANT)
    return TestClient(
        create_app(
            crm_service=CRMService(
                permission, repository=crm_repo, audit_log=audit
            ),
            finance_service=FinanceService(
                permission,
                repository=InMemoryFinanceRepository(tenant_id=TENANT),
                audit_log=audit,
                ar_invoice_reader=_CRMInvoiceReader(crm_repo),
            ),
        )
    )


def _issued_invoice(client: TestClient) -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": f"N1-{uuid4().hex[:8]}", "display_name": "N1 API"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "N1 Opp"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={"opportunity_id": opportunity["id"], "title": "N1 Req"},
    ).json()["data"]
    quote = client.post(
        "/v1/crm/quotes",
        headers=_headers(),
        json={"requirement_id": requirement["id"]},
    ).json()["data"]
    assert (
        client.post(
            f"/v1/crm/quotes/{quote['id']}/lines",
            headers=_headers(),
            json={"description": "line", "quantity": "2", "unit_price": "10"},
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"/v1/crm/quotes/{quote['id']}/issue",
            headers=_headers(),
            json={"idempotency_key": str(uuid4()), "human_confirm": True},
        ).status_code
        == 200
    )
    conversion = client.post(
        f"/v1/crm/quotes/{quote['id']}/convert",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    sales_order = client.post(
        f"/v1/crm/conversions/{conversion['id']}/sales-order",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    sales_order = client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/confirm",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    ).json()["data"]
    delivery_order = client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/delivery-order",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    assert (
        client.post(
            f"/v1/crm/delivery-orders/{delivery_order['id']}/release",
            headers=_headers(),
            json={"idempotency_key": str(uuid4()), "human_confirm": True},
        ).status_code
        == 200
    )
    invoice = client.post(
        f"/v1/crm/delivery-orders/{delivery_order['id']}/ar-invoice",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    issued = client.post(
        f"/v1/crm/ar-invoices/{invoice['id']}/issue",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert issued.status_code == 200
    return issued.json()["data"]


def test_g312_credit_note_create_issue_round_trip() -> None:
    client = _client()
    invoice = _issued_invoice(client)
    created = client.post(
        "/v1/finance/credit-notes",
        headers=_headers(),
        json={
            "invoice_id": invoice["id"],
            "amount": "5.00",
            "idempotency_key": str(uuid4()),
        },
    )
    assert created.status_code == 201
    note = created.json()["data"]
    assert note["status"] == "draft"
    assert note["ar_invoice_id"] == invoice["id"]
    issued = client.post(
        f"/v1/finance/credit-notes/{note['id']}/issue",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert issued.status_code == 200
    assert issued.json()["data"]["status"] == "issued"
    fetched = client.get(
        f"/v1/finance/credit-notes/{note['id']}", headers=_headers()
    )
    assert fetched.status_code == 200
    assert fetched.json()["data"]["status"] == "issued"


def test_g312_rejects_context_override() -> None:
    client = _client()
    invoice = _issued_invoice(client)
    response = client.post(
        "/v1/finance/credit-notes",
        headers=_headers(),
        json={
            "invoice_id": invoice["id"],
            "amount": "1.00",
            "idempotency_key": str(uuid4()),
            "tenant_id": str(uuid4()),
        },
    )
    assert response.status_code == 422


def test_g312_openapi_forbids_gl_journal_psp_refund_tax_filing() -> None:
    spec = _client().get("/openapi.json").json()
    assert "/v1/finance/credit-notes" in spec["paths"]
    assert "/v1/finance/credit-notes/{credit_note_id}/issue" in spec["paths"]
    paths = " ".join(
        path
        for path in spec["paths"]
        if path.startswith("/v1/finance/credit-notes")
    ).casefold()
    for forbidden in (
        "gl",
        "journal",
        "psp",
        "refund",
        "tax-filing",
        "tax_filing",
        "coa",
        "period-close",
        "write-off",
    ):
        assert forbidden not in paths
    assert (
        spec["components"]["schemas"]["CreateARCreditNoteRequest"][
            "additionalProperties"
        ]
        is False
    )
