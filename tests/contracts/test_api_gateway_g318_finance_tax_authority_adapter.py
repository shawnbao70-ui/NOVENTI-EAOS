"""PHX-G318 Finance tax-authority adapter HTTP contracts (NETWORK OFF)."""

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
from noventi.finance.repository import InMemoryFinanceRepository
from noventi.finance.service import (
    TAX_AUTHORITY_POLICY_RESOURCE,
    TAX_INVOICE_RESOURCE,
    TAX_RATE_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
)
from noventi.finance.tax_authority_adapter import resolve_tax_authority_port

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
        correlation_id="corr-g318",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g318-http",
    }


def _client(*, tax_authority_port=None) -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    for resource, actions in (
        (TAX_INVOICE_RESOURCE, {"create", "read", "issue", "void"}),
        (TAX_RATE_RESOURCE, {"create", "read", "archive"}),
        (TAX_AUTHORITY_POLICY_RESOURCE, {"read", "update"}),
    ):
        assert permission.grant(
            _ctx(),
            principal_subject_id=SUBJECT,
            resource_type=resource,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok
    port = (
        tax_authority_port
        if tax_authority_port is not None
        else resolve_tax_authority_port()
    )
    return TestClient(
        create_app(
            finance_service=FinanceService(
                permission,
                repository=InMemoryFinanceRepository(tenant_id=TENANT),
                audit_log=audit,
                ar_invoice_reader=_Invoices(),
                tax_authority_port=port,
            )
        )
    )


def test_g318_adapter_status_default_false(monkeypatch) -> None:
    monkeypatch.delenv("EAOS_TAX_NETWORK", raising=False)
    monkeypatch.delenv("ENABLE_TAX_NETWORK", raising=False)
    monkeypatch.delenv("EAOS_TAX_AUTHORITY_URL", raising=False)
    client = _client()
    response = client.get(
        "/v1/finance/adapters/tax-authority", headers=_headers()
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["network_flag_enabled"] is False
    assert body["adapter_kind"] == "reject_all"
    assert body["live_transport"] is False


def test_g318_openapi_has_status_without_enable_or_filing() -> None:
    spec = _client().get("/openapi.json").json()
    assert "/v1/finance/adapters/tax-authority" in spec["paths"]
    methods = set(spec["paths"]["/v1/finance/adapters/tax-authority"])
    assert "get" in methods
    assert "post" not in methods
    assert "put" not in methods
    assert "patch" not in methods
    paths = " ".join(spec["paths"]).casefold()
    for forbidden in (
        "tax-filing",
        "tax_filing",
        "enable_tax_network",
        "enable-tax-network",
        "live-authority",
        "live_authority",
    ):
        assert forbidden not in paths
    schema = spec["components"]["schemas"]["TaxAuthorityAdapterStatusView"]
    assert schema["additionalProperties"] is False
    assert "network_flag_enabled" in schema["properties"]


def test_g318_flag_on_status_flips_but_issue_fail_closed(monkeypatch) -> None:
    monkeypatch.delenv("EAOS_TAX_AUTHORITY_URL", raising=False)
    monkeypatch.setenv("ENABLE_TAX_NETWORK", "1")
    client = _client(tax_authority_port=resolve_tax_authority_port())
    status = client.get(
        "/v1/finance/adapters/tax-authority", headers=_headers()
    )
    assert status.status_code == 200
    assert status.json()["data"]["network_flag_enabled"] is True
    assert status.json()["data"]["adapter_kind"] == "network_stub"
    assert status.json()["data"]["live_transport"] is False

    assert (
        client.put(
            "/v1/finance/policies/tax-authority",
            headers=_headers(),
            json={"tax_authority_required": True, "expected_version": 0},
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/v1/finance/tax-rates",
            headers=_headers(),
            json={
                "tax_code": "CN_VAT",
                "tax_name": "CN VAT",
                "rate_percent": "13.0000",
            },
        ).status_code
        == 201
    )
    created = client.post(
        "/v1/finance/tax-invoices",
        headers=_headers(),
        json={
            "invoice_id": str(INVOICE),
            "amount": "10.00",
            "idempotency_key": str(uuid4()),
            "tax_code": "CN_VAT",
        },
    )
    assert created.status_code == 201
    tax_invoice_id = created.json()["data"]["id"]
    issued = client.post(
        f"/v1/finance/tax-invoices/{tax_invoice_id}/issue",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert issued.status_code == 409
    detail = issued.json()["detail"]
    assert detail["code"] == "COMMON_CONFLICT"
    assert "not configured" in detail["message"]
