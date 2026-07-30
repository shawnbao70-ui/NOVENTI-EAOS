"""Thin HTTP adapter for Inventory DO Ship I1 (PHX-G311)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from api.gateway.context import derive_tenant_context, reject_context_override
from api.gateway.deps import InventoryGatewayService, get_inventory_service
from api.gateway.errors import raise_for_result
from api.gateway.schemas.inventory import (
    AdjustStockRequest,
    DeliveryShipPostingEnvelope,
    SetShipPodPolicyRequest,
    ShipDeliveryOrderRequest,
    ShipPodPolicyEnvelope,
    StockBalanceEnvelope,
    StockOnHandEnvelope,
    UnshipDeliveryOrderRequest,
)
from kernel.shared.context import ExecutionContext
from noventi.inventory.models import DeliveryShipPosting, StockBalance, TenantShipPodPolicy

router = APIRouter(prefix="/v1/inventory", tags=["Inventory"])
policy_router = APIRouter(prefix="/v1/inventory/policies", tags=["Inventory"])


def _balance(balance: StockBalance) -> dict:
    return {
        "sales_order_line_id": balance.sales_order_line_id,
        "on_hand": balance.on_hand,
        "version": balance.version,
        "updated_at": balance.updated_at,
    }


def _posting(posting: DeliveryShipPosting) -> dict:
    return {
        "id": posting.id,
        "delivery_order_id": posting.delivery_order_id,
        "sales_order_id": posting.sales_order_id,
        "status": posting.status.value,
        "shipped_at": posting.shipped_at,
        "unshipped_at": posting.unshipped_at,
        "version": posting.version,
        "pod_ref": posting.pod_ref,
        "pod_captured_at": posting.pod_captured_at,
    }


def _ship_pod_policy(policy: TenantShipPodPolicy) -> dict:
    return {
        "ship_pod_required": policy.ship_pod_required,
        "updated_at": policy.updated_at,
        "version": policy.version,
    }


@router.post(
    "/stock/adjust",
    response_model=StockOnHandEnvelope,
    status_code=status.HTTP_200_OK,
)
def adjust_stock(
    body: AdjustStockRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    inventory: InventoryGatewayService = Depends(get_inventory_service),
) -> StockOnHandEnvelope:
    reject_context_override(body.model_dump())
    result = inventory.adjust_stock(
        ctx,
        sales_order_line_id=body.sales_order_line_id,
        quantity_delta=body.quantity_delta,
        idempotency_key=body.idempotency_key,
    )
    raise_for_result(result)
    assert result.data is not None
    return StockOnHandEnvelope.model_validate(
        {"data": result.data, "audit_id": result.audit_id}
    )


@router.get(
    "/stock/{sales_order_line_id}",
    response_model=StockBalanceEnvelope,
)
def get_stock_balance(
    sales_order_line_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    inventory: InventoryGatewayService = Depends(get_inventory_service),
) -> StockBalanceEnvelope:
    result = inventory.get_stock_balance(
        ctx, sales_order_line_id=sales_order_line_id
    )
    raise_for_result(result)
    assert result.data is not None
    return StockBalanceEnvelope.model_validate(
        {"data": _balance(result.data)}
    )


@router.post(
    "/delivery-orders/{delivery_order_id}/ship",
    response_model=DeliveryShipPostingEnvelope,
)
def ship_delivery_order(
    delivery_order_id: UUID,
    body: ShipDeliveryOrderRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    inventory: InventoryGatewayService = Depends(get_inventory_service),
) -> DeliveryShipPostingEnvelope:
    reject_context_override(body.model_dump())
    result = inventory.ship_delivery_order(
        ctx,
        delivery_order_id=delivery_order_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
        approval_ref=body.approval_ref,
        pod_ref=body.pod_ref,
    )
    raise_for_result(result)
    assert result.data is not None
    return DeliveryShipPostingEnvelope.model_validate(
        {"data": _posting(result.data), "audit_id": result.audit_id}
    )


@router.post(
    "/delivery-orders/{delivery_order_id}/unship",
    response_model=DeliveryShipPostingEnvelope,
)
def unship_delivery_order(
    delivery_order_id: UUID,
    body: UnshipDeliveryOrderRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    inventory: InventoryGatewayService = Depends(get_inventory_service),
) -> DeliveryShipPostingEnvelope:
    reject_context_override(body.model_dump())
    result = inventory.unship_delivery_order(
        ctx,
        delivery_order_id=delivery_order_id,
        idempotency_key=body.idempotency_key,
        human_confirm=body.human_confirm,
    )
    raise_for_result(result)
    assert result.data is not None
    return DeliveryShipPostingEnvelope.model_validate(
        {"data": _posting(result.data), "audit_id": result.audit_id}
    )


@router.get(
    "/delivery-orders/{delivery_order_id}/ship",
    response_model=DeliveryShipPostingEnvelope,
)
def get_ship_posting(
    delivery_order_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    inventory: InventoryGatewayService = Depends(get_inventory_service),
) -> DeliveryShipPostingEnvelope:
    result = inventory.get_ship_posting(
        ctx, delivery_order_id=delivery_order_id
    )
    raise_for_result(result)
    assert result.data is not None
    return DeliveryShipPostingEnvelope.model_validate(
        {"data": _posting(result.data)}
    )


@policy_router.get(
    "/ship-pod",
    response_model=ShipPodPolicyEnvelope,
)
def get_ship_pod_policy(
    ctx: ExecutionContext = Depends(derive_tenant_context),
    inventory: InventoryGatewayService = Depends(get_inventory_service),
) -> ShipPodPolicyEnvelope:
    result = inventory.get_ship_pod_policy(ctx)
    raise_for_result(result)
    assert result.data is not None
    return ShipPodPolicyEnvelope.model_validate(
        {"data": _ship_pod_policy(result.data)}
    )


@policy_router.put(
    "/ship-pod",
    response_model=ShipPodPolicyEnvelope,
)
def set_ship_pod_policy(
    body: SetShipPodPolicyRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    inventory: InventoryGatewayService = Depends(get_inventory_service),
) -> ShipPodPolicyEnvelope:
    reject_context_override(body.model_dump())
    result = inventory.set_ship_pod_policy(
        ctx,
        ship_pod_required=body.ship_pod_required,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    assert result.data is not None
    return ShipPodPolicyEnvelope.model_validate(
        {
            "data": _ship_pod_policy(result.data),
            "audit_id": result.audit_id,
        }
    )
