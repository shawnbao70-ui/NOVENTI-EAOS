"""PHX-G310 Finance AR Receipt F1 contracts."""

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
    AR_RECEIPT_RESOURCE,
    ARInvoiceSnapshot,
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
        correlation_id=f"corr-g310-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _services(ctx: ExecutionContext, *, grant_finance: bool = True):
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
            },
            scope_level=ScopeLevel.TENANT,
        ).ok
    if grant_finance:
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=AR_RECEIPT_RESOURCE,
            actions={"create", "read", "apply"},
            scope_level=ScopeLevel.TENANT,
        ).ok
    crm_repo = InMemoryCRMRepository(tenant_id=ctx.tenant_id)
    crm = CRMService(permission, repository=crm_repo, audit_log=audit)
    finance = FinanceService(
        permission,
        repository=InMemoryFinanceRepository(tenant_id=ctx.tenant_id),
        audit_log=audit,
        ar_invoice_reader=_CRMInvoiceReader(crm_repo),
    )
    return crm, finance, audit


def _issued_invoice(crm: CRMService, ctx: ExecutionContext):
    customer = crm.create_customer(
        ctx, code=f"F1-{uuid4().hex[:8]}", display_name="F1 Customer"
    ).data
    assert customer is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="F1 Opportunity"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="F1 Requirement"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="F1 line",
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


def test_f1_create_and_apply_to_issued_invoice() -> None:
    ctx = _ctx()
    crm, finance, audit = _services(ctx)
    invoice = _issued_invoice(crm, ctx)
    create_key = uuid4()
    created = finance.create_receipt(
        ctx,
        customer_id=invoice.customer_id,
        amount=Decimal("20.00"),
        currency=invoice.currency,
        idempotency_key=create_key,
    )
    assert created.ok and created.data is not None
    assert created.data.status.value == "draft"
    retry = finance.create_receipt(
        ctx,
        customer_id=invoice.customer_id,
        amount=Decimal("20.00"),
        currency=invoice.currency,
        idempotency_key=create_key,
    )
    assert retry.ok and retry.data is not None
    assert retry.data.id == created.data.id
    apply_key = uuid4()
    applied = finance.apply_receipt_to_invoice(
        ctx,
        receipt_id=created.data.id,
        invoice_id=invoice.id,
        idempotency_key=apply_key,
    )
    assert applied.ok and applied.data is not None
    assert applied.data.status.value == "applied"
    assert applied.data.ar_invoice_id == invoice.id
    replay = finance.apply_receipt_to_invoice(
        ctx,
        receipt_id=created.data.id,
        invoice_id=invoice.id,
        idempotency_key=apply_key,
    )
    assert replay.ok and replay.data is not None
    assert replay.data.id == applied.data.id
    events = [
        event
        for event in audit.list_events()
        if event.action.startswith("Finance.ARReceipt.")
    ]
    assert all(event.details == {} for event in events)


def test_f1_default_deny_is_audited() -> None:
    ctx = _ctx()
    crm, finance, audit = _services(ctx, grant_finance=False)
    invoice = _issued_invoice(crm, ctx)
    denied = finance.create_receipt(
        ctx,
        customer_id=invoice.customer_id,
        amount=Decimal("1.00"),
        currency=invoice.currency,
        idempotency_key=uuid4(),
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event
        for event in audit.list_events()
        if event.action.startswith("Finance.ARReceipt.Create")
    ]
    assert [event.result for event in events] == ["attempted", "denied"]


def test_f1_rejects_draft_voided_over_amount_and_currency_mismatch() -> None:
    ctx = _ctx()
    crm, finance, _ = _services(ctx)
    issued = _issued_invoice(crm, ctx)
    receipt = finance.create_receipt(
        ctx,
        customer_id=issued.customer_id,
        amount=Decimal("20.00"),
        currency=issued.currency,
        idempotency_key=uuid4(),
    ).data
    assert receipt is not None

    second = _issued_invoice(crm, ctx)
    # Leave a draft invoice by creating then not issuing a third chain is heavy;
    # use second invoice before issue path: recreate minimal draft from second DO
    # is unavailable — instead force draft by creating receipt against a fresh
    # issued invoice then void it for voided-path, and use amount/currency checks
    # against a newly issued invoice.
    draft_chain = _issued_invoice(crm, ctx)
    # Re-fetch as issued; create a separate draft by issuing then... skip:
    # draft rejection uses invoice that we void after creating a parallel draft
    # via create_ar_invoice on a new released DO.
    customer = crm.create_customer(
        ctx, code=f"F1D-{uuid4().hex[:8]}", display_name="F1 Draft"
    ).data
    assert customer is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="F1 Draft Opp"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="F1 Draft Req"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="draft",
        quantity=Decimal("1"),
        unit_price=Decimal("5"),
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
        finance.apply_receipt_to_invoice(
            ctx,
            receipt_id=receipt.id,
            invoice_id=draft_invoice.id,
            idempotency_key=uuid4(),
        ).error_code
        == ErrorCode.COMMON_CONFLICT
    )

    assert crm.void_ar_invoice(
        ctx,
        invoice_id=issued.id,
        idempotency_key=uuid4(),
        human_confirm=True,
        reason="retract",
    ).ok
    assert (
        finance.apply_receipt_to_invoice(
            ctx,
            receipt_id=receipt.id,
            invoice_id=issued.id,
            idempotency_key=uuid4(),
        ).error_code
        == ErrorCode.COMMON_CONFLICT
    )

    over = finance.create_receipt(
        ctx,
        customer_id=second.customer_id,
        amount=second.total_amount + Decimal("0.01"),
        currency=second.currency,
        idempotency_key=uuid4(),
    ).data
    assert over is not None
    assert (
        finance.apply_receipt_to_invoice(
            ctx,
            receipt_id=over.id,
            invoice_id=second.id,
            idempotency_key=uuid4(),
        ).error_code
        == ErrorCode.COMMON_VALIDATION_FAILED
    )

    mismatch = finance.create_receipt(
        ctx,
        customer_id=draft_chain.customer_id,
        amount=Decimal("1.00"),
        currency="EUR",
        idempotency_key=uuid4(),
    ).data
    assert mismatch is not None
    assert (
        finance.apply_receipt_to_invoice(
            ctx,
            receipt_id=mismatch.id,
            invoice_id=draft_chain.id,
            idempotency_key=uuid4(),
        ).error_code
        == ErrorCode.COMMON_CONFLICT
    )
