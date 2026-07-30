"""Permissioned Purchase Supplier + AP Bill + Purchase Order service."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Protocol
from uuid import UUID, uuid4

from kernel.permission.models import PermissionEffect, Resource
from kernel.shared.audit import AuditLog
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
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
from noventi.purchase.receipt import InventoryReceiptPort
from noventi.purchase.repository import PurchaseRepository

SUPPLIER_RESOURCE = "pkg.purchase.supplier"
AP_BILL_RESOURCE = "pkg.purchase.ap_bill"
AP_PAYMENT_RESOURCE = "pkg.purchase.ap_payment"
AP_WRITE_OFF_RESOURCE = "pkg.purchase.ap_write_off"
AP_BILL_LINE_RESOURCE = "pkg.purchase.ap_bill_line"
PURCHASE_ORDER_RESOURCE = "pkg.purchase.purchase_order"
PURCHASE_ORDER_LINE_RESOURCE = "pkg.purchase.purchase_order_line"
GOODS_RECEIPT_RESOURCE = "pkg.purchase.goods_receipt"
THREE_WAY_MATCH_RESOURCE = "pkg.purchase.three_way_match"
THREE_WAY_MATCH_TOLERANCE_POLICY_RESOURCE = (
    "pkg.purchase.three_way_match_tolerance_policy"
)
AMOUNT_QUANTUM = Decimal("0.01")
QTY_QUANTUM = Decimal("0.001")
FX_RATE_QUANTUM = Decimal("0.00000001")
PCT_QUANTUM = Decimal("0.0001")
MAX_AMOUNT = Decimal("9999999999999999.99")
MAX_QUANTITY = Decimal("999999999999999.999")
MAX_FX_RATE = Decimal("9999999999.99999999")
MAX_TOLERANCE_PCT = Decimal("100.0000")


class PermissionEvaluator(Protocol):
    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        action: str,
        resource: Resource,
    ) -> KernelResult: ...


@dataclass(frozen=True, slots=True)
class SupplierBalance:
    supplier_id: UUID
    balances: dict[str, Decimal]


class PurchaseService:
    """Purchase use cases: Supplier, AP Bill, Purchase Order shell."""

    def __init__(
        self,
        permission: PermissionEvaluator,
        *,
        repository: PurchaseRepository,
        audit_log: AuditLog,
        inventory_receipt_port: InventoryReceiptPort | None = None,
    ) -> None:
        self._permission = permission
        self._repository = repository
        self._audit = audit_log
        self._inventory_receipt_port = inventory_receipt_port

    def create_supplier(
        self,
        ctx: ExecutionContext,
        *,
        code: str,
        display_name: str,
    ) -> KernelResult[Supplier]:
        supplier_id = uuid4()
        try:
            self._write_intent(
                ctx, "Purchase.Supplier.Create", SUPPLIER_RESOURCE, supplier_id
            )
            denied = self._authorize(ctx, "create", SUPPLIER_RESOURCE)
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Purchase.Supplier.Create",
                    SUPPLIER_RESOURCE,
                    supplier_id,
                    denied,
                )
            now = datetime.now(timezone.utc)
            supplier = Supplier(
                id=supplier_id,
                tenant_id=self._tenant_id(ctx),
                code=self._required(code, "code", 64),
                display_name=self._required(display_name, "display_name", 255),
                status=SupplierStatus.ACTIVE,
                created_at=now,
                updated_at=now,
            )
            self._repository.add_supplier(supplier)
            audit = self._write_result(
                ctx,
                "Purchase.Supplier.Create",
                SUPPLIER_RESOURCE,
                supplier.id,
                "ok",
            )
            return KernelResult.success(supplier, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "supplier code already exists"
            )

    def get_supplier(
        self,
        ctx: ExecutionContext,
        *,
        supplier_id: UUID,
    ) -> KernelResult[Supplier]:
        try:
            denied = self._authorize(
                ctx, "read", SUPPLIER_RESOURCE, supplier_id
            )
            if denied is not None:
                return denied
            supplier = self._repository.get_supplier(supplier_id)
            if supplier is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "supplier not found"
                )
            return KernelResult.success(supplier)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_supplier_balance(
        self, ctx: ExecutionContext, *, supplier_id: UUID
    ) -> KernelResult[SupplierBalance]:
        try:
            denied = self._authorize(
                ctx, "read", SUPPLIER_RESOURCE, supplier_id
            )
            if denied is not None:
                return denied
            self._require_ap_bill_supplier(supplier_id)
            balances: dict[str, Decimal] = {}
            for bill in self._repository.list_ap_bills_for_supplier(supplier_id):
                if bill.status not in (
                    ApBillStatus.POSTED,
                    ApBillStatus.PARTIALLY_PAID,
                ):
                    continue
                remaining = (
                    bill.total_amount - bill.paid_amount - bill.write_off_amount
                )
                balances[bill.currency] = (
                    balances.get(bill.currency, Decimal("0.00")) + remaining
                )
            audit = self._write_result(
                ctx,
                "Purchase.SupplierBalance.Read",
                SUPPLIER_RESOURCE,
                supplier_id,
                "ok",
            )
            return KernelResult.success(
                SupplierBalance(
                    supplier_id=supplier_id,
                    balances=dict(sorted(balances.items())),
                ),
                audit_id=audit.id,
            )
        except KernelError as err:
            return KernelResult.from_error(err)

    def update_supplier(
        self,
        ctx: ExecutionContext,
        *,
        supplier_id: UUID,
        display_name: str,
        expected_version: int,
    ) -> KernelResult[Supplier]:
        try:
            self._write_intent(
                ctx, "Purchase.Supplier.Update", SUPPLIER_RESOURCE, supplier_id
            )
            denied = self._authorize(
                ctx, "update", SUPPLIER_RESOURCE, supplier_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Purchase.Supplier.Update",
                    SUPPLIER_RESOURCE,
                    supplier_id,
                    denied,
                )
            supplier = self._active_supplier(supplier_id)
            self._expected_version(supplier.version, expected_version)
            updated = replace(
                supplier,
                display_name=self._required(display_name, "display_name", 255),
                updated_at=datetime.now(timezone.utc),
                version=supplier.version + 1,
            )
            self._repository.save_supplier(
                updated, expected_version=expected_version
            )
            audit = self._write_result(
                ctx,
                "Purchase.Supplier.Update",
                SUPPLIER_RESOURCE,
                supplier_id,
                "ok",
            )
            return KernelResult.success(updated, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "supplier version conflict"
            )

    def archive_supplier(
        self,
        ctx: ExecutionContext,
        *,
        supplier_id: UUID,
        reason: str,
        expected_version: int,
    ) -> KernelResult[Supplier]:
        try:
            self._write_intent(
                ctx, "Purchase.Supplier.Archive", SUPPLIER_RESOURCE, supplier_id
            )
            denied = self._authorize(
                ctx, "archive", SUPPLIER_RESOURCE, supplier_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Purchase.Supplier.Archive",
                    SUPPLIER_RESOURCE,
                    supplier_id,
                    denied,
                )
            self._required(reason, "reason", 500)
            supplier = self._active_supplier(supplier_id)
            self._expected_version(supplier.version, expected_version)
            now = datetime.now(timezone.utc)
            archived = replace(
                supplier,
                status=SupplierStatus.ARCHIVED,
                archived_at=now,
                updated_at=now,
                version=supplier.version + 1,
            )
            self._repository.save_supplier(
                archived, expected_version=expected_version
            )
            audit = self._write_result(
                ctx,
                "Purchase.Supplier.Archive",
                SUPPLIER_RESOURCE,
                supplier_id,
                "ok",
            )
            return KernelResult.success(archived, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "supplier version conflict"
            )

    def create_ap_bill(
        self,
        ctx: ExecutionContext,
        *,
        supplier_id: UUID,
        code: str,
        currency: str,
        total_amount: Decimal,
        idempotency_key: UUID,
    ) -> KernelResult[ApBill]:
        bill_id = uuid4()
        try:
            self._write_intent(
                ctx, "Purchase.ApBill.Create", AP_BILL_RESOURCE, bill_id
            )
            denied = self._authorize(ctx, "create", AP_BILL_RESOURCE, supplier_id)
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Purchase.ApBill.Create",
                    AP_BILL_RESOURCE,
                    bill_id,
                    denied,
                )
            normalized_code = self._required(code, "code", 64)
            normalized_currency = self._currency(currency)
            normalized_amount = self._amount(total_amount)
            if normalized_amount < 0:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "ap bill total_amount must be non-negative",
                )
            existing = self._repository.get_ap_bill_by_idempotency_key(
                idempotency_key
            )
            if existing is not None:
                if (
                    existing.supplier_id != supplier_id
                    or existing.code != normalized_code
                    or existing.currency != normalized_currency
                    or existing.total_amount != normalized_amount
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "ap bill idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx,
                    "Purchase.ApBill.Create",
                    AP_BILL_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            self._active_supplier(supplier_id)
            bill = ApBill(
                id=bill_id,
                tenant_id=self._tenant_id(ctx),
                supplier_id=supplier_id,
                code=normalized_code,
                currency=normalized_currency,
                total_amount=normalized_amount,
                idempotency_key=idempotency_key,
                status=ApBillStatus.DRAFT,
                created_at=datetime.now(timezone.utc),
            )
            self._repository.add_ap_bill(bill)
            audit = self._write_result(
                ctx,
                "Purchase.ApBill.Create",
                AP_BILL_RESOURCE,
                bill.id,
                "ok",
            )
            return KernelResult.success(bill, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "ap bill create conflict"
            )

    def get_ap_bill(
        self,
        ctx: ExecutionContext,
        *,
        bill_id: UUID,
    ) -> KernelResult[ApBill]:
        try:
            denied = self._authorize(ctx, "read", AP_BILL_RESOURCE, bill_id)
            if denied is not None:
                return denied
            bill = self._repository.get_ap_bill(bill_id)
            if bill is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "ap bill not found"
                )
            return KernelResult.success(bill)
        except KernelError as err:
            return KernelResult.from_error(err)

    def post_ap_bill(
        self,
        ctx: ExecutionContext,
        *,
        bill_id: UUID,
        idempotency_key: UUID | None = None,
        human_confirm: bool = True,
    ) -> KernelResult[ApBill]:
        try:
            self._write_intent(ctx, "Purchase.ApBill.Post", AP_BILL_RESOURCE, bill_id)
            denied = self._authorize(ctx, "post", AP_BILL_RESOURCE, bill_id)
            if denied is not None:
                return self._write_denied(
                    ctx, "Purchase.ApBill.Post", AP_BILL_RESOURCE, bill_id, denied
                )
            if not human_confirm:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required",
                )
            bill = self._draft_ap_bill(bill_id)
            if bill.total_amount <= 0:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "ap bill total_amount must be positive before posting",
                )
            posted = replace(
                bill, status=ApBillStatus.POSTED, version=bill.version + 1
            )
            self._repository.save_ap_bill(posted, expected_version=bill.version)
            audit = self._write_result(
                ctx, "Purchase.ApBill.Post", AP_BILL_RESOURCE, bill_id, "ok"
            )
            return KernelResult.success(posted, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "ap bill post conflict"
            )

    def create_ap_write_off(
        self,
        ctx: ExecutionContext,
        *,
        ap_bill_id: UUID,
        amount: Decimal,
        idempotency_key: UUID,
        human_confirm: bool = True,
        reason: str | None = None,
    ) -> KernelResult[ApWriteOff]:
        write_off_id = uuid4()
        try:
            self._write_intent(
                ctx, "Purchase.ApWriteOff.Create", AP_WRITE_OFF_RESOURCE, write_off_id
            )
            denied = self._authorize(
                ctx, "create", AP_WRITE_OFF_RESOURCE, ap_bill_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx, "Purchase.ApWriteOff.Create", AP_WRITE_OFF_RESOURCE,
                    write_off_id, denied,
                )
            if not human_confirm:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required for AP write-off",
                )
            normalized_amount = self._amount(amount)
            if normalized_amount <= 0:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "write-off amount must be positive",
                )
            normalized_reason = (
                None
                if reason is None
                else self._required(reason, "reason", 500)
            )
            existing = self._repository.get_ap_write_off_by_idempotency_key(
                idempotency_key
            )
            if existing is not None:
                if (
                    existing.ap_bill_id != ap_bill_id
                    or existing.amount != normalized_amount
                    or existing.reason != normalized_reason
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "write-off idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx, "Purchase.ApWriteOff.Create", AP_WRITE_OFF_RESOURCE,
                    existing.id, "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            bill = self._open_ap_bill(ap_bill_id)
            remaining = self._ap_bill_remaining(bill)
            if normalized_amount > remaining:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "write-off amount exceeds AP bill remaining amount",
                )
            write_off = ApWriteOff(
                id=write_off_id,
                tenant_id=self._tenant_id(ctx),
                ap_bill_id=ap_bill_id,
                amount=normalized_amount,
                currency=bill.currency,
                idempotency_key=idempotency_key,
                reason=normalized_reason,
                created_at=datetime.now(timezone.utc),
            )
            self._repository.add_ap_write_off(write_off)
            self._repository.save_ap_bill(
                replace(
                    bill,
                    write_off_amount=bill.write_off_amount + normalized_amount,
                    version=bill.version + 1,
                ),
                expected_version=bill.version,
            )
            audit = self._write_result(
                ctx, "Purchase.ApWriteOff.Create", AP_WRITE_OFF_RESOURCE,
                write_off.id, "ok",
            )
            return KernelResult.success(write_off, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "AP write-off create conflict"
            )

    def close_ap_bill(
        self, ctx: ExecutionContext, *, bill_id: UUID, human_confirm: bool = True
    ) -> KernelResult[ApBill]:
        try:
            self._write_intent(
                ctx, "Purchase.ApBill.Close", AP_WRITE_OFF_RESOURCE, bill_id
            )
            denied = self._authorize(ctx, "update", AP_WRITE_OFF_RESOURCE, bill_id)
            if denied is not None:
                return self._write_denied(
                    ctx, "Purchase.ApBill.Close", AP_WRITE_OFF_RESOURCE,
                    bill_id, denied,
                )
            if not human_confirm:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required for AP bill close",
                )
            bill = self._require_ap_bill(bill_id)
            if bill.status == ApBillStatus.CLOSED:
                return KernelResult.success(bill)
            if bill.status not in (
                ApBillStatus.POSTED,
                ApBillStatus.PARTIALLY_PAID,
                ApBillStatus.PAID,
            ):
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "ap bill is not posted, partially paid, or paid",
                )
            if self._ap_bill_remaining(bill) != Decimal("0.00"):
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "AP bill cannot close until remaining amount is zero",
                )
            closed = replace(
                bill, status=ApBillStatus.CLOSED, version=bill.version + 1
            )
            self._repository.save_ap_bill(closed, expected_version=bill.version)
            audit = self._write_result(
                ctx, "Purchase.ApBill.Close", AP_WRITE_OFF_RESOURCE, bill_id, "ok"
            )
            return KernelResult.success(closed, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "AP bill close conflict"
            )

    def create_ap_payment(
        self,
        ctx: ExecutionContext,
        *,
        supplier_id: UUID,
        amount: Decimal,
        currency: str,
        idempotency_key: UUID,
        functional_currency: str | None = None,
        fx_rate: Decimal | None = None,
        functional_amount: Decimal | None = None,
    ) -> KernelResult[ApPayment]:
        payment_id = uuid4()
        try:
            self._write_intent(
                ctx, "Purchase.ApPayment.Create", AP_PAYMENT_RESOURCE, payment_id
            )
            denied = self._authorize(
                ctx, "create", AP_PAYMENT_RESOURCE, supplier_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Purchase.ApPayment.Create",
                    AP_PAYMENT_RESOURCE,
                    payment_id,
                    denied,
                )
            normalized_amount = self._amount(amount)
            if normalized_amount <= 0:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "ap payment amount must be positive",
                )
            normalized_currency = self._currency(currency)
            (
                normalized_functional_currency,
                normalized_fx_rate,
                normalized_functional_amount,
            ) = self._cash_event_fx(
                currency=normalized_currency,
                amount=normalized_amount,
                functional_currency=functional_currency,
                fx_rate=fx_rate,
                functional_amount=functional_amount,
            )
            existing = self._repository.get_ap_payment_by_idempotency_key(
                idempotency_key
            )
            if existing is not None:
                if (
                    existing.supplier_id != supplier_id
                    or existing.amount != normalized_amount
                    or existing.currency != normalized_currency
                    or existing.functional_currency != normalized_functional_currency
                    or existing.fx_rate != normalized_fx_rate
                    or existing.functional_amount != normalized_functional_amount
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "ap payment idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx,
                    "Purchase.ApPayment.Create",
                    AP_PAYMENT_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            self._active_supplier(supplier_id)
            payment = ApPayment(
                id=payment_id,
                tenant_id=self._tenant_id(ctx),
                supplier_id=supplier_id,
                amount=normalized_amount,
                currency=normalized_currency,
                functional_currency=normalized_functional_currency,
                fx_rate=normalized_fx_rate,
                functional_amount=normalized_functional_amount,
                idempotency_key=idempotency_key,
                status=ApPaymentStatus.DRAFT,
                created_at=datetime.now(timezone.utc),
            )
            self._repository.add_ap_payment(payment)
            audit = self._write_result(
                ctx, "Purchase.ApPayment.Create", AP_PAYMENT_RESOURCE, payment.id, "ok"
            )
            return KernelResult.success(payment, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "ap payment create conflict"
            )

    def get_ap_payment(
        self, ctx: ExecutionContext, *, payment_id: UUID
    ) -> KernelResult[ApPayment]:
        try:
            denied = self._authorize(ctx, "read", AP_PAYMENT_RESOURCE, payment_id)
            if denied is not None:
                return denied
            payment = self._repository.get_ap_payment(payment_id)
            if payment is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "ap payment not found"
                )
            return KernelResult.success(payment)
        except KernelError as err:
            return KernelResult.from_error(err)

    def apply_ap_payment_to_bill(
        self,
        ctx: ExecutionContext,
        *,
        payment_id: UUID,
        bill_id: UUID,
        apply_key: UUID,
    ) -> KernelResult[ApPayment]:
        try:
            self._write_intent(
                ctx, "Purchase.ApPayment.Apply", AP_PAYMENT_RESOURCE, payment_id
            )
            denied = self._authorize(ctx, "apply", AP_PAYMENT_RESOURCE, payment_id)
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Purchase.ApPayment.Apply",
                    AP_PAYMENT_RESOURCE,
                    payment_id,
                    denied,
                )
            existing = self._repository.get_ap_payment_by_apply_key(apply_key)
            if existing is not None:
                if existing.id != payment_id or existing.ap_bill_id != bill_id:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "ap payment apply key was used for another request",
                    )
                audit = self._write_result(
                    ctx,
                    "Purchase.ApPayment.Apply",
                    AP_PAYMENT_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            payment = self._repository.get_ap_payment(payment_id)
            if payment is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "ap payment not found"
                )
            if payment.status != ApPaymentStatus.DRAFT:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT, "ap payment is not draft"
                )
            bill = self._require_ap_bill(bill_id)
            if bill.status not in (
                ApBillStatus.POSTED,
                ApBillStatus.PARTIALLY_PAID,
            ):
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "ap bill is not posted or partially paid",
                )
            if payment.supplier_id != bill.supplier_id:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "ap payment supplier does not match ap bill supplier",
                )
            if payment.currency != bill.currency:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "ap payment currency does not match ap bill currency",
                )
            remaining = self._ap_bill_remaining(bill)
            if payment.amount > remaining:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "ap payment amount exceeds ap bill remaining balance",
                )
            now = datetime.now(timezone.utc)
            applied = replace(
                payment,
                status=ApPaymentStatus.APPLIED,
                ap_bill_id=bill.id,
                ap_bill_version=bill.version,
                apply_key=apply_key,
                applied_at=now,
                version=payment.version + 1,
            )
            updated_bill = replace(
                bill,
                paid_amount=bill.paid_amount + payment.amount,
                status=(
                    ApBillStatus.PAID
                    if payment.amount == remaining
                    else ApBillStatus.PARTIALLY_PAID
                ),
                version=bill.version + 1,
            )
            self._repository.save_ap_payment(
                applied, expected_version=payment.version
            )
            self._repository.save_ap_bill(updated_bill, expected_version=bill.version)
            audit = self._write_result(
                ctx, "Purchase.ApPayment.Apply", AP_PAYMENT_RESOURCE, payment_id, "ok"
            )
            return KernelResult.success(applied, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "ap payment apply conflict"
            )

    def create_ap_bill_line(
        self,
        ctx: ExecutionContext,
        *,
        ap_bill_id: UUID,
        description: str,
        quantity: Decimal,
        unit_price: Decimal,
    ) -> KernelResult[ApBillLine]:
        line_id = uuid4()
        try:
            self._write_intent(
                ctx, "Purchase.ApBillLine.Create", AP_BILL_LINE_RESOURCE, line_id
            )
            denied = self._authorize(
                ctx, "create", AP_BILL_LINE_RESOURCE, ap_bill_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Purchase.ApBillLine.Create",
                    AP_BILL_LINE_RESOURCE,
                    line_id,
                    denied,
                )
            bill = self._draft_ap_bill(ap_bill_id)
            normalized_quantity, normalized_price, amount = self._line_values(
                quantity, unit_price
            )
            now = datetime.now(timezone.utc)
            line = ApBillLine(
                id=line_id,
                tenant_id=self._tenant_id(ctx),
                ap_bill_id=ap_bill_id,
                line_number=self._repository.next_ap_bill_line_number(ap_bill_id),
                description=self._required(description, "description", 500),
                quantity=normalized_quantity,
                unit_price=normalized_price,
                amount=amount,
                status=ApBillLineStatus.ACTIVE,
                created_at=now,
                updated_at=now,
            )
            self._repository.add_ap_bill_line(line)
            self._recompute_bill_total(bill)
            audit = self._write_result(
                ctx,
                "Purchase.ApBillLine.Create",
                AP_BILL_LINE_RESOURCE,
                line.id,
                "ok",
            )
            return KernelResult.success(line, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "ap bill line persistence conflict"
            )

    def get_ap_bill_line(
        self,
        ctx: ExecutionContext,
        *,
        ap_bill_id: UUID,
        line_id: UUID,
    ) -> KernelResult[ApBillLine]:
        try:
            denied = self._authorize(
                ctx, "read", AP_BILL_LINE_RESOURCE, line_id
            )
            if denied is not None:
                return denied
            self._require_ap_bill(ap_bill_id)
            line = self._repository.get_ap_bill_line(ap_bill_id, line_id)
            if line is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "ap bill line not found"
                )
            return KernelResult.success(line)
        except KernelError as err:
            return KernelResult.from_error(err)

    def list_ap_bill_lines(
        self,
        ctx: ExecutionContext,
        *,
        ap_bill_id: UUID,
    ) -> KernelResult[list[ApBillLine]]:
        try:
            denied = self._authorize(
                ctx, "read", AP_BILL_LINE_RESOURCE, ap_bill_id
            )
            if denied is not None:
                return denied
            self._require_ap_bill(ap_bill_id)
            return KernelResult.success(
                self._repository.list_ap_bill_lines(ap_bill_id)
            )
        except KernelError as err:
            return KernelResult.from_error(err)

    def archive_ap_bill_line(
        self,
        ctx: ExecutionContext,
        *,
        ap_bill_id: UUID,
        line_id: UUID,
        reason: str,
        expected_version: int,
    ) -> KernelResult[ApBillLine]:
        try:
            self._write_intent(
                ctx,
                "Purchase.ApBillLine.Archive",
                AP_BILL_LINE_RESOURCE,
                line_id,
            )
            denied = self._authorize(
                ctx, "archive", AP_BILL_LINE_RESOURCE, line_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Purchase.ApBillLine.Archive",
                    AP_BILL_LINE_RESOURCE,
                    line_id,
                    denied,
                )
            self._required(reason, "reason", 500)
            bill = self._draft_ap_bill(ap_bill_id)
            line = self._active_ap_bill_line(ap_bill_id, line_id)
            self._expected_version(line.version, expected_version)
            now = datetime.now(timezone.utc)
            archived = replace(
                line,
                status=ApBillLineStatus.ARCHIVED,
                archived_at=now,
                updated_at=now,
                version=line.version + 1,
            )
            self._repository.save_ap_bill_line(
                archived, expected_version=expected_version
            )
            self._recompute_bill_total(bill)
            audit = self._write_result(
                ctx,
                "Purchase.ApBillLine.Archive",
                AP_BILL_LINE_RESOURCE,
                line_id,
                "ok",
            )
            return KernelResult.success(archived, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "ap bill line version conflict"
            )

    def create_purchase_order(
        self,
        ctx: ExecutionContext,
        *,
        supplier_id: UUID,
        code: str,
        currency: str,
        idempotency_key: UUID,
        notes: str | None = None,
    ) -> KernelResult[PurchaseOrder]:
        order_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "Purchase.PurchaseOrder.Create",
                PURCHASE_ORDER_RESOURCE,
                order_id,
            )
            denied = self._authorize(
                ctx, "create", PURCHASE_ORDER_RESOURCE, supplier_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Purchase.PurchaseOrder.Create",
                    PURCHASE_ORDER_RESOURCE,
                    order_id,
                    denied,
                )
            normalized_code = self._required(code, "code", 64)
            normalized_currency = self._currency(currency)
            normalized_notes = None
            if notes is not None:
                stripped = notes.strip()
                if stripped:
                    normalized_notes = self._required(stripped, "notes", 2000)
            existing = self._repository.get_purchase_order_by_idempotency_key(
                idempotency_key
            )
            if existing is not None:
                if (
                    existing.supplier_id != supplier_id
                    or existing.code != normalized_code
                    or existing.currency != normalized_currency
                    or existing.notes != normalized_notes
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "purchase order idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx,
                    "Purchase.PurchaseOrder.Create",
                    PURCHASE_ORDER_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            self._active_supplier(supplier_id)
            now = datetime.now(timezone.utc)
            order = PurchaseOrder(
                id=order_id,
                tenant_id=self._tenant_id(ctx),
                supplier_id=supplier_id,
                code=normalized_code,
                currency=normalized_currency,
                idempotency_key=idempotency_key,
                status=PurchaseOrderStatus.DRAFT,
                notes=normalized_notes,
                created_at=now,
                updated_at=now,
            )
            self._repository.add_purchase_order(order)
            audit = self._write_result(
                ctx,
                "Purchase.PurchaseOrder.Create",
                PURCHASE_ORDER_RESOURCE,
                order.id,
                "ok",
            )
            return KernelResult.success(order, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "purchase order create conflict"
            )

    def get_purchase_order(
        self,
        ctx: ExecutionContext,
        *,
        purchase_order_id: UUID,
    ) -> KernelResult[PurchaseOrder]:
        try:
            denied = self._authorize(
                ctx, "read", PURCHASE_ORDER_RESOURCE, purchase_order_id
            )
            if denied is not None:
                return denied
            order = self._repository.get_purchase_order(purchase_order_id)
            if order is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "purchase order not found"
                )
            return KernelResult.success(order)
        except KernelError as err:
            return KernelResult.from_error(err)

    def archive_purchase_order(
        self,
        ctx: ExecutionContext,
        *,
        purchase_order_id: UUID,
        reason: str,
        expected_version: int,
    ) -> KernelResult[PurchaseOrder]:
        try:
            self._write_intent(
                ctx,
                "Purchase.PurchaseOrder.Archive",
                PURCHASE_ORDER_RESOURCE,
                purchase_order_id,
            )
            denied = self._authorize(
                ctx, "archive", PURCHASE_ORDER_RESOURCE, purchase_order_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Purchase.PurchaseOrder.Archive",
                    PURCHASE_ORDER_RESOURCE,
                    purchase_order_id,
                    denied,
                )
            self._required(reason, "reason", 500)
            order = self._draft_purchase_order(purchase_order_id)
            self._expected_version(order.version, expected_version)
            now = datetime.now(timezone.utc)
            archived = replace(
                order,
                status=PurchaseOrderStatus.ARCHIVED,
                archived_at=now,
                updated_at=now,
                version=order.version + 1,
            )
            self._repository.save_purchase_order(
                archived, expected_version=expected_version
            )
            audit = self._write_result(
                ctx,
                "Purchase.PurchaseOrder.Archive",
                PURCHASE_ORDER_RESOURCE,
                purchase_order_id,
                "ok",
            )
            return KernelResult.success(archived, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "purchase order version conflict"
            )

    def _active_supplier(self, supplier_id: UUID) -> Supplier:
        supplier = self._repository.get_supplier(supplier_id)
        if supplier is None:
            raise KernelError(ErrorCode.COMMON_NOT_FOUND, "supplier not found")
        if supplier.status != SupplierStatus.ACTIVE:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT, "supplier is archived"
            )
        return supplier

    def create_purchase_order_line(
        self,
        ctx: ExecutionContext,
        *,
        purchase_order_id: UUID,
        inventory_item_id: UUID,
        quantity: Decimal,
        unit_price: Decimal | None = None,
    ) -> KernelResult[PurchaseOrderLine]:
        line_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "Purchase.PurchaseOrderLine.Create",
                PURCHASE_ORDER_LINE_RESOURCE,
                line_id,
            )
            denied = self._authorize(
                ctx, "create", PURCHASE_ORDER_LINE_RESOURCE, purchase_order_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Purchase.PurchaseOrderLine.Create",
                    PURCHASE_ORDER_LINE_RESOURCE,
                    line_id,
                    denied,
                )
            self._draft_purchase_order(purchase_order_id)
            normalized_quantity = self._quantity(quantity)
            normalized_price = None
            if unit_price is not None:
                normalized_price = self._amount(unit_price)
            now = datetime.now(timezone.utc)
            line = PurchaseOrderLine(
                id=line_id,
                tenant_id=self._tenant_id(ctx),
                purchase_order_id=purchase_order_id,
                line_number=self._repository.next_purchase_order_line_number(
                    purchase_order_id
                ),
                inventory_item_id=inventory_item_id,
                quantity=normalized_quantity,
                unit_price=normalized_price,
                status=PurchaseOrderLineStatus.ACTIVE,
                created_at=now,
                updated_at=now,
            )
            self._repository.add_purchase_order_line(line)
            audit = self._write_result(
                ctx,
                "Purchase.PurchaseOrderLine.Create",
                PURCHASE_ORDER_LINE_RESOURCE,
                line.id,
                "ok",
            )
            return KernelResult.success(line, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "purchase order line persistence conflict",
            )

    def create_goods_receipt(
        self,
        ctx: ExecutionContext,
        *,
        purchase_order_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
    ) -> KernelResult[GoodsReceipt]:
        receipt_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "Purchase.GoodsReceipt.Create",
                GOODS_RECEIPT_RESOURCE,
                receipt_id,
            )
            denied = self._authorize(
                ctx, "create", GOODS_RECEIPT_RESOURCE, purchase_order_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Purchase.GoodsReceipt.Create",
                    GOODS_RECEIPT_RESOURCE,
                    receipt_id,
                    denied,
                )
            if not human_confirm:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required",
                )
            if self._inventory_receipt_port is None:
                raise KernelError(
                    ErrorCode.COMMON_INTERNAL,
                    "inventory receipt port is not configured",
                )
            existing = self._repository.get_goods_receipt_by_idempotency_key(
                idempotency_key
            )
            if existing is not None:
                if existing.purchase_order_id != purchase_order_id:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "goods receipt idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx,
                    "Purchase.GoodsReceipt.Create",
                    GOODS_RECEIPT_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            by_po = self._repository.get_goods_receipt_by_po(purchase_order_id)
            if by_po is not None:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "purchase order already has a goods receipt",
                )
            order = self._draft_purchase_order(purchase_order_id)
            lines = [
                line
                for line in self._repository.list_purchase_order_lines(
                    purchase_order_id
                )
                if line.status == PurchaseOrderLineStatus.ACTIVE
            ]
            if not lines:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "purchase order has no open lines to receive",
                )
            line_quantities = tuple(
                (line.inventory_item_id, line.quantity) for line in lines
            )
            now = datetime.now(timezone.utc)
            receipt = GoodsReceipt(
                id=receipt_id,
                tenant_id=self._tenant_id(ctx),
                purchase_order_id=purchase_order_id,
                code=f"GRN-{order.code}",
                status=GoodsReceiptStatus.RECEIVED,
                idempotency_key=idempotency_key,
                received_at=now,
                created_at=now,
            )
            try:
                self._inventory_receipt_port.atomic_po_receive(
                    purchase_order_id=purchase_order_id,
                    goods_receipt_id=receipt.id,
                    line_quantities=line_quantities,
                    idempotency_key=idempotency_key,
                    received_at=now,
                )
            except ValueError as err:
                return KernelResult.failure(
                    ErrorCode.COMMON_CONFLICT,
                    str(err) or "inventory receive failed",
                )
            self._repository.add_goods_receipt(receipt)
            received_order = replace(
                order,
                status=PurchaseOrderStatus.RECEIVED,
                updated_at=now,
                version=order.version + 1,
            )
            self._repository.save_purchase_order(
                received_order, expected_version=order.version
            )
            audit = self._write_result(
                ctx,
                "Purchase.GoodsReceipt.Create",
                GOODS_RECEIPT_RESOURCE,
                receipt.id,
                "ok",
            )
            return KernelResult.success(receipt, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "goods receipt create conflict"
            )

    def create_three_way_match(
        self,
        ctx: ExecutionContext,
        *,
        purchase_order_id: UUID,
        goods_receipt_id: UUID,
        ap_bill_id: UUID,
        idempotency_key: UUID,
    ) -> KernelResult[ThreeWayMatch]:
        match_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "Purchase.ThreeWayMatch.Create",
                THREE_WAY_MATCH_RESOURCE,
                match_id,
            )
            denied = self._authorize(
                ctx, "create", THREE_WAY_MATCH_RESOURCE, purchase_order_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Purchase.ThreeWayMatch.Create",
                    THREE_WAY_MATCH_RESOURCE,
                    match_id,
                    denied,
                )
            existing = self._repository.get_three_way_match_by_idempotency_key(
                idempotency_key
            )
            if existing is not None:
                if (
                    existing.purchase_order_id != purchase_order_id
                    or existing.goods_receipt_id != goods_receipt_id
                    or existing.ap_bill_id != ap_bill_id
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "three-way match idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx,
                    "Purchase.ThreeWayMatch.Create",
                    THREE_WAY_MATCH_RESOURCE,
                    existing.id,
                    "ok",
                )
                if existing.status == ThreeWayMatchStatus.MISMATCH:
                    return KernelResult.failure(
                        ErrorCode.COMMON_CONFLICT,
                        "three-way match mismatch persisted",
                        details={
                            "three_way_match_id": str(existing.id),
                            "status": existing.status.value,
                        },
                        audit_id=audit.id,
                    )
                return KernelResult.success(existing, audit_id=audit.id)
            by_po = self._repository.get_three_way_match_by_po(purchase_order_id)
            if by_po is not None:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "purchase order already has a three-way match",
                )
            order = self._repository.get_purchase_order(purchase_order_id)
            if order is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "purchase order not found"
                )
            receipt = self._repository.get_goods_receipt(goods_receipt_id)
            if receipt is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "goods receipt not found"
                )
            if receipt.purchase_order_id != purchase_order_id:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "goods receipt does not belong to purchase order",
                )
            bill = self._draft_ap_bill(ap_bill_id)
            if bill.supplier_id != order.supplier_id:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "ap bill supplier does not match purchase order supplier",
                )
            bill_lines = [
                line
                for line in self._repository.list_ap_bill_lines(ap_bill_id)
                if line.status == ApBillLineStatus.ACTIVE
            ]
            if not bill_lines:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "ap bill has no active lines",
                )
            po_lines = [
                line
                for line in self._repository.list_purchase_order_lines(
                    purchase_order_id
                )
                if line.status == PurchaseOrderLineStatus.ACTIVE
            ]
            if not po_lines:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "purchase order has no active lines",
                )
            policy = self._three_way_match_tolerance_or_default(ctx)
            match_status = self._evaluate_three_way_amount(
                po_lines, bill, bill_lines, policy=policy
            )
            match = ThreeWayMatch(
                id=match_id,
                tenant_id=self._tenant_id(ctx),
                purchase_order_id=purchase_order_id,
                goods_receipt_id=goods_receipt_id,
                ap_bill_id=ap_bill_id,
                status=match_status,
                idempotency_key=idempotency_key,
                created_at=datetime.now(timezone.utc),
            )
            self._repository.add_three_way_match(match)
            audit = self._write_result(
                ctx,
                "Purchase.ThreeWayMatch.Create",
                THREE_WAY_MATCH_RESOURCE,
                match.id,
                "ok" if match_status == ThreeWayMatchStatus.MATCHED else "mismatch",
            )
            if match_status == ThreeWayMatchStatus.MISMATCH:
                return KernelResult.failure(
                    ErrorCode.COMMON_CONFLICT,
                    "three-way match mismatch: bill totals do not agree with purchase order",
                    details={
                        "three_way_match_id": str(match.id),
                        "status": match.status.value,
                    },
                    audit_id=audit.id,
                )
            return KernelResult.success(match, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "three-way match create conflict"
            )

    def get_three_way_match_tolerance_policy(
        self, ctx: ExecutionContext
    ) -> KernelResult[TenantThreeWayMatchTolerancePolicy]:
        try:
            denied = self._authorize(
                ctx, "read", THREE_WAY_MATCH_TOLERANCE_POLICY_RESOURCE
            )
            if denied is not None:
                return denied
            return KernelResult.success(
                self._three_way_match_tolerance_or_default(ctx)
            )
        except KernelError as err:
            return KernelResult.from_error(err)

    def set_three_way_match_tolerance_policy(
        self,
        ctx: ExecutionContext,
        *,
        amount_tolerance_abs: Decimal | None,
        amount_tolerance_pct: Decimal | None,
        expected_version: int,
    ) -> KernelResult[TenantThreeWayMatchTolerancePolicy]:
        try:
            tenant_id = self._tenant_id(ctx)
            self._write_intent(
                ctx,
                "Purchase.Policy.ThreeWayMatchTolerance.Set",
                THREE_WAY_MATCH_TOLERANCE_POLICY_RESOURCE,
                tenant_id,
            )
            denied = self._authorize(
                ctx, "update", THREE_WAY_MATCH_TOLERANCE_POLICY_RESOURCE
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Purchase.Policy.ThreeWayMatchTolerance.Set",
                    THREE_WAY_MATCH_TOLERANCE_POLICY_RESOURCE,
                    tenant_id,
                    denied,
                )
            abs_tol = self._tolerance_amount(
                amount_tolerance_abs, field="amount_tolerance_abs"
            )
            pct_tol = self._tolerance_pct(
                amount_tolerance_pct, field="amount_tolerance_pct"
            )
            current = self._repository.get_three_way_match_tolerance_policy()
            if current is None:
                if expected_version != 0:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "three-way match tolerance policy version conflict",
                    )
                version = 1
            else:
                if current.version != expected_version:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "three-way match tolerance policy version conflict",
                    )
                version = current.version + 1
            policy = TenantThreeWayMatchTolerancePolicy(
                tenant_id=tenant_id,
                amount_tolerance_abs=abs_tol,
                amount_tolerance_pct=pct_tol,
                updated_at=datetime.now(timezone.utc),
                version=version,
            )
            self._repository.save_three_way_match_tolerance_policy(
                policy, expected_version=expected_version
            )
            audit = self._write_result(
                ctx,
                "Purchase.Policy.ThreeWayMatchTolerance.Set",
                THREE_WAY_MATCH_TOLERANCE_POLICY_RESOURCE,
                tenant_id,
                "ok",
            )
            return KernelResult.success(policy, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "three-way match tolerance policy version conflict",
            )

    def _draft_purchase_order(self, order_id: UUID) -> PurchaseOrder:
        order = self._repository.get_purchase_order(order_id)
        if order is None:
            raise KernelError(
                ErrorCode.COMMON_NOT_FOUND, "purchase order not found"
            )
        if order.status != PurchaseOrderStatus.DRAFT:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT, "purchase order is not draft"
            )
        return order

    def _evaluate_three_way_amount(
        self,
        po_lines: list[PurchaseOrderLine],
        bill: ApBill,
        bill_lines: list[ApBillLine],
        *,
        policy: TenantThreeWayMatchTolerancePolicy,
    ) -> ThreeWayMatchStatus:
        prices_present = all(line.unit_price is not None for line in po_lines)
        if prices_present:
            expected = Decimal("0.00")
            for line in po_lines:
                assert line.unit_price is not None
                expected += (line.quantity * line.unit_price).quantize(
                    AMOUNT_QUANTUM, rounding=ROUND_HALF_UP
                )
            expected = expected.quantize(AMOUNT_QUANTUM, rounding=ROUND_HALF_UP)
            if self._within_amount_tolerance(
                expected, bill.total_amount, policy=policy
            ):
                return ThreeWayMatchStatus.MATCHED
            return ThreeWayMatchStatus.MISMATCH
        po_qty = sum((line.quantity for line in po_lines), Decimal("0"))
        bill_qty = sum((line.quantity for line in bill_lines), Decimal("0"))
        if po_qty == bill_qty:
            return ThreeWayMatchStatus.MATCHED
        return ThreeWayMatchStatus.MISMATCH

    @staticmethod
    def _within_amount_tolerance(
        expected: Decimal,
        actual: Decimal,
        *,
        policy: TenantThreeWayMatchTolerancePolicy,
    ) -> bool:
        diff = abs(expected - actual)
        abs_tol = policy.amount_tolerance_abs or Decimal("0.00")
        pct_tol = policy.amount_tolerance_pct or Decimal("0")
        pct_allowed = (expected * pct_tol / Decimal("100")).quantize(
            AMOUNT_QUANTUM, rounding=ROUND_HALF_UP
        )
        allowed = abs_tol if abs_tol >= pct_allowed else pct_allowed
        return diff <= allowed

    def _three_way_match_tolerance_or_default(
        self, ctx: ExecutionContext
    ) -> TenantThreeWayMatchTolerancePolicy:
        return self._repository.get_three_way_match_tolerance_policy() or (
            TenantThreeWayMatchTolerancePolicy(
                tenant_id=self._tenant_id(ctx),
                amount_tolerance_abs=Decimal("0.00"),
                amount_tolerance_pct=Decimal("0"),
                updated_at=datetime.now(timezone.utc),
                version=0,
            )
        )

    @staticmethod
    def _tolerance_amount(
        value: Decimal | None, *, field: str
    ) -> Decimal:
        if value is None:
            return Decimal("0.00")
        try:
            normalized = Decimal(str(value)).quantize(
                AMOUNT_QUANTUM, rounding=ROUND_HALF_UP
            )
        except (InvalidOperation, ValueError):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                f"{field} must be a finite decimal",
            ) from None
        if (
            not normalized.is_finite()
            or normalized < 0
            or normalized > MAX_AMOUNT
        ):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                f"{field} is outside the supported range",
            )
        return normalized

    @staticmethod
    def _tolerance_pct(value: Decimal | None, *, field: str) -> Decimal:
        if value is None:
            return Decimal("0")
        try:
            normalized = Decimal(str(value)).quantize(
                PCT_QUANTUM, rounding=ROUND_HALF_UP
            )
        except (InvalidOperation, ValueError):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                f"{field} must be a finite decimal",
            ) from None
        if (
            not normalized.is_finite()
            or normalized < 0
            or normalized > MAX_TOLERANCE_PCT
        ):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                f"{field} is outside the supported range",
            )
        return normalized

    @staticmethod
    def _quantity(quantity: Decimal) -> Decimal:
        try:
            normalized = Decimal(str(quantity)).quantize(
                QTY_QUANTUM, rounding=ROUND_HALF_UP
            )
        except (InvalidOperation, ValueError):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "quantity must be a finite decimal",
            ) from None
        if (
            not normalized.is_finite()
            or normalized <= 0
            or normalized > MAX_QUANTITY
        ):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "quantity is outside the supported range",
            )
        return normalized

    def _require_ap_bill(self, bill_id: UUID) -> ApBill:
        bill = self._repository.get_ap_bill(bill_id)
        if bill is None:
            raise KernelError(ErrorCode.COMMON_NOT_FOUND, "ap bill not found")
        return bill

    def _require_ap_bill_supplier(self, supplier_id: UUID) -> Supplier:
        supplier = self._repository.get_supplier(supplier_id)
        if supplier is None:
            raise KernelError(ErrorCode.COMMON_NOT_FOUND, "supplier not found")
        return supplier

    def _draft_ap_bill(self, bill_id: UUID) -> ApBill:
        bill = self._require_ap_bill(bill_id)
        if bill.status != ApBillStatus.DRAFT:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT, "ap bill is not draft"
            )
        return bill

    def _open_ap_bill(self, bill_id: UUID) -> ApBill:
        bill = self._require_ap_bill(bill_id)
        if bill.status not in (
            ApBillStatus.POSTED,
            ApBillStatus.PARTIALLY_PAID,
        ):
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "ap bill is not posted or partially paid",
            )
        return bill

    @staticmethod
    def _ap_bill_remaining(bill: ApBill) -> Decimal:
        return bill.total_amount - bill.paid_amount - bill.write_off_amount

    def _active_ap_bill_line(
        self, ap_bill_id: UUID, line_id: UUID
    ) -> ApBillLine:
        line = self._repository.get_ap_bill_line(ap_bill_id, line_id)
        if line is None:
            raise KernelError(
                ErrorCode.COMMON_NOT_FOUND, "ap bill line not found"
            )
        if line.status != ApBillLineStatus.ACTIVE:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT, "ap bill line is archived"
            )
        return line

    def _recompute_bill_total(self, bill: ApBill) -> None:
        total = Decimal("0.00")
        for line in self._repository.list_ap_bill_lines(bill.id):
            if line.status == ApBillLineStatus.ACTIVE:
                total += line.amount
        total = total.quantize(AMOUNT_QUANTUM, rounding=ROUND_HALF_UP)
        updated = replace(
            bill,
            total_amount=total,
            version=bill.version + 1,
        )
        self._repository.save_ap_bill(updated, expected_version=bill.version)

    def _authorize(
        self,
        ctx: ExecutionContext,
        action: str,
        resource_type: str,
        resource_id: UUID | None = None,
    ) -> KernelResult | None:
        tenant_id = self._tenant_id(ctx)
        result = self._permission.evaluate(
            ctx,
            principal_subject_id=ctx.subject_id,
            action=action,
            resource=Resource(
                tenant_id=tenant_id,
                resource_type=resource_type,
                resource_id=resource_id,
            ),
        )
        if not result.ok:
            return result
        decision = result.data
        if decision is None or decision.effect != PermissionEffect.ALLOW:
            return KernelResult.failure(
                ErrorCode.PERMISSION_DENIED,
                "Purchase action is denied by Permission",
                details={
                    "reason_code": (
                        decision.reason_code
                        if decision is not None
                        else "PERMISSION_DENIED"
                    )
                },
            )
        return None

    def _write_intent(
        self,
        ctx: ExecutionContext,
        action: str,
        resource_type: str,
        resource_id: UUID,
    ) -> None:
        self._tenant_id(ctx)
        self._audit.record(
            ctx,
            action=f"{action}.Intent",
            resource=f"{resource_type}:{resource_id}",
            result="attempted",
            details={},
        )

    def _write_result(
        self,
        ctx: ExecutionContext,
        action: str,
        resource_type: str,
        resource_id: UUID,
        result: str,
    ):
        return self._audit.record(
            ctx,
            action=action,
            resource=f"{resource_type}:{resource_id}",
            result=result,
            details={},
        )

    def _write_denied(
        self,
        ctx: ExecutionContext,
        action: str,
        resource_type: str,
        resource_id: UUID,
        denied: KernelResult,
    ) -> KernelResult:
        audit = self._write_result(
            ctx, action, resource_type, resource_id, "denied"
        )
        return KernelResult.failure(
            denied.error_code or ErrorCode.PERMISSION_DENIED,
            denied.error_message or "Purchase action is denied",
            details=denied.details,
            audit_id=audit.id,
        )

    @staticmethod
    def _tenant_id(ctx: ExecutionContext) -> UUID:
        require_context(ctx, tenant_data_plane=True)
        assert ctx.tenant_id is not None
        return ctx.tenant_id

    @staticmethod
    def _expected_version(current: int, expected: int) -> None:
        if expected < 1 or current != expected:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT, "resource version conflict"
            )

    @staticmethod
    def _required(value: str, field: str, max_length: int) -> str:
        normalized = value.strip()
        if not normalized or len(normalized) > max_length:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                f"{field} is required and must be at most {max_length} characters",
            )
        return normalized

    @staticmethod
    def _currency(currency: str) -> str:
        normalized = currency.strip().upper()
        if len(normalized) != 3 or not normalized.isalpha():
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "currency must be a 3-letter ISO code",
            )
        return normalized

    @staticmethod
    def _amount(amount: Decimal) -> Decimal:
        try:
            value = Decimal(amount)
        except (InvalidOperation, TypeError, ValueError) as err:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "amount is invalid",
            ) from err
        quantized = value.quantize(AMOUNT_QUANTUM, rounding=ROUND_HALF_UP)
        if quantized > MAX_AMOUNT:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "amount exceeds maximum",
            )
        return quantized

    @staticmethod
    def _fx_rate(rate: Decimal) -> Decimal:
        try:
            value = Decimal(rate)
        except (InvalidOperation, TypeError, ValueError) as err:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "fx rate is invalid"
            ) from err
        quantized = value.quantize(FX_RATE_QUANTUM, rounding=ROUND_HALF_UP)
        if quantized <= 0 or quantized > MAX_FX_RATE:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "fx rate is invalid"
            )
        return quantized

    def _cash_event_fx(
        self,
        *,
        currency: str,
        amount: Decimal,
        functional_currency: str | None,
        fx_rate: Decimal | None,
        functional_amount: Decimal | None,
    ) -> tuple[str, Decimal, Decimal]:
        normalized_functional_currency = self._currency(
            functional_currency or currency
        )
        if normalized_functional_currency == currency:
            normalized_fx_rate = (
                Decimal("1.00000000")
                if fx_rate is None
                else self._fx_rate(fx_rate)
            )
            if normalized_fx_rate != Decimal("1.00000000"):
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "same-currency cash event must use fx_rate 1",
                )
            expected_functional_amount = amount
        else:
            if fx_rate is None:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "fx_rate is required when currencies differ",
                )
            normalized_fx_rate = self._fx_rate(fx_rate)
            expected_functional_amount = self._amount(
                amount * normalized_fx_rate
            )
        normalized_functional_amount = (
            expected_functional_amount
            if functional_amount is None
            else self._amount(functional_amount)
        )
        if normalized_functional_amount != expected_functional_amount:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "functional_amount must equal amount multiplied by fx_rate",
            )
        return (
            normalized_functional_currency,
            normalized_fx_rate,
            normalized_functional_amount,
        )

    @staticmethod
    def _line_values(
        quantity: Decimal, unit_price: Decimal
    ) -> tuple[Decimal, Decimal, Decimal]:
        try:
            normalized_quantity = Decimal(str(quantity)).quantize(
                QTY_QUANTUM, rounding=ROUND_HALF_UP
            )
            normalized_price = Decimal(str(unit_price)).quantize(
                AMOUNT_QUANTUM, rounding=ROUND_HALF_UP
            )
            amount = (normalized_quantity * normalized_price).quantize(
                AMOUNT_QUANTUM, rounding=ROUND_HALF_UP
            )
        except (InvalidOperation, ValueError):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "ap bill line quantity and price must be finite decimals",
            ) from None
        if (
            not normalized_quantity.is_finite()
            or not normalized_price.is_finite()
            or not amount.is_finite()
            or normalized_quantity <= 0
            or normalized_price < 0
            or normalized_quantity > MAX_QUANTITY
            or normalized_price > MAX_AMOUNT
            or amount > MAX_AMOUNT
        ):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "ap bill line quantity or price is outside the supported range",
            )
        return normalized_quantity, normalized_price, amount
