"""PHX-G380 Commercial domain-event honesty contracts."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.event_bus.domain_emit import DomainEventEmitter
from kernel.event_bus.outbox import OutboxStatus
from kernel.event_bus.repository import InMemoryEventRepository
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.models import DeliveryOrderStatus, SalesOrderStatus
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
from noventi.inventory.repository import InMemoryInventoryRepository
from noventi.inventory.service import (
    DELIVERY_SHIP_RESOURCE,
    DELIVERY_UNSHIP_RESOURCE,
    STOCK_RESOURCE,
    DeliveryOrderShipLineSnapshot,
    DeliveryOrderShipSnapshot,
    InventoryService,
)
from tests.contracts.test_inventory_i1_do_ship import _released_delivery_order

SUBJECT, TENANT = uuid4(), uuid4()


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


def _ctx(tenant_id: UUID | None = None) -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT if tenant_id is None else uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant_id or TENANT,
        correlation_id=f"corr-g380-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _grant_commercial(permission: PermissionService, ctx: ExecutionContext) -> None:
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
        STOCK_RESOURCE,
        DELIVERY_SHIP_RESOURCE,
        DELIVERY_UNSHIP_RESOURCE,
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
                "ship",
                "unship",
            },
            scope_level=ScopeLevel.TENANT,
        ).ok


def test_g380_confirm_emits_sales_order_confirmed() -> None:
    ctx = _ctx()
    audit = InMemoryAuditLog()
    events = InMemoryEventRepository()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_Eligibility(),
    )
    _grant_commercial(permission, ctx)
    crm = CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=ctx.tenant_id),
        audit_log=audit,
        domain_events=DomainEventEmitter(events),
    )
    customer = crm.create_customer(
        ctx, code=f"G380-{uuid4().hex[:8]}", display_name="G380"
    ).data
    assert customer is not None
    opportunity = crm.create_opportunity(
        ctx, customer_id=customer.id, title="G380 Opp"
    ).data
    assert opportunity is not None
    requirement = crm.create_requirement(
        ctx, opportunity_id=opportunity.id, title="G380 Req"
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

    confirm_key = uuid4()
    confirmed = crm.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=confirm_key,
        human_confirm=True,
    )
    assert confirmed.ok and confirmed.data is not None

    pending = [
        entry
        for entry in events.outbox.values()
        if entry.status == OutboxStatus.PENDING
    ]
    assert len(pending) == 1
    entry = pending[0]
    assert entry.event_name == "crm.sales_order.confirmed"
    assert entry.producer == "crm.package"
    assert entry.tenant_id == ctx.tenant_id
    assert entry.payload == {
        "sales_order_id": str(sales_order.id),
        "tenant_id": str(ctx.tenant_id),
    }

    retry = crm.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=confirm_key,
        human_confirm=True,
    )
    assert retry.ok
    assert (
        len(
            [
                item
                for item in events.outbox.values()
                if item.event_name == "crm.sales_order.confirmed"
            ]
        )
        == 1
    )


def test_g380_ship_emits_delivery_order_shipped() -> None:
    ctx = _ctx()
    audit = InMemoryAuditLog()
    events = InMemoryEventRepository()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_Eligibility(),
    )
    _grant_commercial(permission, ctx)
    crm_repo = InMemoryCRMRepository(tenant_id=ctx.tenant_id)

    def _mark_shipped(
        delivery_order_id: UUID, expected_version: int, _shipped_at
    ) -> None:
        delivery_order = crm_repo.get_delivery_order(delivery_order_id)
        if delivery_order is None or delivery_order.version != expected_version:
            raise ValueError("delivery order ship status conflict")
        sales_order = crm_repo.get_sales_order(delivery_order.sales_order_id)
        if sales_order is None:
            raise ValueError("sales order not found")
        quantity = sum(
            (line.quantity for line in crm_repo.list_sales_order_lines(sales_order.id)),
            start=Decimal("0"),
        )
        crm_repo.save_delivery_order(
            replace(
                delivery_order,
                status=DeliveryOrderStatus.SHIPPED,
                version=delivery_order.version + 1,
            ),
            expected_version=expected_version,
        )
        crm_repo.save_sales_order(
            replace(
                sales_order,
                status=SalesOrderStatus.SHIPPED,
                shipped_quantity=sales_order.shipped_quantity + quantity,
                version=sales_order.version + 1,
            ),
            expected_version=sales_order.version,
        )

    emitter = DomainEventEmitter(events)
    crm = CRMService(
        permission,
        repository=crm_repo,
        audit_log=audit,
        domain_events=emitter,
    )
    inventory = InventoryService(
        permission,
        repository=InMemoryInventoryRepository(
            tenant_id=ctx.tenant_id,
            mark_delivery_order_shipped=_mark_shipped,
        ),
        audit_log=audit,
        delivery_order_reader=_CRMShipReader(crm_repo),
        domain_events=emitter,
    )
    delivery_order, lines, _customer = _released_delivery_order(crm, ctx)
    for line in lines:
        assert inventory.adjust_stock(
            ctx,
            sales_order_line_id=line.id,
            quantity_delta=line.quantity,
            idempotency_key=uuid4(),
        ).ok

    # Drop confirm event noise before asserting ship emit.
    events.outbox.clear()
    shipped = inventory.ship_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert shipped.ok and shipped.data is not None

    pending = [
        entry
        for entry in events.outbox.values()
        if entry.status == OutboxStatus.PENDING
    ]
    assert len(pending) == 1
    entry = pending[0]
    assert entry.event_name == "inventory.delivery_order.shipped"
    assert entry.producer == "inventory.package"
    assert entry.tenant_id == ctx.tenant_id
    assert entry.payload == {
        "delivery_order_id": str(delivery_order.id),
        "sales_order_id": str(delivery_order.sales_order_id),
        "tenant_id": str(ctx.tenant_id),
    }


def test_g380_in_memory_gateway_works_without_emitter() -> None:
    """Optional domain_events remains no-op so gateway in-memory tests keep working."""
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    ctx = ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g380-http",
        request_time=ExecutionContext.utc_now(),
    )
    _grant_commercial(permission, ctx)
    client = TestClient(
        create_app(
            crm_service=CRMService(
                permission,
                repository=InMemoryCRMRepository(tenant_id=TENANT),
                audit_log=audit,
            )
        )
    )
    headers = {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g380-http",
    }
    customer = client.post(
        "/v1/crm/customers",
        headers=headers,
        json={"code": f"G380-{uuid4().hex[:8]}", "display_name": "G380 HTTP"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=headers,
        json={"customer_id": customer["id"], "title": "Opp"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=headers,
        json={"opportunity_id": opportunity["id"], "title": "Req"},
    ).json()["data"]
    quote = client.post(
        "/v1/crm/quotes",
        headers=headers,
        json={"requirement_id": requirement["id"]},
    ).json()["data"]
    assert (
        client.post(
            f"/v1/crm/quotes/{quote['id']}/lines",
            headers=headers,
            json={
                "description": "line",
                "quantity": "1",
                "unit_price": "10",
            },
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"/v1/crm/quotes/{quote['id']}/issue",
            headers=headers,
            json={"idempotency_key": str(uuid4()), "human_confirm": True},
        ).status_code
        == 200
    )
    conversion = client.post(
        f"/v1/crm/quotes/{quote['id']}/convert",
        headers=headers,
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    sales_order = client.post(
        f"/v1/crm/conversions/{conversion['id']}/sales-order",
        headers=headers,
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    response = client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/confirm",
        headers=headers,
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "confirmed"
