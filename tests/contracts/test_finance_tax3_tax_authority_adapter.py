"""PHX-G318 Finance Tax3 tax-authority adapter contracts (NETWORK OFF)."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from noventi.crm.repository import InMemoryCRMRepository  # noqa: F401
from noventi.finance.repository import InMemoryFinanceRepository
from noventi.finance.service import (
    TAX_AUTHORITY_POLICY_RESOURCE,
    TAX_INVOICE_RESOURCE,
    TAX_RATE_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
    InMemoryFakeTaxAuthority,
    RejectAllTaxAuthority,
)
from noventi.finance.tax_authority_adapter import (
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
        correlation_id=f"corr-g318-{uuid4()}",
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


def test_tax3_default_env_is_reject_all(monkeypatch) -> None:
    monkeypatch.delenv("EAOS_TAX_NETWORK", raising=False)
    monkeypatch.delenv("ENABLE_TAX_NETWORK", raising=False)
    monkeypatch.delenv("EAOS_TAX_AUTHORITY_URL", raising=False)
    assert tax_network_enabled() is False
    status = tax_authority_adapter_status()
    assert status.network_flag_enabled is False
    assert status.adapter_kind == "reject_all"
    assert status.live_transport is False
    port = resolve_tax_authority_port()
    assert isinstance(port, RejectAllTaxAuthority)


def test_tax3_network_flag_on_still_fail_closed(monkeypatch) -> None:
    monkeypatch.delenv("EAOS_TAX_AUTHORITY_URL", raising=False)
    monkeypatch.setenv("ENABLE_TAX_NETWORK", "1")
    assert tax_network_enabled() is True
    status = tax_authority_adapter_status()
    assert status.network_flag_enabled is True
    assert status.adapter_kind == "network_stub"
    assert status.live_transport is False
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
    assert (
        rejected.error_message
        == "Tax authority network transport is not configured"
    )


def test_tax3_fake_injection_unchanged(monkeypatch) -> None:
    monkeypatch.delenv("EAOS_TAX_NETWORK", raising=False)
    monkeypatch.delenv("ENABLE_TAX_NETWORK", raising=False)
    ctx = _ctx()
    service, invoice = _service(
        ctx, tax_authority_port=InMemoryFakeTaxAuthority()
    )
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
    assert issued.data.authority_status == "validated"
    assert issued.data.authority_ref == f"fake-authority-{draft.data.id.hex}"


def test_tax3_eaos_tax_network_alias(monkeypatch) -> None:
    monkeypatch.delenv("ENABLE_TAX_NETWORK", raising=False)
    monkeypatch.delenv("EAOS_TAX_AUTHORITY_URL", raising=False)
    monkeypatch.setenv("EAOS_TAX_NETWORK", "yes")
    assert tax_network_enabled() is True
    assert isinstance(resolve_tax_authority_port(), NetworkTaxAuthorityAdapter)
