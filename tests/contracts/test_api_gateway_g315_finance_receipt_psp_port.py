"""PHX-G315 Finance receipt PSP-policy HTTP contracts."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.repository import InMemoryCRMRepository
from noventi.finance.repository import InMemoryFinanceRepository
from noventi.finance.service import (
    AR_RECEIPT_RESOURCE,
    RECEIPT_PSP_POLICY_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
    InMemoryFakePsp,
)

SUBJECT, TENANT, CUSTOMER, INVOICE = uuid4(), uuid4(), uuid4(), uuid4()


class _Invoices:
    def get_ar_invoice_snapshot(self, invoice_id: UUID) -> ARInvoiceSnapshot | None:
        if invoice_id != INVOICE:
            return None
        return ARInvoiceSnapshot(
            id=INVOICE, tenant_id=TENANT, customer_id=CUSTOMER, currency="USD",
            total_amount=Decimal("10.00"), status="issued", version=1,
        )


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT, subject_type=SubjectType.HUMAN, tenant_id=TENANT,
        correlation_id="corr-g315", request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT), "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT), "X-Correlation-Id": "corr-g315-http",
    }


def _client() -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit, grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    for resource, actions in (
        (AR_RECEIPT_RESOURCE, {"create", "read", "apply"}),
        (RECEIPT_PSP_POLICY_RESOURCE, {"read", "update"}),
    ):
        assert permission.grant(
            _ctx(), principal_subject_id=SUBJECT, resource_type=resource,
            actions=actions, scope_level=ScopeLevel.TENANT,
        ).ok
    return TestClient(create_app(finance_service=FinanceService(
        permission, repository=InMemoryFinanceRepository(tenant_id=TENANT),
        audit_log=audit, ar_invoice_reader=_Invoices(), psp_port=InMemoryFakePsp(),
    )))


def test_g315_policy_endpoint_is_closed_and_psp_state_is_exposed() -> None:
    client = _client()
    default = client.get("/v1/finance/policies/receipt-psp", headers=_headers())
    assert default.status_code == 200
    assert default.json()["data"]["receipt_psp_required"] is False
    updated = client.put(
        "/v1/finance/policies/receipt-psp", headers=_headers(),
        json={"receipt_psp_required": True, "expected_version": 0},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["version"] == 1
    assert client.put(
        "/v1/finance/policies/receipt-psp", headers=_headers(),
        json={"receipt_psp_required": True, "expected_version": 1, "tenant_id": str(uuid4())},
    ).status_code == 422

    created = client.post(
        "/v1/finance/receipts", headers=_headers(), json={
            "customer_id": str(CUSTOMER), "amount": "10.00", "currency": "USD",
            "idempotency_key": str(uuid4()),
        },
    )
    assert created.status_code == 201
    receipt = created.json()["data"]
    applied = client.post(
        f"/v1/finance/receipts/{receipt['id']}/apply", headers=_headers(),
        json={"invoice_id": str(INVOICE), "idempotency_key": str(uuid4())},
    )
    assert applied.status_code == 200
    assert applied.json()["data"]["psp_status"] == "applied"
    assert applied.json()["data"]["psp_ref"].startswith("fake-psp-")

    spec = client.get("/openapi.json").json()
    assert "/v1/finance/policies/receipt-psp" in spec["paths"]
    assert spec["components"]["schemas"]["SetReceiptPspPolicyRequest"]["additionalProperties"] is False
