"""Inventory restock port used by CRM Return Authorization RET2."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Protocol
from uuid import UUID


class ReturnRestockPort(Protocol):
    def shipped_line_quantities(
        self, delivery_order_id: UUID
    ) -> tuple[tuple[UUID, Decimal], ...]: ...

    def atomic_rma_restock(
        self,
        *,
        return_authorization_id: UUID,
        delivery_order_id: UUID,
        line_quantities: tuple[tuple[UUID, Decimal], ...],
        idempotency_key: UUID,
        restocked_at: datetime,
    ) -> None: ...
