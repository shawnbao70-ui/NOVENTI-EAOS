"""CRM restock port adapter backed by InventoryRepository."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from noventi.inventory.repository import InventoryRepository


class InventoryReturnRestockAdapter:
    def __init__(self, repository: InventoryRepository) -> None:
        self._repository = repository

    def shipped_line_quantities(
        self, delivery_order_id: UUID
    ) -> tuple[tuple[UUID, Decimal], ...]:
        return self._repository.list_do_ship_quantities(delivery_order_id)

    def atomic_rma_restock(
        self,
        *,
        return_authorization_id: UUID,
        delivery_order_id: UUID,
        line_quantities: tuple[tuple[UUID, Decimal], ...],
        idempotency_key: UUID,
        restocked_at: datetime,
    ) -> None:
        self._repository.atomic_rma_restock(
            return_authorization_id=return_authorization_id,
            delivery_order_id=delivery_order_id,
            line_quantities=line_quantities,
            idempotency_key=idempotency_key,
            restocked_at=restocked_at,
        )
