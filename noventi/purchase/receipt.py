"""Inventory receive port used by Purchase Goods Receipt AP4."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Protocol
from uuid import UUID


class InventoryReceiptPort(Protocol):
    def atomic_po_receive(
        self,
        *,
        purchase_order_id: UUID,
        goods_receipt_id: UUID,
        line_quantities: tuple[tuple[UUID, Decimal], ...],
        idempotency_key: UUID,
        received_at: datetime,
    ) -> None: ...

    def get_item_on_hand(self, inventory_item_id: UUID) -> Decimal: ...
