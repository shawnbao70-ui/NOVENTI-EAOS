"""PHX-G385 DO.release domain-event honesty contracts."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from kernel.event_bus.domain_emit import DomainEventEmitter
from kernel.event_bus.outbox import OutboxStatus
from kernel.event_bus.repository import InMemoryEventRepository
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import (
    AR_INVOICE_RESOURCE,
    CONVERSION_RESOURCE,
    CUSTOMER_RESOURCE,
    DELIVERY_ORDER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    POLICY_RESOURCE,
    QUOTE_LINE_RESOURCE,
    QUOTE_RESOURCE,
    REQUIREMENT_RESOURCE,
    SALES_ORDER_RESOURCE,
    CRMService,
)

SUBJECT, TENANT = uuid4(), uuid4()


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=f"corr-g385-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _grant(permission: PermissionService, ctx: ExecutionContext) -> None:
    for resource in (
        CUSTOMER_RESOURCE,
        OPPORTUNITY_RESOURCE,
        REQUIREMENT_RESOURCE,
        QUOTE_RESOURCE,
        QUOTE_LINE_RESOURCE,
        CONVERSION_RESOURCE,
        SALES_ORDER_RESOURCE,
        DELIVERY_ORDER_RESOURCE,
        POLICY_RESOURCE,
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
                "adjust",
            },
            scope_level=ScopeLevel.TENANT,
        ).ok


def _draft_delivery_order(crm: CRMService, ctx: ExecutionContext):
    customer = crm.create_customer(
        ctx, code=f"G385-{uuid4().hex[:8]}", display_name="G385"
    ).data
    assert customer is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="G385 Opp"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="G385 Req"
    ).data
    assert requirement is not None
    quote = crm.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert crm.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="line",
        quantity=Decimal("1"),
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
    confirmed = crm.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).data
    assert confirmed is not None
    delivery_order = crm.create_delivery_order(
        ctx, sales_order_id=confirmed.id, idempotency_key=uuid4()
    ).data
    assert delivery_order is not None
    return delivery_order


def test_g385_release_emits_delivery_order_released() -> None:
    ctx = _ctx()
    audit = InMemoryAuditLog()
    events = InMemoryEventRepository()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_Eligibility(),
    )
    _grant(permission, ctx)
    crm = CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=ctx.tenant_id),
        audit_log=audit,
        domain_events=DomainEventEmitter(events),
    )
    delivery_order = _draft_delivery_order(crm, ctx)
    # Drop convert/confirm noise before asserting release emit.
    events.outbox.clear()

    release_key = uuid4()
    released = crm.release_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=release_key,
        human_confirm=True,
    )
    assert released.ok and released.data is not None

    pending = [
        entry
        for entry in events.outbox.values()
        if entry.status == OutboxStatus.PENDING
    ]
    assert len(pending) == 1
    entry = pending[0]
    assert entry.event_name == "crm.delivery_order.released"
    assert entry.producer == "crm.package"
    assert entry.tenant_id == ctx.tenant_id
    assert entry.payload == {
        "delivery_order_id": str(delivery_order.id),
        "sales_order_id": str(delivery_order.sales_order_id),
        "tenant_id": str(ctx.tenant_id),
    }

    retry = crm.release_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=release_key,
        human_confirm=True,
    )
    assert retry.ok
    assert (
        len(
            [
                item
                for item in events.outbox.values()
                if item.event_name == "crm.delivery_order.released"
            ]
        )
        == 1
    )
