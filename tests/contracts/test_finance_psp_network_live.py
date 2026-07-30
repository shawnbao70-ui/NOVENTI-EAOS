"""PHX-G331 Finance PSP-NET live provider adapter contracts."""

from __future__ import annotations

import json
import socket
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode, KernelError
from noventi.crm.repository import InMemoryCRMRepository  # noqa: F401
from noventi.finance.models import ARReceipt, ReceiptStatus
from noventi.finance.psp_provider_adapter import (
    HttpPspAdapter,
    StripeLikePspAdapter,
    psp_adapter_status,
    psp_network_enabled,
    resolve_psp_port,
)
from noventi.finance.repository import InMemoryFinanceRepository
from noventi.finance.service import (
    AR_RECEIPT_RESOURCE,
    RECEIPT_PSP_POLICY_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
    InMemoryFakePsp,
    RejectAllPsp,
)


class _Invoices:
    def __init__(self, invoice: ARInvoiceSnapshot) -> None:
        self.invoice = invoice

    def get_ar_invoice_snapshot(
        self, invoice_id: UUID
    ) -> ARInvoiceSnapshot | None:
        return self.invoice if invoice_id == self.invoice.id else None


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=uuid4(),
        correlation_id=f"corr-g331-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(
    ctx: ExecutionContext, *, psp_port=None
) -> tuple[FinanceService, ARInvoiceSnapshot]:
    assert ctx.tenant_id is not None
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_Eligibility(),
    )
    for resource, actions in (
        (AR_RECEIPT_RESOURCE, {"create", "read", "apply"}),
        (RECEIPT_PSP_POLICY_RESOURCE, {"read", "update"}),
    ):
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=resource,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok
    invoice = ARInvoiceSnapshot(
        id=uuid4(),
        tenant_id=ctx.tenant_id,
        customer_id=uuid4(),
        currency="USD",
        total_amount=Decimal("10.00"),
        status="issued",
        version=1,
    )
    kwargs: dict = {
        "repository": InMemoryFinanceRepository(tenant_id=ctx.tenant_id),
        "audit_log": audit,
        "ar_invoice_reader": _Invoices(invoice),
    }
    if psp_port is not None:
        kwargs["psp_port"] = psp_port
    return FinanceService(permission, **kwargs), invoice


def _receipt(service: FinanceService, ctx: ExecutionContext, invoice: ARInvoiceSnapshot):
    result = service.create_receipt(
        ctx,
        customer_id=invoice.customer_id,
        amount=invoice.total_amount,
        currency=invoice.currency,
        idempotency_key=uuid4(),
    )
    assert result.data is not None
    return result.data


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


def test_g331_default_live_transport_false(monkeypatch) -> None:
    _clear_psp_env(monkeypatch)
    assert psp_network_enabled() is False
    status = psp_adapter_status()
    assert status.provider == "off"
    assert status.network_flag_enabled is False
    assert status.adapter_kind == "reject_all"
    assert status.live_transport is False
    assert status.endpoint_configured is False
    assert isinstance(resolve_psp_port(), RejectAllPsp)


def test_g331_flag_provider_no_url_still_stub(monkeypatch) -> None:
    _clear_psp_env(monkeypatch)
    monkeypatch.setenv("EAOS_PSP_PROVIDER", "stripe_like")
    monkeypatch.setenv("ENABLE_PSP_NETWORK", "1")
    status = psp_adapter_status()
    assert status.network_flag_enabled is True
    assert status.adapter_kind == "stripe_like_stub"
    assert status.live_transport is False
    assert status.endpoint_configured is False
    port = resolve_psp_port()
    assert isinstance(port, StripeLikePspAdapter)

    ctx = _ctx()
    service, invoice = _service(ctx, psp_port=port)
    assert service.set_receipt_psp_policy(
        ctx, receipt_psp_required=True, expected_version=0
    ).ok
    receipt = _receipt(service, ctx, invoice)
    rejected = service.apply_receipt_to_invoice(
        ctx,
        receipt_id=receipt.id,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
    )
    assert rejected.error_code == ErrorCode.COMMON_CONFLICT
    assert "not configured" in (rejected.error_message or "")


def test_g331_flag_provider_url_mocked_success(monkeypatch) -> None:
    _clear_psp_env(monkeypatch)
    monkeypatch.setenv("EAOS_PSP_PROVIDER", "stripe_like")
    monkeypatch.setenv("ENABLE_PSP_NETWORK", "1")
    monkeypatch.setenv("EAOS_PSP_URL", "https://psp.example.test/apply")
    monkeypatch.setenv("EAOS_PSP_BEARER", "secret-token-never-log")

    captured: dict = {}

    def fake_urlopen(request, timeout=5):  # type: ignore[no-untyped-def]
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["method"] = request.get_method()
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["authorization"] = request.get_header("Authorization")
        payload = {
            "psp_ref": "psp-ref-g331",
            "psp_status": "captured",
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

    status = psp_adapter_status()
    assert status.adapter_kind == "http_live"
    assert status.live_transport is True
    assert status.endpoint_configured is True
    port = resolve_psp_port()
    assert isinstance(port, HttpPspAdapter)

    ctx = _ctx()
    service, invoice = _service(ctx, psp_port=port)
    assert service.set_receipt_psp_policy(
        ctx, receipt_psp_required=True, expected_version=0
    ).ok
    receipt = _receipt(service, ctx, invoice)
    applied = service.apply_receipt_to_invoice(
        ctx,
        receipt_id=receipt.id,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
    )
    assert applied.ok and applied.data is not None
    assert applied.data.psp_ref == "psp-ref-g331"
    assert applied.data.psp_status == "captured"
    assert captured["url"] == "https://psp.example.test/apply"
    assert captured["method"] == "POST"
    assert captured["body"]["receipt_id"] == str(receipt.id)
    assert captured["body"]["invoice_id"] == str(invoice.id)
    assert captured["body"]["currency"] == "USD"
    assert captured["body"]["customer_id"] == str(invoice.customer_id)
    assert captured["authorization"] == "Bearer secret-token-never-log"


def test_g331_flag_provider_url_mocked_failure(monkeypatch) -> None:
    _clear_psp_env(monkeypatch)
    monkeypatch.setenv("EAOS_PSP_PROVIDER", "stripe_like")
    monkeypatch.setenv("EAOS_PSP_NETWORK", "yes")
    monkeypatch.setenv("EAOS_PSP_URL", "https://psp.example.test/apply")

    def fake_urlopen(request, timeout=5):  # type: ignore[no-untyped-def]
        raise TimeoutError("simulated")

    def forbid_socket(*_a, **_k):  # type: ignore[no-untyped-def]
        raise AssertionError("real socket to external hosts is forbidden")

    monkeypatch.setattr(
        "noventi.finance.psp_provider_adapter.urllib.request.urlopen",
        fake_urlopen,
    )
    monkeypatch.setattr(socket, "create_connection", forbid_socket)

    port = resolve_psp_port()
    assert isinstance(port, HttpPspAdapter)
    ctx = _ctx()
    service, invoice = _service(ctx, psp_port=port)
    assert service.set_receipt_psp_policy(
        ctx, receipt_psp_required=True, expected_version=0
    ).ok
    receipt = _receipt(service, ctx, invoice)
    rejected = service.apply_receipt_to_invoice(
        ctx,
        receipt_id=receipt.id,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
    )
    assert rejected.error_code == ErrorCode.COMMON_CONFLICT
    assert "network request failed" in (rejected.error_message or "")
    assert "secret" not in (rejected.error_message or "").casefold()


def test_g331_http_adapter_bad_json_fail_closed(monkeypatch) -> None:
    _clear_psp_env(monkeypatch)

    def fake_urlopen(request, timeout=5):  # type: ignore[no-untyped-def]
        return _FakeHttpResponse(status=200, body=b"not-json")

    monkeypatch.setattr(
        "noventi.finance.psp_provider_adapter.urllib.request.urlopen",
        fake_urlopen,
    )
    adapter = HttpPspAdapter(
        url="https://psp.example.test/apply",
        bearer="do-not-leak",
    )
    now = datetime.now(timezone.utc)
    receipt = ARReceipt(
        id=uuid4(),
        tenant_id=uuid4(),
        customer_id=uuid4(),
        code="R-1",
        currency="USD",
        amount=Decimal("10.00"),
        idempotency_key=uuid4(),
        status=ReceiptStatus.DRAFT,
        created_at=now,
    )
    invoice = ARInvoiceSnapshot(
        id=uuid4(),
        tenant_id=receipt.tenant_id,
        customer_id=receipt.customer_id,
        currency="USD",
        total_amount=Decimal("10.00"),
        status="issued",
        version=1,
    )
    with pytest.raises(KernelError) as exc_info:
        adapter.apply_receipt(receipt=receipt, invoice=invoice)
    assert exc_info.value.code == ErrorCode.COMMON_CONFLICT
    assert "do-not-leak" not in str(exc_info.value)


def test_g331_fake_ignores_network_and_url(monkeypatch) -> None:
    _clear_psp_env(monkeypatch)
    monkeypatch.setenv("EAOS_PSP_PROVIDER", "fake")
    monkeypatch.setenv("ENABLE_PSP_NETWORK", "1")
    monkeypatch.setenv("EAOS_PSP_URL", "https://psp.example.test/apply")
    status = psp_adapter_status()
    assert status.adapter_kind == "fake"
    assert status.live_transport is False
    assert status.endpoint_configured is True
    assert isinstance(resolve_psp_port(), InMemoryFakePsp)


def test_g331_url_without_flag_not_live(monkeypatch) -> None:
    _clear_psp_env(monkeypatch)
    monkeypatch.setenv("EAOS_PSP_PROVIDER", "stripe_like")
    monkeypatch.setenv("EAOS_PSP_URL", "https://psp.example.test/apply")
    status = psp_adapter_status()
    assert status.endpoint_configured is True
    assert status.network_flag_enabled is False
    assert status.live_transport is False
    assert status.adapter_kind == "stripe_like_stub"
    assert isinstance(resolve_psp_port(), StripeLikePspAdapter)


def test_g331_foundation_tip_unchanged() -> None:
    versions = Path("alembic/versions")
    # PSP-NET added no migration; tip remains 0061.
    assert (versions / "0061_crm_return_restock_g330.py").exists()
