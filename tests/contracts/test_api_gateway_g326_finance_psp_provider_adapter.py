"""PHX-G326 Finance PSP provider adapter HTTP contracts (NETWORK OFF)."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.repository import InMemoryCRMRepository  # noqa: F401
from noventi.finance.psp_provider_adapter import resolve_psp_port
from noventi.finance.repository import InMemoryFinanceRepository
from noventi.finance.service import (
    AR_RECEIPT_RESOURCE,
    RECEIPT_PSP_POLICY_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
)

SUBJECT, TENANT, CUSTOMER, INVOICE = uuid4(), uuid4(), uuid4(), uuid4()


class _Invoices:
    def get_ar_invoice_snapshot(
        self, invoice_id: UUID
    ) -> ARInvoiceSnapshot | None:
        if invoice_id != INVOICE:
            return None
        return ARInvoiceSnapshot(
            id=INVOICE,
            tenant_id=TENANT,
            customer_id=CUSTOMER,
            currency="USD",
            total_amount=Decimal("10.00"),
            status="issued",
            version=1,
        )


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g326",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g326-http",
    }


def _client(*, psp_port=None) -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    for resource, actions in (
        (AR_RECEIPT_RESOURCE, {"create", "read", "apply"}),
        (RECEIPT_PSP_POLICY_RESOURCE, {"read", "update"}),
    ):
        assert permission.grant(
            _ctx(),
            principal_subject_id=SUBJECT,
            resource_type=resource,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok
    port = psp_port if psp_port is not None else resolve_psp_port()
    return TestClient(
        create_app(
            finance_service=FinanceService(
                permission,
                repository=InMemoryFinanceRepository(tenant_id=TENANT),
                audit_log=audit,
                ar_invoice_reader=_Invoices(),
                psp_port=port,
            )
        )
    )


def test_g326_adapter_status_default_false(monkeypatch) -> None:
    monkeypatch.delenv("EAOS_PSP_PROVIDER", raising=False)
    monkeypatch.delenv("EAOS_PSP_NETWORK", raising=False)
    monkeypatch.delenv("ENABLE_PSP_NETWORK", raising=False)
    monkeypatch.delenv("EAOS_PSP_URL", raising=False)
    client = _client()
    response = client.get("/v1/finance/adapters/psp", headers=_headers())
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["provider"] == "off"
    assert body["network_flag_enabled"] is False
    assert body["adapter_kind"] == "reject_all"
    assert body["live_transport"] is False
    assert body["endpoint_configured"] is False


def test_g326_openapi_has_status_without_enable_network() -> None:
    spec = _client().get("/openapi.json").json()
    assert "/v1/finance/adapters/psp" in spec["paths"]
    methods = set(spec["paths"]["/v1/finance/adapters/psp"])
    assert "get" in methods
    assert "post" not in methods
    assert "put" not in methods
    assert "patch" not in methods
    paths = " ".join(spec["paths"]).casefold()
    for forbidden in (
        "enable_psp_network",
        "enable-psp-network",
        "psp-webhook",
        "psp_webhook",
        "live-psp",
        "live_psp",
    ):
        assert forbidden not in paths
    schema = spec["components"]["schemas"]["PspAdapterStatusView"]
    assert schema["additionalProperties"] is False
    assert "provider" in schema["properties"]
    assert "network_flag_enabled" in schema["properties"]
    assert "live_transport" in schema["properties"]
    assert "endpoint_configured" in schema["properties"]
    assert set(schema["properties"]["adapter_kind"]["enum"]) == {
        "reject_all",
        "fake",
        "stripe_like_stub",
        "http_live",
    }


def test_g326_flag_on_status_flips_but_apply_fail_closed(monkeypatch) -> None:
    monkeypatch.setenv("EAOS_PSP_PROVIDER", "stripe_like")
    monkeypatch.setenv("ENABLE_PSP_NETWORK", "1")
    monkeypatch.delenv("EAOS_PSP_URL", raising=False)
    client = _client(psp_port=resolve_psp_port())
    status = client.get("/v1/finance/adapters/psp", headers=_headers())
    assert status.status_code == 200
    assert status.json()["data"]["provider"] == "stripe_like"
    assert status.json()["data"]["network_flag_enabled"] is True
    assert status.json()["data"]["adapter_kind"] == "stripe_like_stub"
    assert status.json()["data"]["live_transport"] is False
    assert status.json()["data"]["endpoint_configured"] is False

    assert (
        client.put(
            "/v1/finance/policies/receipt-psp",
            headers=_headers(),
            json={"receipt_psp_required": True, "expected_version": 0},
        ).status_code
        == 200
    )
    created = client.post(
        "/v1/finance/receipts",
        headers=_headers(),
        json={
            "customer_id": str(CUSTOMER),
            "amount": "10.00",
            "currency": "USD",
            "idempotency_key": str(uuid4()),
        },
    )
    assert created.status_code == 201
    receipt_id = created.json()["data"]["id"]
    applied = client.post(
        f"/v1/finance/receipts/{receipt_id}/apply",
        headers=_headers(),
        json={
            "invoice_id": str(INVOICE),
            "idempotency_key": str(uuid4()),
        },
    )
    assert applied.status_code == 409
    detail = applied.json()["detail"]
    assert detail["code"] == "COMMON_CONFLICT"
    assert "not configured" in detail["message"]
