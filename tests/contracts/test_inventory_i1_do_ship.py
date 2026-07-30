"""PHX-G311 Inventory DO Ship I1 contracts."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from uuid import UUID, uuid4

from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from noventi.crm.models import DeliveryOrderStatus
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
from noventi.inventory.repository import InMemoryInventoryRepository
from noventi.inventory.service import (
    DELIVERY_SHIP_RESOURCE,
    STOCK_RESOURCE,
    DeliveryOrderShipLineSnapshot,
    DeliveryOrderShipSnapshot,
    InventoryService,
)


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


class _CRMShipReader:
    def __init__(self, crm_repo: InMemoryCRMRepository) -> None:
        self._crm = crm_repo

    def get_delivery_order_ship_snapshot(
        self, delivery_order_id: UUID
    ) -> DeliveryOrderShipSnapshot | None:
        delivery_order = self._crm.get_delivery_order(delivery_order_id)
        if delivery_order is None:
            return None
        sales_order = self._crm.get_sales_order(delivery_order.sales_order_id)
        if sales_order is None:
            return None
        requirement = self._crm.get_requirement(sales_order.requirement_id)
        if requirement is None:
            return None
        opportunity = self._crm.get_opportunity(requirement.opportunity_id)
        if opportunity is None:
            return None
        customer = self._crm.get_customer(opportunity.customer_id)
        if customer is None:
            return None
        lines = self._crm.list_sales_order_lines(sales_order.id)
        return DeliveryOrderShipSnapshot(
            id=delivery_order.id,
            tenant_id=delivery_order.tenant_id,
            status=delivery_order.status.value,
            version=delivery_order.version,
            sales_order_id=sales_order.id,
            sales_order_status=sales_order.status.value,
            sales_order_version=sales_order.version,
            customer_id=customer.id,
            commercial_hold=customer.commercial_hold,
            lines=tuple(
                DeliveryOrderShipLineSnapshot(id=line.id, quantity=line.quantity)
                for line in lines
            ),
        )


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=uuid4(),
        correlation_id=f"corr-g311-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _services(ctx: ExecutionContext, *, grant_ship: bool = True):
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
        STOCK_RESOURCE,
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
                "adjust",
            },
            scope_level=ScopeLevel.TENANT,
        ).ok
    ship_actions = {"read", "ship"} if grant_ship else {"read"}
    assert permission.grant(
        ctx,
        principal_subject_id=ctx.subject_id,
        resource_type=DELIVERY_SHIP_RESOURCE,
        actions=ship_actions,
        scope_level=ScopeLevel.TENANT,
    ).ok
    crm_repo = InMemoryCRMRepository(tenant_id=ctx.tenant_id)

    def _mark_shipped(
        delivery_order_id: UUID,
        expected_version: int,
        _shipped_at,
    ) -> None:
        delivery_order = crm_repo.get_delivery_order(delivery_order_id)
        if delivery_order is None or delivery_order.version != expected_version:
            raise ValueError("delivery order ship status conflict")
        crm_repo.save_delivery_order(
            replace(
                delivery_order,
                status=DeliveryOrderStatus.SHIPPED,
                version=delivery_order.version + 1,
            ),
            expected_version=expected_version,
        )

    crm = CRMService(permission, repository=crm_repo, audit_log=audit)
    inventory = InventoryService(
        permission,
        repository=InMemoryInventoryRepository(
            tenant_id=ctx.tenant_id,
            mark_delivery_order_shipped=_mark_shipped,
        ),
        audit_log=audit,
        delivery_order_reader=_CRMShipReader(crm_repo),
    )
    return crm, inventory, audit, crm_repo


def _released_delivery_order(crm: CRMService, ctx: ExecutionContext):
    customer = crm.create_customer(
        ctx, code=f"I1-{uuid4().hex[:8]}", display_name="I1 Customer"
    ).data
    assert customer is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="I1 Opportunity"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="I1 Requirement"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="I1 line",
        quantity=Decimal("2.0000"),
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
    released = crm.release_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).data
    assert released is not None
    lines = crm.list_sales_order_lines(
        ctx, sales_order_id=sales_order.id
    ).data
    assert lines
    return released, lines, customer


def test_i1_ship_decrements_stock_and_mirrors_do_status() -> None:
    ctx = _ctx()
    crm, inventory, audit, _ = _services(ctx)
    delivery_order, lines, _ = _released_delivery_order(crm, ctx)
    for line in lines:
        assert inventory.adjust_stock(
            ctx,
            sales_order_line_id=line.id,
            quantity_delta=line.quantity,
            idempotency_key=uuid4(),
        ).ok
    key = uuid4()
    shipped = inventory.ship_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=key,
        human_confirm=True,
    )
    assert shipped.ok and shipped.data is not None
    assert shipped.data.status.value == "shipped"
    replay = inventory.ship_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=key,
        human_confirm=True,
    )
    assert replay.ok and replay.data is not None
    assert replay.data.id == shipped.data.id
    for line in lines:
        balance = inventory.get_stock_balance(
            ctx, sales_order_line_id=line.id
        ).data
        assert balance is not None
        assert balance.on_hand == Decimal("0.0000")
    do = crm.get_delivery_order(
        ctx, delivery_order_id=delivery_order.id
    ).data
    assert do is not None
    assert do.status.value == "shipped"
    events = [
        event
        for event in audit.list_events()
        if event.action.startswith("Inventory.DeliveryOrder.Ship")
    ]
    assert all(event.details == {} for event in events)


def test_i1_default_deny_and_stock_fail_closed() -> None:
    ctx = _ctx()
    crm, inventory, audit, _ = _services(ctx, grant_ship=False)
    delivery_order, lines, _ = _released_delivery_order(crm, ctx)
    denied = inventory.ship_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event
        for event in audit.list_events()
        if event.action.startswith("Inventory.DeliveryOrder.Ship")
    ]
    assert [event.result for event in events] == ["attempted", "denied"]

    ctx2 = _ctx()
    crm2, inventory2, _, _ = _services(ctx2)
    delivery_order2, _, _ = _released_delivery_order(crm2, ctx2)
    insufficient = inventory2.ship_delivery_order(
        ctx2,
        delivery_order_id=delivery_order2.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert insufficient.error_code == ErrorCode.COMMON_CONFLICT


def test_i1_commercial_hold_and_release_preconditions() -> None:
    ctx = _ctx()
    crm, inventory, _, _ = _services(ctx)
    delivery_order, lines, customer = _released_delivery_order(crm, ctx)
    for line in lines:
        assert inventory.adjust_stock(
            ctx,
            sales_order_line_id=line.id,
            quantity_delta=line.quantity,
            idempotency_key=uuid4(),
        ).ok
    assert crm.set_customer_commercial_hold(
        ctx,
        customer_id=customer.id,
        commercial_hold=True,
        expected_version=customer.version,
    ).ok
    held = inventory.ship_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert held.error_code == ErrorCode.COMMON_CONFLICT

    # Release still works on a fresh draft DO chain (regress release gate).
    customer2 = crm.create_customer(
        ctx, code=f"I1R-{uuid4().hex[:8]}", display_name="Release Regress"
    ).data
    assert customer2 is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer2.id, title="Release Opp"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="Release Req"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="line",
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
    draft_do = crm.create_delivery_order(
        ctx, sales_order_id=sales_order.id, idempotency_key=uuid4()
    ).data
    assert draft_do is not None
    released = crm.release_delivery_order(
        ctx,
        delivery_order_id=draft_do.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert released.ok and released.data is not None
    assert released.data.status.value == "released"
