"""PHX-G304 CRM Commercial Hold gate C11 contracts."""

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
        correlation_id=f"corr-g304-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(ctx: ExecutionContext, *, grant_customer_update: bool = True):
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_Eligibility(),
    )
    for resource in (
        OPPORTUNITY_RESOURCE,
        REQUIREMENT_RESOURCE,
        QUOTE_RESOURCE,
        QUOTE_LINE_RESOURCE,
        CONVERSION_RESOURCE,
        SALES_ORDER_RESOURCE,
        DELIVERY_ORDER_RESOURCE,
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
            },
            scope_level=ScopeLevel.TENANT,
        ).ok
    customer_actions = {"create", "read", "archive"}
    if grant_customer_update:
        customer_actions.add("update")
    assert permission.grant(
        ctx,
        principal_subject_id=ctx.subject_id,
        resource_type=CUSTOMER_RESOURCE,
        actions=customer_actions,
        scope_level=ScopeLevel.TENANT,
    ).ok
    return CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=ctx.tenant_id),
        audit_log=audit,
    ), audit


def _created_sales_order(service: CRMService, ctx: ExecutionContext):
    customer = service.create_customer(
        ctx, code=f"C11-{uuid4().hex[:8]}", display_name="C11 Customer"
    ).data
    assert customer is not None
    opportunity = service.create_opportunity(
        ctx, customer_id=customer.id, title="C11 Opportunity"
    ).data
    assert opportunity is not None
    requirement = service.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C11 Requirement"
    ).data
    assert requirement is not None
    quote = service.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert service.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="C11 line",
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
    return customer, sales_order


def test_c11_default_commercial_hold_is_false() -> None:
    ctx = _ctx()
    service, _ = _service(ctx)
    customer = service.create_customer(
        ctx, code=f"C11-{uuid4().hex[:8]}", display_name="Default Hold"
    ).data
    assert customer is not None
    assert customer.commercial_hold is False


def test_c11_set_hold_requires_update_grant_and_is_audited() -> None:
    ctx = _ctx()
    service, audit = _service(ctx, grant_customer_update=False)
    customer = service.create_customer(
        ctx, code=f"C11-{uuid4().hex[:8]}", display_name="Denied Hold"
    ).data
    assert customer is not None
    denied = service.set_customer_commercial_hold(
        ctx,
        customer_id=customer.id,
        commercial_hold=True,
        expected_version=customer.version,
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event
        for event in audit.list_events()
        if event.action.startswith("CRM.Customer.CommercialHold.Set")
    ]
    assert [event.result for event in events] == ["attempted", "denied"]


def test_c11_hold_blocks_confirm_and_delivery_order() -> None:
    ctx = _ctx()
    service, _ = _service(ctx)
    customer, sales_order = _created_sales_order(service, ctx)
    held = service.set_customer_commercial_hold(
        ctx,
        customer_id=customer.id,
        commercial_hold=True,
        expected_version=customer.version,
    )
    assert held.ok and held.data is not None
    confirm = service.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert confirm.error_code == ErrorCode.COMMON_CONFLICT
    assert confirm.error_message == "customer is on commercial hold"
    # Confirm first while clear, then hold before DO.
    service.set_customer_commercial_hold(
        ctx,
        customer_id=held.data.id,
        commercial_hold=False,
        expected_version=held.data.version,
    )
    confirmed = service.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert confirmed.ok and confirmed.data is not None
    customer = service.get_customer(ctx, customer_id=customer.id).data
    assert customer is not None
    held_again = service.set_customer_commercial_hold(
        ctx,
        customer_id=customer.id,
        commercial_hold=True,
        expected_version=customer.version,
    )
    assert held_again.ok
    delivery = service.create_delivery_order(
        ctx,
        sales_order_id=confirmed.data.id,
        idempotency_key=uuid4(),
    )
    assert delivery.error_code == ErrorCode.COMMON_CONFLICT
    assert delivery.error_message == "customer is on commercial hold"


def test_c11_clear_hold_allows_confirm_then_delivery_order() -> None:
    ctx = _ctx()
    service, audit = _service(ctx)
    customer, sales_order = _created_sales_order(service, ctx)
    held = service.set_customer_commercial_hold(
        ctx,
        customer_id=customer.id,
        commercial_hold=True,
        expected_version=customer.version,
    ).data
    assert held is not None
    cleared = service.set_customer_commercial_hold(
        ctx,
        customer_id=held.id,
        commercial_hold=False,
        expected_version=held.version,
    )
    assert cleared.ok and cleared.data is not None
    assert cleared.data.commercial_hold is False
    confirmed = service.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert confirmed.ok and confirmed.data is not None
    delivery = service.create_delivery_order(
        ctx,
        sales_order_id=confirmed.data.id,
        idempotency_key=uuid4(),
    )
    assert delivery.ok and delivery.data is not None
    assert delivery.data.status.value == "draft"
    ok_events = [
        event
        for event in audit.list_events()
        if event.action == "CRM.Customer.CommercialHold.Set" and event.result == "ok"
    ]
    assert len(ok_events) >= 2
