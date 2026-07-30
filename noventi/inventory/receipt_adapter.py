"""Purchase receive port adapter backed by InventoryRepository."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from noventi.inventory.repository import InventoryRepository


class InventoryPurchaseReceiptAdapter:
    def __init__(self, repository: InventoryRepository) -> None:
        self._repository = repository

    def atomic_po_receive(
        self,
        *,
        purchase_order_id: UUID,
        goods_receipt_id: UUID,
        line_quantities: tuple[tuple[UUID, Decimal], ...],
        idempotency_key: UUID,
        received_at: datetime,
    ) -> None:
        self._repository.atomic_po_receive(
            purchase_order_id=purchase_order_id,
            goods_receipt_id=goods_receipt_id,
            line_quantities=line_quantities,
            idempotency_key=idempotency_key,
            received_at=received_at,
        )

    def get_item_on_hand(self, inventory_item_id: UUID) -> Decimal:
        balance = self._repository.get_item_stock_balance(inventory_item_id)
        if balance is None:
            return Decimal("0")
        return balance.on_hand
