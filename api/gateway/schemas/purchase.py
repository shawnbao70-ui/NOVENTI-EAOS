"""Closed HTTP DTOs for Purchase AP1–AP5 slices."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreateSupplierRequest(_ClosedModel):
    code: str = Field(min_length=1, max_length=64)
    display_name: str = Field(min_length=1, max_length=255)


class UpdateSupplierRequest(_ClosedModel):
    display_name: str = Field(min_length=1, max_length=255)
    expected_version: int = Field(ge=1)


class ArchiveSupplierRequest(_ClosedModel):
    reason: str = Field(min_length=1, max_length=500)
    expected_version: int = Field(ge=1)


class CreateApBillRequest(_ClosedModel):
    supplier_id: UUID
    code: str = Field(min_length=1, max_length=64)
    currency: str = Field(min_length=3, max_length=3)
    total_amount: Decimal = Field(ge=0, max_digits=18, decimal_places=2)
    idempotency_key: UUID


class PostApBillRequest(_ClosedModel):
    idempotency_key: UUID | None = None
    human_confirm: Literal[True]


class CreateApWriteOffRequest(_ClosedModel):
    ap_bill_id: UUID
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    idempotency_key: UUID
    human_confirm: Literal[True]
    reason: str | None = Field(default=None, min_length=1, max_length=500)


class CloseApBillRequest(_ClosedModel):
    human_confirm: Literal[True]


class CreateApPaymentRequest(_ClosedModel):
    supplier_id: UUID
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3)
    functional_currency: str | None = Field(
        default=None, min_length=3, max_length=3
    )
    fx_rate: Decimal | None = Field(
        default=None, gt=0, max_digits=18, decimal_places=8
    )
    functional_amount: Decimal | None = Field(
        default=None, gt=0, max_digits=18, decimal_places=2
    )
    idempotency_key: UUID


class ApplyApPaymentRequest(_ClosedModel):
    ap_bill_id: UUID
    apply_key: UUID


class CreateApBillLineRequest(_ClosedModel):
    description: str = Field(min_length=1, max_length=500)
    quantity: Decimal = Field(gt=0, max_digits=18, decimal_places=3)
    unit_price: Decimal = Field(ge=0, max_digits=18, decimal_places=2)


class ArchiveApBillLineRequest(_ClosedModel):
    reason: str = Field(min_length=1, max_length=500)
    expected_version: int = Field(ge=1)


class CreatePurchaseOrderRequest(_ClosedModel):
    supplier_id: UUID
    code: str = Field(min_length=1, max_length=64)
    currency: str = Field(min_length=3, max_length=3)
    idempotency_key: UUID
    notes: str | None = Field(default=None, max_length=2000)


class ArchivePurchaseOrderRequest(_ClosedModel):
    reason: str = Field(min_length=1, max_length=500)
    expected_version: int = Field(ge=1)


class CreatePurchaseOrderLineRequest(_ClosedModel):
    inventory_item_id: UUID
    quantity: Decimal = Field(gt=0, max_digits=18, decimal_places=3)
    unit_price: Decimal | None = Field(
        default=None, ge=0, max_digits=18, decimal_places=2
    )


class CreateGoodsReceiptRequest(_ClosedModel):
    idempotency_key: UUID
    human_confirm: bool


class CreateThreeWayMatchRequest(_ClosedModel):
    purchase_order_id: UUID
    goods_receipt_id: UUID
    ap_bill_id: UUID
    idempotency_key: UUID


class SupplierView(_ClosedModel):
    id: UUID
    code: str
    display_name: str
    status: Literal["active", "archived"]
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None
    version: int


class ApBillView(_ClosedModel):
    id: UUID
    supplier_id: UUID
    code: str
    currency: str
    total_amount: Decimal
    paid_amount: Decimal
    write_off_amount: Decimal
    remaining_amount: Decimal
    status: Literal["draft", "posted", "partially_paid", "paid", "closed"]
    created_at: datetime
    version: int


class ApBillLineView(_ClosedModel):
    id: UUID
    ap_bill_id: UUID
    line_number: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal
    status: Literal["active", "archived"]
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None
    version: int


class ApPaymentView(_ClosedModel):
    id: UUID
    supplier_id: UUID
    amount: Decimal
    currency: str
    functional_currency: str
    fx_rate: Decimal
    functional_amount: Decimal
    status: Literal["draft", "applied"]
    ap_bill_id: UUID | None
    ap_bill_version: int | None
    apply_key: UUID | None
    created_at: datetime
    applied_at: datetime | None
    version: int


class ApWriteOffView(_ClosedModel):
    id: UUID
    ap_bill_id: UUID
    amount: Decimal
    currency: str
    reason: str | None
    created_at: datetime
    version: int


class PurchaseOrderView(_ClosedModel):
    id: UUID
    supplier_id: UUID
    code: str
    currency: str
    notes: str | None
    status: Literal["draft", "archived", "received"]
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None
    version: int


class PurchaseOrderLineView(_ClosedModel):
    id: UUID
    purchase_order_id: UUID
    line_number: int
    inventory_item_id: UUID
    quantity: Decimal
    unit_price: Decimal | None
    status: Literal["active"]
    created_at: datetime
    updated_at: datetime
    version: int


class GoodsReceiptView(_ClosedModel):
    id: UUID
    purchase_order_id: UUID
    code: str
    status: Literal["received"]
    received_at: datetime
    created_at: datetime
    version: int


class ThreeWayMatchView(_ClosedModel):
    id: UUID
    purchase_order_id: UUID
    goods_receipt_id: UUID
    ap_bill_id: UUID
    status: Literal["matched", "mismatch"]
    created_at: datetime
    version: int


class SupplierEnvelope(_ClosedModel):
    data: SupplierView
    audit_id: UUID | None = None


class SupplierBalanceView(_ClosedModel):
    supplier_id: UUID
    balances: dict[str, Decimal]


class SupplierBalanceEnvelope(_ClosedModel):
    data: SupplierBalanceView
    audit_id: UUID | None = None


class Supplier360BillTraceView(_ClosedModel):
    id: UUID
    code: str
    status: Literal[
        "draft", "posted", "partially_paid", "paid", "closed"
    ]
    currency: str
    total_amount: Decimal


class Supplier360PaymentTraceView(_ClosedModel):
    id: UUID
    status: Literal["draft", "applied"]
    currency: str
    amount: Decimal
    ap_bill_id: UUID | None


class Supplier360View(_ClosedModel):
    supplier_id: UUID
    supplier_code: str
    display_name: str
    status: Literal["active", "archived"]
    balances: dict[str, Decimal]
    bill_traces: list[Supplier360BillTraceView]
    payment_traces: list[Supplier360PaymentTraceView]


class Supplier360Envelope(_ClosedModel):
    data: Supplier360View
    audit_id: UUID | None = None


class SupplierAdvisoryView(_ClosedModel):
    """Advisory projection over Supplier360 read source (PHX-G391)."""

    supplier_id: UUID
    read_source: Literal["supplier360"] = "supplier360"
    supplier360: Supplier360View
    execution_authority: Literal["none"] = "none"
    commercial_auto_write: Literal[False] = False


class SupplierAdvisoryEnvelope(_ClosedModel):
    data: SupplierAdvisoryView
    audit_id: UUID | None = None


class ApBillEnvelope(_ClosedModel):
    data: ApBillView
    audit_id: UUID | None = None


class ApPaymentEnvelope(_ClosedModel):
    data: ApPaymentView
    audit_id: UUID | None = None


class ApWriteOffEnvelope(_ClosedModel):
    data: ApWriteOffView
    audit_id: UUID | None = None


class ApBillLineEnvelope(_ClosedModel):
    data: ApBillLineView
    audit_id: UUID | None = None


class ApBillLineListEnvelope(_ClosedModel):
    data: list[ApBillLineView]


class PurchaseOrderEnvelope(_ClosedModel):
    data: PurchaseOrderView
    audit_id: UUID | None = None


class PurchaseOrderLineEnvelope(_ClosedModel):
    data: PurchaseOrderLineView
    audit_id: UUID | None = None


class GoodsReceiptEnvelope(_ClosedModel):
    data: GoodsReceiptView
    audit_id: UUID | None = None


class ThreeWayMatchEnvelope(_ClosedModel):
    data: ThreeWayMatchView
    audit_id: UUID | None = None


class SetThreeWayMatchTolerancePolicyRequest(_ClosedModel):
    amount_tolerance_abs: Decimal | None = Field(
        default=None, ge=0, max_digits=18, decimal_places=2
    )
    amount_tolerance_pct: Decimal | None = Field(
        default=None, ge=0, max_digits=9, decimal_places=4
    )
    expected_version: int = Field(ge=0)


class ThreeWayMatchTolerancePolicyView(_ClosedModel):
    amount_tolerance_abs: Decimal
    amount_tolerance_pct: Decimal
    updated_at: datetime
    version: int


class ThreeWayMatchTolerancePolicyEnvelope(_ClosedModel):
    data: ThreeWayMatchTolerancePolicyView
    audit_id: UUID | None = None
