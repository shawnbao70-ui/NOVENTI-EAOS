"""Thin HTTP adapter for Purchase AP1–AP5 slices."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from api.gateway.context import derive_tenant_context, reject_context_override
from api.gateway.deps import (
    PurchaseGatewayService,
    Supplier360GatewayService,
    get_purchase_service,
    get_supplier360_service,
)
from api.gateway.errors import raise_for_result
from api.gateway.schemas.purchase import (
    ApBillEnvelope,
    ApBillLineEnvelope,
    ApBillLineListEnvelope,
    ApPaymentEnvelope,
    ApWriteOffEnvelope,
    ApplyApPaymentRequest,
    ArchiveApBillLineRequest,
    ArchivePurchaseOrderRequest,
    ArchiveSupplierRequest,
    CreateApBillLineRequest,
    CreateApBillRequest,
    CreateApPaymentRequest,
    CreateApWriteOffRequest,
    CreateGoodsReceiptRequest,
    CreatePurchaseOrderLineRequest,
    CreatePurchaseOrderRequest,
    CreateSupplierRequest,
    CreateThreeWayMatchRequest,
    GoodsReceiptEnvelope,
    PurchaseOrderEnvelope,
    PurchaseOrderLineEnvelope,
    PostApBillRequest,
    CloseApBillRequest,
    SetThreeWayMatchTolerancePolicyRequest,
    SupplierEnvelope,
    SupplierBalanceEnvelope,
    Supplier360Envelope,
    SupplierAdvisoryEnvelope,
    ThreeWayMatchEnvelope,
    ThreeWayMatchTolerancePolicyEnvelope,
    UpdateSupplierRequest,
)
from kernel.shared.context import ExecutionContext
from noventi.purchase.models import (
    ApBill,
    ApBillLine,
    ApPayment,
    ApWriteOff,
    GoodsReceipt,
    PurchaseOrder,
    PurchaseOrderLine,
    Supplier,
    TenantThreeWayMatchTolerancePolicy,
    ThreeWayMatch,
)
from noventi.purchase.supplier360 import Supplier360Projection

supplier_router = APIRouter(prefix="/v1/purchase/suppliers", tags=["Purchase"])
ap_bill_router = APIRouter(prefix="/v1/purchase/ap-bills", tags=["Purchase"])
ap_payment_router = APIRouter(
    prefix="/v1/purchase/ap-payments", tags=["Purchase"]
)
ap_write_off_router = APIRouter(
    prefix="/v1/purchase/ap-write-offs", tags=["Purchase"]
)
purchase_order_router = APIRouter(
    prefix="/v1/purchase/purchase-orders", tags=["Purchase"]
)
three_way_match_router = APIRouter(
    prefix="/v1/purchase/three-way-matches", tags=["Purchase"]
)
policy_router = APIRouter(prefix="/v1/purchase/policies", tags=["Purchase"])


def _supplier(supplier: Supplier) -> dict:
    return {
        "id": supplier.id,
        "code": supplier.code,
        "display_name": supplier.display_name,
        "status": supplier.status.value,
        "created_at": supplier.created_at,
        "updated_at": supplier.updated_at,
        "archived_at": supplier.archived_at,
        "version": supplier.version,
    }


def _ap_bill(bill: ApBill) -> dict:
    return {
        "id": bill.id,
        "supplier_id": bill.supplier_id,
        "code": bill.code,
        "currency": bill.currency,
        "total_amount": bill.total_amount,
        "paid_amount": bill.paid_amount,
        "write_off_amount": bill.write_off_amount,
        "remaining_amount": (
            bill.total_amount - bill.paid_amount - bill.write_off_amount
        ),
        "status": bill.status.value,
        "created_at": bill.created_at,
        "version": bill.version,
    }


def _ap_bill_line(line: ApBillLine) -> dict:
    return {
        "id": line.id,
        "ap_bill_id": line.ap_bill_id,
        "line_number": line.line_number,
        "description": line.description,
        "quantity": line.quantity,
        "unit_price": line.unit_price,
        "amount": line.amount,
        "status": line.status.value,
        "created_at": line.created_at,
        "updated_at": line.updated_at,
        "archived_at": line.archived_at,
        "version": line.version,
    }


def _ap_payment(payment: ApPayment) -> dict:
    return {
        "id": payment.id,
        "supplier_id": payment.supplier_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "functional_currency": payment.functional_currency,
        "fx_rate": payment.fx_rate,
        "functional_amount": payment.functional_amount,
        "status": payment.status.value,
        "ap_bill_id": payment.ap_bill_id,
        "ap_bill_version": payment.ap_bill_version,
        "apply_key": payment.apply_key,
        "created_at": payment.created_at,
        "applied_at": payment.applied_at,
        "version": payment.version,
    }


def _ap_write_off(write_off: ApWriteOff) -> dict:
    return {
        "id": write_off.id,
        "ap_bill_id": write_off.ap_bill_id,
        "amount": write_off.amount,
        "currency": write_off.currency,
        "reason": write_off.reason,
        "created_at": write_off.created_at,
        "version": write_off.version,
    }


def _purchase_order(order: PurchaseOrder) -> dict:
    return {
        "id": order.id,
        "supplier_id": order.supplier_id,
        "code": order.code,
        "currency": order.currency,
        "notes": order.notes,
        "status": order.status.value,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "archived_at": order.archived_at,
        "version": order.version,
    }


def _purchase_order_line(line: PurchaseOrderLine) -> dict:
    return {
        "id": line.id,
        "purchase_order_id": line.purchase_order_id,
        "line_number": line.line_number,
        "inventory_item_id": line.inventory_item_id,
        "quantity": line.quantity,
        "unit_price": line.unit_price,
        "status": line.status.value,
        "created_at": line.created_at,
        "updated_at": line.updated_at,
        "version": line.version,
    }


def _goods_receipt(receipt: GoodsReceipt) -> dict:
    return {
        "id": receipt.id,
        "purchase_order_id": receipt.purchase_order_id,
        "code": receipt.code,
        "status": receipt.status.value,
        "received_at": receipt.received_at,
        "created_at": receipt.created_at,
        "version": receipt.version,
    }


def _three_way_match(match: ThreeWayMatch) -> dict:
    return {
        "id": match.id,
        "purchase_order_id": match.purchase_order_id,
        "goods_receipt_id": match.goods_receipt_id,
        "ap_bill_id": match.ap_bill_id,
        "status": match.status.value,
        "created_at": match.created_at,
        "version": match.version,
    }


@supplier_router.post(
    "",
    response_model=SupplierEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_supplier(
    body: CreateSupplierRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> SupplierEnvelope:
    reject_context_override(body.model_dump())
    result = purchase.create_supplier(
        ctx,
        code=body.code,
        display_name=body.display_name,
    )
    raise_for_result(result)
    assert result.data is not None
    return SupplierEnvelope.model_validate(
        {"data": _supplier(result.data), "audit_id": result.audit_id}
    )


@supplier_router.get("/{supplier_id}", response_model=SupplierEnvelope)
def get_supplier(
    supplier_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> SupplierEnvelope:
    result = purchase.get_supplier(ctx, supplier_id=supplier_id)
    raise_for_result(result)
    assert result.data is not None
    return SupplierEnvelope.model_validate({"data": _supplier(result.data)})


@supplier_router.get(
    "/{supplier_id}/balances", response_model=SupplierBalanceEnvelope
)
def get_supplier_balances(
    supplier_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> SupplierBalanceEnvelope:
    result = purchase.get_supplier_balance(ctx, supplier_id=supplier_id)
    raise_for_result(result)
    assert result.data is not None
    return SupplierBalanceEnvelope.model_validate(
        {
            "data": {
                "supplier_id": result.data.supplier_id,
                "balances": result.data.balances,
            },
            "audit_id": result.audit_id,
        }
    )


def _supplier360(projection: Supplier360Projection) -> dict:
    return {
        "supplier_id": projection.supplier_id,
        "supplier_code": projection.supplier_code,
        "display_name": projection.display_name,
        "status": projection.status.value,
        "balances": projection.balances,
        "bill_traces": [
            {
                "id": bill.id,
                "code": bill.code,
                "status": bill.status.value,
                "currency": bill.currency,
                "total_amount": bill.total_amount,
            }
            for bill in projection.bill_traces
        ],
        "payment_traces": [
            {
                "id": payment.id,
                "status": payment.status.value,
                "currency": payment.currency,
                "amount": payment.amount,
                "ap_bill_id": payment.ap_bill_id,
            }
            for payment in projection.payment_traces
        ],
    }


@supplier_router.get(
    "/{supplier_id}/360", response_model=Supplier360Envelope
)
def get_supplier360(
    supplier_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    supplier360: Supplier360GatewayService = Depends(get_supplier360_service),
) -> Supplier360Envelope:
    result = supplier360.get_supplier360(ctx, supplier_id)
    raise_for_result(result)
    assert result.data is not None
    return Supplier360Envelope.model_validate(
        {
            "data": _supplier360(result.data),
            "audit_id": result.audit_id,
        }
    )


@supplier_router.get(
    "/{supplier_id}/advisory", response_model=SupplierAdvisoryEnvelope
)
def get_supplier_advisory(
    supplier_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    supplier360: Supplier360GatewayService = Depends(get_supplier360_service),
) -> SupplierAdvisoryEnvelope:
    """Read-only advisory over Supplier360; execution_authority remains none (G391)."""

    result = supplier360.get_supplier360(ctx, supplier_id)
    raise_for_result(result)
    assert result.data is not None
    projection = _supplier360(result.data)
    return SupplierAdvisoryEnvelope.model_validate(
        {
            "data": {
                "supplier_id": projection["supplier_id"],
                "read_source": "supplier360",
                "supplier360": projection,
                "execution_authority": "none",
                "commercial_auto_write": False,
            },
            "audit_id": result.audit_id,
        }
    )


@supplier_router.patch("/{supplier_id}", response_model=SupplierEnvelope)
def update_supplier(
    supplier_id: UUID,
    body: UpdateSupplierRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> SupplierEnvelope:
    reject_context_override(body.model_dump())
    result = purchase.update_supplier(
        ctx,
        supplier_id=supplier_id,
        display_name=body.display_name,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return SupplierEnvelope.model_validate(
        {"data": _supplier(result.data), "audit_id": result.audit_id}
    )


@supplier_router.post(
    "/{supplier_id}/archive", response_model=SupplierEnvelope
)
def archive_supplier(
    supplier_id: UUID,
    body: ArchiveSupplierRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> SupplierEnvelope:
    reject_context_override(body.model_dump())
    result = purchase.archive_supplier(
        ctx,
        supplier_id=supplier_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return SupplierEnvelope.model_validate(
        {"data": _supplier(result.data), "audit_id": result.audit_id}
    )


@ap_bill_router.post(
    "",
    response_model=ApBillEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_ap_bill(
    body: CreateApBillRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> ApBillEnvelope:
    reject_context_override(body.model_dump())
    result = purchase.create_ap_bill(
        ctx,
        supplier_id=body.supplier_id,
        code=body.code,
        currency=body.currency,
        total_amount=body.total_amount,
        idempotency_key=body.idempotency_key,
    )
    raise_for_result(result)
    assert result.data is not None
    return ApBillEnvelope.model_validate(
        {"data": _ap_bill(result.data), "audit_id": result.audit_id}
    )


@ap_bill_router.get("/{bill_id}", response_model=ApBillEnvelope)
def get_ap_bill(
    bill_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> ApBillEnvelope:
    result = purchase.get_ap_bill(ctx, bill_id=bill_id)
    raise_for_result(result)
    assert result.data is not None
    return ApBillEnvelope.model_validate({"data": _ap_bill(result.data)})


@ap_bill_router.post("/{bill_id}/post", response_model=ApBillEnvelope)
def post_ap_bill(
    bill_id: UUID,
    body: PostApBillRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> ApBillEnvelope:
    reject_context_override(body.model_dump())
    result = purchase.post_ap_bill(
        ctx,
        bill_id=bill_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return ApBillEnvelope.model_validate(
        {"data": _ap_bill(result.data), "audit_id": result.audit_id}
    )


@ap_write_off_router.post(
    "", response_model=ApWriteOffEnvelope, status_code=status.HTTP_201_CREATED
)
def create_ap_write_off(
    body: CreateApWriteOffRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> ApWriteOffEnvelope:
    reject_context_override(body.model_dump())
    result = purchase.create_ap_write_off(
        ctx,
        ap_bill_id=body.ap_bill_id,
        amount=body.amount,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
        reason=body.reason,
    )
    raise_for_result(result)
    assert result.data is not None
    return ApWriteOffEnvelope.model_validate(
        {"data": _ap_write_off(result.data), "audit_id": result.audit_id}
    )


@ap_bill_router.post("/{bill_id}/close", response_model=ApBillEnvelope)
def close_ap_bill(
    bill_id: UUID,
    body: CloseApBillRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> ApBillEnvelope:
    reject_context_override(body.model_dump())
    result = purchase.close_ap_bill(
        ctx, bill_id=bill_id, human_confirm=body.human_confirm
    )
    raise_for_result(result)
    assert result.data is not None
    return ApBillEnvelope.model_validate(
        {"data": _ap_bill(result.data), "audit_id": result.audit_id}
    )


@ap_payment_router.post(
    "", response_model=ApPaymentEnvelope, status_code=status.HTTP_201_CREATED
)
def create_ap_payment(
    body: CreateApPaymentRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> ApPaymentEnvelope:
    reject_context_override(body.model_dump())
    result = purchase.create_ap_payment(
        ctx,
        supplier_id=body.supplier_id,
        amount=body.amount,
        currency=body.currency,
        functional_currency=body.functional_currency,
        fx_rate=body.fx_rate,
        functional_amount=body.functional_amount,
        idempotency_key=body.idempotency_key,
    )
    raise_for_result(result)
    assert result.data is not None
    return ApPaymentEnvelope.model_validate(
        {"data": _ap_payment(result.data), "audit_id": result.audit_id}
    )


@ap_payment_router.get("/{payment_id}", response_model=ApPaymentEnvelope)
def get_ap_payment(
    payment_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> ApPaymentEnvelope:
    result = purchase.get_ap_payment(ctx, payment_id=payment_id)
    raise_for_result(result)
    assert result.data is not None
    return ApPaymentEnvelope.model_validate({"data": _ap_payment(result.data)})


@ap_payment_router.post(
    "/{payment_id}/apply", response_model=ApPaymentEnvelope
)
def apply_ap_payment_to_bill(
    payment_id: UUID,
    body: ApplyApPaymentRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> ApPaymentEnvelope:
    reject_context_override(body.model_dump())
    result = purchase.apply_ap_payment_to_bill(
        ctx,
        payment_id=payment_id,
        bill_id=body.ap_bill_id,
        apply_key=body.apply_key,
    )
    raise_for_result(result)
    assert result.data is not None
    return ApPaymentEnvelope.model_validate(
        {"data": _ap_payment(result.data), "audit_id": result.audit_id}
    )


@ap_bill_router.post(
    "/{bill_id}/lines",
    response_model=ApBillLineEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_ap_bill_line(
    bill_id: UUID,
    body: CreateApBillLineRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> ApBillLineEnvelope:
    reject_context_override(body.model_dump())
    result = purchase.create_ap_bill_line(
        ctx,
        ap_bill_id=bill_id,
        description=body.description,
        quantity=body.quantity,
        unit_price=body.unit_price,
    )
    raise_for_result(result)
    assert result.data is not None
    return ApBillLineEnvelope.model_validate(
        {"data": _ap_bill_line(result.data), "audit_id": result.audit_id}
    )


@ap_bill_router.get(
    "/{bill_id}/lines",
    response_model=ApBillLineListEnvelope,
)
def list_ap_bill_lines(
    bill_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> ApBillLineListEnvelope:
    result = purchase.list_ap_bill_lines(ctx, ap_bill_id=bill_id)
    raise_for_result(result)
    assert result.data is not None
    return ApBillLineListEnvelope.model_validate(
        {"data": [_ap_bill_line(item) for item in result.data]}
    )


@ap_bill_router.get(
    "/{bill_id}/lines/{line_id}",
    response_model=ApBillLineEnvelope,
)
def get_ap_bill_line(
    bill_id: UUID,
    line_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> ApBillLineEnvelope:
    result = purchase.get_ap_bill_line(
        ctx, ap_bill_id=bill_id, line_id=line_id
    )
    raise_for_result(result)
    assert result.data is not None
    return ApBillLineEnvelope.model_validate(
        {"data": _ap_bill_line(result.data)}
    )


@ap_bill_router.post(
    "/{bill_id}/lines/{line_id}/archive",
    response_model=ApBillLineEnvelope,
)
def archive_ap_bill_line(
    bill_id: UUID,
    line_id: UUID,
    body: ArchiveApBillLineRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> ApBillLineEnvelope:
    reject_context_override(body.model_dump())
    result = purchase.archive_ap_bill_line(
        ctx,
        ap_bill_id=bill_id,
        line_id=line_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return ApBillLineEnvelope.model_validate(
        {"data": _ap_bill_line(result.data), "audit_id": result.audit_id}
    )


@purchase_order_router.post(
    "",
    response_model=PurchaseOrderEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_purchase_order(
    body: CreatePurchaseOrderRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> PurchaseOrderEnvelope:
    reject_context_override(body.model_dump())
    result = purchase.create_purchase_order(
        ctx,
        supplier_id=body.supplier_id,
        code=body.code,
        currency=body.currency,
        idempotency_key=body.idempotency_key,
        notes=body.notes,
    )
    raise_for_result(result)
    assert result.data is not None
    return PurchaseOrderEnvelope.model_validate(
        {"data": _purchase_order(result.data), "audit_id": result.audit_id}
    )


@purchase_order_router.get(
    "/{purchase_order_id}", response_model=PurchaseOrderEnvelope
)
def get_purchase_order(
    purchase_order_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> PurchaseOrderEnvelope:
    result = purchase.get_purchase_order(
        ctx, purchase_order_id=purchase_order_id
    )
    raise_for_result(result)
    assert result.data is not None
    return PurchaseOrderEnvelope.model_validate(
        {"data": _purchase_order(result.data)}
    )


@purchase_order_router.post(
    "/{purchase_order_id}/archive", response_model=PurchaseOrderEnvelope
)
def archive_purchase_order(
    purchase_order_id: UUID,
    body: ArchivePurchaseOrderRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> PurchaseOrderEnvelope:
    reject_context_override(body.model_dump())
    result = purchase.archive_purchase_order(
        ctx,
        purchase_order_id=purchase_order_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return PurchaseOrderEnvelope.model_validate(
        {"data": _purchase_order(result.data), "audit_id": result.audit_id}
    )


@purchase_order_router.post(
    "/{purchase_order_id}/lines",
    response_model=PurchaseOrderLineEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_purchase_order_line(
    purchase_order_id: UUID,
    body: CreatePurchaseOrderLineRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> PurchaseOrderLineEnvelope:
    reject_context_override(body.model_dump())
    result = purchase.create_purchase_order_line(
        ctx,
        purchase_order_id=purchase_order_id,
        inventory_item_id=body.inventory_item_id,
        quantity=body.quantity,
        unit_price=body.unit_price,
    )
    raise_for_result(result)
    assert result.data is not None
    return PurchaseOrderLineEnvelope.model_validate(
        {
            "data": _purchase_order_line(result.data),
            "audit_id": result.audit_id,
        }
    )


@purchase_order_router.post(
    "/{purchase_order_id}/goods-receipt",
    response_model=GoodsReceiptEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_goods_receipt(
    purchase_order_id: UUID,
    body: CreateGoodsReceiptRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> GoodsReceiptEnvelope:
    reject_context_override(body.model_dump())
    result = purchase.create_goods_receipt(
        ctx,
        purchase_order_id=purchase_order_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return GoodsReceiptEnvelope.model_validate(
        {"data": _goods_receipt(result.data), "audit_id": result.audit_id}
    )


@three_way_match_router.post(
    "",
    response_model=ThreeWayMatchEnvelope,
    status_code=status.HTTP_201_CREATED,
)
def create_three_way_match(
    body: CreateThreeWayMatchRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> ThreeWayMatchEnvelope:
    reject_context_override(body.model_dump())
    result = purchase.create_three_way_match(
        ctx,
        purchase_order_id=body.purchase_order_id,
        goods_receipt_id=body.goods_receipt_id,
        ap_bill_id=body.ap_bill_id,
        idempotency_key=body.idempotency_key,
    )
    raise_for_result(result)
    assert result.data is not None
    return ThreeWayMatchEnvelope.model_validate(
        {"data": _three_way_match(result.data), "audit_id": result.audit_id}
    )


def _three_way_match_tolerance_policy(
    policy: TenantThreeWayMatchTolerancePolicy,
) -> dict:
    return {
        "amount_tolerance_abs": policy.amount_tolerance_abs,
        "amount_tolerance_pct": policy.amount_tolerance_pct,
        "updated_at": policy.updated_at,
        "version": policy.version,
    }


@policy_router.get(
    "/three-way-match-tolerance",
    response_model=ThreeWayMatchTolerancePolicyEnvelope,
)
def get_three_way_match_tolerance_policy(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> ThreeWayMatchTolerancePolicyEnvelope:
    result = purchase.get_three_way_match_tolerance_policy(ctx)
    raise_for_result(result)
    assert result.data is not None
    return ThreeWayMatchTolerancePolicyEnvelope.model_validate(
        {"data": _three_way_match_tolerance_policy(result.data)}
    )


@policy_router.put(
    "/three-way-match-tolerance",
    response_model=ThreeWayMatchTolerancePolicyEnvelope,
)
def set_three_way_match_tolerance_policy(
    body: SetThreeWayMatchTolerancePolicyRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    purchase: PurchaseGatewayService = Depends(get_purchase_service),
) -> ThreeWayMatchTolerancePolicyEnvelope:
    reject_context_override(body.model_dump())
    result = purchase.set_three_way_match_tolerance_policy(
        ctx,
        amount_tolerance_abs=body.amount_tolerance_abs,
        amount_tolerance_pct=body.amount_tolerance_pct,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return ThreeWayMatchTolerancePolicyEnvelope.model_validate(
        {
            "data": _three_way_match_tolerance_policy(result.data),
            "audit_id": result.audit_id,
        }
    )