"""PHX-G315 Finance F2 PSP-port contracts."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from noventi.crm.repository import InMemoryCRMRepository
from noventi.finance.repository import InMemoryFinanceRepository
from noventi.finance.service import (
    AR_RECEIPT_RESOURCE,
    RECEIPT_PSP_POLICY_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
    InMemoryFakePsp,
)


class _Invoices:
    def __init__(self, invoice: ARInvoiceSnapshot) -> None:
        self.invoice = invoice

    def get_ar_invoice_snapshot(self, invoice_id: UUID) -> ARInvoiceSnapshot | None:
        return self.invoice if invoice_id == self.invoice.id else None


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=uuid4(),
        correlation_id=f"corr-g315-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(ctx: ExecutionContext, *, fake: bool = False) -> tuple[FinanceService, ARInvoiceSnapshot]:
    assert ctx.tenant_id is not None
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit, grant_administrators={ctx.subject_id},
        principal_eligibility=_Eligibility(),
    )
    for resource, actions in (
        (AR_RECEIPT_RESOURCE, {"create", "read", "apply"}),
        (RECEIPT_PSP_POLICY_RESOURCE, {"read", "update"}),
    ):
        assert permission.grant(
            ctx, principal_subject_id=ctx.subject_id, resource_type=resource,
            actions=actions, scope_level=ScopeLevel.TENANT,
        ).ok
    invoice = ARInvoiceSnapshot(
        id=uuid4(), tenant_id=ctx.tenant_id, customer_id=uuid4(),
        currency="USD", total_amount=Decimal("10.00"), status="issued", version=1,
    )
    return (
        FinanceService(
            permission, repository=InMemoryFinanceRepository(tenant_id=ctx.tenant_id),
            audit_log=audit, ar_invoice_reader=_Invoices(invoice),
            psp_port=InMemoryFakePsp() if fake else None,
        ),
        invoice,
    )


def _receipt(service: FinanceService, ctx: ExecutionContext, invoice: ARInvoiceSnapshot):
    result = service.create_receipt(
        ctx, customer_id=invoice.customer_id, amount=invoice.total_amount,
        currency=invoice.currency, idempotency_key=uuid4(),
    )
    assert result.data is not None
    return result.data


def test_f2_psp_is_opt_in_and_reject_all_fails_closed() -> None:
    ctx = _ctx()
    service, invoice = _service(ctx)
    receipt = _receipt(service, ctx, invoice)
    assert service.apply_receipt_to_invoice(
        ctx, receipt_id=receipt.id, invoice_id=invoice.id, idempotency_key=uuid4()
    ).ok

    second = _receipt(service, ctx, invoice)
    policy = service.set_receipt_psp_policy(
        ctx, receipt_psp_required=True, expected_version=0
    )
    assert policy.ok and policy.data is not None and policy.data.version == 1
    rejected = service.apply_receipt_to_invoice(
        ctx, receipt_id=second.id, invoice_id=invoice.id, idempotency_key=uuid4()
    )
    assert rejected.error_code == ErrorCode.COMMON_CONFLICT
    assert rejected.error_message == "PSP port is unavailable"
    assert service.get_receipt(ctx, receipt_id=second.id).data.status.value == "draft"


def test_f2_fake_psp_persists_reference_and_status() -> None:
    ctx = _ctx()
    service, invoice = _service(ctx, fake=True)
    assert service.set_receipt_psp_policy(
        ctx, receipt_psp_required=True, expected_version=0
    ).ok
    receipt = _receipt(service, ctx, invoice)
    applied = service.apply_receipt_to_invoice(
        ctx, receipt_id=receipt.id, invoice_id=invoice.id, idempotency_key=uuid4()
    )
    assert applied.ok and applied.data is not None
    assert applied.data.psp_ref == f"fake-psp-{receipt.id.hex}"
    assert applied.data.psp_status == "applied"
