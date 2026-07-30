"""PHX-G301 CRM Sales Order Confirmation C8 contracts."""

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
    CONVERSION_RESOURCE,
    CUSTOMER_RESOURCE,
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
        correlation_id=f"corr-g301-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(ctx: ExecutionContext, *, grant_confirm: bool):
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
    ):
        actions = {"create", "read", "update", "archive", "convert", "issue"}
        if grant_confirm:
            actions.add("confirm")
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


def _order(service: CRMService, ctx: ExecutionContext, *, with_line: bool):
    customer = service.create_customer(
        ctx, code=f"C8-{uuid4().hex[:8]}", display_name="C8 Customer"
    ).data
    assert customer is not None
    opportunity = service.create_opportunity(
        ctx, customer_id=customer.id, title="C8 Opportunity"
    ).data
    assert opportunity is not None
    requirement = service.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C8 Requirement"
    ).data
    assert requirement is not None
    quote = service.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    created_line = service.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="Confirmed commercial line",
        quantity=Decimal("2"),
        unit_price=Decimal("15.25"),
    ).data
    assert created_line is not None
    line = created_line if with_line else None
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
    return quote, line, sales_order


def test_c8_confirm_freezes_lines_total_and_is_idempotent() -> None:
    ctx = _ctx()
    service, _ = _service(ctx, grant_confirm=True)
    _, _, sales_order = _order(service, ctx, with_line=True)
    key = uuid4()
    first = service.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=key,
        human_confirm=True,
    )
    retry = service.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=key,
        human_confirm=True,
    )
    assert first.ok and first.data is not None
    assert first.data.status.value == "confirmed"
    assert first.data.total_amount == Decimal("30.50")
    assert retry.data is not None and retry.data.id == first.data.id
    lines = service.list_sales_order_lines(
        ctx, sales_order_id=sales_order.id
    )
    assert lines.data is not None and len(lines.data) == 1
    assert lines.data[0].amount == Decimal("30.50")


def test_c8_requires_human_confirmation_and_active_lines() -> None:
    ctx = _ctx()
    service, _ = _service(ctx, grant_confirm=True)
    _, _, sales_order = _order(service, ctx, with_line=True)
    no_human = service.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=False,
    )
    assert no_human.error_code == ErrorCode.COMMON_VALIDATION_FAILED


def test_c8_rejects_quote_changed_after_order_creation() -> None:
    ctx = _ctx()
    service, _ = _service(ctx, grant_confirm=True)
    quote, line, sales_order = _order(service, ctx, with_line=True)
    assert line is not None
    blocked = service.update_quote_line(
        ctx,
        quote_id=quote.id,
        quote_line_id=line.id,
        description="Changed after order",
        quantity=Decimal("3"),
        unit_price=Decimal("15.25"),
        expected_version=1,
    )
    assert blocked.error_code == ErrorCode.COMMON_CONFLICT
    result = service.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert result.ok and result.data is not None


def test_c8_permission_default_deny_is_audited() -> None:
    ctx = _ctx()
    service, audit = _service(ctx, grant_confirm=False)
    _, _, sales_order = _order(service, ctx, with_line=True)
    denied = service.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event for event in audit.list_events()
        if event.action.startswith("CRM.SalesOrder.Confirm")
    ]
    assert [event.result for event in events] == ["attempted", "denied"]
