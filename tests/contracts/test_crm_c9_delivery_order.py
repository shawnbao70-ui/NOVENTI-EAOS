"""PHX-G302 CRM Delivery Order shell C9 contracts."""

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
        correlation_id=f"corr-g302-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(ctx: ExecutionContext, *, grant_delivery: bool):
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_Eligibility(),
    )
    resources = [
        CUSTOMER_RESOURCE,
        OPPORTUNITY_RESOURCE,
        REQUIREMENT_RESOURCE,
        QUOTE_RESOURCE,
        QUOTE_LINE_RESOURCE,
        CONVERSION_RESOURCE,
        SALES_ORDER_RESOURCE,
    ]
    if grant_delivery:
        resources.append(DELIVERY_ORDER_RESOURCE)
    for resource in resources:
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
    return CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=ctx.tenant_id),
        audit_log=audit,
    ), audit


def _sales_order(service: CRMService, ctx: ExecutionContext, *, confirmed: bool):
    customer = service.create_customer(
        ctx, code=f"C9-{uuid4().hex[:8]}", display_name="C9 Customer"
    ).data
    assert customer is not None
    opportunity = service.create_opportunity(
        ctx, customer_id=customer.id, title="C9 Opportunity"
    ).data
    assert opportunity is not None
    requirement = service.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C9 Requirement"
    ).data
    assert requirement is not None
    quote = service.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert service.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="C9 line",
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
    if confirmed:
        sales_order = service.confirm_sales_order(
            ctx,
            sales_order_id=sales_order.id,
            idempotency_key=uuid4(),
            human_confirm=True,
        ).data
        assert sales_order is not None
    return sales_order


def test_c9_requires_confirmed_sales_order() -> None:
    ctx = _ctx()
    service, _ = _service(ctx, grant_delivery=True)
    sales_order = _sales_order(service, ctx, confirmed=False)
    result = service.create_delivery_order(
        ctx, sales_order_id=sales_order.id, idempotency_key=uuid4()
    )
    assert result.error_code == ErrorCode.COMMON_CONFLICT


def test_c9_delivery_shell_is_idempotent_and_frozen() -> None:
    ctx = _ctx()
    service, _ = _service(ctx, grant_delivery=True)
    sales_order = _sales_order(service, ctx, confirmed=True)
    key = uuid4()
    first = service.create_delivery_order(
        ctx, sales_order_id=sales_order.id, idempotency_key=key
    )
    retry = service.create_delivery_order(
        ctx, sales_order_id=sales_order.id, idempotency_key=key
    )
    assert first.ok and first.data is not None
    assert retry.data is not None and retry.data.id == first.data.id
    assert first.data.status.value == "draft"
    assert first.data.total_amount == Decimal("20.00")
    assert first.data.sales_order_version == sales_order.version


def test_c9_permission_default_deny_is_audited() -> None:
    ctx = _ctx()
    service, audit = _service(ctx, grant_delivery=False)
    sales_order = _sales_order(service, ctx, confirmed=True)
    denied = service.create_delivery_order(
        ctx, sales_order_id=sales_order.id, idempotency_key=uuid4()
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event for event in audit.list_events()
        if event.action.startswith("CRM.DeliveryOrder")
    ]
    assert [event.result for event in events] == ["attempted", "denied"]
