"""SQL composition for the read-only Customer360 projection."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import and_, func, or_, select
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
from noventi.crm.customer360 import (
    Customer360AppliedReceiptTrace,
    Customer360CreditNoteTrace,
    Customer360InvoiceTrace,
    Customer360Projection,
    Customer360Service,
)
from noventi.crm.models import ARInvoiceStatus
from noventi.crm.persistence import (
    ARInvoiceRecord,
    CustomerRecord,
    DeliveryOrderRecord,
    OpportunityRecord,
    RequirementRecord,
    SalesOrderRecord,
)
from noventi.finance.models import CreditNoteStatus, ReceiptStatus
from noventi.finance.persistence import ARCreditNoteRecord, ARReceiptRecord
from noventi.inventory.persistence import DeliveryShipPostingRecord


class SQLAlchemyCustomer360Repository:
    """Tenant-scoped live composition over CRM, Inventory, and Finance."""

    def __init__(self, session: Session, *, tenant_id: UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def get_customer360(
        self, customer_id: UUID
    ) -> Customer360Projection | None:
        customer = self._session.scalar(
            select(CustomerRecord).where(
                CustomerRecord.id == customer_id,
                CustomerRecord.tenant_id == self._tenant_id,
            )
        )
        if customer is None:
            return None

        opportunities_count = self._count_opportunities(customer_id)
        open_sales_orders_count = self._count_open_sales_orders(customer_id)
        open_delivery_orders_count = self._count_open_delivery_orders(
            customer_id
        )

        invoices = self._session.scalars(
            select(ARInvoiceRecord)
            .where(
                ARInvoiceRecord.tenant_id == self._tenant_id,
                ARInvoiceRecord.customer_id == customer_id,
            )
            .order_by(
                ARInvoiceRecord.created_at,
                ARInvoiceRecord.code,
                ARInvoiceRecord.id,
            )
        ).all()
        receipts = self._session.scalars(
            select(ARReceiptRecord)
            .where(
                ARReceiptRecord.tenant_id == self._tenant_id,
                ARReceiptRecord.customer_id == customer_id,
                ARReceiptRecord.status == ReceiptStatus.APPLIED.value,
                ARReceiptRecord.ar_invoice_id.is_not(None),
            )
            .order_by(
                ARReceiptRecord.created_at,
                ARReceiptRecord.code,
                ARReceiptRecord.id,
            )
        ).all()
        credit_notes = self._session.scalars(
            select(ARCreditNoteRecord)
            .where(
                ARCreditNoteRecord.tenant_id == self._tenant_id,
                ARCreditNoteRecord.customer_id == customer_id,
            )
            .order_by(
                ARCreditNoteRecord.created_at,
                ARCreditNoteRecord.code,
                ARCreditNoteRecord.id,
            )
        ).all()

        return Customer360Projection(
            customer_id=customer.id,
            customer_code=customer.code,
            display_name=customer.display_name,
            commercial_hold=bool(customer.commercial_hold),
            opportunities_count=opportunities_count,
            open_sales_orders_count=open_sales_orders_count,
            open_delivery_orders_count=open_delivery_orders_count,
            invoice_traces=tuple(
                Customer360InvoiceTrace(
                    id=invoice.id,
                    code=invoice.code,
                    status=ARInvoiceStatus(invoice.status),
                    currency=invoice.currency,
                    total_amount=invoice.total_amount,
                )
                for invoice in invoices
            ),
            applied_receipt_traces=tuple(
                Customer360AppliedReceiptTrace(
                    id=receipt.id,
                    code=receipt.code,
                    status=ReceiptStatus(receipt.status),
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
                    status=CreditNoteStatus(credit_note.status),
                    currency=credit_note.currency,
                    amount=credit_note.amount,
                    ar_invoice_id=credit_note.ar_invoice_id,
                )
                for credit_note in credit_notes
            ),
        )

    def _count_opportunities(self, customer_id: UUID) -> int:
        count = self._session.scalar(
            select(func.count(OpportunityRecord.id)).where(
                OpportunityRecord.tenant_id == self._tenant_id,
                OpportunityRecord.customer_id == customer_id,
            )
        )
        return int(count or 0)

    def _count_open_sales_orders(self, customer_id: UUID) -> int:
        count = self._session.scalar(
            select(func.count(SalesOrderRecord.id))
            .join(
                RequirementRecord,
                and_(
                    RequirementRecord.id
                    == SalesOrderRecord.requirement_id,
                    RequirementRecord.tenant_id
                    == SalesOrderRecord.tenant_id,
                ),
            )
            .join(
                OpportunityRecord,
                and_(
                    OpportunityRecord.id
                    == RequirementRecord.opportunity_id,
                    OpportunityRecord.tenant_id
                    == RequirementRecord.tenant_id,
                ),
            )
            .outerjoin(
                DeliveryOrderRecord,
                and_(
                    DeliveryOrderRecord.sales_order_id
                    == SalesOrderRecord.id,
                    DeliveryOrderRecord.tenant_id
                    == SalesOrderRecord.tenant_id,
                ),
            )
            .outerjoin(
                DeliveryShipPostingRecord,
                and_(
                    DeliveryShipPostingRecord.delivery_order_id
                    == DeliveryOrderRecord.id,
                    DeliveryShipPostingRecord.tenant_id
                    == DeliveryOrderRecord.tenant_id,
                ),
            )
            .where(
                SalesOrderRecord.tenant_id == self._tenant_id,
                RequirementRecord.tenant_id == self._tenant_id,
                OpportunityRecord.tenant_id == self._tenant_id,
                or_(
                    DeliveryOrderRecord.id.is_(None),
                    and_(
                        DeliveryOrderRecord.tenant_id
                        == self._tenant_id,
                        DeliveryShipPostingRecord.id.is_(None),
                    ),
                ),
                OpportunityRecord.customer_id == customer_id,
            )
        )
        return int(count or 0)

    def _count_open_delivery_orders(self, customer_id: UUID) -> int:
        count = self._session.scalar(
            select(func.count(DeliveryOrderRecord.id))
            .join(
                SalesOrderRecord,
                and_(
                    SalesOrderRecord.id
                    == DeliveryOrderRecord.sales_order_id,
                    SalesOrderRecord.tenant_id
                    == DeliveryOrderRecord.tenant_id,
                ),
            )
            .join(
                RequirementRecord,
                and_(
                    RequirementRecord.id
                    == SalesOrderRecord.requirement_id,
                    RequirementRecord.tenant_id
                    == SalesOrderRecord.tenant_id,
                ),
            )
            .join(
                OpportunityRecord,
                and_(
                    OpportunityRecord.id
                    == RequirementRecord.opportunity_id,
                    OpportunityRecord.tenant_id
                    == RequirementRecord.tenant_id,
                ),
            )
            .outerjoin(
                DeliveryShipPostingRecord,
                and_(
                    DeliveryShipPostingRecord.delivery_order_id
                    == DeliveryOrderRecord.id,
                    DeliveryShipPostingRecord.tenant_id
                    == DeliveryOrderRecord.tenant_id,
                ),
            )
            .where(
                DeliveryOrderRecord.tenant_id == self._tenant_id,
                SalesOrderRecord.tenant_id == self._tenant_id,
                RequirementRecord.tenant_id == self._tenant_id,
                OpportunityRecord.tenant_id == self._tenant_id,
                DeliveryOrderRecord.status.in_(("draft", "released")),
                DeliveryShipPostingRecord.id.is_(None),
                OpportunityRecord.customer_id == customer_id,
            )
        )
        return int(count or 0)


class TransactionalCustomer360Service:
    """Read-only UoW composition; all incidental permission state is rolled back."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get_customer360(
        self, ctx: ExecutionContext, customer_id: UUID
    ) -> KernelResult[Customer360Projection]:
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
                service = Customer360Service(
                    permission,
                    repository=SQLAlchemyCustomer360Repository(
                        session,
                        tenant_id=ctx.tenant_id,
                    ),
                )
                with session.no_autoflush:
                    return service.get_customer360(ctx, customer_id)
        except KernelError as error:
            return KernelResult.from_error(error)
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL,
                "Customer360 persistence unavailable",
            )
