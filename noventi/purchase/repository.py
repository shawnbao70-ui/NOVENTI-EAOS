"""Tenant-bound repository contract for Purchase AP1–AP5."""

from __future__ import annotations

from decimal import Decimal
from typing import Protocol
from uuid import UUID

from noventi.purchase.models import (
    ApBill,
    ApBillLine,
    ApPayment,
    ApWriteOff,
    GoodsReceipt,
    PurchaseOrder,
    PurchaseOrderLine,
    Supplier,
    TenantThreeWayMatchTolerancePolicy,
    ThreeWayMatch,
)


class PurchaseRepository(Protocol):
    def add_supplier(self, supplier: Supplier) -> None: ...

    def get_supplier(self, supplier_id: UUID) -> Supplier | None: ...

    def save_supplier(
        self, supplier: Supplier, *, expected_version: int
    ) -> None: ...

    def add_ap_bill(self, bill: ApBill) -> None: ...

    def get_ap_bill(self, bill_id: UUID) -> ApBill | None: ...

    def list_ap_bills_for_supplier(
        self, supplier_id: UUID
    ) -> list[ApBill]: ...

    def get_ap_bill_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ApBill | None: ...

    def save_ap_bill(self, bill: ApBill, *, expected_version: int) -> None: ...

    def add_ap_write_off(self, write_off: ApWriteOff) -> None: ...

    def get_ap_write_off_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ApWriteOff | None: ...

    def list_ap_write_offs(self, ap_bill_id: UUID) -> list[ApWriteOff]: ...

    def add_ap_payment(self, payment: ApPayment) -> None: ...

    def get_ap_payment(self, payment_id: UUID) -> ApPayment | None: ...

    def get_ap_payment_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ApPayment | None: ...

    def get_ap_payment_by_apply_key(self, apply_key: UUID) -> ApPayment | None: ...

    def list_ap_payments_for_bill(self, ap_bill_id: UUID) -> list[ApPayment]: ...

    def list_ap_payments_for_supplier(
        self, supplier_id: UUID
    ) -> list[ApPayment]: ...

    def save_ap_payment(
        self, payment: ApPayment, *, expected_version: int
    ) -> None: ...

    def next_ap_bill_line_number(self, ap_bill_id: UUID) -> int: ...

    def add_ap_bill_line(self, line: ApBillLine) -> None: ...

    def get_ap_bill_line(
        self, ap_bill_id: UUID, line_id: UUID
    ) -> ApBillLine | None: ...

    def list_ap_bill_lines(self, ap_bill_id: UUID) -> list[ApBillLine]: ...

    def save_ap_bill_line(
        self, line: ApBillLine, *, expected_version: int
    ) -> None: ...

    def add_purchase_order(self, order: PurchaseOrder) -> None: ...

    def get_purchase_order(self, order_id: UUID) -> PurchaseOrder | None: ...

    def get_purchase_order_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> PurchaseOrder | None: ...

    def save_purchase_order(
        self, order: PurchaseOrder, *, expected_version: int
    ) -> None: ...

    def next_purchase_order_line_number(self, purchase_order_id: UUID) -> int: ...

    def add_purchase_order_line(self, line: PurchaseOrderLine) -> None: ...

    def list_purchase_order_lines(
        self, purchase_order_id: UUID
    ) -> list[PurchaseOrderLine]: ...

    def add_goods_receipt(self, receipt: GoodsReceipt) -> None: ...

    def get_goods_receipt(self, receipt_id: UUID) -> GoodsReceipt | None: ...

    def get_goods_receipt_by_po(
        self, purchase_order_id: UUID
    ) -> GoodsReceipt | None: ...

    def get_goods_receipt_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> GoodsReceipt | None: ...

    def add_three_way_match(self, match: ThreeWayMatch) -> None: ...

    def get_three_way_match_by_po(
        self, purchase_order_id: UUID
    ) -> ThreeWayMatch | None: ...

    def get_three_way_match_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ThreeWayMatch | None: ...

    def get_three_way_match_tolerance_policy(
        self,
    ) -> TenantThreeWayMatchTolerancePolicy | None: ...

    def save_three_way_match_tolerance_policy(
        self,
        policy: TenantThreeWayMatchTolerancePolicy,
        *,
        expected_version: int,
    ) -> None: ...


class InMemoryPurchaseRepository:
    """Hermetic tenant-bound adapter used by package contract tests."""

    def __init__(self, *, tenant_id: UUID) -> None:
        self._tenant_id = tenant_id
        self._suppliers: dict[UUID, Supplier] = {}
        self._ap_bills: dict[UUID, ApBill] = {}
        self._ap_write_offs: dict[UUID, ApWriteOff] = {}
        self._ap_payments: dict[UUID, ApPayment] = {}
        self._ap_bill_lines: dict[UUID, ApBillLine] = {}
        self._purchase_orders: dict[UUID, PurchaseOrder] = {}
        self._purchase_order_lines: dict[UUID, PurchaseOrderLine] = {}
        self._goods_receipts: dict[UUID, GoodsReceipt] = {}
        self._three_way_matches: dict[UUID, ThreeWayMatch] = {}
        self._three_way_match_tolerance_policy: (
            TenantThreeWayMatchTolerancePolicy | None
        ) = None

    def add_supplier(self, supplier: Supplier) -> None:
        if supplier.tenant_id != self._tenant_id:
            raise ValueError("supplier is outside repository tenant")
        if any(
            item.code.casefold() == supplier.code.casefold()
            for item in self._suppliers.values()
        ):
            raise ValueError("supplier code already exists")
        self._suppliers[supplier.id] = supplier

    def get_supplier(self, supplier_id: UUID) -> Supplier | None:
        supplier = self._suppliers.get(supplier_id)
        if supplier is None or supplier.tenant_id != self._tenant_id:
            return None
        return supplier

    def save_supplier(
        self, supplier: Supplier, *, expected_version: int
    ) -> None:
        current = self.get_supplier(supplier.id)
        if current is None or current.version != expected_version:
            raise ValueError("supplier version conflict")
        self._suppliers[supplier.id] = supplier

    def add_ap_bill(self, bill: ApBill) -> None:
        if bill.tenant_id != self._tenant_id:
            raise ValueError("ap bill is outside repository tenant")
        self._validate_ap_bill_balance(bill)
        if any(
            item.code.casefold() == bill.code.casefold()
            for item in self._ap_bills.values()
        ):
            raise ValueError("ap bill code already exists")
        if any(
            item.idempotency_key == bill.idempotency_key
            for item in self._ap_bills.values()
        ):
            raise ValueError("ap bill idempotency key already exists")
        self._ap_bills[bill.id] = bill

    def get_ap_bill(self, bill_id: UUID) -> ApBill | None:
        bill = self._ap_bills.get(bill_id)
        if bill is None or bill.tenant_id != self._tenant_id:
            return None
        return bill

    def list_ap_bills_for_supplier(
        self, supplier_id: UUID
    ) -> list[ApBill]:
        return sorted(
            (
                bill
                for bill in self._ap_bills.values()
                if bill.tenant_id == self._tenant_id
                and bill.supplier_id == supplier_id
            ),
            key=lambda item: (item.created_at, item.code, item.id),
        )

    def get_ap_bill_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ApBill | None:
        for bill in self._ap_bills.values():
            if (
                bill.tenant_id == self._tenant_id
                and bill.idempotency_key == idempotency_key
            ):
                return bill
        return None

    def save_ap_bill(self, bill: ApBill, *, expected_version: int) -> None:
        current = self.get_ap_bill(bill.id)
        if current is None or current.version != expected_version:
            raise ValueError("ap bill version conflict")
        self._validate_ap_bill_balance(bill)
        self._ap_bills[bill.id] = bill

    @staticmethod
    def _validate_ap_bill_balance(bill: ApBill) -> None:
        if (
            bill.paid_amount < Decimal("0.00")
            or bill.write_off_amount < Decimal("0.00")
            or bill.paid_amount + bill.write_off_amount > bill.total_amount
        ):
            raise ValueError("ap bill settlement is outside bill balance")

    def add_ap_write_off(self, write_off: ApWriteOff) -> None:
        if write_off.tenant_id != self._tenant_id:
            raise ValueError("ap write-off is outside repository tenant")
        if any(
            item.idempotency_key == write_off.idempotency_key
            for item in self._ap_write_offs.values()
        ):
            raise ValueError("ap write-off idempotency key already exists")
        self._ap_write_offs[write_off.id] = write_off

    def get_ap_write_off_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ApWriteOff | None:
        return next(
            (
                write_off
                for write_off in self._ap_write_offs.values()
                if write_off.tenant_id == self._tenant_id
                and write_off.idempotency_key == idempotency_key
            ),
            None,
        )

    def list_ap_write_offs(self, ap_bill_id: UUID) -> list[ApWriteOff]:
        return [
            write_off
            for write_off in self._ap_write_offs.values()
            if write_off.tenant_id == self._tenant_id
            and write_off.ap_bill_id == ap_bill_id
        ]

    def add_ap_payment(self, payment: ApPayment) -> None:
        if payment.tenant_id != self._tenant_id:
            raise ValueError("ap payment is outside repository tenant")
        if any(
            item.idempotency_key == payment.idempotency_key
            for item in self._ap_payments.values()
        ):
            raise ValueError("ap payment idempotency key already exists")
        self._ap_payments[payment.id] = payment

    def get_ap_payment(self, payment_id: UUID) -> ApPayment | None:
        payment = self._ap_payments.get(payment_id)
        if payment is None or payment.tenant_id != self._tenant_id:
            return None
        return payment

    def get_ap_payment_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ApPayment | None:
        return next(
            (
                payment
                for payment in self._ap_payments.values()
                if payment.tenant_id == self._tenant_id
                and payment.idempotency_key == idempotency_key
            ),
            None,
        )

    def get_ap_payment_by_apply_key(self, apply_key: UUID) -> ApPayment | None:
        return next(
            (
                payment
                for payment in self._ap_payments.values()
                if payment.tenant_id == self._tenant_id
                and payment.apply_key == apply_key
            ),
            None,
        )

    def list_ap_payments_for_bill(self, ap_bill_id: UUID) -> list[ApPayment]:
        return [
            payment
            for payment in self._ap_payments.values()
            if payment.tenant_id == self._tenant_id
            and payment.ap_bill_id == ap_bill_id
        ]

    def list_ap_payments_for_supplier(
        self, supplier_id: UUID
    ) -> list[ApPayment]:
        return sorted(
            (
                payment
                for payment in self._ap_payments.values()
                if payment.tenant_id == self._tenant_id
                and payment.supplier_id == supplier_id
            ),
            key=lambda item: (item.created_at, item.id),
        )

    def save_ap_payment(
        self, payment: ApPayment, *, expected_version: int
    ) -> None:
        current = self.get_ap_payment(payment.id)
        if current is None or current.version != expected_version:
            raise ValueError("ap payment version conflict")
        self._ap_payments[payment.id] = payment

    def next_ap_bill_line_number(self, ap_bill_id: UUID) -> int:
        numbers = [
            line.line_number
            for line in self._ap_bill_lines.values()
            if line.ap_bill_id == ap_bill_id
            and line.tenant_id == self._tenant_id
        ]
        return (max(numbers) if numbers else 0) + 1

    def add_ap_bill_line(self, line: ApBillLine) -> None:
        if line.tenant_id != self._tenant_id:
            raise ValueError("ap bill line is outside repository tenant")
        if any(
            item.ap_bill_id == line.ap_bill_id
            and item.line_number == line.line_number
            for item in self._ap_bill_lines.values()
        ):
            raise ValueError("ap bill line number already exists")
        self._ap_bill_lines[line.id] = line

    def get_ap_bill_line(
        self, ap_bill_id: UUID, line_id: UUID
    ) -> ApBillLine | None:
        line = self._ap_bill_lines.get(line_id)
        if (
            line is None
            or line.tenant_id != self._tenant_id
            or line.ap_bill_id != ap_bill_id
        ):
            return None
        return line

    def list_ap_bill_lines(self, ap_bill_id: UUID) -> list[ApBillLine]:
        lines = [
            line
            for line in self._ap_bill_lines.values()
            if line.ap_bill_id == ap_bill_id
            and line.tenant_id == self._tenant_id
        ]
        return sorted(lines, key=lambda item: item.line_number)

    def save_ap_bill_line(
        self, line: ApBillLine, *, expected_version: int
    ) -> None:
        current = self.get_ap_bill_line(line.ap_bill_id, line.id)
        if current is None or current.version != expected_version:
            raise ValueError("ap bill line version conflict")
        self._ap_bill_lines[line.id] = line

    def add_purchase_order(self, order: PurchaseOrder) -> None:
        if order.tenant_id != self._tenant_id:
            raise ValueError("purchase order is outside repository tenant")
        if any(
            item.code.casefold() == order.code.casefold()
            for item in self._purchase_orders.values()
        ):
            raise ValueError("purchase order code already exists")
        if any(
            item.idempotency_key == order.idempotency_key
            for item in self._purchase_orders.values()
        ):
            raise ValueError("purchase order idempotency key already exists")
        self._purchase_orders[order.id] = order

    def get_purchase_order(self, order_id: UUID) -> PurchaseOrder | None:
        order = self._purchase_orders.get(order_id)
        if order is None or order.tenant_id != self._tenant_id:
            return None
        return order

    def get_purchase_order_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> PurchaseOrder | None:
        for order in self._purchase_orders.values():
            if (
                order.tenant_id == self._tenant_id
                and order.idempotency_key == idempotency_key
            ):
                return order
        return None

    def save_purchase_order(
        self, order: PurchaseOrder, *, expected_version: int
    ) -> None:
        current = self.get_purchase_order(order.id)
        if current is None or current.version != expected_version:
            raise ValueError("purchase order version conflict")
        self._purchase_orders[order.id] = order

    def next_purchase_order_line_number(self, purchase_order_id: UUID) -> int:
        numbers = [
            line.line_number
            for line in self._purchase_order_lines.values()
            if line.purchase_order_id == purchase_order_id
            and line.tenant_id == self._tenant_id
        ]
        return (max(numbers) if numbers else 0) + 1

    def add_purchase_order_line(self, line: PurchaseOrderLine) -> None:
        if line.tenant_id != self._tenant_id:
            raise ValueError("purchase order line is outside repository tenant")
        if any(
            item.purchase_order_id == line.purchase_order_id
            and item.line_number == line.line_number
            for item in self._purchase_order_lines.values()
        ):
            raise ValueError("purchase order line number already exists")
        self._purchase_order_lines[line.id] = line

    def list_purchase_order_lines(
        self, purchase_order_id: UUID
    ) -> list[PurchaseOrderLine]:
        lines = [
            line
            for line in self._purchase_order_lines.values()
            if line.purchase_order_id == purchase_order_id
            and line.tenant_id == self._tenant_id
        ]
        return sorted(lines, key=lambda item: item.line_number)

    def add_goods_receipt(self, receipt: GoodsReceipt) -> None:
        if receipt.tenant_id != self._tenant_id:
            raise ValueError("goods receipt is outside repository tenant")
        if any(
            item.purchase_order_id == receipt.purchase_order_id
            for item in self._goods_receipts.values()
        ):
            raise ValueError("goods receipt already exists for purchase order")
        if any(
            item.idempotency_key == receipt.idempotency_key
            for item in self._goods_receipts.values()
        ):
            raise ValueError("goods receipt idempotency key already exists")
        self._goods_receipts[receipt.id] = receipt

    def get_goods_receipt(self, receipt_id: UUID) -> GoodsReceipt | None:
        receipt = self._goods_receipts.get(receipt_id)
        if receipt is None or receipt.tenant_id != self._tenant_id:
            return None
        return receipt

    def get_goods_receipt_by_po(
        self, purchase_order_id: UUID
    ) -> GoodsReceipt | None:
        for receipt in self._goods_receipts.values():
            if (
                receipt.tenant_id == self._tenant_id
                and receipt.purchase_order_id == purchase_order_id
            ):
                return receipt
        return None

    def get_goods_receipt_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> GoodsReceipt | None:
        for receipt in self._goods_receipts.values():
            if (
                receipt.tenant_id == self._tenant_id
                and receipt.idempotency_key == idempotency_key
            ):
                return receipt
        return None

    def add_three_way_match(self, match: ThreeWayMatch) -> None:
        if match.tenant_id != self._tenant_id:
            raise ValueError("three-way match is outside repository tenant")
        if any(
            item.purchase_order_id == match.purchase_order_id
            for item in self._three_way_matches.values()
        ):
            raise ValueError("three-way match already exists for purchase order")
        if any(
            item.idempotency_key == match.idempotency_key
            for item in self._three_way_matches.values()
        ):
            raise ValueError("three-way match idempotency key already exists")
        self._three_way_matches[match.id] = match

    def get_three_way_match_by_po(
        self, purchase_order_id: UUID
    ) -> ThreeWayMatch | None:
        for match in self._three_way_matches.values():
            if (
                match.tenant_id == self._tenant_id
                and match.purchase_order_id == purchase_order_id
            ):
                return match
        return None

    def get_three_way_match_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ThreeWayMatch | None:
        for match in self._three_way_matches.values():
            if (
                match.tenant_id == self._tenant_id
                and match.idempotency_key == idempotency_key
            ):
                return match
        return None

    def get_three_way_match_tolerance_policy(
        self,
    ) -> TenantThreeWayMatchTolerancePolicy | None:
        return self._three_way_match_tolerance_policy

    def save_three_way_match_tolerance_policy(
        self,
        policy: TenantThreeWayMatchTolerancePolicy,
        *,
        expected_version: int,
    ) -> None:
        if policy.tenant_id != self._tenant_id:
            raise ValueError(
                "three-way match tolerance policy is outside repository tenant"
            )
        current = self._three_way_match_tolerance_policy
        if current is None:
            if expected_version != 0:
                raise ValueError(
                    "three-way match tolerance policy version conflict"
                )
        elif current.version != expected_version:
            raise ValueError(
                "three-way match tolerance policy version conflict"
            )
        self._three_way_match_tolerance_policy = policy
