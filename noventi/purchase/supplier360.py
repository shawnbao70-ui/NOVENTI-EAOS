"""Read-only Supplier360 projection service (PHX-G368)."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
from uuid import UUID

from kernel.permission.models import PermissionEffect, Resource
from kernel.shared.audit import AuditLog
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult
from noventi.purchase.models import ApBillStatus, ApPaymentStatus, SupplierStatus

SUPPLIER360_RESOURCE = "pkg.purchase.supplier360"


@dataclass(frozen=True, slots=True)
class Supplier360BillTrace:
    id: UUID
    code: str
    status: ApBillStatus
    currency: str
    total_amount: Decimal


@dataclass(frozen=True, slots=True)
class Supplier360PaymentTrace:
    id: UUID
    status: ApPaymentStatus
    currency: str
    amount: Decimal
    ap_bill_id: UUID | None


@dataclass(frozen=True, slots=True)
class Supplier360Projection:
    supplier_id: UUID
    supplier_code: str
    display_name: str
    status: SupplierStatus
    balances: dict[str, Decimal]
    bill_traces: tuple[Supplier360BillTrace, ...]
    payment_traces: tuple[Supplier360PaymentTrace, ...]


class Supplier360Repository(Protocol):
    def get_supplier360(
        self, supplier_id: UUID
    ) -> Supplier360Projection | None: ...


class Supplier360PermissionEvaluator(Protocol):
    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        action: str,
        resource: Resource,
    ) -> KernelResult: ...


class InMemorySupplier360Repository:
    """Constructor-populated read repository intended for service tests."""

    def __init__(
        self, projections: Iterable[Supplier360Projection] = ()
    ) -> None:
        self._projections = {
            projection.supplier_id: projection for projection in projections
        }

    def get_supplier360(
        self, supplier_id: UUID
    ) -> Supplier360Projection | None:
        return self._projections.get(supplier_id)


class AssembledSupplier360Repository:
    """Hermetic live assemble over an in-memory Purchase repository."""

    def __init__(self, purchase_repository: object) -> None:
        self._purchase = purchase_repository

    def get_supplier360(
        self, supplier_id: UUID
    ) -> Supplier360Projection | None:
        supplier = self._purchase.get_supplier(supplier_id)  # type: ignore[attr-defined]
        if supplier is None:
            return None
        bills = self._purchase.list_ap_bills_for_supplier(supplier_id)  # type: ignore[attr-defined]
        payments = self._purchase.list_ap_payments_for_supplier(supplier_id)  # type: ignore[attr-defined]
        balances: dict[str, Decimal] = {}
        for bill in bills:
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
        return Supplier360Projection(
            supplier_id=supplier.id,
            supplier_code=supplier.code,
            display_name=supplier.display_name,
            status=supplier.status,
            balances=dict(sorted(balances.items())),
            bill_traces=tuple(
                Supplier360BillTrace(
                    id=bill.id,
                    code=bill.code,
                    status=bill.status,
                    currency=bill.currency,
                    total_amount=bill.total_amount,
                )
                for bill in bills
            ),
            payment_traces=tuple(
                Supplier360PaymentTrace(
                    id=payment.id,
                    status=payment.status,
                    currency=payment.currency,
                    amount=payment.amount,
                    ap_bill_id=payment.ap_bill_id,
                )
                for payment in payments
            ),
        )


class Supplier360Service:
    def __init__(
        self,
        permission: Supplier360PermissionEvaluator,
        *,
        repository: Supplier360Repository,
        audit_log: AuditLog,
    ) -> None:
        self._permission = permission
        self._repository = repository
        self._audit = audit_log

    def get_supplier360(
        self, ctx: ExecutionContext, supplier_id: UUID
    ) -> KernelResult[Supplier360Projection]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            permission = self._permission.evaluate(
                ctx,
                principal_subject_id=ctx.subject_id,
                action="read",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type=SUPPLIER360_RESOURCE,
                    resource_id=supplier_id,
                ),
            )
            if not permission.ok:
                return permission
            decision = permission.data
            if decision is None or decision.effect != PermissionEffect.ALLOW:
                audit = self._audit.record(
                    ctx,
                    action="Purchase.Supplier360.Read",
                    resource=f"{SUPPLIER360_RESOURCE}:{supplier_id}",
                    result="denied",
                    details={},
                )
                return KernelResult.failure(
                    ErrorCode.PERMISSION_DENIED,
                    "Supplier360 read is denied by Permission",
                    details={
                        "reason_code": (
                            decision.reason_code
                            if decision is not None
                            else ErrorCode.PERMISSION_DENIED.value
                        )
                    },
                    audit_id=audit.id,
                )
            projection = self._repository.get_supplier360(supplier_id)
            if projection is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND,
                    "supplier not found",
                )
            audit = self._audit.record(
                ctx,
                action="Purchase.Supplier360.Read",
                resource=f"{SUPPLIER360_RESOURCE}:{supplier_id}",
                result="ok",
                details={},
            )
            return KernelResult.success(projection, audit_id=audit.id)
        except KernelError as error:
            return KernelResult.from_error(error)
