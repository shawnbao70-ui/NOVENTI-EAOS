"""PHX-G330 CRM Return Authorization restock RET2 package contracts."""

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
    RETURN_AUTHORIZATION_RESOURCE,
    SALES_ORDER_RESOURCE,
    CRMService,
)
from noventi.inventory.repository import InMemoryInventoryRepository
from noventi.inventory.restock_adapter import InventoryReturnRestockAdapter
from noventi.inventory.service import (
    DELIVERY_SHIP_RESOURCE,
    STOCK_RESOURCE,
    InventoryService,
)
from tests.contracts.test_inventory_i1_do_ship import (
    _CRMShipReader,
    _released_delivery_order,
)


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=uuid4(),
        correlation_id=f"corr-g330-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _services(ctx: ExecutionContext):
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
        DELIVERY_SHIP_RESOURCE,
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
            },
            scope_level=ScopeLevel.TENANT,
        ).ok
    assert permission.grant(
        ctx,
        principal_subject_id=ctx.subject_id,
        resource_type=RETURN_AUTHORIZATION_RESOURCE,
        actions={"create", "read", "restock"},
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

    inventory_repo = InMemoryInventoryRepository(
        tenant_id=ctx.tenant_id,
        mark_delivery_order_shipped=_mark_shipped,
    )
    crm = CRMService(
        permission,
        repository=crm_repo,
        audit_log=audit,
        return_restock_port=InventoryReturnRestockAdapter(inventory_repo),
    )
    inventory = InventoryService(
        permission,
        repository=inventory_repo,
        audit_log=audit,
        delivery_order_reader=_CRMShipReader(crm_repo),
    )
    return crm, inventory, audit, inventory_repo


def _draft_rma(crm: CRMService, inventory: InventoryService, ctx):
    delivery_order, lines, _ = _released_delivery_order(crm, ctx)
    for line in lines:
        assert inventory.adjust_stock(
            ctx,
            sales_order_line_id=line.id,
            quantity_delta=line.quantity,
            idempotency_key=uuid4(),
        ).ok
    assert inventory.ship_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    created = crm.create_return_authorization(
        ctx,
        delivery_order_id=delivery_order.id,
        reason="damaged goods",
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert created.ok and created.data is not None
    return created.data, lines


def test_ret2_restock_increases_on_hand_and_is_idempotent() -> None:
    ctx = _ctx()
    crm, inventory, audit, inventory_repo = _services(ctx)
    authorization, lines = _draft_rma(crm, inventory, ctx)
    line = lines[0]
    after_ship = inventory.get_stock_balance(
        ctx, sales_order_line_id=line.id
    )
    assert after_ship.ok and after_ship.data is not None
    assert after_ship.data.on_hand == Decimal("0")

    key = uuid4()
    restocked = crm.restock_return_authorization(
        ctx,
        return_authorization_id=authorization.id,
        human_confirm=True,
        idempotency_key=key,
    )
    assert restocked.ok and restocked.data is not None
    assert restocked.data.status.value == "restocked"
    assert restocked.data.restock_key == key
    assert restocked.data.restocked_at is not None

    balance = inventory.get_stock_balance(ctx, sales_order_line_id=line.id)
    assert balance.ok and balance.data is not None
    assert balance.data.on_hand == line.quantity

    ledger = [
        entry
        for entry in inventory_repo._ledger.values()
        if entry.return_authorization_id == authorization.id
    ]
    assert len(ledger) == 1
    assert ledger[0].entry_type.value == "rma_restock"
    assert ledger[0].quantity_delta == line.quantity

    replay = crm.restock_return_authorization(
        ctx,
        return_authorization_id=authorization.id,
        human_confirm=True,
        idempotency_key=key,
    )
    assert replay.ok and replay.data is not None
    assert replay.data.id == authorization.id

    conflict = crm.restock_return_authorization(
        ctx,
        return_authorization_id=authorization.id,
        human_confirm=True,
        idempotency_key=uuid4(),
    )
    assert conflict.error_code == ErrorCode.COMMON_CONFLICT

    actions = [
        event.action
        for event in audit.list_events()
        if event.action.startswith("CRM.ReturnAuthorization.Restock")
        and not event.action.endswith(".Intent")
    ]
    assert "CRM.ReturnAuthorization.Restock" in actions


def test_ret2_default_deny_restock() -> None:
    ctx = _ctx()
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_Eligibility(),
    )
    crm = CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=ctx.tenant_id),
        audit_log=audit,
        return_restock_port=InventoryReturnRestockAdapter(
            InMemoryInventoryRepository(tenant_id=ctx.tenant_id)
        ),
    )
    denied = crm.restock_return_authorization(
        ctx,
        return_authorization_id=uuid4(),
        human_confirm=True,
        idempotency_key=uuid4(),
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
