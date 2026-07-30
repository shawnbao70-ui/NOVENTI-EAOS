"""PHX-G328 Finance tax-authority live network HTTP contracts."""

from __future__ import annotations

import json
import socket
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
        correlation_id="corr-g328",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g328-http",
    }


def _clear_tax_env(monkeypatch) -> None:
    for name in (
        "EAOS_TAX_NETWORK",
        "ENABLE_TAX_NETWORK",
        "EAOS_TAX_AUTHORITY_URL",
        "EAOS_TAX_AUTHORITY_BEARER",
        "EAOS_TAX_AUTHORITY_TIMEOUT_SEC",
    ):
        monkeypatch.delenv(name, raising=False)


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


class _FakeHttpResponse:
    def __init__(self, *, status: int, body: bytes) -> None:
        self.status = status
        self._body = body

    def getcode(self) -> int:
        return self.status

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _FakeHttpResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None


def test_g328_adapter_status_default_false(monkeypatch) -> None:
    _clear_tax_env(monkeypatch)
    client = _client()
    response = client.get(
        "/v1/finance/adapters/tax-authority", headers=_headers()
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["network_flag_enabled"] is False
    assert body["adapter_kind"] == "reject_all"
    assert body["live_transport"] is False
    assert body["endpoint_configured"] is False


def test_g328_openapi_status_closed_no_put_enable(monkeypatch) -> None:
    _clear_tax_env(monkeypatch)
    spec = _client().get("/openapi.json").json()
    assert "/v1/finance/adapters/tax-authority" in spec["paths"]
    methods = set(spec["paths"]["/v1/finance/adapters/tax-authority"])
    assert "get" in methods
    assert "post" not in methods
    assert "put" not in methods
    assert "patch" not in methods
    schema = spec["components"]["schemas"]["TaxAuthorityAdapterStatusView"]
    assert schema["additionalProperties"] is False
    props = schema["properties"]
    assert "network_flag_enabled" in props
    assert "endpoint_configured" in props
    assert "live_transport" in props
    assert set(props["adapter_kind"]["enum"]) == {
        "reject_all",
        "network_stub",
        "http_live",
    }


def test_g328_flag_on_no_url_stub_status(monkeypatch) -> None:
    _clear_tax_env(monkeypatch)
    monkeypatch.setenv("ENABLE_TAX_NETWORK", "1")
    client = _client(tax_authority_port=resolve_tax_authority_port())
    status = client.get(
        "/v1/finance/adapters/tax-authority", headers=_headers()
    )
    assert status.status_code == 200
    body = status.json()["data"]
    assert body["network_flag_enabled"] is True
    assert body["adapter_kind"] == "network_stub"
    assert body["live_transport"] is False
    assert body["endpoint_configured"] is False


def test_g328_flag_on_url_live_status_and_issue(monkeypatch) -> None:
    _clear_tax_env(monkeypatch)
    monkeypatch.setenv("ENABLE_TAX_NETWORK", "1")
    monkeypatch.setenv(
        "EAOS_TAX_AUTHORITY_URL", "https://tax.example.test/validate"
    )

    def fake_urlopen(request, timeout=5):  # type: ignore[no-untyped-def]
        payload = {
            "authority_ref": "gw-auth-ref-g328",
            "authority_status": "validated",
        }
        return _FakeHttpResponse(
            status=200, body=json.dumps(payload).encode("utf-8")
        )

    def forbid_socket(*_a, **_k):  # type: ignore[no-untyped-def]
        raise AssertionError("real socket to external hosts is forbidden")

    monkeypatch.setattr(
        "noventi.finance.tax_authority_adapter.urllib.request.urlopen",
        fake_urlopen,
    )
    monkeypatch.setattr(socket, "create_connection", forbid_socket)

    client = _client(tax_authority_port=resolve_tax_authority_port())
    status = client.get(
        "/v1/finance/adapters/tax-authority", headers=_headers()
    )
    assert status.status_code == 200
    body = status.json()["data"]
    assert body["adapter_kind"] == "http_live"
    assert body["live_transport"] is True
    assert body["endpoint_configured"] is True

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
    assert issued.status_code == 200
    data = issued.json()["data"]
    assert data["authority_ref"] == "gw-auth-ref-g328"
    assert data["authority_status"] == "validated"


def test_g328_flag_on_url_failure_conflict(monkeypatch) -> None:
    _clear_tax_env(monkeypatch)
    monkeypatch.setenv("ENABLE_TAX_NETWORK", "1")
    monkeypatch.setenv(
        "EAOS_TAX_AUTHORITY_URL", "https://tax.example.test/validate"
    )

    def fake_urlopen(request, timeout=5):  # type: ignore[no-untyped-def]
        raise OSError("simulated network down")

    monkeypatch.setattr(
        "noventi.finance.tax_authority_adapter.urllib.request.urlopen",
        fake_urlopen,
    )
    monkeypatch.setattr(
        socket,
        "create_connection",
        lambda *_a, **_k: (_ for _ in ()).throw(
            AssertionError("real socket forbidden")
        ),
    )

    client = _client(tax_authority_port=resolve_tax_authority_port())
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
    assert "network request failed" in detail["message"]
