"""PHX-G309 CRM AR Invoice Void C16 contracts."""

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


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=uuid4(),
        correlation_id=f"corr-g309-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(ctx: ExecutionContext, *, grant_void: bool = True):
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
        actions = {
            "create",
            "read",
            "update",
            "archive",
            "convert",
            "issue",
            "confirm",
            "release",
        }
        if grant_void:
            actions.add("void")
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=resource,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok
    return CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=ctx.tenant_id),
        audit_log=audit,
    ), audit


def _issued_invoice(service: CRMService, ctx: ExecutionContext):
    customer = service.create_customer(
        ctx, code=f"C16-{uuid4().hex[:8]}", display_name="C16 Customer"
    ).data
    assert customer is not None
    opportunity = service.create_opportunity(
        ctx, customer_id=customer.id, title="C16 Opportunity"
    ).data
    assert opportunity is not None
    requirement = service.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C16 Requirement"
    ).data
    assert requirement is not None
    quote = service.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert service.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="C16 line",
        quantity=Decimal("2"),
        unit_price=Decimal("10"),
    ).ok
    assert service.issue_quote(
        ctx,
        quote_id=quote.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    conversion = service.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    ).data
    assert conversion is not None
    sales_order = service.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=uuid4()
    ).data
    assert sales_order is not None
    sales_order = service.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).data
    assert sales_order is not None
    delivery_order = service.create_delivery_order(
        ctx, sales_order_id=sales_order.id, idempotency_key=uuid4()
    ).data
    assert delivery_order is not None
    assert service.release_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    invoice = service.create_ar_invoice(
        ctx, delivery_order_id=delivery_order.id, idempotency_key=uuid4()
    ).data
    assert invoice is not None
    issued = service.issue_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).data
    assert issued is not None and issued.status.value == "issued"
    return issued


def test_c16_void_default_deny_is_audited() -> None:
    ctx = _ctx()
    service, audit = _service(ctx, grant_void=False)
    invoice = _issued_invoice(service, ctx)
    denied = service.void_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
        human_confirm=True,
        reason="Operator retract",
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event
        for event in audit.list_events()
        if event.action.startswith("CRM.ARInvoice.Void")
    ]
    assert [event.result for event in events] == ["attempted", "denied"]


def test_c16_void_requires_human_confirm_and_reason() -> None:
    ctx = _ctx()
    service, _ = _service(ctx)
    invoice = _issued_invoice(service, ctx)
    missing_confirm = service.void_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
        human_confirm=False,
        reason="Operator retract",
    )
    assert missing_confirm.error_code == ErrorCode.COMMON_VALIDATION_FAILED
    missing_reason = service.void_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
        human_confirm=True,
        reason="   ",
    )
    assert missing_reason.error_code == ErrorCode.COMMON_VALIDATION_FAILED


def test_c16_draft_cannot_void_issued_can() -> None:
    ctx = _ctx()
    service, _ = _service(ctx)
    invoice = _issued_invoice(service, ctx)
    # recreate draft path via second customer chain is heavy; use create-before-issue
    customer = service.create_customer(
        ctx, code=f"C16D-{uuid4().hex[:8]}", display_name="C16 Draft"
    ).data
    assert customer is not None
    opportunity = service.create_opportunity(
        ctx, customer_id=customer.id, title="C16 Draft Opp"
    ).data
    assert opportunity is not None
    requirement = service.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C16 Draft Req"
    ).data
    assert requirement is not None
    quote = service.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert service.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="draft line",
        quantity=Decimal("1"),
        unit_price=Decimal("1"),
    ).ok
    assert service.issue_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4(), human_confirm=True
    ).ok
    conversion = service.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    ).data
    assert conversion is not None
    sales_order = service.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=uuid4()
    ).data
    assert sales_order is not None
    sales_order = service.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).data
    assert sales_order is not None
    delivery_order = service.create_delivery_order(
        ctx, sales_order_id=sales_order.id, idempotency_key=uuid4()
    ).data
    assert delivery_order is not None
    assert service.release_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    draft = service.create_ar_invoice(
        ctx, delivery_order_id=delivery_order.id, idempotency_key=uuid4()
    ).data
    assert draft is not None
    blocked = service.void_ar_invoice(
        ctx,
        invoice_id=draft.id,
        idempotency_key=uuid4(),
        human_confirm=True,
        reason="too early",
    )
    assert blocked.error_code == ErrorCode.COMMON_CONFLICT
    assert blocked.error_message == "only issued invoices can be voided"
    voided = service.void_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
        human_confirm=True,
        reason="Operator retract",
    )
    assert voided.ok and voided.data is not None
    assert voided.data.status.value == "voided"
    assert voided.data.void_reason == "Operator retract"


def test_c16_void_is_idempotent_and_wrong_key_conflicts() -> None:
    ctx = _ctx()
    service, _ = _service(ctx)
    invoice = _issued_invoice(service, ctx)
    key = uuid4()
    first = service.void_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=key,
        human_confirm=True,
        reason="Operator retract",
    )
    retry = service.void_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=key,
        human_confirm=True,
        reason="Operator retract",
    )
    assert first.ok and first.data is not None
    assert retry.data is not None and retry.data.id == first.data.id
    conflict = service.void_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
        human_confirm=True,
        reason="Different key",
    )
    assert conflict.error_code == ErrorCode.COMMON_CONFLICT


def test_c16_voided_cannot_issue_again() -> None:
    ctx = _ctx()
    service, _ = _service(ctx)
    invoice = _issued_invoice(service, ctx)
    assert service.void_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
        human_confirm=True,
        reason="Operator retract",
    ).ok
    reissue = service.issue_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert reissue.error_code == ErrorCode.COMMON_CONFLICT
    assert reissue.error_message == "AR invoice cannot be issued"
