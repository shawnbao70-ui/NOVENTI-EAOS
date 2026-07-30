"""PHX-G333 Purchase Goods Receipt + inventory AP4 package contracts."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from noventi.inventory.receipt_adapter import InventoryPurchaseReceiptAdapter
from noventi.inventory.repository import InMemoryInventoryRepository
from noventi.purchase.repository import InMemoryPurchaseRepository
from noventi.purchase.service import (
    GOODS_RECEIPT_RESOURCE,
    PURCHASE_ORDER_LINE_RESOURCE,
    PURCHASE_ORDER_RESOURCE,
    SUPPLIER_RESOURCE,
    PurchaseService,
)


class _Allow:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=uuid4(),
        correlation_id=f"corr-ap4-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(ctx: ExecutionContext):
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_Allow(),
    )
    for resource, actions in (
        (SUPPLIER_RESOURCE, {"create", "read", "archive"}),
        (PURCHASE_ORDER_RESOURCE, {"create", "read", "archive"}),
        (PURCHASE_ORDER_LINE_RESOURCE, {"create", "read"}),
        (GOODS_RECEIPT_RESOURCE, {"create", "read"}),
    ):
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=resource,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok
    purchase_repo = InMemoryPurchaseRepository(tenant_id=ctx.tenant_id)
    inventory_repo = InMemoryInventoryRepository(tenant_id=ctx.tenant_id)
    service = PurchaseService(
        permission,
        repository=purchase_repo,
        audit_log=audit,
        inventory_receipt_port=InventoryPurchaseReceiptAdapter(inventory_repo),
    )
    return service, purchase_repo, inventory_repo


def _draft_po_with_line(service: PurchaseService, ctx: ExecutionContext):
    supplier = service.create_supplier(
        ctx, code="SUP-AP4", display_name="AP4 Supplier"
    )
    assert supplier.ok and supplier.data is not None
    order = service.create_purchase_order(
        ctx,
        supplier_id=supplier.data.id,
        code="PO-AP4",
        currency="USD",
        idempotency_key=uuid4(),
    )
    assert order.ok and order.data is not None
    item_id = uuid4()
    line = service.create_purchase_order_line(
        ctx,
        purchase_order_id=order.data.id,
        inventory_item_id=item_id,
        quantity=Decimal("10.000"),
        unit_price=Decimal("2.50"),
    )
    assert line.ok and line.data is not None
    return order.data, item_id


def test_ap4_receive_increases_item_on_hand() -> None:
    ctx = _ctx()
    service, purchase_repo, inventory_repo = _service(ctx)
    order, item_id = _draft_po_with_line(service, ctx)

    key = uuid4()
    receipt = service.create_goods_receipt(
        ctx,
        purchase_order_id=order.id,
        idempotency_key=key,
        human_confirm=True,
    )
    assert receipt.ok and receipt.data is not None
    assert receipt.data.status.value == "received"

    balance = inventory_repo.get_item_stock_balance(item_id)
    assert balance is not None
    assert balance.on_hand == Decimal("10.000")

    replay = service.create_goods_receipt(
        ctx,
        purchase_order_id=order.id,
        idempotency_key=key,
        human_confirm=True,
    )
    assert replay.ok and replay.data is not None
    assert replay.data.id == receipt.data.id
    assert inventory_repo.get_item_stock_balance(item_id).on_hand == Decimal(
        "10.000"
    )

    updated_po = purchase_repo.get_purchase_order(order.id)
    assert updated_po is not None
    assert updated_po.status.value == "received"


def test_ap4_inventory_failure_does_not_persist_receipt() -> None:
    ctx = _ctx()
    service, purchase_repo, inventory_repo = _service(ctx)
    order, _item_id = _draft_po_with_line(service, ctx)
    inventory_repo._fail_next_po_receive = True

    failed = service.create_goods_receipt(
        ctx,
        purchase_order_id=order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert failed.error_code == ErrorCode.COMMON_CONFLICT
    assert purchase_repo.get_goods_receipt_by_po(order.id) is None
    assert purchase_repo.get_purchase_order(order.id).status.value == "draft"


def test_ap4_requires_human_confirm() -> None:
    ctx = _ctx()
    service, _, _ = _service(ctx)
    order, _ = _draft_po_with_line(service, ctx)
    denied = service.create_goods_receipt(
        ctx,
        purchase_order_id=order.id,
        idempotency_key=uuid4(),
        human_confirm=False,
    )
    assert denied.error_code == ErrorCode.COMMON_VALIDATION_FAILED
