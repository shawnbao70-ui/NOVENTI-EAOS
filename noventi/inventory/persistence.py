"""SQLAlchemy persistence and transactional composition for Inventory I1."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from typing import TypeVar
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
    select,
    text,
    update,
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from kernel.event_bus.domain_emit import DomainEventEmitter
from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
from kernel.infrastructure.persistence.event_repository import SQLAlchemyOutboxWriter
from kernel.infrastructure.persistence.identity_permission import (
    SQLAlchemyPrincipalEligibility,
)
from kernel.infrastructure.persistence.metadata import NAMING_CONVENTION
from kernel.infrastructure.persistence.permission_repository import (
    SQLAlchemyPermissionRepository,
)
from kernel.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext
from kernel.shared.errors import ErrorCode
from kernel.shared.results import KernelResult
from noventi.inventory.models import (
    DeliveryShipPosting,
    DeliveryShipStatus,
    InventoryLedgerEntry,
    InventoryLedgerEntryType,
    ItemStockBalance,
    StockBalance,
    TenantShipPodPolicy,
)
from noventi.inventory.service import (
    DeliveryOrderShipApprovalGate,
    DeliveryOrderShipApprovalPolicyReadPort,
    DeliveryOrderShipLineSnapshot,
    DeliveryOrderShipSnapshot,
    InventoryService,
)

T = TypeVar("T")


def _crm_persistence():
    """Lazy import breaks inventory.persistence ↔ crm package cycles."""
    from noventi.crm.persistence import (
        CustomerRecord,
        DeliveryOrderRecord,
        DeliveryOrderLineRecord,
        OpportunityRecord,
        RequirementRecord,
        SalesOrderLineRecord,
        SalesOrderRecord,
    )

    return (
        CustomerRecord,
        DeliveryOrderRecord,
        DeliveryOrderLineRecord,
        OpportunityRecord,
        RequirementRecord,
        SalesOrderLineRecord,
        SalesOrderRecord,
    )


class InventoryBase(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class StockBalanceRecord(InventoryBase):
    __tablename__ = "stock_balances"
    __table_args__ = (
        UniqueConstraint("tenant_id", "sales_order_line_id"),
        CheckConstraint("version > 0", name="version_positive"),
        {"schema": "inventory"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    sales_order_line_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False
    )
    on_hand: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class ItemStockBalanceRecord(InventoryBase):
    __tablename__ = "item_stock_balances"
    __table_args__ = (
        UniqueConstraint("tenant_id", "inventory_item_id"),
        CheckConstraint("version > 0", name="version_positive"),
        {"schema": "inventory"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    inventory_item_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False
    )
    on_hand: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class InventoryLedgerEntryRecord(InventoryBase):
    __tablename__ = "ledger_entries"
    __table_args__ = (
        UniqueConstraint("tenant_id", "idempotency_key", "sales_order_line_id"),
        CheckConstraint(
            "entry_type IN ('adjustment','do_ship','do_unship','rma_restock','po_receive')",
            name="entry_type_valid",
        ),
        Index(
            "ix_inventory_ledger_tenant_line",
            "tenant_id",
            "sales_order_line_id",
        ),
        {"schema": "inventory"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    sales_order_line_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    delivery_order_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    return_authorization_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    inventory_item_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    purchase_order_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    goods_receipt_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    entry_type: Mapped[str] = mapped_column(String(32), nullable=False)
    quantity_delta: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class DeliveryShipPostingRecord(InventoryBase):
    __tablename__ = "delivery_ship_postings"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id",
            "idempotency_key",
            name="uq_delivery_ship_postings_tenant_key",
        ),
        CheckConstraint("status IN ('shipped','unshipped')", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "ix_inventory_ship_postings_tenant_do_status",
            "tenant_id",
            "delivery_order_id",
            "status",
        ),
        {"schema": "inventory"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    delivery_order_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False
    )
    sales_order_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    shipped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    unshipped_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    unship_key: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    pod_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    pod_captured_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class TenantShipPodPolicyRecord(InventoryBase):
    __tablename__ = "tenant_ship_pod_policies"
    __table_args__ = (
        CheckConstraint("version > 0", name="version_positive"),
        {"schema": "inventory"},
    )

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True
    )
    ship_pod_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )


class SQLAlchemyDeliveryOrderShipReadAdapter:
    def __init__(self, session: Session, *, tenant_id: UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def get_delivery_order_ship_snapshot(
        self, delivery_order_id: UUID
    ) -> DeliveryOrderShipSnapshot | None:
        (
            CustomerRecord,
            DeliveryOrderRecord,
            DeliveryOrderLineRecord,
            OpportunityRecord,
            RequirementRecord,
            _,
            SalesOrderRecord,
        ) = _crm_persistence()
        delivery_order = self._session.scalar(
            select(DeliveryOrderRecord).where(
                DeliveryOrderRecord.id == delivery_order_id,
                DeliveryOrderRecord.tenant_id == self._tenant_id,
            )
        )
        if delivery_order is None:
            return None
        sales_order = self._session.scalar(
            select(SalesOrderRecord).where(
                SalesOrderRecord.id == delivery_order.sales_order_id,
                SalesOrderRecord.tenant_id == self._tenant_id,
            )
        )
        if sales_order is None:
            return None
        requirement = self._session.scalar(
            select(RequirementRecord).where(
                RequirementRecord.id == sales_order.requirement_id,
                RequirementRecord.tenant_id == self._tenant_id,
            )
        )
        if requirement is None:
            return None
        opportunity = self._session.scalar(
            select(OpportunityRecord).where(
                OpportunityRecord.id == requirement.opportunity_id,
                OpportunityRecord.tenant_id == self._tenant_id,
            )
        )
        if opportunity is None:
            return None
        customer = self._session.scalar(
            select(CustomerRecord).where(
                CustomerRecord.id == opportunity.customer_id,
                CustomerRecord.tenant_id == self._tenant_id,
            )
        )
        if customer is None:
            return None
        lines = self._session.scalars(
            select(DeliveryOrderLineRecord)
            .where(
                DeliveryOrderLineRecord.delivery_order_id == delivery_order.id,
                DeliveryOrderLineRecord.tenant_id == self._tenant_id,
            )
            .order_by(DeliveryOrderLineRecord.sales_order_line_id)
        ).all()
        return DeliveryOrderShipSnapshot(
            id=delivery_order.id,
            tenant_id=delivery_order.tenant_id,
            status=delivery_order.status,
            version=delivery_order.version,
            sales_order_id=sales_order.id,
            sales_order_status=sales_order.status,
            sales_order_version=sales_order.version,
            customer_id=customer.id,
            commercial_hold=bool(customer.commercial_hold),
            lines=tuple(
                DeliveryOrderShipLineSnapshot(
                    id=line.sales_order_line_id, quantity=line.quantity
                )
                for line in lines
            ),
        )


class SQLAlchemyDeliveryOrderShipApprovalPolicyReadAdapter(
    DeliveryOrderShipApprovalPolicyReadPort
):
    def __init__(self, session: Session, *, tenant_id: UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def do_ship_approval_required(self) -> bool:
        from noventi.crm.persistence import TenantConfirmPolicyRecord

        record = self._session.scalar(
            select(TenantConfirmPolicyRecord).where(
                TenantConfirmPolicyRecord.tenant_id == self._tenant_id
            )
        )
        return bool(record is not None and record.do_ship_approval_required)


class SQLAlchemyInventoryRepository:
    def __init__(self, session: Session, *, tenant_id: UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def get_adjustment_by_key(
        self, idempotency_key: UUID
    ) -> InventoryLedgerEntry | None:
        record = self._session.scalar(
            select(InventoryLedgerEntryRecord).where(
                InventoryLedgerEntryRecord.tenant_id == self._tenant_id,
                InventoryLedgerEntryRecord.idempotency_key == idempotency_key,
                InventoryLedgerEntryRecord.entry_type
                == InventoryLedgerEntryType.ADJUSTMENT.value,
            )
        )
        return self._ledger_domain(record) if record is not None else None

    def atomic_adjust(
        self,
        *,
        sales_order_line_id: UUID,
        quantity_delta: Decimal,
        idempotency_key: UUID,
        adjusted_at: datetime,
    ) -> StockBalance:
        current = self._balance_record(sales_order_line_id)
        on_hand = (
            current.on_hand if current is not None else Decimal("0.0000")
        ) + quantity_delta
        if on_hand < 0:
            raise ValueError("insufficient stock")
        if current is None:
            balance = StockBalance(
                tenant_id=self._tenant_id,
                sales_order_line_id=sales_order_line_id,
                on_hand=on_hand,
                version=1,
                updated_at=adjusted_at,
            )
            self._session.add(
                StockBalanceRecord(
                    id=uuid4(),
                    tenant_id=balance.tenant_id,
                    sales_order_line_id=balance.sales_order_line_id,
                    on_hand=balance.on_hand,
                    version=balance.version,
                    updated_at=balance.updated_at,
                )
            )
        else:
            result = self._session.execute(
                update(StockBalanceRecord)
                .where(
                    StockBalanceRecord.id == current.id,
                    StockBalanceRecord.tenant_id == self._tenant_id,
                    StockBalanceRecord.version == current.version,
                )
                .values(
                    on_hand=on_hand,
                    version=current.version + 1,
                    updated_at=adjusted_at,
                )
            )
            if result.rowcount != 1:
                raise ValueError("stock balance version conflict")
            balance = StockBalance(
                tenant_id=self._tenant_id,
                sales_order_line_id=sales_order_line_id,
                on_hand=on_hand,
                version=current.version + 1,
                updated_at=adjusted_at,
            )
        self._session.add(
            InventoryLedgerEntryRecord(
                id=uuid4(),
                tenant_id=self._tenant_id,
                sales_order_line_id=sales_order_line_id,
                delivery_order_id=None,
                entry_type=InventoryLedgerEntryType.ADJUSTMENT.value,
                quantity_delta=quantity_delta,
                balance_after=on_hand,
                idempotency_key=idempotency_key,
                created_at=adjusted_at,
            )
        )
        return balance

    def get_stock_balance(
        self, sales_order_line_id: UUID
    ) -> StockBalance | None:
        record = self._balance_record(sales_order_line_id)
        if record is None:
            return None
        return StockBalance(
            tenant_id=record.tenant_id,
            sales_order_line_id=record.sales_order_line_id,
            on_hand=record.on_hand,
            version=record.version,
            updated_at=record.updated_at,
        )

    def get_ship_posting(
        self, delivery_order_id: UUID
    ) -> DeliveryShipPosting | None:
        active = self._session.scalar(
            select(DeliveryShipPostingRecord).where(
                DeliveryShipPostingRecord.delivery_order_id == delivery_order_id,
                DeliveryShipPostingRecord.tenant_id == self._tenant_id,
                DeliveryShipPostingRecord.status
                == DeliveryShipStatus.SHIPPED.value,
            )
        )
        if active is not None:
            return self._ship_domain(active)
        record = self._session.scalar(
            select(DeliveryShipPostingRecord)
            .where(
                DeliveryShipPostingRecord.delivery_order_id == delivery_order_id,
                DeliveryShipPostingRecord.tenant_id == self._tenant_id,
            )
            .order_by(DeliveryShipPostingRecord.shipped_at.desc())
        )
        return self._ship_domain(record) if record is not None else None

    def get_ship_posting_by_key(
        self, idempotency_key: UUID
    ) -> DeliveryShipPosting | None:
        record = self._session.scalar(
            select(DeliveryShipPostingRecord).where(
                DeliveryShipPostingRecord.idempotency_key == idempotency_key,
                DeliveryShipPostingRecord.tenant_id == self._tenant_id,
            )
        )
        return self._ship_domain(record) if record is not None else None

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
        active = self._session.scalar(
            select(DeliveryShipPostingRecord).where(
                DeliveryShipPostingRecord.delivery_order_id == delivery_order_id,
                DeliveryShipPostingRecord.tenant_id == self._tenant_id,
                DeliveryShipPostingRecord.status
                == DeliveryShipStatus.SHIPPED.value,
            )
        )
        if active is not None:
            raise ValueError("delivery order is already shipped")
        if self.get_ship_posting_by_key(idempotency_key) is not None:
            raise ValueError("delivery ship idempotency conflict")
        (
            _,
            DeliveryOrderRecord,
            DeliveryOrderLineRecord,
            _,
            _,
            SalesOrderLineRecord,
            SalesOrderRecord,
        ) = _crm_persistence()
        for line_id, quantity in line_quantities:
            sales_order_line = self._session.scalar(
                select(SalesOrderLineRecord).where(
                    SalesOrderLineRecord.id == line_id,
                    SalesOrderLineRecord.tenant_id == self._tenant_id,
                    SalesOrderLineRecord.sales_order_id == sales_order_id,
                )
            )
            if sales_order_line is None:
                raise ValueError("delivery order line is not on sales order")
            shipped_entries = self._session.scalars(
                select(InventoryLedgerEntryRecord).where(
                    InventoryLedgerEntryRecord.tenant_id == self._tenant_id,
                    InventoryLedgerEntryRecord.sales_order_line_id == line_id,
                    InventoryLedgerEntryRecord.entry_type
                    == InventoryLedgerEntryType.DO_SHIP.value,
                )
            ).all()
            unshipped_entries = self._session.scalars(
                select(InventoryLedgerEntryRecord).where(
                    InventoryLedgerEntryRecord.tenant_id == self._tenant_id,
                    InventoryLedgerEntryRecord.sales_order_line_id == line_id,
                    InventoryLedgerEntryRecord.entry_type
                    == InventoryLedgerEntryType.DO_UNSHIP.value,
                )
            ).all()
            shipped_quantity = sum(
                (-entry.quantity_delta for entry in shipped_entries), Decimal("0")
            ) - sum(
                (entry.quantity_delta for entry in unshipped_entries), Decimal("0")
            )
            if quantity > sales_order_line.quantity - shipped_quantity:
                raise ValueError("delivery order quantity exceeds remaining quantity")
            balance = self.get_stock_balance(line_id)
            on_hand = balance.on_hand if balance is not None else Decimal("0")
            if on_hand < quantity:
                raise ValueError("insufficient stock")
        for line_id, quantity in line_quantities:
            balance_record = self._balance_record(line_id)
            if balance_record is None:
                raise ValueError("insufficient stock")
            new_on_hand = balance_record.on_hand - quantity
            result = self._session.execute(
                update(StockBalanceRecord)
                .where(
                    StockBalanceRecord.id == balance_record.id,
                    StockBalanceRecord.tenant_id == self._tenant_id,
                    StockBalanceRecord.version == balance_record.version,
                )
                .values(
                    on_hand=new_on_hand,
                    version=balance_record.version + 1,
                    updated_at=shipped_at,
                )
            )
            if result.rowcount != 1:
                raise ValueError("stock balance version conflict")
            self._session.add(
                InventoryLedgerEntryRecord(
                    id=uuid4(),
                    tenant_id=self._tenant_id,
                    sales_order_line_id=line_id,
                    delivery_order_id=delivery_order_id,
                    entry_type=InventoryLedgerEntryType.DO_SHIP.value,
                    quantity_delta=-quantity,
                    balance_after=new_on_hand,
                    idempotency_key=idempotency_key,
                    created_at=shipped_at,
                )
            )
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
        self._session.add(
            DeliveryShipPostingRecord(
                id=posting.id,
                tenant_id=posting.tenant_id,
                delivery_order_id=posting.delivery_order_id,
                sales_order_id=posting.sales_order_id,
                idempotency_key=posting.idempotency_key,
                shipped_at=posting.shipped_at,
                status=posting.status.value,
                version=posting.version,
                pod_ref=posting.pod_ref,
                pod_captured_at=posting.pod_captured_at,
            )
        )
        do_result = self._session.execute(
            update(DeliveryOrderRecord)
            .where(
                DeliveryOrderRecord.id == delivery_order_id,
                DeliveryOrderRecord.tenant_id == self._tenant_id,
                DeliveryOrderRecord.version == expected_delivery_order_version,
                DeliveryOrderRecord.status == "released",
            )
            .values(
                status="shipped",
                version=expected_delivery_order_version + 1,
            )
        )
        if do_result.rowcount != 1:
            raise ValueError("delivery order ship status conflict")
        line_result = self._session.execute(
            update(DeliveryOrderLineRecord)
            .where(
                DeliveryOrderLineRecord.delivery_order_id == delivery_order_id,
                DeliveryOrderLineRecord.tenant_id == self._tenant_id,
            )
            .values(status="shipped")
        )
        if line_result.rowcount != len(line_quantities):
            raise ValueError("delivery order line ship status conflict")
        sales_order = self._session.scalar(
            select(SalesOrderRecord).where(
                SalesOrderRecord.id == sales_order_id,
                SalesOrderRecord.tenant_id == self._tenant_id,
            )
        )
        if sales_order is None:
            raise ValueError("sales order not found")
        shipped_quantity = sales_order.shipped_quantity + sum(
            (quantity for _, quantity in line_quantities), Decimal("0")
        )
        status = (
            "shipped"
            if shipped_quantity >= sales_order.ordered_quantity
            else "partially_shipped"
        )
        so_result = self._session.execute(
            update(SalesOrderRecord)
            .where(
                SalesOrderRecord.id == sales_order_id,
                SalesOrderRecord.tenant_id == self._tenant_id,
                SalesOrderRecord.version == sales_order.version,
            )
            .values(
                status=status,
                shipped_quantity=shipped_quantity,
                version=sales_order.version + 1,
            )
        )
        if so_result.rowcount != 1:
            raise ValueError("sales order fulfillment status conflict")
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
        active = self._session.scalar(
            select(DeliveryShipPostingRecord).where(
                DeliveryShipPostingRecord.delivery_order_id == delivery_order_id,
                DeliveryShipPostingRecord.tenant_id == self._tenant_id,
                DeliveryShipPostingRecord.status
                == DeliveryShipStatus.SHIPPED.value,
            )
        )
        posting = self._ship_domain(active) if active is not None else None
        if posting is None or posting.status != DeliveryShipStatus.SHIPPED:
            raise ValueError("delivery order is not shipped")
        if posting.sales_order_id != sales_order_id:
            raise ValueError("delivery order sales order conflict")
        (
            _,
            DeliveryOrderRecord,
            DeliveryOrderLineRecord,
            _,
            _,
            _,
            SalesOrderRecord,
        ) = _crm_persistence()
        for line_id, quantity in line_quantities:
            balance = self._balance_record(line_id)
            on_hand = (balance.on_hand if balance is not None else Decimal("0.0000")) + quantity
            if balance is None:
                self._session.add(
                    StockBalanceRecord(
                        id=uuid4(),
                        tenant_id=self._tenant_id,
                        sales_order_line_id=line_id,
                        on_hand=on_hand,
                        version=1,
                        updated_at=unshipped_at,
                    )
                )
            else:
                result = self._session.execute(
                    update(StockBalanceRecord)
                    .where(
                        StockBalanceRecord.id == balance.id,
                        StockBalanceRecord.tenant_id == self._tenant_id,
                        StockBalanceRecord.version == balance.version,
                    )
                    .values(
                        on_hand=on_hand,
                        version=balance.version + 1,
                        updated_at=unshipped_at,
                    )
                )
                if result.rowcount != 1:
                    raise ValueError("stock balance version conflict")
            self._session.add(
                InventoryLedgerEntryRecord(
                    id=uuid4(),
                    tenant_id=self._tenant_id,
                    sales_order_line_id=line_id,
                    delivery_order_id=delivery_order_id,
                    entry_type=InventoryLedgerEntryType.DO_UNSHIP.value,
                    quantity_delta=quantity,
                    balance_after=on_hand,
                    idempotency_key=idempotency_key,
                    created_at=unshipped_at,
                )
            )
        do_result = self._session.execute(
            update(DeliveryOrderRecord)
            .where(
                DeliveryOrderRecord.id == delivery_order_id,
                DeliveryOrderRecord.tenant_id == self._tenant_id,
                DeliveryOrderRecord.version == expected_delivery_order_version,
                DeliveryOrderRecord.status == "shipped",
            )
            .values(status="released", version=expected_delivery_order_version + 1)
        )
        if do_result.rowcount != 1:
            raise ValueError("delivery order unship status conflict")
        self._session.execute(
            update(DeliveryOrderLineRecord)
            .where(
                DeliveryOrderLineRecord.delivery_order_id == delivery_order_id,
                DeliveryOrderLineRecord.tenant_id == self._tenant_id,
            )
            .values(status="open")
        )
        sales_order = self._session.scalar(
            select(SalesOrderRecord).where(
                SalesOrderRecord.id == sales_order_id,
                SalesOrderRecord.tenant_id == self._tenant_id,
            )
        )
        if sales_order is None:
            raise ValueError("sales order not found")
        quantity = sum((value for _, value in line_quantities), Decimal("0"))
        shipped_quantity = sales_order.shipped_quantity - quantity
        if shipped_quantity < 0:
            raise ValueError("sales order shipped quantity conflict")
        status = "confirmed" if shipped_quantity == 0 else "partially_shipped"
        so_result = self._session.execute(
            update(SalesOrderRecord)
            .where(
                SalesOrderRecord.id == sales_order_id,
                SalesOrderRecord.tenant_id == self._tenant_id,
                SalesOrderRecord.version == sales_order.version,
            )
            .values(
                status=status,
                shipped_quantity=shipped_quantity,
                version=sales_order.version + 1,
            )
        )
        if so_result.rowcount != 1:
            raise ValueError("sales order fulfillment status conflict")
        record = self._session.scalar(
            select(DeliveryShipPostingRecord).where(
                DeliveryShipPostingRecord.id == posting.id,
                DeliveryShipPostingRecord.tenant_id == self._tenant_id,
                DeliveryShipPostingRecord.status == "shipped",
            )
        )
        if record is None:
            raise ValueError("delivery order ship posting conflict")
        result = self._session.execute(
            update(DeliveryShipPostingRecord)
            .where(
                DeliveryShipPostingRecord.id == record.id,
                DeliveryShipPostingRecord.version == record.version,
            )
            .values(
                status=DeliveryShipStatus.UNSHIPPED.value,
                unshipped_at=unshipped_at,
                unship_key=idempotency_key,
                version=record.version + 1,
            )
        )
        if result.rowcount != 1:
            raise ValueError("delivery order unship posting conflict")
        return DeliveryShipPosting(
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

    def get_ship_pod_policy(self) -> TenantShipPodPolicy | None:
        record = self._session.get(TenantShipPodPolicyRecord, self._tenant_id)
        if record is None:
            return None
        return TenantShipPodPolicy(
            tenant_id=record.tenant_id,
            ship_pod_required=bool(record.ship_pod_required),
            updated_at=record.updated_at,
            version=record.version,
        )

    def save_ship_pod_policy(
        self,
        policy: TenantShipPodPolicy,
        *,
        expected_version: int,
    ) -> None:
        if policy.tenant_id != self._tenant_id:
            raise ValueError("ship POD policy is outside repository tenant")
        current = self.get_ship_pod_policy()
        if current is None:
            if expected_version != 0:
                raise ValueError("ship POD policy version conflict")
            self._session.add(
                TenantShipPodPolicyRecord(
                    tenant_id=policy.tenant_id,
                    ship_pod_required=policy.ship_pod_required,
                    updated_at=policy.updated_at,
                    version=policy.version,
                )
            )
            return
        if current.version != expected_version:
            raise ValueError("ship POD policy version conflict")
        result = self._session.execute(
            update(TenantShipPodPolicyRecord)
            .where(
                TenantShipPodPolicyRecord.tenant_id == self._tenant_id,
                TenantShipPodPolicyRecord.version == expected_version,
            )
            .values(
                ship_pod_required=policy.ship_pod_required,
                updated_at=policy.updated_at,
                version=policy.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("ship POD policy version conflict")

    def list_do_ship_quantities(
        self, delivery_order_id: UUID
    ) -> tuple[tuple[UUID, Decimal], ...]:
        active = self._session.scalar(
            select(DeliveryShipPostingRecord).where(
                DeliveryShipPostingRecord.delivery_order_id == delivery_order_id,
                DeliveryShipPostingRecord.tenant_id == self._tenant_id,
                DeliveryShipPostingRecord.status
                == DeliveryShipStatus.SHIPPED.value,
            )
        )
        if active is None:
            return ()
        records = self._session.scalars(
            select(InventoryLedgerEntryRecord).where(
                InventoryLedgerEntryRecord.delivery_order_id
                == delivery_order_id,
                InventoryLedgerEntryRecord.tenant_id == self._tenant_id,
                InventoryLedgerEntryRecord.entry_type
                == InventoryLedgerEntryType.DO_SHIP.value,
                InventoryLedgerEntryRecord.idempotency_key
                == active.idempotency_key,
            )
        ).all()
        return tuple(
            (record.sales_order_line_id, -record.quantity_delta)
            for record in records
            if record.sales_order_line_id is not None
        )

    def atomic_rma_restock(
        self,
        *,
        return_authorization_id: UUID,
        delivery_order_id: UUID,
        line_quantities: tuple[tuple[UUID, Decimal], ...],
        idempotency_key: UUID,
        restocked_at: datetime,
    ) -> None:
        existing = self._session.scalar(
            select(InventoryLedgerEntryRecord).where(
                InventoryLedgerEntryRecord.return_authorization_id
                == return_authorization_id,
                InventoryLedgerEntryRecord.tenant_id == self._tenant_id,
                InventoryLedgerEntryRecord.entry_type
                == InventoryLedgerEntryType.RMA_RESTOCK.value,
            )
        )
        if existing is not None:
            raise ValueError("return authorization already restocked")
        for line_id, quantity in line_quantities:
            current = self._balance_record(line_id)
            on_hand = (
                current.on_hand if current is not None else Decimal("0.0000")
            ) + quantity
            if current is None:
                self._session.add(
                    StockBalanceRecord(
                        id=uuid4(),
                        tenant_id=self._tenant_id,
                        sales_order_line_id=line_id,
                        on_hand=on_hand,
                        version=1,
                        updated_at=restocked_at,
                    )
                )
            else:
                result = self._session.execute(
                    update(StockBalanceRecord)
                    .where(
                        StockBalanceRecord.id == current.id,
                        StockBalanceRecord.tenant_id == self._tenant_id,
                        StockBalanceRecord.version == current.version,
                    )
                    .values(
                        on_hand=on_hand,
                        version=current.version + 1,
                        updated_at=restocked_at,
                    )
                )
                if result.rowcount != 1:
                    raise ValueError("stock balance version conflict")
            self._session.add(
                InventoryLedgerEntryRecord(
                    id=uuid4(),
                    tenant_id=self._tenant_id,
                    sales_order_line_id=line_id,
                    delivery_order_id=delivery_order_id,
                    return_authorization_id=return_authorization_id,
                    entry_type=InventoryLedgerEntryType.RMA_RESTOCK.value,
                    quantity_delta=quantity,
                    balance_after=on_hand,
                    idempotency_key=idempotency_key,
                    created_at=restocked_at,
                )
            )

    def get_item_stock_balance(
        self, inventory_item_id: UUID
    ) -> ItemStockBalance | None:
        record = self._item_balance_record(inventory_item_id)
        if record is None:
            return None
        return ItemStockBalance(
            tenant_id=record.tenant_id,
            inventory_item_id=record.inventory_item_id,
            on_hand=record.on_hand,
            version=record.version,
            updated_at=record.updated_at,
        )

    def atomic_po_receive(
        self,
        *,
        purchase_order_id: UUID,
        goods_receipt_id: UUID,
        line_quantities: tuple[tuple[UUID, Decimal], ...],
        idempotency_key: UUID,
        received_at: datetime,
    ) -> None:
        existing = self._session.scalar(
            select(InventoryLedgerEntryRecord).where(
                InventoryLedgerEntryRecord.goods_receipt_id == goods_receipt_id,
                InventoryLedgerEntryRecord.tenant_id == self._tenant_id,
                InventoryLedgerEntryRecord.entry_type
                == InventoryLedgerEntryType.PO_RECEIVE.value,
            )
        )
        if existing is not None:
            raise ValueError("goods receipt already received into inventory")
        if not line_quantities:
            raise ValueError("no purchase order lines to receive")
        for item_id, quantity in line_quantities:
            current = self._item_balance_record(item_id)
            on_hand = (
                current.on_hand if current is not None else Decimal("0.0000")
            ) + quantity
            if current is None:
                self._session.add(
                    ItemStockBalanceRecord(
                        id=uuid4(),
                        tenant_id=self._tenant_id,
                        inventory_item_id=item_id,
                        on_hand=on_hand,
                        version=1,
                        updated_at=received_at,
                    )
                )
            else:
                result = self._session.execute(
                    update(ItemStockBalanceRecord)
                    .where(
                        ItemStockBalanceRecord.id == current.id,
                        ItemStockBalanceRecord.tenant_id == self._tenant_id,
                        ItemStockBalanceRecord.version == current.version,
                    )
                    .values(
                        on_hand=on_hand,
                        version=current.version + 1,
                        updated_at=received_at,
                    )
                )
                if result.rowcount != 1:
                    raise ValueError("item stock balance version conflict")
            self._session.add(
                InventoryLedgerEntryRecord(
                    id=uuid4(),
                    tenant_id=self._tenant_id,
                    sales_order_line_id=None,
                    delivery_order_id=None,
                    return_authorization_id=None,
                    inventory_item_id=item_id,
                    purchase_order_id=purchase_order_id,
                    goods_receipt_id=goods_receipt_id,
                    entry_type=InventoryLedgerEntryType.PO_RECEIVE.value,
                    quantity_delta=quantity,
                    balance_after=on_hand,
                    idempotency_key=idempotency_key,
                    created_at=received_at,
                )
            )

    def _balance_record(
        self, sales_order_line_id: UUID
    ) -> StockBalanceRecord | None:
        return self._session.scalar(
            select(StockBalanceRecord).where(
                StockBalanceRecord.sales_order_line_id == sales_order_line_id,
                StockBalanceRecord.tenant_id == self._tenant_id,
            )
        )

    def _item_balance_record(
        self, inventory_item_id: UUID
    ) -> ItemStockBalanceRecord | None:
        return self._session.scalar(
            select(ItemStockBalanceRecord).where(
                ItemStockBalanceRecord.inventory_item_id == inventory_item_id,
                ItemStockBalanceRecord.tenant_id == self._tenant_id,
            )
        )

    @staticmethod
    def _ledger_domain(
        record: InventoryLedgerEntryRecord,
    ) -> InventoryLedgerEntry:
        return InventoryLedgerEntry(
            id=record.id,
            tenant_id=record.tenant_id,
            sales_order_line_id=record.sales_order_line_id,
            delivery_order_id=record.delivery_order_id,
            entry_type=InventoryLedgerEntryType(record.entry_type),
            quantity_delta=record.quantity_delta,
            balance_after=record.balance_after,
            idempotency_key=record.idempotency_key,
            created_at=record.created_at,
            return_authorization_id=record.return_authorization_id,
            inventory_item_id=record.inventory_item_id,
            purchase_order_id=record.purchase_order_id,
            goods_receipt_id=record.goods_receipt_id,
        )

    @staticmethod
    def _ship_domain(record: DeliveryShipPostingRecord) -> DeliveryShipPosting:
        return DeliveryShipPosting(
            id=record.id,
            tenant_id=record.tenant_id,
            delivery_order_id=record.delivery_order_id,
            sales_order_id=record.sales_order_id,
            idempotency_key=record.idempotency_key,
            shipped_at=record.shipped_at,
            unshipped_at=record.unshipped_at,
            unship_key=record.unship_key,
            status=DeliveryShipStatus(record.status),
            version=record.version,
            pod_ref=record.pod_ref,
            pod_captured_at=record.pod_captured_at,
        )


class TransactionalInventoryService:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        *,
        do_ship_approval_gate: DeliveryOrderShipApprovalGate | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._do_ship_approval_gate = do_ship_approval_gate

    def set_do_ship_approval_gate(
        self, gate: DeliveryOrderShipApprovalGate | None
    ) -> None:
        self._do_ship_approval_gate = gate

    def adjust_stock(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[Decimal]:
        return self._execute(
            ctx, lambda service: service.adjust_stock(ctx, **kwargs)
        )

    def get_stock_balance(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[StockBalance]:
        return self._execute(
            ctx, lambda service: service.get_stock_balance(ctx, **kwargs)
        )

    def ship_delivery_order(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[DeliveryShipPosting]:
        return self._execute(
            ctx, lambda service: service.ship_delivery_order(ctx, **kwargs)
        )

    def get_ship_posting(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[DeliveryShipPosting]:
        return self._execute(
            ctx, lambda service: service.get_ship_posting(ctx, **kwargs)
        )

    def unship_delivery_order(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[DeliveryShipPosting]:
        return self._execute(
            ctx, lambda service: service.unship_delivery_order(ctx, **kwargs)
        )

    def get_ship_pod_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantShipPodPolicy]:
        return self._execute(
            ctx, lambda service: service.get_ship_pod_policy(ctx, **kwargs)
        )

    def set_ship_pod_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantShipPodPolicy]:
        return self._execute(
            ctx, lambda service: service.set_ship_pod_policy(ctx, **kwargs)
        )

    def _execute(
        self,
        ctx: ExecutionContext,
        operation: Callable[[InventoryService], KernelResult[T]],
    ) -> KernelResult[T]:
        if ctx.tenant_id is None or ctx.platform_scope:
            return KernelResult.failure(
                ErrorCode.CTX_INVALID,
                "Inventory requires a tenant data-plane context",
            )
        try:
            with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
                audit = SQLAlchemyAuditLog(
                    unit_of_work.session,
                    tenant_id=ctx.tenant_id,
                )
                permission = PermissionService(
                    repository=SQLAlchemyPermissionRepository(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                    ),
                    audit_log=audit,
                    principal_eligibility=SQLAlchemyPrincipalEligibility(
                        unit_of_work.session
                    ),
                )
                service = InventoryService(
                    permission,
                    repository=SQLAlchemyInventoryRepository(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                    ),
                    audit_log=audit,
                    delivery_order_reader=SQLAlchemyDeliveryOrderShipReadAdapter(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                    ),
                    do_ship_approval_policy_reader=(
                        SQLAlchemyDeliveryOrderShipApprovalPolicyReadAdapter(
                            unit_of_work.session,
                            tenant_id=ctx.tenant_id,
                        )
                    ),
                    do_ship_approval_gate=self._do_ship_approval_gate,
                    domain_events=DomainEventEmitter(
                        SQLAlchemyOutboxWriter(unit_of_work.session)
                    ),
                )
                result = operation(service)
                unit_of_work.commit()
                return result
        except IntegrityError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "Inventory persistence conflict"
            )
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL, "Inventory persistence unavailable"
            )
