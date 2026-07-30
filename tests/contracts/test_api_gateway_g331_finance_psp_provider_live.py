"""PHX-G331 Finance PSP live network HTTP contracts."""

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
        correlation_id="corr-g331",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g331-http",
    }


def _clear_psp_env(monkeypatch) -> None:
    for name in (
        "EAOS_PSP_PROVIDER",
        "EAOS_PSP_NETWORK",
        "ENABLE_PSP_NETWORK",
        "EAOS_PSP_URL",
        "EAOS_PSP_BEARER",
        "EAOS_PSP_TIMEOUT_SEC",
    ):
        monkeypatch.delenv(name, raising=False)


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


def test_g331_adapter_status_default_false(monkeypatch) -> None:
    _clear_psp_env(monkeypatch)
    client = _client()
    response = client.get("/v1/finance/adapters/psp", headers=_headers())
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["provider"] == "off"
    assert body["network_flag_enabled"] is False
    assert body["adapter_kind"] == "reject_all"
    assert body["live_transport"] is False
    assert body["endpoint_configured"] is False


def test_g331_openapi_status_closed_no_put_enable(monkeypatch) -> None:
    _clear_psp_env(monkeypatch)
    spec = _client().get("/openapi.json").json()
    assert "/v1/finance/adapters/psp" in spec["paths"]
    methods = set(spec["paths"]["/v1/finance/adapters/psp"])
    assert "get" in methods
    assert "post" not in methods
    assert "put" not in methods
    assert "patch" not in methods
    schema = spec["components"]["schemas"]["PspAdapterStatusView"]
    assert schema["additionalProperties"] is False
    props = schema["properties"]
    assert "provider" in props
    assert "network_flag_enabled" in props
    assert "endpoint_configured" in props
    assert "live_transport" in props
    assert set(props["adapter_kind"]["enum"]) == {
        "reject_all",
        "fake",
        "stripe_like_stub",
        "http_live",
    }


def test_g331_flag_provider_no_url_stub_status(monkeypatch) -> None:
    _clear_psp_env(monkeypatch)
    monkeypatch.setenv("EAOS_PSP_PROVIDER", "stripe_like")
    monkeypatch.setenv("ENABLE_PSP_NETWORK", "1")
    client = _client(psp_port=resolve_psp_port())
    status = client.get("/v1/finance/adapters/psp", headers=_headers())
    assert status.status_code == 200
    body = status.json()["data"]
    assert body["provider"] == "stripe_like"
    assert body["network_flag_enabled"] is True
    assert body["adapter_kind"] == "stripe_like_stub"
    assert body["live_transport"] is False
    assert body["endpoint_configured"] is False


def test_g331_flag_provider_url_live_status_and_apply(monkeypatch) -> None:
    _clear_psp_env(monkeypatch)
    monkeypatch.setenv("EAOS_PSP_PROVIDER", "stripe_like")
    monkeypatch.setenv("ENABLE_PSP_NETWORK", "1")
    monkeypatch.setenv("EAOS_PSP_URL", "https://psp.example.test/apply")

    def fake_urlopen(request, timeout=5):  # type: ignore[no-untyped-def]
        payload = {
            "psp_ref": "gw-psp-ref-g331",
            "psp_status": "applied",
        }
        return _FakeHttpResponse(
            status=200, body=json.dumps(payload).encode("utf-8")
        )

    def forbid_socket(*_a, **_k):  # type: ignore[no-untyped-def]
        raise AssertionError("real socket to external hosts is forbidden")

    monkeypatch.setattr(
        "noventi.finance.psp_provider_adapter.urllib.request.urlopen",
        fake_urlopen,
    )
    monkeypatch.setattr(socket, "create_connection", forbid_socket)

    client = _client(psp_port=resolve_psp_port())
    status = client.get("/v1/finance/adapters/psp", headers=_headers())
    assert status.status_code == 200
    body = status.json()["data"]
    assert body["adapter_kind"] == "http_live"
    assert body["live_transport"] is True
    assert body["endpoint_configured"] is True

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
    assert applied.status_code == 200
    data = applied.json()["data"]
    assert data["psp_ref"] == "gw-psp-ref-g331"
    assert data["psp_status"] == "applied"


def test_g331_flag_provider_url_failure_conflict(monkeypatch) -> None:
    _clear_psp_env(monkeypatch)
    monkeypatch.setenv("EAOS_PSP_PROVIDER", "stripe_like")
    monkeypatch.setenv("ENABLE_PSP_NETWORK", "1")
    monkeypatch.setenv("EAOS_PSP_URL", "https://psp.example.test/apply")

    def fake_urlopen(request, timeout=5):  # type: ignore[no-untyped-def]
        raise OSError("simulated network down")

    monkeypatch.setattr(
        "noventi.finance.psp_provider_adapter.urllib.request.urlopen",
        fake_urlopen,
    )
    monkeypatch.setattr(
        socket,
        "create_connection",
        lambda *_a, **_k: (_ for _ in ()).throw(
            AssertionError("real socket forbidden")
        ),
    )

    client = _client(psp_port=resolve_psp_port())
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
    assert "network request failed" in detail["message"]
