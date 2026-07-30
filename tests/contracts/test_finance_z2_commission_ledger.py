"""PHX-G314 Finance Commission Ledger Z2 contracts."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import (
    AR_INVOICE_RESOURCE,
    CONVERSION_RESOURCE,
    CUSTOMER_RESOURCE,
    DELIVERY_ORDER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    QUOTE_LINE_RESOURCE,
    QUOTE_RESOURCE,
    REQUIREMENT_RESOURCE,
    SALES_ORDER_RESOURCE,
    CRMService,
)
from noventi.finance.repository import InMemoryFinanceRepository
from noventi.finance.service import (
    AR_CREDIT_NOTE_RESOURCE,
    AR_RECEIPT_RESOURCE,
    ARInvoiceSnapshot,
    COMMISSION_RESOURCE,
    FinanceService,
)


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


class _CRMInvoiceReader:
    def __init__(self, crm_repo: InMemoryCRMRepository) -> None:
        self._crm = crm_repo

    def get_ar_invoice_snapshot(
        self, invoice_id: UUID
    ) -> ARInvoiceSnapshot | None:
        invoice = self._crm.get_ar_invoice(invoice_id)
        if invoice is None:
            return None
        return ARInvoiceSnapshot(
            id=invoice.id,
            tenant_id=invoice.tenant_id,
            customer_id=invoice.customer_id,
            currency=invoice.currency,
            total_amount=invoice.total_amount,
            status=invoice.status.value,
            version=invoice.version,
        )


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=uuid4(),
        correlation_id=f"corr-g314-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _services(ctx: ExecutionContext, *, grant_commission: bool = True):
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_Eligibility(),
    )
    for resource in (
        CUSTOMER_RESOURCE,
        OPPORTUNITY_RESOURCE,
        REQUIREMENT_RESOURCE,
        QUOTE_RESOURCE,
        QUOTE_LINE_RESOURCE,
        CONVERSION_RESOURCE,
        SALES_ORDER_RESOURCE,
        DELIVERY_ORDER_RESOURCE,
        AR_INVOICE_RESOURCE,
        AR_RECEIPT_RESOURCE,
        AR_CREDIT_NOTE_RESOURCE,
    ):
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=resource,
            actions={
                "create",
                "read",
                "update",
                "archive",
                "convert",
                "issue",
                "confirm",
                "release",
                "void",
                "apply",
            },
            scope_level=ScopeLevel.TENANT,
        ).ok
    commission_actions = (
        {"create", "read"} if grant_commission else {"read"}
    )
    assert permission.grant(
        ctx,
        principal_subject_id=ctx.subject_id,
        resource_type=COMMISSION_RESOURCE,
        actions=commission_actions,
        scope_level=ScopeLevel.TENANT,
    ).ok
    crm_repo = InMemoryCRMRepository(tenant_id=ctx.tenant_id)
    crm = CRMService(permission, repository=crm_repo, audit_log=audit)
    finance = FinanceService(
        permission,
        repository=InMemoryFinanceRepository(tenant_id=ctx.tenant_id),
        audit_log=audit,
        ar_invoice_reader=_CRMInvoiceReader(crm_repo),
        beneficiary_eligibility=_Eligibility(),
    )
    return crm, finance, audit


def _issued_invoice(crm: CRMService, ctx: ExecutionContext):
    customer = crm.create_customer(
        ctx, code=f"Z2-{uuid4().hex[:8]}", display_name="Z2 Customer"
    ).data
    assert customer is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="Z2 Opportunity"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="Z2 Requirement"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="Z2 line",
        quantity=Decimal("2"),
        unit_price=Decimal("10"),
    ).ok
    assert crm.issue_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4(), human_confirm=True
    ).ok
    conversion = crm.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    ).data
    assert conversion is not None
    sales_order = crm.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=uuid4()
    ).data
    assert sales_order is not None
    sales_order = crm.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).data
    assert sales_order is not None
    delivery_order = crm.create_delivery_order(
        ctx, sales_order_id=sales_order.id, idempotency_key=uuid4()
    ).data
    assert delivery_order is not None
    assert crm.release_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    invoice = crm.create_ar_invoice(
        ctx, delivery_order_id=delivery_order.id, idempotency_key=uuid4()
    ).data
    assert invoice is not None
    issued = crm.issue_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).data
    assert issued is not None
    return issued


def test_z2_accrue_idempotent_and_default_deny() -> None:
    ctx = _ctx()
    crm, finance, audit = _services(ctx, grant_commission=False)
    invoice = _issued_invoice(crm, ctx)
    denied = finance.accrue_commission(
        ctx,
        invoice_id=invoice.id,
        beneficiary_subject_id=ctx.subject_id,
        amount=Decimal("3.00"),
        currency=invoice.currency,
        idempotency_key=uuid4(),
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event
        for event in audit.list_events()
        if event.action.startswith("Finance.Commission.Accrue")
    ]
    assert [event.result for event in events] == ["attempted", "denied"]

    ctx2 = _ctx()
    crm2, finance2, _ = _services(ctx2, grant_commission=True)
    invoice2 = _issued_invoice(crm2, ctx2)
    key = uuid4()
    first = finance2.accrue_commission(
        ctx2,
        invoice_id=invoice2.id,
        beneficiary_subject_id=ctx2.subject_id,
        amount=Decimal("3.00"),
        currency=invoice2.currency,
        idempotency_key=key,
    )
    retry = finance2.accrue_commission(
        ctx2,
        invoice_id=invoice2.id,
        beneficiary_subject_id=ctx2.subject_id,
        amount=Decimal("3.00"),
        currency=invoice2.currency,
        idempotency_key=key,
    )
    assert first.ok and first.data is not None
    assert first.data.status.value == "accrued"
    assert retry.data is not None and retry.data.id == first.data.id


def test_z2_rejects_draft_currency_mismatch_and_duplicate_beneficiary() -> None:
    ctx = _ctx()
    crm, finance, _ = _services(ctx)
    invoice = _issued_invoice(crm, ctx)
    draft_path = _issued_invoice(crm, ctx)
    # create a second draft invoice without issue
    customer = crm.create_customer(
        ctx, code=f"Z2D-{uuid4().hex[:8]}", display_name="Draft"
    ).data
    assert customer is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="Draft"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="Draft"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="d",
        quantity=Decimal("1"),
        unit_price=Decimal("1"),
    ).ok
    assert crm.issue_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4(), human_confirm=True
    ).ok
    conversion = crm.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    ).data
    assert conversion is not None
    sales_order = crm.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=uuid4()
    ).data
    assert sales_order is not None
    sales_order = crm.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).data
    assert sales_order is not None
    delivery_order = crm.create_delivery_order(
        ctx, sales_order_id=sales_order.id, idempotency_key=uuid4()
    ).data
    assert delivery_order is not None
    assert crm.release_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    draft_invoice = crm.create_ar_invoice(
        ctx, delivery_order_id=delivery_order.id, idempotency_key=uuid4()
    ).data
    assert draft_invoice is not None
    assert (
        finance.accrue_commission(
            ctx,
            invoice_id=draft_invoice.id,
            beneficiary_subject_id=ctx.subject_id,
            amount=Decimal("1.00"),
            currency=draft_invoice.currency,
            idempotency_key=uuid4(),
        ).error_code
        == ErrorCode.COMMON_CONFLICT
    )
    assert (
        finance.accrue_commission(
            ctx,
            invoice_id=invoice.id,
            beneficiary_subject_id=ctx.subject_id,
            amount=Decimal("1.00"),
            currency="EUR",
            idempotency_key=uuid4(),
        ).error_code
        == ErrorCode.COMMON_VALIDATION_FAILED
    )
    assert finance.accrue_commission(
        ctx,
        invoice_id=invoice.id,
        beneficiary_subject_id=ctx.subject_id,
        amount=Decimal("1.00"),
        currency=invoice.currency,
        idempotency_key=uuid4(),
    ).ok
    assert (
        finance.accrue_commission(
            ctx,
            invoice_id=invoice.id,
            beneficiary_subject_id=ctx.subject_id,
            amount=Decimal("2.00"),
            currency=invoice.currency,
            idempotency_key=uuid4(),
        ).error_code
        == ErrorCode.COMMON_CONFLICT
    )
    _ = draft_path
