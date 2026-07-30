"""SQLAlchemy persistence and transactional composition for Purchase."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from typing import TypeVar
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    MetaData,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
    func,
    select,
    text,
    update,
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
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
from noventi.purchase.models import (
    ApBill,
    ApBillLine,
    ApBillLineStatus,
    ApBillStatus,
    ApPayment,
    ApPaymentStatus,
    ApWriteOff,
    GoodsReceipt,
    GoodsReceiptStatus,
    PurchaseOrder,
    PurchaseOrderLine,
    PurchaseOrderLineStatus,
    PurchaseOrderStatus,
    Supplier,
    SupplierStatus,
    TenantThreeWayMatchTolerancePolicy,
    ThreeWayMatch,
    ThreeWayMatchStatus,
)
from noventi.purchase.service import PurchaseService

T = TypeVar("T")
PURCHASE_STATUSES = "'active','archived'"


class PurchaseBase(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class SupplierRecord(PurchaseBase):
    __tablename__ = "suppliers"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        CheckConstraint(
            f"status IN ({PURCHASE_STATUSES})", name="status_valid"
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "uq_purchase_suppliers_tenant_code_ci",
            "tenant_id",
            text("lower(code)"),
            unique=True,
        ),
        Index("ix_purchase_suppliers_tenant_status", "tenant_id", "status"),
        {"schema": "purchase"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )


class ApBillRecord(PurchaseBase):
    """DB FKs to kernel.tenants / purchase.suppliers are owned by Alembic."""

    __tablename__ = "ap_bills"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "code"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        CheckConstraint("total_amount >= 0", name="total_amount_non_negative"),
        CheckConstraint("paid_amount >= 0", name="paid_amount_non_negative"),
        CheckConstraint(
            "write_off_amount >= 0", name="write_off_amount_non_negative"
        ),
        CheckConstraint(
            "paid_amount + write_off_amount <= total_amount",
            name="settlement_not_over_total",
        ),
        CheckConstraint(
            "status IN ('draft','posted','partially_paid','paid','closed')",
            name="status_valid",
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_purchase_ap_bills_tenant_status", "tenant_id", "status"),
        Index(
            "ix_purchase_ap_bills_tenant_supplier",
            "tenant_id",
            "supplier_id",
        ),
        {"schema": "purchase"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    supplier_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    write_off_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )


class ApWriteOffRecord(PurchaseBase):
    __tablename__ = "ap_write_offs"
    __table_args__ = (
        ForeignKeyConstraint(
            ["ap_bill_id", "tenant_id"],
            ["purchase.ap_bills.id", "purchase.ap_bills.tenant_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_purchase_ap_write_offs_tenant_bill", "tenant_id", "ap_bill_id"),
        {"schema": "purchase"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    ap_bill_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )


class ApPaymentRecord(PurchaseBase):
    """DB FKs to kernel.tenants / purchase records are owned by Alembic."""

    __tablename__ = "ap_payments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["supplier_id", "tenant_id"],
            ["purchase.suppliers.id", "purchase.suppliers.tenant_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["ap_bill_id", "tenant_id"],
            ["purchase.ap_bills.id", "purchase.ap_bills.tenant_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint("status IN ('draft','applied')", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "uq_purchase_ap_payments_tenant_apply_key",
            "tenant_id",
            "apply_key",
            unique=True,
            postgresql_where=text("apply_key IS NOT NULL"),
        ),
        Index(
            "ix_purchase_ap_payments_tenant_bill",
            "tenant_id",
            "ap_bill_id",
        ),
        {"schema": "purchase"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    supplier_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    functional_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    fx_rate: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    functional_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    ap_bill_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    ap_bill_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    apply_key: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    applied_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )


class ApBillLineRecord(PurchaseBase):
    """DB FKs to kernel.tenants / purchase.ap_bills are owned by Alembic."""

    __tablename__ = "ap_bill_lines"
    __table_args__ = (
        ForeignKeyConstraint(
            ["ap_bill_id", "tenant_id"],
            ["purchase.ap_bills.id", "purchase.ap_bills.tenant_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "ap_bill_id", "line_number"),
        CheckConstraint(
            f"status IN ({PURCHASE_STATUSES})", name="status_valid"
        ),
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("unit_price >= 0", name="unit_price_non_negative"),
        CheckConstraint("amount >= 0", name="amount_non_negative"),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "ix_purchase_ap_bill_lines_tenant_bill",
            "tenant_id",
            "ap_bill_id",
        ),
        {"schema": "purchase"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    ap_bill_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )


class PurchaseOrderRecord(PurchaseBase):
    """DB FKs to kernel.tenants / purchase.suppliers are owned by Alembic."""

    __tablename__ = "purchase_orders"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "code"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        CheckConstraint(
            "status IN ('draft','archived','received')", name="status_valid"
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_purchase_purchase_orders_tenant_status", "tenant_id", "status"),
        Index(
            "ix_purchase_purchase_orders_tenant_supplier",
            "tenant_id",
            "supplier_id",
        ),
        {"schema": "purchase"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    supplier_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )


class PurchaseOrderLineRecord(PurchaseBase):
    """DB FKs owned by Alembic (AP4)."""

    __tablename__ = "purchase_order_lines"
    __table_args__ = (
        ForeignKeyConstraint(
            ["purchase_order_id", "tenant_id"],
            ["purchase.purchase_orders.id", "purchase.purchase_orders.tenant_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "purchase_order_id", "line_number"),
        CheckConstraint("status IN ('active')", name="status_valid"),
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "ix_purchase_po_lines_tenant_po",
            "tenant_id",
            "purchase_order_id",
        ),
        {"schema": "purchase"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    purchase_order_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    inventory_item_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )


class GoodsReceiptRecord(PurchaseBase):
    """DB FKs owned by Alembic (AP4)."""

    __tablename__ = "goods_receipts"
    __table_args__ = (
        ForeignKeyConstraint(
            ["purchase_order_id", "tenant_id"],
            ["purchase.purchase_orders.id", "purchase.purchase_orders.tenant_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "purchase_order_id"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        UniqueConstraint("tenant_id", "code"),
        CheckConstraint("status IN ('received')", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "ix_purchase_goods_receipts_tenant_po",
            "tenant_id",
            "purchase_order_id",
        ),
        {"schema": "purchase"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    purchase_order_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )


class ThreeWayMatchRecord(PurchaseBase):
    """DB FKs owned by Alembic (AP5)."""

    __tablename__ = "three_way_matches"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "purchase_order_id"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        CheckConstraint(
            "status IN ('matched','mismatch')", name="status_valid"
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "ix_purchase_three_way_matches_tenant_po",
            "tenant_id",
            "purchase_order_id",
        ),
        {"schema": "purchase"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    purchase_order_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    goods_receipt_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    ap_bill_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )


class TenantThreeWayMatchTolerancePolicyRecord(PurchaseBase):
    __tablename__ = "tenant_three_way_match_policies"
    __table_args__ = (
        CheckConstraint("version > 0", name="version_positive"),
        CheckConstraint(
            "amount_tolerance_abs IS NULL OR amount_tolerance_abs >= 0",
            name="abs_nonneg",
        ),
        CheckConstraint(
            "amount_tolerance_pct IS NULL OR amount_tolerance_pct >= 0",
            name="pct_nonneg",
        ),
        {"schema": "purchase"},
    )

    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True
    )
    amount_tolerance_abs: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2), nullable=True, server_default=text("0")
    )
    amount_tolerance_pct: Mapped[Decimal | None] = mapped_column(
        Numeric(9, 4), nullable=True, server_default=text("0")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )


class SQLAlchemyPurchaseRepository:
    def __init__(self, session: Session, *, tenant_id: UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def add_supplier(self, supplier: Supplier) -> None:
        self._require_tenant(supplier.tenant_id)
        self._session.add(self._supplier_record(supplier))

    def get_supplier(self, supplier_id: UUID) -> Supplier | None:
        record = self._session.scalar(
            select(SupplierRecord).where(
                SupplierRecord.id == supplier_id,
                SupplierRecord.tenant_id == self._tenant_id,
            )
        )
        return self._supplier_domain(record) if record is not None else None

    def save_supplier(
        self, supplier: Supplier, *, expected_version: int
    ) -> None:
        self._require_tenant(supplier.tenant_id)
        result = self._session.execute(
            update(SupplierRecord)
            .where(
                SupplierRecord.id == supplier.id,
                SupplierRecord.tenant_id == self._tenant_id,
                SupplierRecord.version == expected_version,
            )
            .values(
                display_name=supplier.display_name,
                status=supplier.status.value,
                updated_at=supplier.updated_at,
                archived_at=supplier.archived_at,
                version=supplier.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("supplier version conflict")

    def add_ap_bill(self, bill: ApBill) -> None:
        self._require_tenant(bill.tenant_id)
        self._session.add(self._ap_bill_record(bill))

    def get_ap_bill(self, bill_id: UUID) -> ApBill | None:
        record = self._session.scalar(
            select(ApBillRecord).where(
                ApBillRecord.id == bill_id,
                ApBillRecord.tenant_id == self._tenant_id,
            )
        )
        return self._ap_bill_domain(record) if record is not None else None

    def list_ap_bills_for_supplier(
        self, supplier_id: UUID
    ) -> list[ApBill]:
        records = self._session.scalars(
            select(ApBillRecord)
            .where(
                ApBillRecord.supplier_id == supplier_id,
                ApBillRecord.tenant_id == self._tenant_id,
            )
            .order_by(ApBillRecord.created_at, ApBillRecord.code, ApBillRecord.id)
        ).all()
        return [self._ap_bill_domain(record) for record in records]

    def get_ap_bill_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ApBill | None:
        record = self._session.scalar(
            select(ApBillRecord).where(
                ApBillRecord.idempotency_key == idempotency_key,
                ApBillRecord.tenant_id == self._tenant_id,
            )
        )
        return self._ap_bill_domain(record) if record is not None else None

    def save_ap_bill(self, bill: ApBill, *, expected_version: int) -> None:
        self._require_tenant(bill.tenant_id)
        result = self._session.execute(
            update(ApBillRecord)
            .where(
                ApBillRecord.id == bill.id,
                ApBillRecord.tenant_id == self._tenant_id,
                ApBillRecord.version == expected_version,
            )
            .values(
                total_amount=bill.total_amount,
                paid_amount=bill.paid_amount,
                write_off_amount=bill.write_off_amount,
                status=bill.status.value,
                version=bill.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("ap bill version conflict")

    def add_ap_write_off(self, write_off: ApWriteOff) -> None:
        self._require_tenant(write_off.tenant_id)
        self._session.add(self._ap_write_off_record(write_off))

    def get_ap_write_off_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ApWriteOff | None:
        record = self._session.scalar(
            select(ApWriteOffRecord).where(
                ApWriteOffRecord.idempotency_key == idempotency_key,
                ApWriteOffRecord.tenant_id == self._tenant_id,
            )
        )
        return self._ap_write_off_domain(record) if record is not None else None

    def list_ap_write_offs(self, ap_bill_id: UUID) -> list[ApWriteOff]:
        records = self._session.scalars(
            select(ApWriteOffRecord).where(
                ApWriteOffRecord.ap_bill_id == ap_bill_id,
                ApWriteOffRecord.tenant_id == self._tenant_id,
            )
        ).all()
        return [self._ap_write_off_domain(record) for record in records]

    def add_ap_payment(self, payment: ApPayment) -> None:
        self._require_tenant(payment.tenant_id)
        self._session.add(self._ap_payment_record(payment))

    def get_ap_payment(self, payment_id: UUID) -> ApPayment | None:
        record = self._session.scalar(
            select(ApPaymentRecord).where(
                ApPaymentRecord.id == payment_id,
                ApPaymentRecord.tenant_id == self._tenant_id,
            )
        )
        return self._ap_payment_domain(record) if record is not None else None

    def get_ap_payment_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ApPayment | None:
        record = self._session.scalar(
            select(ApPaymentRecord).where(
                ApPaymentRecord.idempotency_key == idempotency_key,
                ApPaymentRecord.tenant_id == self._tenant_id,
            )
        )
        return self._ap_payment_domain(record) if record is not None else None

    def get_ap_payment_by_apply_key(self, apply_key: UUID) -> ApPayment | None:
        record = self._session.scalar(
            select(ApPaymentRecord).where(
                ApPaymentRecord.apply_key == apply_key,
                ApPaymentRecord.tenant_id == self._tenant_id,
            )
        )
        return self._ap_payment_domain(record) if record is not None else None

    def list_ap_payments_for_bill(self, ap_bill_id: UUID) -> list[ApPayment]:
        records = self._session.scalars(
            select(ApPaymentRecord).where(
                ApPaymentRecord.ap_bill_id == ap_bill_id,
                ApPaymentRecord.tenant_id == self._tenant_id,
            )
        ).all()
        return [self._ap_payment_domain(record) for record in records]

    def list_ap_payments_for_supplier(
        self, supplier_id: UUID
    ) -> list[ApPayment]:
        records = self._session.scalars(
            select(ApPaymentRecord)
            .where(
                ApPaymentRecord.supplier_id == supplier_id,
                ApPaymentRecord.tenant_id == self._tenant_id,
            )
            .order_by(ApPaymentRecord.created_at, ApPaymentRecord.id)
        ).all()
        return [self._ap_payment_domain(record) for record in records]

    def save_ap_payment(
        self, payment: ApPayment, *, expected_version: int
    ) -> None:
        self._require_tenant(payment.tenant_id)
        result = self._session.execute(
            update(ApPaymentRecord)
            .where(
                ApPaymentRecord.id == payment.id,
                ApPaymentRecord.tenant_id == self._tenant_id,
                ApPaymentRecord.version == expected_version,
            )
            .values(
                status=payment.status.value,
                ap_bill_id=payment.ap_bill_id,
                ap_bill_version=payment.ap_bill_version,
                apply_key=payment.apply_key,
                applied_at=payment.applied_at,
                version=payment.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("ap payment version conflict")

    def next_ap_bill_line_number(self, ap_bill_id: UUID) -> int:
        current = self._session.scalar(
            select(func.max(ApBillLineRecord.line_number)).where(
                ApBillLineRecord.ap_bill_id == ap_bill_id,
                ApBillLineRecord.tenant_id == self._tenant_id,
            )
        )
        return int(current or 0) + 1

    def add_ap_bill_line(self, line: ApBillLine) -> None:
        self._require_tenant(line.tenant_id)
        self._session.add(self._ap_bill_line_record(line))

    def get_ap_bill_line(
        self, ap_bill_id: UUID, line_id: UUID
    ) -> ApBillLine | None:
        record = self._session.scalar(
            select(ApBillLineRecord).where(
                ApBillLineRecord.id == line_id,
                ApBillLineRecord.ap_bill_id == ap_bill_id,
                ApBillLineRecord.tenant_id == self._tenant_id,
            )
        )
        return self._ap_bill_line_domain(record) if record is not None else None

    def list_ap_bill_lines(self, ap_bill_id: UUID) -> list[ApBillLine]:
        records = self._session.scalars(
            select(ApBillLineRecord)
            .where(
                ApBillLineRecord.ap_bill_id == ap_bill_id,
                ApBillLineRecord.tenant_id == self._tenant_id,
            )
            .order_by(ApBillLineRecord.line_number)
        ).all()
        return [self._ap_bill_line_domain(record) for record in records]

    def save_ap_bill_line(
        self, line: ApBillLine, *, expected_version: int
    ) -> None:
        self._require_tenant(line.tenant_id)
        result = self._session.execute(
            update(ApBillLineRecord)
            .where(
                ApBillLineRecord.id == line.id,
                ApBillLineRecord.ap_bill_id == line.ap_bill_id,
                ApBillLineRecord.tenant_id == self._tenant_id,
                ApBillLineRecord.version == expected_version,
            )
            .values(
                description=line.description,
                quantity=line.quantity,
                unit_price=line.unit_price,
                amount=line.amount,
                status=line.status.value,
                updated_at=line.updated_at,
                archived_at=line.archived_at,
                version=line.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("ap bill line version conflict")

    def add_purchase_order(self, order: PurchaseOrder) -> None:
        self._require_tenant(order.tenant_id)
        self._session.add(self._purchase_order_record(order))

    def get_purchase_order(self, order_id: UUID) -> PurchaseOrder | None:
        record = self._session.scalar(
            select(PurchaseOrderRecord).where(
                PurchaseOrderRecord.id == order_id,
                PurchaseOrderRecord.tenant_id == self._tenant_id,
            )
        )
        return self._purchase_order_domain(record) if record is not None else None

    def get_purchase_order_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> PurchaseOrder | None:
        record = self._session.scalar(
            select(PurchaseOrderRecord).where(
                PurchaseOrderRecord.idempotency_key == idempotency_key,
                PurchaseOrderRecord.tenant_id == self._tenant_id,
            )
        )
        return self._purchase_order_domain(record) if record is not None else None

    def save_purchase_order(
        self, order: PurchaseOrder, *, expected_version: int
    ) -> None:
        self._require_tenant(order.tenant_id)
        result = self._session.execute(
            update(PurchaseOrderRecord)
            .where(
                PurchaseOrderRecord.id == order.id,
                PurchaseOrderRecord.tenant_id == self._tenant_id,
                PurchaseOrderRecord.version == expected_version,
            )
            .values(
                status=order.status.value,
                notes=order.notes,
                updated_at=order.updated_at,
                archived_at=order.archived_at,
                version=order.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("purchase order version conflict")

    def next_purchase_order_line_number(self, purchase_order_id: UUID) -> int:
        current = self._session.scalar(
            select(func.max(PurchaseOrderLineRecord.line_number)).where(
                PurchaseOrderLineRecord.purchase_order_id == purchase_order_id,
                PurchaseOrderLineRecord.tenant_id == self._tenant_id,
            )
        )
        return int(current or 0) + 1

    def add_purchase_order_line(self, line: PurchaseOrderLine) -> None:
        self._require_tenant(line.tenant_id)
        self._session.add(self._purchase_order_line_record(line))

    def list_purchase_order_lines(
        self, purchase_order_id: UUID
    ) -> list[PurchaseOrderLine]:
        records = self._session.scalars(
            select(PurchaseOrderLineRecord)
            .where(
                PurchaseOrderLineRecord.purchase_order_id == purchase_order_id,
                PurchaseOrderLineRecord.tenant_id == self._tenant_id,
            )
            .order_by(PurchaseOrderLineRecord.line_number)
        ).all()
        return [self._purchase_order_line_domain(record) for record in records]

    def add_goods_receipt(self, receipt: GoodsReceipt) -> None:
        self._require_tenant(receipt.tenant_id)
        self._session.add(self._goods_receipt_record(receipt))

    def get_goods_receipt(self, receipt_id: UUID) -> GoodsReceipt | None:
        record = self._session.scalar(
            select(GoodsReceiptRecord).where(
                GoodsReceiptRecord.id == receipt_id,
                GoodsReceiptRecord.tenant_id == self._tenant_id,
            )
        )
        return self._goods_receipt_domain(record) if record is not None else None

    def get_goods_receipt_by_po(
        self, purchase_order_id: UUID
    ) -> GoodsReceipt | None:
        record = self._session.scalar(
            select(GoodsReceiptRecord).where(
                GoodsReceiptRecord.purchase_order_id == purchase_order_id,
                GoodsReceiptRecord.tenant_id == self._tenant_id,
            )
        )
        return self._goods_receipt_domain(record) if record is not None else None

    def get_goods_receipt_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> GoodsReceipt | None:
        record = self._session.scalar(
            select(GoodsReceiptRecord).where(
                GoodsReceiptRecord.idempotency_key == idempotency_key,
                GoodsReceiptRecord.tenant_id == self._tenant_id,
            )
        )
        return self._goods_receipt_domain(record) if record is not None else None

    def add_three_way_match(self, match: ThreeWayMatch) -> None:
        self._require_tenant(match.tenant_id)
        self._session.add(self._three_way_match_record(match))

    def get_three_way_match_by_po(
        self, purchase_order_id: UUID
    ) -> ThreeWayMatch | None:
        record = self._session.scalar(
            select(ThreeWayMatchRecord).where(
                ThreeWayMatchRecord.purchase_order_id == purchase_order_id,
                ThreeWayMatchRecord.tenant_id == self._tenant_id,
            )
        )
        return (
            self._three_way_match_domain(record) if record is not None else None
        )

    def get_three_way_match_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ThreeWayMatch | None:
        record = self._session.scalar(
            select(ThreeWayMatchRecord).where(
                ThreeWayMatchRecord.idempotency_key == idempotency_key,
                ThreeWayMatchRecord.tenant_id == self._tenant_id,
            )
        )
        return (
            self._three_way_match_domain(record) if record is not None else None
        )

    def get_three_way_match_tolerance_policy(
        self,
    ) -> TenantThreeWayMatchTolerancePolicy | None:
        record = self._session.get(
            TenantThreeWayMatchTolerancePolicyRecord, self._tenant_id
        )
        if record is None:
            return None
        return TenantThreeWayMatchTolerancePolicy(
            tenant_id=record.tenant_id,
            amount_tolerance_abs=(
                Decimal("0.00")
                if record.amount_tolerance_abs is None
                else Decimal(str(record.amount_tolerance_abs))
            ),
            amount_tolerance_pct=(
                Decimal("0")
                if record.amount_tolerance_pct is None
                else Decimal(str(record.amount_tolerance_pct))
            ),
            updated_at=record.updated_at,
            version=record.version,
        )

    def save_three_way_match_tolerance_policy(
        self,
        policy: TenantThreeWayMatchTolerancePolicy,
        *,
        expected_version: int,
    ) -> None:
        self._require_tenant(policy.tenant_id)
        if expected_version == 0:
            self._session.add(
                TenantThreeWayMatchTolerancePolicyRecord(
                    tenant_id=policy.tenant_id,
                    amount_tolerance_abs=policy.amount_tolerance_abs,
                    amount_tolerance_pct=policy.amount_tolerance_pct,
                    updated_at=policy.updated_at,
                    version=policy.version,
                )
            )
            return
        result = self._session.execute(
            update(TenantThreeWayMatchTolerancePolicyRecord)
            .where(
                TenantThreeWayMatchTolerancePolicyRecord.tenant_id
                == self._tenant_id,
                TenantThreeWayMatchTolerancePolicyRecord.version
                == expected_version,
            )
            .values(
                amount_tolerance_abs=policy.amount_tolerance_abs,
                amount_tolerance_pct=policy.amount_tolerance_pct,
                updated_at=policy.updated_at,
                version=policy.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError(
                "three-way match tolerance policy version conflict"
            )

    def _require_tenant(self, tenant_id: UUID) -> None:
        if tenant_id != self._tenant_id:
            raise ValueError("Purchase record is outside repository tenant")

    @staticmethod
    def _supplier_record(supplier: Supplier) -> SupplierRecord:
        return SupplierRecord(
            id=supplier.id,
            tenant_id=supplier.tenant_id,
            code=supplier.code,
            display_name=supplier.display_name,
            status=supplier.status.value,
            created_at=supplier.created_at,
            updated_at=supplier.updated_at,
            archived_at=supplier.archived_at,
            version=supplier.version,
        )

    @staticmethod
    def _ap_bill_record(bill: ApBill) -> ApBillRecord:
        return ApBillRecord(
            id=bill.id,
            tenant_id=bill.tenant_id,
            supplier_id=bill.supplier_id,
            code=bill.code,
            currency=bill.currency,
            total_amount=bill.total_amount,
            paid_amount=bill.paid_amount,
            write_off_amount=bill.write_off_amount,
            idempotency_key=bill.idempotency_key,
            status=bill.status.value,
            created_at=bill.created_at,
            version=bill.version,
        )

    @staticmethod
    def _supplier_domain(record: SupplierRecord) -> Supplier:
        return Supplier(
            id=record.id,
            tenant_id=record.tenant_id,
            code=record.code,
            display_name=record.display_name,
            status=SupplierStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            archived_at=record.archived_at,
            version=record.version,
        )

    @staticmethod
    def _ap_bill_domain(record: ApBillRecord) -> ApBill:
        return ApBill(
            id=record.id,
            tenant_id=record.tenant_id,
            supplier_id=record.supplier_id,
            code=record.code,
            currency=record.currency,
            total_amount=record.total_amount,
            paid_amount=record.paid_amount,
            write_off_amount=record.write_off_amount,
            idempotency_key=record.idempotency_key,
            status=ApBillStatus(record.status),
            created_at=record.created_at,
            version=record.version,
        )

    @staticmethod
    def _ap_write_off_record(write_off: ApWriteOff) -> ApWriteOffRecord:
        return ApWriteOffRecord(
            id=write_off.id,
            tenant_id=write_off.tenant_id,
            ap_bill_id=write_off.ap_bill_id,
            amount=write_off.amount,
            currency=write_off.currency,
            idempotency_key=write_off.idempotency_key,
            reason=write_off.reason,
            created_at=write_off.created_at,
            version=write_off.version,
        )

    @staticmethod
    def _ap_write_off_domain(record: ApWriteOffRecord) -> ApWriteOff:
        return ApWriteOff(
            id=record.id,
            tenant_id=record.tenant_id,
            ap_bill_id=record.ap_bill_id,
            amount=record.amount,
            currency=record.currency,
            idempotency_key=record.idempotency_key,
            reason=record.reason,
            created_at=record.created_at,
            version=record.version,
        )

    @staticmethod
    def _ap_payment_record(payment: ApPayment) -> ApPaymentRecord:
        return ApPaymentRecord(
            id=payment.id,
            tenant_id=payment.tenant_id,
            supplier_id=payment.supplier_id,
            amount=payment.amount,
            currency=payment.currency,
            functional_currency=payment.functional_currency,
            fx_rate=payment.fx_rate,
            functional_amount=payment.functional_amount,
            idempotency_key=payment.idempotency_key,
            status=payment.status.value,
            created_at=payment.created_at,
            ap_bill_id=payment.ap_bill_id,
            ap_bill_version=payment.ap_bill_version,
            apply_key=payment.apply_key,
            applied_at=payment.applied_at,
            version=payment.version,
        )

    @staticmethod
    def _ap_payment_domain(record: ApPaymentRecord) -> ApPayment:
        return ApPayment(
            id=record.id,
            tenant_id=record.tenant_id,
            supplier_id=record.supplier_id,
            amount=record.amount,
            currency=record.currency,
            functional_currency=record.functional_currency,
            fx_rate=record.fx_rate,
            functional_amount=record.functional_amount,
            idempotency_key=record.idempotency_key,
            status=ApPaymentStatus(record.status),
            created_at=record.created_at,
            ap_bill_id=record.ap_bill_id,
            ap_bill_version=record.ap_bill_version,
            apply_key=record.apply_key,
            applied_at=record.applied_at,
            version=record.version,
        )

    @staticmethod
    def _ap_bill_line_record(line: ApBillLine) -> ApBillLineRecord:
        return ApBillLineRecord(
            id=line.id,
            tenant_id=line.tenant_id,
            ap_bill_id=line.ap_bill_id,
            line_number=line.line_number,
            description=line.description,
            quantity=line.quantity,
            unit_price=line.unit_price,
            amount=line.amount,
            status=line.status.value,
            created_at=line.created_at,
            updated_at=line.updated_at,
            archived_at=line.archived_at,
            version=line.version,
        )

    @staticmethod
    def _ap_bill_line_domain(record: ApBillLineRecord) -> ApBillLine:
        return ApBillLine(
            id=record.id,
            tenant_id=record.tenant_id,
            ap_bill_id=record.ap_bill_id,
            line_number=record.line_number,
            description=record.description,
            quantity=record.quantity,
            unit_price=record.unit_price,
            amount=record.amount,
            status=ApBillLineStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            archived_at=record.archived_at,
            version=record.version,
        )

    @staticmethod
    def _purchase_order_record(order: PurchaseOrder) -> PurchaseOrderRecord:
        return PurchaseOrderRecord(
            id=order.id,
            tenant_id=order.tenant_id,
            supplier_id=order.supplier_id,
            code=order.code,
            currency=order.currency,
            notes=order.notes,
            idempotency_key=order.idempotency_key,
            status=order.status.value,
            created_at=order.created_at,
            updated_at=order.updated_at,
            archived_at=order.archived_at,
            version=order.version,
        )

    @staticmethod
    def _purchase_order_domain(record: PurchaseOrderRecord) -> PurchaseOrder:
        return PurchaseOrder(
            id=record.id,
            tenant_id=record.tenant_id,
            supplier_id=record.supplier_id,
            code=record.code,
            currency=record.currency,
            notes=record.notes,
            idempotency_key=record.idempotency_key,
            status=PurchaseOrderStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            archived_at=record.archived_at,
            version=record.version,
        )

    @staticmethod
    def _purchase_order_line_record(
        line: PurchaseOrderLine,
    ) -> PurchaseOrderLineRecord:
        return PurchaseOrderLineRecord(
            id=line.id,
            tenant_id=line.tenant_id,
            purchase_order_id=line.purchase_order_id,
            line_number=line.line_number,
            inventory_item_id=line.inventory_item_id,
            quantity=line.quantity,
            unit_price=line.unit_price,
            status=line.status.value,
            created_at=line.created_at,
            updated_at=line.updated_at,
            version=line.version,
        )

    @staticmethod
    def _purchase_order_line_domain(
        record: PurchaseOrderLineRecord,
    ) -> PurchaseOrderLine:
        return PurchaseOrderLine(
            id=record.id,
            tenant_id=record.tenant_id,
            purchase_order_id=record.purchase_order_id,
            line_number=record.line_number,
            inventory_item_id=record.inventory_item_id,
            quantity=record.quantity,
            unit_price=record.unit_price,
            status=PurchaseOrderLineStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            version=record.version,
        )

    @staticmethod
    def _goods_receipt_record(receipt: GoodsReceipt) -> GoodsReceiptRecord:
        return GoodsReceiptRecord(
            id=receipt.id,
            tenant_id=receipt.tenant_id,
            purchase_order_id=receipt.purchase_order_id,
            code=receipt.code,
            status=receipt.status.value,
            idempotency_key=receipt.idempotency_key,
            received_at=receipt.received_at,
            created_at=receipt.created_at,
            version=receipt.version,
        )

    @staticmethod
    def _goods_receipt_domain(record: GoodsReceiptRecord) -> GoodsReceipt:
        return GoodsReceipt(
            id=record.id,
            tenant_id=record.tenant_id,
            purchase_order_id=record.purchase_order_id,
            code=record.code,
            status=GoodsReceiptStatus(record.status),
            idempotency_key=record.idempotency_key,
            received_at=record.received_at,
            created_at=record.created_at,
            version=record.version,
        )

    @staticmethod
    def _three_way_match_record(match: ThreeWayMatch) -> ThreeWayMatchRecord:
        return ThreeWayMatchRecord(
            id=match.id,
            tenant_id=match.tenant_id,
            purchase_order_id=match.purchase_order_id,
            goods_receipt_id=match.goods_receipt_id,
            ap_bill_id=match.ap_bill_id,
            status=match.status.value,
            idempotency_key=match.idempotency_key,
            created_at=match.created_at,
            version=match.version,
        )

    @staticmethod
    def _three_way_match_domain(record: ThreeWayMatchRecord) -> ThreeWayMatch:
        return ThreeWayMatch(
            id=record.id,
            tenant_id=record.tenant_id,
            purchase_order_id=record.purchase_order_id,
            goods_receipt_id=record.goods_receipt_id,
            ap_bill_id=record.ap_bill_id,
            status=ThreeWayMatchStatus(record.status),
            idempotency_key=record.idempotency_key,
            created_at=record.created_at,
            version=record.version,
        )


class TransactionalPurchaseService:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create_supplier(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[Supplier]:
        return self._execute(
            ctx, lambda service: service.create_supplier(ctx, **kwargs)
        )

    def get_supplier(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[Supplier]:
        return self._execute(
            ctx, lambda service: service.get_supplier(ctx, **kwargs)
        )

    def get_supplier_balance(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult:
        return self._execute(
            ctx, lambda service: service.get_supplier_balance(ctx, **kwargs)
        )

    def update_supplier(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[Supplier]:
        return self._execute(
            ctx, lambda service: service.update_supplier(ctx, **kwargs)
        )

    def archive_supplier(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[Supplier]:
        return self._execute(
            ctx, lambda service: service.archive_supplier(ctx, **kwargs)
        )

    def create_ap_bill(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ApBill]:
        return self._execute(
            ctx, lambda service: service.create_ap_bill(ctx, **kwargs)
        )

    def get_ap_bill(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ApBill]:
        return self._execute(
            ctx, lambda service: service.get_ap_bill(ctx, **kwargs)
        )

    def post_ap_bill(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ApBill]:
        return self._execute(
            ctx, lambda service: service.post_ap_bill(ctx, **kwargs)
        )

    def create_ap_write_off(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ApWriteOff]:
        return self._execute(
            ctx, lambda service: service.create_ap_write_off(ctx, **kwargs)
        )

    def close_ap_bill(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ApBill]:
        return self._execute(
            ctx, lambda service: service.close_ap_bill(ctx, **kwargs)
        )

    def create_ap_payment(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ApPayment]:
        return self._execute(
            ctx, lambda service: service.create_ap_payment(ctx, **kwargs)
        )

    def get_ap_payment(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ApPayment]:
        return self._execute(
            ctx, lambda service: service.get_ap_payment(ctx, **kwargs)
        )

    def apply_ap_payment_to_bill(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ApPayment]:
        return self._execute(
            ctx, lambda service: service.apply_ap_payment_to_bill(ctx, **kwargs)
        )

    def create_ap_bill_line(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ApBillLine]:
        return self._execute(
            ctx, lambda service: service.create_ap_bill_line(ctx, **kwargs)
        )

    def get_ap_bill_line(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ApBillLine]:
        return self._execute(
            ctx, lambda service: service.get_ap_bill_line(ctx, **kwargs)
        )

    def list_ap_bill_lines(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[list[ApBillLine]]:
        return self._execute(
            ctx, lambda service: service.list_ap_bill_lines(ctx, **kwargs)
        )

    def archive_ap_bill_line(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ApBillLine]:
        return self._execute(
            ctx, lambda service: service.archive_ap_bill_line(ctx, **kwargs)
        )

    def create_purchase_order(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[PurchaseOrder]:
        return self._execute(
            ctx, lambda service: service.create_purchase_order(ctx, **kwargs)
        )

    def get_purchase_order(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[PurchaseOrder]:
        return self._execute(
            ctx, lambda service: service.get_purchase_order(ctx, **kwargs)
        )

    def archive_purchase_order(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[PurchaseOrder]:
        return self._execute(
            ctx, lambda service: service.archive_purchase_order(ctx, **kwargs)
        )

    def create_purchase_order_line(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[PurchaseOrderLine]:
        return self._execute(
            ctx,
            lambda service: service.create_purchase_order_line(ctx, **kwargs),
        )

    def create_goods_receipt(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GoodsReceipt]:
        return self._execute(
            ctx, lambda service: service.create_goods_receipt(ctx, **kwargs)
        )

    def create_three_way_match(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ThreeWayMatch]:
        return self._execute(
            ctx, lambda service: service.create_three_way_match(ctx, **kwargs)
        )

    def get_three_way_match_tolerance_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantThreeWayMatchTolerancePolicy]:
        return self._execute(
            ctx,
            lambda service: service.get_three_way_match_tolerance_policy(
                ctx, **kwargs
            ),
        )

    def set_three_way_match_tolerance_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantThreeWayMatchTolerancePolicy]:
        return self._execute(
            ctx,
            lambda service: service.set_three_way_match_tolerance_policy(
                ctx, **kwargs
            ),
        )

    def _execute(
        self,
        ctx: ExecutionContext,
        operation: Callable[[PurchaseService], KernelResult[T]],
    ) -> KernelResult[T]:
        if ctx.tenant_id is None or ctx.platform_scope:
            return KernelResult.failure(
                ErrorCode.CTX_INVALID,
                "Purchase requires a tenant data-plane context",
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
                from noventi.inventory.persistence import (
                    SQLAlchemyInventoryRepository,
                )
                from noventi.inventory.receipt_adapter import (
                    InventoryPurchaseReceiptAdapter,
                )

                inventory_repo = SQLAlchemyInventoryRepository(
                    unit_of_work.session,
                    tenant_id=ctx.tenant_id,
                )
                service = PurchaseService(
                    permission,
                    repository=SQLAlchemyPurchaseRepository(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                    ),
                    audit_log=audit,
                    inventory_receipt_port=InventoryPurchaseReceiptAdapter(
                        inventory_repo
                    ),
                )
                result = operation(service)
                unit_of_work.commit()
                return result
        except IntegrityError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "Purchase persistence conflict"
            )
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL, "Purchase persistence unavailable"
            )
