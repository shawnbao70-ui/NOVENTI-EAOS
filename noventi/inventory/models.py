"""Inventory-owned stock and delivery shipment models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID


class InventoryLedgerEntryType(StrEnum):
    ADJUSTMENT = "adjustment"
    DO_SHIP = "do_ship"
    DO_UNSHIP = "do_unship"
    RMA_RESTOCK = "rma_restock"
    PO_RECEIVE = "po_receive"


class DeliveryShipStatus(StrEnum):
    SHIPPED = "shipped"
    UNSHIPPED = "unshipped"


@dataclass(slots=True)
class StockBalance:
    tenant_id: UUID
    sales_order_line_id: UUID
    on_hand: Decimal
    version: int
    updated_at: datetime


@dataclass(slots=True)
class ItemStockBalance:
    tenant_id: UUID
    inventory_item_id: UUID
    on_hand: Decimal
    version: int
    updated_at: datetime


@dataclass(slots=True)
class InventoryLedgerEntry:
    id: UUID
    tenant_id: UUID
    entry_type: InventoryLedgerEntryType
    quantity_delta: Decimal
    balance_after: Decimal
    idempotency_key: UUID
    created_at: datetime
    sales_order_line_id: UUID | None = None
    delivery_order_id: UUID | None = None
    return_authorization_id: UUID | None = None
    inventory_item_id: UUID | None = None
    purchase_order_id: UUID | None = None
    goods_receipt_id: UUID | None = None


@dataclass(slots=True)
class DeliveryShipPosting:
    id: UUID
    tenant_id: UUID
    delivery_order_id: UUID
    sales_order_id: UUID
    idempotency_key: UUID
    shipped_at: datetime
    unshipped_at: datetime | None = None
    unship_key: UUID | None = None
    status: DeliveryShipStatus = DeliveryShipStatus.SHIPPED
    version: int = 1
    pod_ref: str | None = None
    pod_captured_at: datetime | None = None


@dataclass(slots=True)
class TenantShipPodPolicy:
    tenant_id: UUID
    ship_pod_required: bool
    updated_at: datetime
    version: int = 1
