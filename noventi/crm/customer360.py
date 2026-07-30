"""Read-only Customer360 projection service (PHX-G313)."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from kernel.permission.models import PermissionEffect, Resource
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult
from noventi.crm.models import ARInvoiceStatus
from noventi.finance.models import CreditNoteStatus, ReceiptStatus

CUSTOMER360_RESOURCE = "pkg.crm.customer360"


@dataclass(frozen=True, slots=True)
class Customer360InvoiceTrace:
    id: UUID
    code: str
    status: ARInvoiceStatus
    currency: str
    total_amount: Decimal


@dataclass(frozen=True, slots=True)
class Customer360AppliedReceiptTrace:
    id: UUID
    code: str
    status: ReceiptStatus
    currency: str
    amount: Decimal
    ar_invoice_id: UUID


@dataclass(frozen=True, slots=True)
class Customer360CreditNoteTrace:
    id: UUID
    code: str
    status: CreditNoteStatus
    currency: str
    amount: Decimal
    ar_invoice_id: UUID


@dataclass(frozen=True, slots=True)
class Customer360Projection:
    customer_id: UUID
    customer_code: str
    display_name: str
    commercial_hold: bool
    opportunities_count: int
    open_sales_orders_count: int
    open_delivery_orders_count: int
    invoice_traces: tuple[Customer360InvoiceTrace, ...]
    applied_receipt_traces: tuple[Customer360AppliedReceiptTrace, ...]
    credit_note_traces: tuple[Customer360CreditNoteTrace, ...]


class Customer360Repository(Protocol):
    def get_customer360(
        self, customer_id: UUID
    ) -> Customer360Projection | None: ...


class Customer360PermissionEvaluator(Protocol):
    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        action: str,
        resource: Resource,
    ) -> KernelResult: ...


class InMemoryCustomer360Repository:
    """Constructor-populated read repository intended for service tests."""

    def __init__(
        self, projections: Iterable[Customer360Projection] = ()
    ) -> None:
        self._projections = {
            projection.customer_id: projection for projection in projections
        }

    def get_customer360(
        self, customer_id: UUID
    ) -> Customer360Projection | None:
        return self._projections.get(customer_id)


class AssembledCustomer360Repository:
    """Hermetic live assemble over in-memory CRM + Finance (+ optional ship set)."""

    def __init__(
        self,
        crm_repository: object,
        finance_repository: object,
        *,
        shipped_delivery_order_ids: Iterable[UUID] = (),
    ) -> None:
        self._crm = crm_repository
        self._finance = finance_repository
        self._shipped = set(shipped_delivery_order_ids)

    def get_customer360(
        self, customer_id: UUID
    ) -> Customer360Projection | None:
        customer = self._crm.get_customer(customer_id)  # type: ignore[attr-defined]
        if customer is None:
            return None
        opportunities = self._crm.list_opportunities_for_customer(  # type: ignore[attr-defined]
            customer_id
        )
        sales_orders = self._crm.list_sales_orders_for_customer(  # type: ignore[attr-defined]
            customer_id
        )
        delivery_orders = self._crm.list_delivery_orders_for_customer(  # type: ignore[attr-defined]
            customer_id
        )
        open_delivery_orders = [
            delivery_order
            for delivery_order in delivery_orders
            if delivery_order.status.value in ("draft", "released")
            and delivery_order.id not in self._shipped
        ]
        open_sales_orders = [
            sales_order
            for sales_order in sales_orders
            if self._sales_order_is_open(sales_order.id, delivery_orders)
        ]
        invoices = self._crm.list_ar_invoices_for_customer(customer_id)  # type: ignore[attr-defined]
        receipts = self._finance.list_applied_receipts_for_customer(  # type: ignore[attr-defined]
            customer_id
        )
        credit_notes = self._finance.list_credit_notes_for_customer(  # type: ignore[attr-defined]
            customer_id
        )
        return Customer360Projection(
            customer_id=customer.id,
            customer_code=customer.code,
            display_name=customer.display_name,
            commercial_hold=bool(customer.commercial_hold),
            opportunities_count=len(opportunities),
            open_sales_orders_count=len(open_sales_orders),
            open_delivery_orders_count=len(open_delivery_orders),
            invoice_traces=tuple(
                Customer360InvoiceTrace(
                    id=invoice.id,
                    code=invoice.code,
                    status=invoice.status,
                    currency=invoice.currency,
                    total_amount=invoice.total_amount,
                )
                for invoice in invoices
            ),
            applied_receipt_traces=tuple(
                Customer360AppliedReceiptTrace(
                    id=receipt.id,
                    code=receipt.code,
                    status=receipt.status,
                    currency=receipt.currency,
                    amount=receipt.amount,
                    ar_invoice_id=receipt.ar_invoice_id,
                )
                for receipt in receipts
                if receipt.ar_invoice_id is not None
            ),
            credit_note_traces=tuple(
                Customer360CreditNoteTrace(
                    id=credit_note.id,
                    code=credit_note.code,
                    status=credit_note.status,
                    currency=credit_note.currency,
                    amount=credit_note.amount,
                    ar_invoice_id=credit_note.ar_invoice_id,
                )
                for credit_note in credit_notes
            ),
        )

    def _sales_order_is_open(
        self, sales_order_id: UUID, delivery_orders: Iterable
    ) -> bool:
        matching = [
            delivery_order
            for delivery_order in delivery_orders
            if delivery_order.sales_order_id == sales_order_id
        ]
        if not matching:
            return True
        return any(
            delivery_order.id not in self._shipped for delivery_order in matching
        )


class Customer360Service:
    def __init__(
        self,
        permission: Customer360PermissionEvaluator,
        *,
        repository: Customer360Repository,
    ) -> None:
        self._permission = permission
        self._repository = repository

    def get_customer360(
        self, ctx: ExecutionContext, customer_id: UUID
    ) -> KernelResult[Customer360Projection]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            permission = self._permission.evaluate(
                ctx,
                principal_subject_id=ctx.subject_id,
                action="read",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type=CUSTOMER360_RESOURCE,
                    resource_id=customer_id,
                ),
            )
            if not permission.ok:
                return permission
            decision = permission.data
            if decision is None or decision.effect != PermissionEffect.ALLOW:
                return KernelResult.failure(
                    ErrorCode.PERMISSION_DENIED,
                    "Customer360 read is denied by Permission",
                    details={
                        "reason_code": (
                            decision.reason_code
                            if decision is not None
                            else ErrorCode.PERMISSION_DENIED.value
                        )
                    },
                )
            projection = self._repository.get_customer360(customer_id)
            if projection is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND,
                    "customer not found",
                )
            return KernelResult.success(projection)
        except KernelError as error:
            return KernelResult.from_error(error)
