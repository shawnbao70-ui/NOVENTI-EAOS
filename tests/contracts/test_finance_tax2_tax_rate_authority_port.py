"""PHX-G317 Finance Tax2 tax-rate + authority-port contracts."""

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
        correlation_id=f"corr-g317-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(
    ctx: ExecutionContext, *, fake: bool = False
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
    return (
        FinanceService(
            permission,
            repository=InMemoryFinanceRepository(tenant_id=ctx.tenant_id),
            audit_log=audit,
            ar_invoice_reader=_Invoices(invoice),
            tax_authority_port=InMemoryFakeTaxAuthority() if fake else None,
        ),
        invoice,
    )


def _tax_invoice(
    service: FinanceService,
    ctx: ExecutionContext,
    invoice: ARInvoiceSnapshot,
    *,
    tax_code: str | None = None,
):
    result = service.create_tax_invoice(
        ctx,
        invoice_id=invoice.id,
        amount=invoice.total_amount,
        idempotency_key=uuid4(),
        tax_code=tax_code,
    )
    assert result.data is not None
    return result.data


def test_tax2_authority_is_opt_in_and_reject_all_fails_closed() -> None:
    ctx = _ctx()
    service, invoice = _service(ctx)
    created_rate = service.create_tax_rate(
        ctx,
        tax_code="CN_VAT",
        tax_name="CN VAT",
        rate_percent=Decimal("13.00"),
    )
    assert created_rate.ok and created_rate.data is not None

    draft = _tax_invoice(service, ctx, invoice, tax_code="CN_VAT")
    assert service.issue_tax_invoice(
        ctx,
        tax_invoice_id=draft.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok

    second = _tax_invoice(service, ctx, invoice, tax_code="CN_VAT")
    policy = service.set_tax_authority_policy(
        ctx, tax_authority_required=True, expected_version=0
    )
    assert policy.ok and policy.data is not None and policy.data.version == 1
    rejected = service.issue_tax_invoice(
        ctx,
        tax_invoice_id=second.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert rejected.error_code == ErrorCode.COMMON_CONFLICT
    assert rejected.error_message == "Tax authority port is unavailable"
    assert (
        service.get_tax_invoice(ctx, tax_invoice_id=second.id).data.status.value
        == "draft"
    )


def test_tax2_fake_authority_persists_reference_and_status() -> None:
    ctx = _ctx()
    service, invoice = _service(ctx, fake=True)
    assert service.create_tax_rate(
        ctx,
        tax_code="CN_VAT",
        tax_name="CN VAT",
        rate_percent=Decimal("13.00"),
    ).ok
    assert service.set_tax_authority_policy(
        ctx, tax_authority_required=True, expected_version=0
    ).ok
    draft = _tax_invoice(service, ctx, invoice, tax_code="CN_VAT")
    issued = service.issue_tax_invoice(
        ctx,
        tax_invoice_id=draft.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert issued.ok and issued.data is not None
    assert issued.data.authority_ref == f"fake-authority-{draft.id.hex}"
    assert issued.data.authority_status == "validated"
    assert issued.data.tax_code == "CN_VAT"


def test_tax2_tax_rate_create_get_and_archived_cannot_validate() -> None:
    ctx = _ctx()
    service, invoice = _service(ctx, fake=True)
    created = service.create_tax_rate(
        ctx,
        tax_code="ID_PPN",
        tax_name="ID PPN",
        rate_percent=Decimal("11.00"),
    )
    assert created.ok and created.data is not None
    fetched = service.get_tax_rate(ctx, tax_rate_id=created.data.id)
    assert fetched.ok and fetched.data is not None
    assert fetched.data.tax_code == "ID_PPN"
    by_code = service.get_tax_rate_by_code(ctx, tax_code="ID_PPN")
    assert by_code.ok and by_code.data is not None
    assert by_code.data.id == created.data.id

    archived = service.archive_tax_rate(
        ctx, tax_rate_id=created.data.id, expected_version=created.data.version
    )
    assert archived.ok and archived.data is not None
    assert archived.data.status.value == "archived"

    assert service.set_tax_authority_policy(
        ctx, tax_authority_required=True, expected_version=0
    ).ok
    draft = _tax_invoice(service, ctx, invoice, tax_code="ID_PPN")
    rejected = service.issue_tax_invoice(
        ctx,
        tax_invoice_id=draft.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert rejected.error_code == ErrorCode.COMMON_CONFLICT
    assert rejected.error_message == "tax rate is not active"
