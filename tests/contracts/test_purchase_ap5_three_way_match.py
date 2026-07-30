"""PHX-G334 Purchase Three-Way Match AP5 package contracts."""

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
from noventi.purchase.models import ThreeWayMatchStatus
from noventi.purchase.repository import InMemoryPurchaseRepository
from noventi.purchase.service import (
    AP_BILL_LINE_RESOURCE,
    AP_BILL_RESOURCE,
    GOODS_RECEIPT_RESOURCE,
    PURCHASE_ORDER_LINE_RESOURCE,
    PURCHASE_ORDER_RESOURCE,
    SUPPLIER_RESOURCE,
    THREE_WAY_MATCH_RESOURCE,
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
        correlation_id=f"corr-ap5-{uuid4()}",
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
        (AP_BILL_RESOURCE, {"create", "read"}),
        (AP_BILL_LINE_RESOURCE, {"create", "read", "archive"}),
        (PURCHASE_ORDER_RESOURCE, {"create", "read", "archive"}),
        (PURCHASE_ORDER_LINE_RESOURCE, {"create", "read"}),
        (GOODS_RECEIPT_RESOURCE, {"create", "read"}),
        (THREE_WAY_MATCH_RESOURCE, {"create", "read"}),
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
    return service, purchase_repo


def _received_po_and_bill(
    service: PurchaseService,
    ctx: ExecutionContext,
    *,
    unit_price: Decimal = Decimal("2.50"),
    bill_amount: Decimal | None = None,
):
    supplier = service.create_supplier(
        ctx, code="SUP-AP5", display_name="AP5 Supplier"
    )
    assert supplier.ok and supplier.data is not None
    order = service.create_purchase_order(
        ctx,
        supplier_id=supplier.data.id,
        code="PO-AP5",
        currency="USD",
        idempotency_key=uuid4(),
    )
    assert order.ok and order.data is not None
    line = service.create_purchase_order_line(
        ctx,
        purchase_order_id=order.data.id,
        inventory_item_id=uuid4(),
        quantity=Decimal("4.000"),
        unit_price=unit_price,
    )
    assert line.ok
    receipt = service.create_goods_receipt(
        ctx,
        purchase_order_id=order.data.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert receipt.ok and receipt.data is not None
    expected = bill_amount
    if expected is None and unit_price is not None:
        expected = (Decimal("4.000") * unit_price).quantize(Decimal("0.01"))
    elif expected is None:
        expected = Decimal("0.00")
    bill = service.create_ap_bill(
        ctx,
        supplier_id=supplier.data.id,
        code="APB-AP5",
        currency="USD",
        total_amount=expected,
        idempotency_key=uuid4(),
    )
    assert bill.ok and bill.data is not None
    bill_line = service.create_ap_bill_line(
        ctx,
        ap_bill_id=bill.data.id,
        description="parts",
        quantity=Decimal("4.000"),
        unit_price=unit_price if unit_price is not None else Decimal("1.00"),
    )
    assert bill_line.ok
    return order.data, receipt.data, bill.data


def test_ap5_matched_three_way_match() -> None:
    ctx = _ctx()
    service, repo = _service(ctx)
    order, receipt, bill = _received_po_and_bill(service, ctx)
    key = uuid4()
    matched = service.create_three_way_match(
        ctx,
        purchase_order_id=order.id,
        goods_receipt_id=receipt.id,
        ap_bill_id=bill.id,
        idempotency_key=key,
    )
    assert matched.ok and matched.data is not None
    assert matched.data.status == ThreeWayMatchStatus.MATCHED

    replay = service.create_three_way_match(
        ctx,
        purchase_order_id=order.id,
        goods_receipt_id=receipt.id,
        ap_bill_id=bill.id,
        idempotency_key=key,
    )
    assert replay.ok and replay.data is not None
    assert replay.data.id == matched.data.id


def test_ap5_mismatch_persisted_with_conflict() -> None:
    ctx = _ctx()
    service, repo = _service(ctx)
    order, receipt, _bill = _received_po_and_bill(service, ctx)
    bad_bill = service.create_ap_bill(
        ctx,
        supplier_id=order.supplier_id,
        code="APB-BAD",
        currency="USD",
        total_amount=Decimal("1.00"),
        idempotency_key=uuid4(),
    )
    assert bad_bill.ok and bad_bill.data is not None
    assert service.create_ap_bill_line(
        ctx,
        ap_bill_id=bad_bill.data.id,
        description="wrong",
        quantity=Decimal("1.000"),
        unit_price=Decimal("1.00"),
    ).ok

    result = service.create_three_way_match(
        ctx,
        purchase_order_id=order.id,
        goods_receipt_id=receipt.id,
        ap_bill_id=bad_bill.data.id,
        idempotency_key=uuid4(),
    )
    assert result.error_code == ErrorCode.COMMON_CONFLICT
    assert "mismatch" in (result.error_message or "").casefold()
    stored = repo.get_three_way_match_by_po(order.id)
    assert stored is not None
    assert stored.status == ThreeWayMatchStatus.MISMATCH


def test_ap5_fail_closed_grn_must_belong_to_po() -> None:
    ctx = _ctx()
    service, _ = _service(ctx)
    order_a, receipt_a, bill = _received_po_and_bill(service, ctx)
    order_b = service.create_purchase_order(
        ctx,
        supplier_id=order_a.supplier_id,
        code="PO-AP5-B",
        currency="USD",
        idempotency_key=uuid4(),
    )
    assert order_b.ok and order_b.data is not None
    assert service.create_purchase_order_line(
        ctx,
        purchase_order_id=order_b.data.id,
        inventory_item_id=uuid4(),
        quantity=Decimal("1.000"),
        unit_price=Decimal("1.00"),
    ).ok
    receipt_b = service.create_goods_receipt(
        ctx,
        purchase_order_id=order_b.data.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert receipt_b.ok and receipt_b.data is not None

    denied = service.create_three_way_match(
        ctx,
        purchase_order_id=order_a.id,
        goods_receipt_id=receipt_b.data.id,
        ap_bill_id=bill.id,
        idempotency_key=uuid4(),
    )
    assert denied.error_code == ErrorCode.COMMON_CONFLICT
    assert "belong" in (denied.error_message or "").casefold()
