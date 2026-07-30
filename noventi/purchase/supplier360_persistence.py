"""SQL composition for the read-only Supplier360 projection."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
from kernel.infrastructure.persistence.identity_permission import (
    SQLAlchemyPrincipalEligibility,
)
from kernel.infrastructure.persistence.permission_repository import (
    SQLAlchemyPermissionRepository,
)
from kernel.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult
from noventi.purchase.models import ApBillStatus, ApPaymentStatus, SupplierStatus
from noventi.purchase.persistence import (
    ApBillRecord,
    ApPaymentRecord,
    SupplierRecord,
)
from noventi.purchase.supplier360 import (
    Supplier360BillTrace,
    Supplier360PaymentTrace,
    Supplier360Projection,
    Supplier360Service,
)


class SQLAlchemySupplier360Repository:
    """Tenant-scoped live composition over Purchase supplier + AP artifacts."""

    def __init__(self, session: Session, *, tenant_id: UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def get_supplier360(
        self, supplier_id: UUID
    ) -> Supplier360Projection | None:
        supplier = self._session.scalar(
            select(SupplierRecord).where(
                SupplierRecord.id == supplier_id,
                SupplierRecord.tenant_id == self._tenant_id,
            )
        )
        if supplier is None:
            return None

        bills = self._session.scalars(
            select(ApBillRecord)
            .where(
                ApBillRecord.tenant_id == self._tenant_id,
                ApBillRecord.supplier_id == supplier_id,
            )
            .order_by(
                ApBillRecord.created_at,
                ApBillRecord.code,
                ApBillRecord.id,
            )
        ).all()
        payments = self._session.scalars(
            select(ApPaymentRecord)
            .where(
                ApPaymentRecord.tenant_id == self._tenant_id,
                ApPaymentRecord.supplier_id == supplier_id,
            )
            .order_by(
                ApPaymentRecord.created_at,
                ApPaymentRecord.id,
            )
        ).all()

        balances: dict[str, Decimal] = {}
        for bill in bills:
            status = ApBillStatus(bill.status)
            if status not in (
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
            status=SupplierStatus(supplier.status),
            balances=dict(sorted(balances.items())),
            bill_traces=tuple(
                Supplier360BillTrace(
                    id=bill.id,
                    code=bill.code,
                    status=ApBillStatus(bill.status),
                    currency=bill.currency,
                    total_amount=bill.total_amount,
                )
                for bill in bills
            ),
            payment_traces=tuple(
                Supplier360PaymentTrace(
                    id=payment.id,
                    status=ApPaymentStatus(payment.status),
                    currency=payment.currency,
                    amount=payment.amount,
                    ap_bill_id=payment.ap_bill_id,
                )
                for payment in payments
            ),
        )


class TransactionalSupplier360Service:
    """Read-only UoW composition; permission incidental state is rolled back."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get_supplier360(
        self, ctx: ExecutionContext, supplier_id: UUID
    ) -> KernelResult[Supplier360Projection]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
                session = unit_of_work.session
                audit = SQLAlchemyAuditLog(
                    session,
                    tenant_id=ctx.tenant_id,
                )
                permission = PermissionService(
                    repository=SQLAlchemyPermissionRepository(
                        session,
                        tenant_id=ctx.tenant_id,
                    ),
                    audit_log=audit,
                    principal_eligibility=SQLAlchemyPrincipalEligibility(
                        session
                    ),
                )
                service = Supplier360Service(
                    permission,
                    repository=SQLAlchemySupplier360Repository(
                        session,
                        tenant_id=ctx.tenant_id,
                    ),
                    audit_log=audit,
                )
                with session.no_autoflush:
                    return service.get_supplier360(ctx, supplier_id)
        except KernelError as error:
            return KernelResult.from_error(error)
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL,
                "Supplier360 persistence unavailable",
            )
