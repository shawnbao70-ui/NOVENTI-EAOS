"""Tenant-bound repository contract for Inventory I1."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from typing import Protocol
from uuid import UUID, uuid4

from noventi.inventory.models import (
    DeliveryShipPosting,
    DeliveryShipStatus,
    InventoryLedgerEntry,
    InventoryLedgerEntryType,
    ItemStockBalance,
    StockBalance,
    TenantShipPodPolicy,
)


class InventoryRepository(Protocol):
    def get_adjustment_by_key(
        self, idempotency_key: UUID
    ) -> InventoryLedgerEntry | None: ...

    def atomic_adjust(
        self,
        *,
        sales_order_line_id: UUID,
        quantity_delta: Decimal,
        idempotency_key: UUID,
        adjusted_at: datetime,
    ) -> StockBalance: ...

    def get_stock_balance(
        self, sales_order_line_id: UUID
    ) -> StockBalance | None: ...

    def get_item_stock_balance(
        self, inventory_item_id: UUID
    ) -> ItemStockBalance | None: ...

    def get_ship_posting(
        self, delivery_order_id: UUID
    ) -> DeliveryShipPosting | None: ...

    def get_ship_posting_by_key(
        self, idempotency_key: UUID
    ) -> DeliveryShipPosting | None: ...

    def atomic_ship(
        self,
        *,
        delivery_order_id: UUID,
        sales_order_id: UUID,
        expected_delivery_order_version: int,
        line_quantities: tuple[tuple[UUID, Decimal], ...],
        idempotency_key: UUID,
        shipped_at: datetime,
        pod_ref: str | None = None,
        pod_captured_at: datetime | None = None,
    ) -> DeliveryShipPosting: ...

    def atomic_unship(
        self,
        *,
        delivery_order_id: UUID,
        sales_order_id: UUID,
        expected_delivery_order_version: int,
        line_quantities: tuple[tuple[UUID, Decimal], ...],
        idempotency_key: UUID,
        unshipped_at: datetime,
    ) -> DeliveryShipPosting: ...

    def list_do_ship_quantities(
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

    def atomic_po_receive(
        self,
        *,
        purchase_order_id: UUID,
        goods_receipt_id: UUID,
        line_quantities: tuple[tuple[UUID, Decimal], ...],
        idempotency_key: UUID,
        received_at: datetime,
    ) -> None: ...

    def get_ship_pod_policy(self) -> TenantShipPodPolicy | None: ...

    def save_ship_pod_policy(
        self,
        policy: TenantShipPodPolicy,
        *,
        expected_version: int,
    ) -> None: ...


class InMemoryInventoryRepository:
    def __init__(
        self,
        *,
        tenant_id: UUID,
        mark_delivery_order_shipped: (
            Callable[[UUID, int, datetime], None] | None
        ) = None,
        mark_delivery_order_unshipped: (
            Callable[[UUID, int, datetime], None] | None
        ) = None,
    ) -> None:
        self._tenant_id = tenant_id
        self._mark_delivery_order_shipped = mark_delivery_order_shipped
        self._mark_delivery_order_unshipped = mark_delivery_order_unshipped
        self._balances: dict[UUID, StockBalance] = {}
        self._item_balances: dict[UUID, ItemStockBalance] = {}
        self._ledger: dict[UUID, InventoryLedgerEntry] = {}
        self._ship_postings: list[DeliveryShipPosting] = []
        self._ship_pod_policy: TenantShipPodPolicy | None = None
        self._fail_next_po_receive = False

    def get_adjustment_by_key(
        self, idempotency_key: UUID
    ) -> InventoryLedgerEntry | None:
        for entry in self._ledger.values():
            if (
                entry.tenant_id == self._tenant_id
                and entry.idempotency_key == idempotency_key
                and entry.entry_type == InventoryLedgerEntryType.ADJUSTMENT
            ):
                return entry
        return None

    def atomic_adjust(
        self,
        *,
        sales_order_line_id: UUID,
        quantity_delta: Decimal,
        idempotency_key: UUID,
        adjusted_at: datetime,
    ) -> StockBalance:
        if self.get_adjustment_by_key(idempotency_key) is not None:
            raise ValueError("adjustment idempotency conflict")
        current = self._balances.get(sales_order_line_id)
        on_hand = (current.on_hand if current is not None else Decimal("0")) + (
            quantity_delta
        )
        if on_hand < 0:
            raise ValueError("insufficient stock")
        balance = StockBalance(
            tenant_id=self._tenant_id,
            sales_order_line_id=sales_order_line_id,
            on_hand=on_hand,
            version=(current.version + 1) if current is not None else 1,
            updated_at=adjusted_at,
        )
        self._balances[sales_order_line_id] = balance
        entry = InventoryLedgerEntry(
            id=uuid4(),
            tenant_id=self._tenant_id,
            sales_order_line_id=sales_order_line_id,
            delivery_order_id=None,
            entry_type=InventoryLedgerEntryType.ADJUSTMENT,
            quantity_delta=quantity_delta,
            balance_after=on_hand,
            idempotency_key=idempotency_key,
            created_at=adjusted_at,
        )
        self._ledger[entry.id] = entry
        return balance

    def get_stock_balance(
        self, sales_order_line_id: UUID
    ) -> StockBalance | None:
        balance = self._balances.get(sales_order_line_id)
        if balance is None or balance.tenant_id != self._tenant_id:
            return None
        return balance

    def get_item_stock_balance(
        self, inventory_item_id: UUID
    ) -> ItemStockBalance | None:
        balance = self._item_balances.get(inventory_item_id)
        if balance is None or balance.tenant_id != self._tenant_id:
            return None
        return balance

    def get_ship_posting(
        self, delivery_order_id: UUID
    ) -> DeliveryShipPosting | None:
        candidates = [
            posting
            for posting in self._ship_postings
            if posting.delivery_order_id == delivery_order_id
            and posting.tenant_id == self._tenant_id
        ]
        if not candidates:
            return None
        for posting in candidates:
            if posting.status == DeliveryShipStatus.SHIPPED:
                return posting
        return max(candidates, key=lambda posting: posting.shipped_at)

    def get_ship_posting_by_key(
        self, idempotency_key: UUID
    ) -> DeliveryShipPosting | None:
        for posting in self._ship_postings:
            if (
                posting.idempotency_key == idempotency_key
                and posting.tenant_id == self._tenant_id
            ):
                return posting
        return None

    def atomic_ship(
        self,
        *,
        delivery_order_id: UUID,
        sales_order_id: UUID,
        expected_delivery_order_version: int,
        line_quantities: tuple[tuple[UUID, Decimal], ...],
        idempotency_key: UUID,
        shipped_at: datetime,
        pod_ref: str | None = None,
        pod_captured_at: datetime | None = None,
    ) -> DeliveryShipPosting:
        active = self.get_ship_posting(delivery_order_id)
        if active is not None and active.status == DeliveryShipStatus.SHIPPED:
            raise ValueError("delivery order is already shipped")
        if self.get_ship_posting_by_key(idempotency_key) is not None:
            raise ValueError("delivery ship idempotency conflict")
        for line_id, quantity in line_quantities:
            balance = self.get_stock_balance(line_id)
            on_hand = balance.on_hand if balance is not None else Decimal("0")
            if on_hand < quantity:
                raise ValueError("insufficient stock")
        for line_id, quantity in line_quantities:
            balance = self.get_stock_balance(line_id)
            assert balance is not None
            new_on_hand = balance.on_hand - quantity
            updated = StockBalance(
                tenant_id=self._tenant_id,
                sales_order_line_id=line_id,
                on_hand=new_on_hand,
                version=balance.version + 1,
                updated_at=shipped_at,
            )
            self._balances[line_id] = updated
            entry = InventoryLedgerEntry(
                id=uuid4(),
                tenant_id=self._tenant_id,
                sales_order_line_id=line_id,
                delivery_order_id=delivery_order_id,
                entry_type=InventoryLedgerEntryType.DO_SHIP,
                quantity_delta=-quantity,
                balance_after=new_on_hand,
                idempotency_key=idempotency_key,
                created_at=shipped_at,
            )
            self._ledger[entry.id] = entry
        posting = DeliveryShipPosting(
            id=uuid4(),
            tenant_id=self._tenant_id,
            delivery_order_id=delivery_order_id,
            sales_order_id=sales_order_id,
            idempotency_key=idempotency_key,
            shipped_at=shipped_at,
            status=DeliveryShipStatus.SHIPPED,
            pod_ref=pod_ref,
            pod_captured_at=pod_captured_at,
        )
        self._ship_postings.append(posting)
        if self._mark_delivery_order_shipped is not None:
            self._mark_delivery_order_shipped(
                delivery_order_id,
                expected_delivery_order_version,
                shipped_at,
            )
        return posting

    def atomic_unship(
        self,
        *,
        delivery_order_id: UUID,
        sales_order_id: UUID,
        expected_delivery_order_version: int,
        line_quantities: tuple[tuple[UUID, Decimal], ...],
        idempotency_key: UUID,
        unshipped_at: datetime,
    ) -> DeliveryShipPosting:
        posting = self.get_ship_posting(delivery_order_id)
        if posting is None or posting.status != DeliveryShipStatus.SHIPPED:
            raise ValueError("delivery order is not shipped")
        if posting.sales_order_id != sales_order_id:
            raise ValueError("delivery order sales order conflict")
        for line_id, quantity in line_quantities:
            current = self._balances.get(line_id)
            on_hand = (current.on_hand if current is not None else Decimal("0")) + quantity
            self._balances[line_id] = StockBalance(
                tenant_id=self._tenant_id,
                sales_order_line_id=line_id,
                on_hand=on_hand,
                version=(current.version + 1) if current is not None else 1,
                updated_at=unshipped_at,
            )
            entry = InventoryLedgerEntry(
                id=uuid4(),
                tenant_id=self._tenant_id,
                sales_order_line_id=line_id,
                delivery_order_id=delivery_order_id,
                entry_type=InventoryLedgerEntryType.DO_UNSHIP,
                quantity_delta=quantity,
                balance_after=on_hand,
                idempotency_key=idempotency_key,
                created_at=unshipped_at,
            )
            self._ledger[entry.id] = entry
        updated = DeliveryShipPosting(
            id=posting.id,
            tenant_id=posting.tenant_id,
            delivery_order_id=posting.delivery_order_id,
            sales_order_id=posting.sales_order_id,
            idempotency_key=posting.idempotency_key,
            shipped_at=posting.shipped_at,
            unshipped_at=unshipped_at,
            unship_key=idempotency_key,
            status=DeliveryShipStatus.UNSHIPPED,
            version=posting.version + 1,
            pod_ref=posting.pod_ref,
            pod_captured_at=posting.pod_captured_at,
        )
        self._ship_postings = [
            updated if item.id == posting.id else item
            for item in self._ship_postings
        ]
        if self._mark_delivery_order_unshipped is not None:
            self._mark_delivery_order_unshipped(
                delivery_order_id, expected_delivery_order_version, unshipped_at
            )
        return updated

    def list_do_ship_quantities(
        self, delivery_order_id: UUID
    ) -> tuple[tuple[UUID, Decimal], ...]:
        posting = self.get_ship_posting(delivery_order_id)
        if posting is None or posting.status != DeliveryShipStatus.SHIPPED:
            return ()
        lines: list[tuple[UUID, Decimal]] = []
        for entry in self._ledger.values():
            if (
                entry.tenant_id == self._tenant_id
                and entry.delivery_order_id == delivery_order_id
                and entry.entry_type == InventoryLedgerEntryType.DO_SHIP
                and entry.idempotency_key == posting.idempotency_key
            ):
                if entry.sales_order_line_id is None:
                    continue
                lines.append((entry.sales_order_line_id, -entry.quantity_delta))
        return tuple(lines)

    def atomic_rma_restock(
        self,
        *,
        return_authorization_id: UUID,
        delivery_order_id: UUID,
        line_quantities: tuple[tuple[UUID, Decimal], ...],
        idempotency_key: UUID,
        restocked_at: datetime,
    ) -> None:
        for entry in self._ledger.values():
            if (
                entry.tenant_id == self._tenant_id
                and entry.return_authorization_id == return_authorization_id
                and entry.entry_type == InventoryLedgerEntryType.RMA_RESTOCK
            ):
                raise ValueError("return authorization already restocked")
        for line_id, quantity in line_quantities:
            current = self._balances.get(line_id)
            on_hand = (
                current.on_hand if current is not None else Decimal("0")
            ) + quantity
            balance = StockBalance(
                tenant_id=self._tenant_id,
                sales_order_line_id=line_id,
                on_hand=on_hand,
                version=(current.version + 1) if current is not None else 1,
                updated_at=restocked_at,
            )
            self._balances[line_id] = balance
            entry = InventoryLedgerEntry(
                id=uuid4(),
                tenant_id=self._tenant_id,
                sales_order_line_id=line_id,
                delivery_order_id=delivery_order_id,
                entry_type=InventoryLedgerEntryType.RMA_RESTOCK,
                quantity_delta=quantity,
                balance_after=on_hand,
                idempotency_key=idempotency_key,
                created_at=restocked_at,
                return_authorization_id=return_authorization_id,
            )
            self._ledger[entry.id] = entry

    def atomic_po_receive(
        self,
        *,
        purchase_order_id: UUID,
        goods_receipt_id: UUID,
        line_quantities: tuple[tuple[UUID, Decimal], ...],
        idempotency_key: UUID,
        received_at: datetime,
    ) -> None:
        if self._fail_next_po_receive:
            self._fail_next_po_receive = False
            raise ValueError("inventory receive failed")
        for entry in self._ledger.values():
            if (
                entry.tenant_id == self._tenant_id
                and entry.goods_receipt_id == goods_receipt_id
                and entry.entry_type == InventoryLedgerEntryType.PO_RECEIVE
            ):
                raise ValueError("goods receipt already received into inventory")
        if not line_quantities:
            raise ValueError("no purchase order lines to receive")
        for item_id, quantity in line_quantities:
            current = self._item_balances.get(item_id)
            on_hand = (
                current.on_hand if current is not None else Decimal("0")
            ) + quantity
            balance = ItemStockBalance(
                tenant_id=self._tenant_id,
                inventory_item_id=item_id,
                on_hand=on_hand,
                version=(current.version + 1) if current is not None else 1,
                updated_at=received_at,
            )
            self._item_balances[item_id] = balance
            entry = InventoryLedgerEntry(
                id=uuid4(),
                tenant_id=self._tenant_id,
                entry_type=InventoryLedgerEntryType.PO_RECEIVE,
                quantity_delta=quantity,
                balance_after=on_hand,
                idempotency_key=idempotency_key,
                created_at=received_at,
                inventory_item_id=item_id,
                purchase_order_id=purchase_order_id,
                goods_receipt_id=goods_receipt_id,
            )
            self._ledger[entry.id] = entry

    def get_ship_pod_policy(self) -> TenantShipPodPolicy | None:
        return self._ship_pod_policy

    def save_ship_pod_policy(
        self,
        policy: TenantShipPodPolicy,
        *,
        expected_version: int,
    ) -> None:
        if policy.tenant_id != self._tenant_id:
            raise ValueError("ship POD policy is outside repository tenant")
        current = self._ship_pod_policy
        if current is None:
            if expected_version != 0:
                raise ValueError("ship POD policy version conflict")
        elif current.version != expected_version:
            raise ValueError("ship POD policy version conflict")
        self._ship_pod_policy = policy
