"""PHX-G313 Customer360 assemble contracts (hermetic)."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from noventi.crm.customer360 import (
    CUSTOMER360_RESOURCE,
    AssembledCustomer360Repository,
    Customer360Service,
)
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
        correlation_id=f"corr-g313-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _stack(ctx: ExecutionContext, *, grant_360: bool = True):
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
    if grant_360:
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=CUSTOMER360_RESOURCE,
            actions={"read"},
            scope_level=ScopeLevel.TENANT,
        ).ok
    crm_repo = InMemoryCRMRepository(tenant_id=ctx.tenant_id)
    finance_repo = InMemoryFinanceRepository(tenant_id=ctx.tenant_id)
    crm = CRMService(permission, repository=crm_repo, audit_log=audit)
    finance = FinanceService(
        permission,
        repository=finance_repo,
        audit_log=audit,
        ar_invoice_reader=_CRMInvoiceReader(crm_repo),
    )
    customer360 = Customer360Service(
        permission,
        repository=AssembledCustomer360Repository(crm_repo, finance_repo),
    )
    return crm, finance, customer360


def _issued_invoice(ctx: ExecutionContext, crm: CRMService):
    customer = crm.create_customer(
        ctx, code=f"Z1-{uuid4().hex[:8]}", display_name="Z1 Cust"
    ).data
    assert customer is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="Z1 Opp"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="Z1 Req"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="line",
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
    return customer, issued


def test_g313_assemble_aggregates_crm_finance_traces() -> None:
    ctx = _ctx()
    crm, finance, customer360 = _stack(ctx)
    customer, invoice = _issued_invoice(ctx, crm)
    receipt = finance.create_receipt(
        ctx,
        customer_id=customer.id,
        amount=Decimal("5.00"),
        currency=invoice.currency,
        idempotency_key=uuid4(),
    ).data
    assert receipt is not None
    assert finance.apply_receipt_to_invoice(
        ctx,
        receipt_id=receipt.id,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
    ).ok
    credit = finance.create_credit_note(
        ctx,
        invoice_id=invoice.id,
        amount=Decimal("1.00"),
        idempotency_key=uuid4(),
    ).data
    assert credit is not None
    assert finance.issue_credit_note(
        ctx,
        credit_note_id=credit.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok

    result = customer360.get_customer360(ctx, customer.id)
    assert result.ok
    assert result.data is not None
    projection = result.data
    assert projection.customer_id == customer.id
    assert projection.opportunities_count == 1
    assert projection.open_sales_orders_count == 1
    assert projection.open_delivery_orders_count == 1
    assert len(projection.invoice_traces) == 1
    assert projection.invoice_traces[0].status.value == "issued"
    assert len(projection.applied_receipt_traces) == 1
    assert projection.applied_receipt_traces[0].ar_invoice_id == invoice.id
    assert len(projection.credit_note_traces) == 1
    assert projection.credit_note_traces[0].status.value == "issued"


def test_g313_default_deny_without_customer360_read() -> None:
    ctx = _ctx()
    crm, _finance, customer360 = _stack(ctx, grant_360=False)
    customer = crm.create_customer(
        ctx, code=f"Z1-deny-{uuid4().hex[:8]}", display_name="Deny"
    ).data
    assert customer is not None
    result = customer360.get_customer360(ctx, customer.id)
    assert not result.ok
    assert result.error_code == ErrorCode.PERMISSION_DENIED


def test_g313_customer360_has_no_write_surface() -> None:
    assert not hasattr(Customer360Service, "create_customer360")
    assert not hasattr(Customer360Service, "update_customer360")
    assert not hasattr(Customer360Service, "apply_customer360")
    assert not hasattr(Customer360Service, "execute")
    assert not hasattr(Customer360Service, "authorize")
