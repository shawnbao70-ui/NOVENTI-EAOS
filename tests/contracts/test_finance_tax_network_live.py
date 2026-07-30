"""PHX-G328 Finance Tax-NET live tax authority adapter contracts."""

from __future__ import annotations

import json
import socket
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode, KernelError
from noventi.crm.repository import InMemoryCRMRepository  # noqa: F401
from noventi.finance.repository import InMemoryFinanceRepository
from noventi.finance.service import (
    TAX_AUTHORITY_POLICY_RESOURCE,
    TAX_INVOICE_RESOURCE,
    TAX_RATE_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
    RejectAllTaxAuthority,
)
from noventi.finance.tax_authority_adapter import (
    HttpTaxAuthorityAdapter,
    NetworkTaxAuthorityAdapter,
    resolve_tax_authority_port,
    tax_authority_adapter_status,
    tax_network_enabled,
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
        correlation_id=f"corr-g328-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(
    ctx: ExecutionContext, *, tax_authority_port=None
) -> tuple[FinanceService, ARInvoiceSnapshot]:
    assert ctx.tenant_id is not None
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_Eligibility(),
    )
    for resource, actions in (
        (TAX_INVOICE_RESOURCE, {"create", "read", "issue", "void"}),
        (TAX_RATE_RESOURCE, {"create", "read", "archive"}),
        (TAX_AUTHORITY_POLICY_RESOURCE, {"read", "update"}),
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
    if tax_authority_port is not None:
        kwargs["tax_authority_port"] = tax_authority_port
    return FinanceService(permission, **kwargs), invoice


def _clear_tax_env(monkeypatch) -> None:
    for name in (
        "EAOS_TAX_NETWORK",
        "ENABLE_TAX_NETWORK",
        "EAOS_TAX_AUTHORITY_URL",
        "EAOS_TAX_AUTHORITY_BEARER",
        "EAOS_TAX_AUTHORITY_TIMEOUT_SEC",
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


def test_g328_default_live_transport_false(monkeypatch) -> None:
    _clear_tax_env(monkeypatch)
    assert tax_network_enabled() is False
    status = tax_authority_adapter_status()
    assert status.network_flag_enabled is False
    assert status.adapter_kind == "reject_all"
    assert status.live_transport is False
    assert status.endpoint_configured is False
    assert isinstance(resolve_tax_authority_port(), RejectAllTaxAuthority)


def test_g328_flag_on_no_url_still_stub(monkeypatch) -> None:
    _clear_tax_env(monkeypatch)
    monkeypatch.setenv("ENABLE_TAX_NETWORK", "1")
    status = tax_authority_adapter_status()
    assert status.network_flag_enabled is True
    assert status.adapter_kind == "network_stub"
    assert status.live_transport is False
    assert status.endpoint_configured is False
    port = resolve_tax_authority_port()
    assert isinstance(port, NetworkTaxAuthorityAdapter)

    ctx = _ctx()
    service, invoice = _service(ctx, tax_authority_port=port)
    assert service.create_tax_rate(
        ctx,
        tax_code="CN_VAT",
        tax_name="CN VAT",
        rate_percent=Decimal("13.00"),
    ).ok
    assert service.set_tax_authority_policy(
        ctx, tax_authority_required=True, expected_version=0
    ).ok
    draft = service.create_tax_invoice(
        ctx,
        invoice_id=invoice.id,
        amount=invoice.total_amount,
        idempotency_key=uuid4(),
        tax_code="CN_VAT",
    )
    assert draft.data is not None
    rejected = service.issue_tax_invoice(
        ctx,
        tax_invoice_id=draft.data.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert rejected.error_code == ErrorCode.COMMON_CONFLICT
    assert "not configured" in (rejected.error_message or "")


def test_g328_flag_on_with_url_mocked_success(monkeypatch) -> None:
    _clear_tax_env(monkeypatch)
    monkeypatch.setenv("ENABLE_TAX_NETWORK", "1")
    monkeypatch.setenv(
        "EAOS_TAX_AUTHORITY_URL", "https://tax.example.test/validate"
    )
    monkeypatch.setenv("EAOS_TAX_AUTHORITY_BEARER", "secret-token-never-log")

    captured: dict = {}

    def fake_urlopen(request, timeout=5):  # type: ignore[no-untyped-def]
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["method"] = request.get_method()
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["authorization"] = request.get_header("Authorization")
        payload = {
            "authority_ref": "auth-ref-g328",
            "authority_status": "accepted",
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

    status = tax_authority_adapter_status()
    assert status.adapter_kind == "http_live"
    assert status.live_transport is True
    assert status.endpoint_configured is True
    port = resolve_tax_authority_port()
    assert isinstance(port, HttpTaxAuthorityAdapter)

    ctx = _ctx()
    service, invoice = _service(ctx, tax_authority_port=port)
    assert service.create_tax_rate(
        ctx,
        tax_code="CN_VAT",
        tax_name="CN VAT",
        rate_percent=Decimal("13.00"),
    ).ok
    assert service.set_tax_authority_policy(
        ctx, tax_authority_required=True, expected_version=0
    ).ok
    draft = service.create_tax_invoice(
        ctx,
        invoice_id=invoice.id,
        amount=invoice.total_amount,
        idempotency_key=uuid4(),
        tax_code="CN_VAT",
    )
    assert draft.data is not None
    issued = service.issue_tax_invoice(
        ctx,
        tax_invoice_id=draft.data.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert issued.ok and issued.data is not None
    assert issued.data.authority_ref == "auth-ref-g328"
    assert issued.data.authority_status == "accepted"
    assert captured["url"] == "https://tax.example.test/validate"
    assert captured["method"] == "POST"
    assert captured["body"]["tax_code"] == "CN_VAT"
    assert captured["body"]["currency"] == "USD"
    assert captured["authorization"] == "Bearer secret-token-never-log"


def test_g328_flag_on_with_url_mocked_failure(monkeypatch) -> None:
    _clear_tax_env(monkeypatch)
    monkeypatch.setenv("EAOS_TAX_NETWORK", "yes")
    monkeypatch.setenv(
        "EAOS_TAX_AUTHORITY_URL", "https://tax.example.test/validate"
    )

    def fake_urlopen(request, timeout=5):  # type: ignore[no-untyped-def]
        raise TimeoutError("simulated")

    def forbid_socket(*_a, **_k):  # type: ignore[no-untyped-def]
        raise AssertionError("real socket to external hosts is forbidden")

    monkeypatch.setattr(
        "noventi.finance.tax_authority_adapter.urllib.request.urlopen",
        fake_urlopen,
    )
    monkeypatch.setattr(socket, "create_connection", forbid_socket)

    port = resolve_tax_authority_port()
    assert isinstance(port, HttpTaxAuthorityAdapter)
    ctx = _ctx()
    service, invoice = _service(ctx, tax_authority_port=port)
    assert service.create_tax_rate(
        ctx,
        tax_code="CN_VAT",
        tax_name="CN VAT",
        rate_percent=Decimal("13.00"),
    ).ok
    assert service.set_tax_authority_policy(
        ctx, tax_authority_required=True, expected_version=0
    ).ok
    draft = service.create_tax_invoice(
        ctx,
        invoice_id=invoice.id,
        amount=invoice.total_amount,
        idempotency_key=uuid4(),
        tax_code="CN_VAT",
    )
    assert draft.data is not None
    rejected = service.issue_tax_invoice(
        ctx,
        tax_invoice_id=draft.data.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert rejected.error_code == ErrorCode.COMMON_CONFLICT
    assert "network request failed" in (rejected.error_message or "")
    assert "secret" not in (rejected.error_message or "").casefold()


def test_g328_http_adapter_bad_json_fail_closed(monkeypatch) -> None:
    _clear_tax_env(monkeypatch)

    def fake_urlopen(request, timeout=5):  # type: ignore[no-untyped-def]
        return _FakeHttpResponse(status=200, body=b"not-json")

    monkeypatch.setattr(
        "noventi.finance.tax_authority_adapter.urllib.request.urlopen",
        fake_urlopen,
    )
    adapter = HttpTaxAuthorityAdapter(
        url="https://tax.example.test/validate",
        bearer="do-not-leak",
    )
    from noventi.finance.models import TaxInvoice, TaxInvoiceStatus, TaxRate, TaxRateStatus
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    tax_invoice = TaxInvoice(
        id=uuid4(),
        tenant_id=uuid4(),
        customer_id=uuid4(),
        ar_invoice_id=uuid4(),
        ar_invoice_version=1,
        code="TI-1",
        currency="USD",
        amount=Decimal("10.00"),
        idempotency_key=uuid4(),
        status=TaxInvoiceStatus.DRAFT,
        created_at=now,
        tax_code="CN_VAT",
    )
    tax_rate = TaxRate(
        id=uuid4(),
        tenant_id=tax_invoice.tenant_id,
        tax_code="CN_VAT",
        tax_name="CN VAT",
        rate_percent=Decimal("13.00"),
        status=TaxRateStatus.ACTIVE,
        created_at=now,
        updated_at=now,
    )
    with pytest.raises(KernelError) as exc_info:
        adapter.validate_rate(tax_invoice=tax_invoice, tax_rate=tax_rate)
    assert exc_info.value.code == ErrorCode.COMMON_CONFLICT
    assert "do-not-leak" not in str(exc_info.value)


def test_g328_url_without_flag_not_live(monkeypatch) -> None:
    _clear_tax_env(monkeypatch)
    monkeypatch.setenv(
        "EAOS_TAX_AUTHORITY_URL", "https://tax.example.test/validate"
    )
    status = tax_authority_adapter_status()
    assert status.endpoint_configured is True
    assert status.network_flag_enabled is False
    assert status.live_transport is False
    assert status.adapter_kind == "reject_all"
    assert isinstance(resolve_tax_authority_port(), RejectAllTaxAuthority)


def test_g328_foundation_tip_unchanged() -> None:
    from pathlib import Path

    versions = Path("alembic/versions")
    # Tax-NET added no migration; 0059 remains in the linear chain.
    assert (versions / "0059_crm_return_authorization_g325.py").exists()
