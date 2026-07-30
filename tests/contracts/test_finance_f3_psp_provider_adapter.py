"""PHX-G326 Finance F3 PSP provider adapter contracts (NETWORK OFF)."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from noventi.crm.repository import InMemoryCRMRepository  # noqa: F401
from noventi.finance.psp_provider_adapter import (
    StripeLikePspAdapter,
    psp_adapter_status,
    psp_network_enabled,
    psp_provider,
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
        correlation_id=f"corr-g326-{uuid4()}",
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


def test_f3_default_env_is_reject_all(monkeypatch) -> None:
    monkeypatch.delenv("EAOS_PSP_PROVIDER", raising=False)
    monkeypatch.delenv("EAOS_PSP_NETWORK", raising=False)
    monkeypatch.delenv("ENABLE_PSP_NETWORK", raising=False)
    monkeypatch.delenv("EAOS_PSP_URL", raising=False)
    assert psp_provider() == "off"
    assert psp_network_enabled() is False
    status = psp_adapter_status()
    assert status.provider == "off"
    assert status.network_flag_enabled is False
    assert status.adapter_kind == "reject_all"
    assert status.live_transport is False
    assert status.endpoint_configured is False
    port = resolve_psp_port()
    assert isinstance(port, RejectAllPsp)


def test_f3_network_flag_on_stripe_like_still_fail_closed(monkeypatch) -> None:
    monkeypatch.setenv("EAOS_PSP_PROVIDER", "stripe_like")
    monkeypatch.setenv("ENABLE_PSP_NETWORK", "1")
    monkeypatch.delenv("EAOS_PSP_URL", raising=False)
    assert psp_network_enabled() is True
    status = psp_adapter_status()
    assert status.provider == "stripe_like"
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
    assert (
        rejected.error_message
        == "PSP network transport is not configured"
    )


def test_f3_stripe_like_without_network_still_stub(monkeypatch) -> None:
    monkeypatch.setenv("EAOS_PSP_PROVIDER", "stripe_like")
    monkeypatch.delenv("EAOS_PSP_NETWORK", raising=False)
    monkeypatch.delenv("ENABLE_PSP_NETWORK", raising=False)
    monkeypatch.delenv("EAOS_PSP_URL", raising=False)
    assert isinstance(resolve_psp_port(), StripeLikePspAdapter)
    status = psp_adapter_status()
    assert status.adapter_kind == "stripe_like_stub"
    assert status.network_flag_enabled is False
    assert status.live_transport is False
    assert status.endpoint_configured is False


def test_f3_fake_via_env_works_when_policy_required(monkeypatch) -> None:
    monkeypatch.setenv("EAOS_PSP_PROVIDER", "fake")
    monkeypatch.delenv("EAOS_PSP_NETWORK", raising=False)
    monkeypatch.delenv("ENABLE_PSP_NETWORK", raising=False)
    monkeypatch.delenv("EAOS_PSP_URL", raising=False)
    port = resolve_psp_port()
    assert isinstance(port, InMemoryFakePsp)
    status = psp_adapter_status()
    assert status.provider == "fake"
    assert status.adapter_kind == "fake"
    assert status.live_transport is False
    assert status.endpoint_configured is False

    ctx = _ctx()
    service, invoice = _service(ctx)  # resolve via env inside FinanceService
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
    assert applied.data.psp_ref == f"fake-psp-{receipt.id.hex}"
    assert applied.data.psp_status == "applied"


def test_f3_explicit_injection_unchanged(monkeypatch) -> None:
    monkeypatch.delenv("EAOS_PSP_PROVIDER", raising=False)
    monkeypatch.delenv("ENABLE_PSP_NETWORK", raising=False)
    ctx = _ctx()
    service, invoice = _service(ctx, psp_port=InMemoryFakePsp())
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
    assert applied.data.psp_status == "applied"


def test_f3_eaos_psp_network_alias(monkeypatch) -> None:
    monkeypatch.delenv("ENABLE_PSP_NETWORK", raising=False)
    monkeypatch.setenv("EAOS_PSP_NETWORK", "yes")
    monkeypatch.setenv("EAOS_PSP_PROVIDER", "stripe_like")
    assert psp_network_enabled() is True
    assert isinstance(resolve_psp_port(), StripeLikePspAdapter)
