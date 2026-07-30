"""PHX-G313 Customer360 HTTP contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.customer360 import (
    CUSTOMER360_RESOURCE,
    AssembledCustomer360Repository,
    Customer360Service,
)
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
        correlation_id="corr-g313",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g313-http",
    }


def _client(*, grant_360: bool = True) -> TestClient:
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
    if grant_360:
        assert permission.grant(
            _ctx(),
            principal_subject_id=SUBJECT,
            resource_type=CUSTOMER360_RESOURCE,
            actions={"read"},
            scope_level=ScopeLevel.TENANT,
        ).ok
    crm_repo = InMemoryCRMRepository(tenant_id=TENANT)
    finance_repo = InMemoryFinanceRepository(tenant_id=TENANT)
    return TestClient(
        create_app(
            crm_service=CRMService(
                permission, repository=crm_repo, audit_log=audit
            ),
            customer360_service=Customer360Service(
                permission,
                repository=AssembledCustomer360Repository(
                    crm_repo, finance_repo
                ),
            ),
            finance_service=FinanceService(
                permission,
                repository=finance_repo,
                audit_log=audit,
                ar_invoice_reader=_CRMInvoiceReader(crm_repo),
            ),
        )
    )


def _seed_customer_with_opportunity(client: TestClient) -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": f"Z1-{uuid4().hex[:8]}", "display_name": "Z1 API"},
    ).json()["data"]
    assert (
        client.post(
            "/v1/crm/opportunities",
            headers=_headers(),
            json={"customer_id": customer["id"], "title": "Z1 Opp"},
        ).status_code
        == 201
    )
    return customer


def test_g313_customer360_read_round_trip() -> None:
    client = _client()
    customer = _seed_customer_with_opportunity(client)
    response = client.get(
        f"/v1/crm/customers/{customer['id']}/360", headers=_headers()
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["customer_id"] == customer["id"]
    assert body["customer_code"] == customer["code"]
    assert body["display_name"] == customer["display_name"]
    assert body["commercial_hold"] is False
    assert body["opportunities_count"] == 1
    assert body["open_sales_orders_count"] == 0
    assert body["open_delivery_orders_count"] == 0
    assert body["invoice_traces"] == []
    assert body["applied_receipt_traces"] == []
    assert body["credit_note_traces"] == []


def test_g313_default_deny_without_grant() -> None:
    client = _client(grant_360=False)
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": f"Z1D-{uuid4().hex[:8]}", "display_name": "Deny"},
    ).json()["data"]
    response = client.get(
        f"/v1/crm/customers/{customer['id']}/360", headers=_headers()
    )
    assert response.status_code == 403


def test_g313_no_write_methods_on_360() -> None:
    client = _client()
    customer = _seed_customer_with_opportunity(client)
    path = f"/v1/crm/customers/{customer['id']}/360"
    assert client.post(path, headers=_headers(), json={}).status_code == 405
    assert client.put(path, headers=_headers(), json={}).status_code == 405
    assert client.patch(path, headers=_headers(), json={}).status_code == 405
    assert client.delete(path, headers=_headers()).status_code == 405


def test_g313_openapi_forbids_brain_twin_commission_payout_writes() -> None:
    spec = _client().get("/openapi.json").json()
    path_key = "/v1/crm/customers/{customer_id}/360"
    assert path_key in spec["paths"]
    assert list(spec["paths"][path_key].keys()) == ["get"]
    paths = " ".join(
        path
        for path in spec["paths"]
        if path.startswith("/v1/crm/customers") and path.endswith("/360")
    ).casefold()
    for forbidden in (
        "brain",
        "execute",
        "twin",
        "authorize",
        "commission",
        "payout",
    ):
        assert forbidden not in paths
    schemas = spec["components"]["schemas"]
    assert schemas["Customer360View"]["additionalProperties"] is False
    assert schemas["Customer360Envelope"]["additionalProperties"] is False
