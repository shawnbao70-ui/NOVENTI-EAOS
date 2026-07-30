"""Supplier, AP Bill, and Purchase Order models owned by ``noventi.purchase``."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID


class SupplierStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class ApBillStatus(StrEnum):
    DRAFT = "draft"
    POSTED = "posted"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    CLOSED = "closed"


class ApPaymentStatus(StrEnum):
    DRAFT = "draft"
    APPLIED = "applied"


class ApBillLineStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class PurchaseOrderStatus(StrEnum):
    DRAFT = "draft"
    ARCHIVED = "archived"
    RECEIVED = "received"


class PurchaseOrderLineStatus(StrEnum):
    ACTIVE = "active"


class GoodsReceiptStatus(StrEnum):
    RECEIVED = "received"


class ThreeWayMatchStatus(StrEnum):
    MATCHED = "matched"
    MISMATCH = "mismatch"


@dataclass(slots=True)
class Supplier:
    id: UUID
    tenant_id: UUID
    code: str
    display_name: str
    status: SupplierStatus
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None
    version: int = 1


@dataclass(slots=True)
class ApBill:
    id: UUID
    tenant_id: UUID
    supplier_id: UUID
    code: str
    currency: str
    total_amount: Decimal
    idempotency_key: UUID
    status: ApBillStatus
    created_at: datetime
    paid_amount: Decimal = Decimal("0.00")
    write_off_amount: Decimal = Decimal("0.00")
    version: int = 1


@dataclass(slots=True)
class ApWriteOff:
    id: UUID
    tenant_id: UUID
    ap_bill_id: UUID
    amount: Decimal
    currency: str
    idempotency_key: UUID
    created_at: datetime
    reason: str | None = None
    version: int = 1


@dataclass(slots=True)
class ApPayment:
    id: UUID
    tenant_id: UUID
    supplier_id: UUID
    amount: Decimal
    currency: str
    idempotency_key: UUID
    status: ApPaymentStatus
    created_at: datetime
    functional_currency: str = ""
    fx_rate: Decimal = Decimal("1.00000000")
    functional_amount: Decimal = Decimal("0.00")
    ap_bill_id: UUID | None = None
    ap_bill_version: int | None = None
    apply_key: UUID | None = None
    applied_at: datetime | None = None
    version: int = 1


@dataclass(slots=True)
class ApBillLine:
    id: UUID
    tenant_id: UUID
    ap_bill_id: UUID
    line_number: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal
    status: ApBillLineStatus
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None
    version: int = 1


@dataclass(slots=True)
class PurchaseOrder:
    id: UUID
    tenant_id: UUID
    supplier_id: UUID
    code: str
    currency: str
    idempotency_key: UUID
    status: PurchaseOrderStatus
    created_at: datetime
    updated_at: datetime
    notes: str | None = None
    archived_at: datetime | None = None
    version: int = 1


@dataclass(slots=True)
class PurchaseOrderLine:
    id: UUID
    tenant_id: UUID
    purchase_order_id: UUID
    line_number: int
    inventory_item_id: UUID
    quantity: Decimal
    status: PurchaseOrderLineStatus
    created_at: datetime
    updated_at: datetime
    unit_price: Decimal | None = None
    version: int = 1


@dataclass(slots=True)
class GoodsReceipt:
    id: UUID
    tenant_id: UUID
    purchase_order_id: UUID
    code: str
    status: GoodsReceiptStatus
    idempotency_key: UUID
    received_at: datetime
    created_at: datetime
    version: int = 1


@dataclass(slots=True)
class ThreeWayMatch:
    id: UUID
    tenant_id: UUID
    purchase_order_id: UUID
    goods_receipt_id: UUID
    ap_bill_id: UUID
    status: ThreeWayMatchStatus
    idempotency_key: UUID
    created_at: datetime
    version: int = 1


@dataclass(slots=True)
class TenantThreeWayMatchTolerancePolicy:
    tenant_id: UUID
    amount_tolerance_abs: Decimal
    amount_tolerance_pct: Decimal
    updated_at: datetime
    version: int = 1
