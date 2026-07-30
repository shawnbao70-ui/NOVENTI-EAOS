"""PHX-G310 Finance AR Receipt HTTP contracts."""

from __future__ import annotations

from dataclasses import replace
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
    AR_RECEIPT_RESOURCE,
    AR_WRITE_OFF_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
)
from noventi.purchase.repository import InMemoryPurchaseRepository
from noventi.purchase.service import (
    AP_BILL_RESOURCE,
    AP_PAYMENT_RESOURCE,
    AP_WRITE_OFF_RESOURCE,
    SUPPLIER_RESOURCE,
    PurchaseService,
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
            functional_currency=invoice.functional_currency,
            fx_rate=invoice.fx_rate,
        )

    def list_ar_invoice_snapshots_for_customer(
        self, customer_id: UUID
    ) -> list[ARInvoiceSnapshot]:
        return [
            snapshot
            for invoice in self._crm.list_ar_invoices_for_customer(customer_id)
            if (
                snapshot := self.get_ar_invoice_snapshot(invoice.id)
            )
            is not None
        ]

    def close_ar_invoice(
        self, *, invoice_id: UUID, expected_version: int
    ) -> None:
        invoice = self._crm.get_ar_invoice(invoice_id)
        if invoice is None or invoice.version != expected_version:
            raise ValueError("AR invoice close conflict")
        from noventi.crm.models import ARInvoiceStatus

        self._crm.save_ar_invoice(
            replace(
                invoice,
                status=ARInvoiceStatus.CLOSED,
                version=invoice.version + 1,
            ),
            expected_version=invoice.version,
        )


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g310",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g310-http",
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
        AR_WRITE_OFF_RESOURCE,
        SUPPLIER_RESOURCE,
        AP_BILL_RESOURCE,
        AP_PAYMENT_RESOURCE,
        AP_WRITE_OFF_RESOURCE,
    ):
        actions = {
            "create",
            "read",
            "update",
            "archive",
            "convert",
            "issue",
            "post",
            "confirm",
            "release",
            "void",
            "apply",
        }
        assert permission.grant(
            _ctx(),
            principal_subject_id=SUBJECT,
            resource_type=resource,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok
    crm_repo = InMemoryCRMRepository(tenant_id=TENANT)
    return TestClient(
        create_app(
            crm_service=CRMService(
                permission,
                repository=crm_repo,
                audit_log=audit,
            ),
            finance_service=FinanceService(
                permission,
                repository=InMemoryFinanceRepository(tenant_id=TENANT),
                audit_log=audit,
                ar_invoice_reader=_CRMInvoiceReader(crm_repo),
                ar_invoice_closer=_CRMInvoiceReader(crm_repo),
            ),
            purchase_service=PurchaseService(
                permission,
                repository=InMemoryPurchaseRepository(tenant_id=TENANT),
                audit_log=audit,
            ),
        )
    )


def _issued_invoice(client: TestClient) -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": f"F1-{uuid4().hex[:8]}", "display_name": "F1 API Customer"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "F1 Opportunity"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={"opportunity_id": opportunity["id"], "title": "F1 Requirement"},
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
            json={"description": "F1 line", "quantity": "2", "unit_price": "10"},
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


def test_g310_receipt_create_apply_round_trip() -> None:
    client = _client()
    invoice = _issued_invoice(client)
    created = client.post(
        "/v1/finance/receipts",
        headers=_headers(),
        json={
            "customer_id": invoice["customer_id"],
            "amount": invoice["total_amount"],
            "currency": invoice["currency"],
            "idempotency_key": str(uuid4()),
        },
    )
    assert created.status_code == 201
    receipt = created.json()["data"]
    assert receipt["status"] == "draft"
    applied = client.post(
        f"/v1/finance/receipts/{receipt['id']}/apply",
        headers=_headers(),
        json={
            "invoice_id": invoice["id"],
            "idempotency_key": str(uuid4()),
        },
    )
    assert applied.status_code == 200
    body = applied.json()["data"]
    assert body["status"] == "applied"
    assert body["ar_invoice_id"] == invoice["id"]
    fetched = client.get(
        f"/v1/finance/receipts/{receipt['id']}", headers=_headers()
    )
    assert fetched.status_code == 200
    assert fetched.json()["data"]["status"] == "applied"


def test_g310_rejects_context_override() -> None:
    client = _client()
    invoice = _issued_invoice(client)
    response = client.post(
        "/v1/finance/receipts",
        headers=_headers(),
        json={
            "customer_id": invoice["customer_id"],
            "amount": "1.00",
            "currency": invoice["currency"],
            "idempotency_key": str(uuid4()),
            "tenant_id": str(uuid4()),
        },
    )
    assert response.status_code == 422


def test_g310_openapi_forbids_psp_ledger_gl_refund_writeoff() -> None:
    spec = _client().get("/openapi.json").json()
    assert "/v1/finance/receipts" in spec["paths"]
    assert "/v1/finance/receipts/{receipt_id}/apply" in spec["paths"]
    paths = " ".join(
        path
        for path in spec["paths"]
        if path.startswith("/v1/finance/receipts")
    ).casefold()
    for forbidden in (
        "psp",
        "ledger",
        "gl",
        "refund",
        "write-off",
        "write_off",
        "webhook",
        "credit-note",
    ):
        assert forbidden not in paths
    assert (
        spec["components"]["schemas"]["CreateARReceiptRequest"][
            "additionalProperties"
        ]
        is False
    )
    assert (
        spec["components"]["schemas"]["ApplyARReceiptRequest"][
            "additionalProperties"
        ]
        is False
    )
