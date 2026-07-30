"""SQLAlchemy persistence and transactional composition for Finance F1."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from typing import TypeVar
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Boolean,
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
from noventi.crm.credit_note import CRMReturnAuthorizationCreditNoteLinkAdapter
from noventi.crm.persistence import ARInvoiceRecord, SQLAlchemyCRMRepository
from noventi.purchase.persistence import ApBillRecord, ApPaymentRecord
from noventi.finance.models import (
    ARCreditNote,
    ARRefund,
    ARRefundStatus,
    ARReceipt,
    ARReceiptAllocation,
    ARWriteOff,
    BankStatement,
    BankStatementLine,
    BankStatementLineStatus,
    BankStatementStatus,
    CommissionEntry,
    CommissionStatus,
    CreditNoteStatus,
    GlAccount,
    GlAccountStatus,
    GlAccountType,
    GlBridgeMap,
    GlBridgePosting,
    GlBridgeSourceType,
    GlFxRevaluation,
    GlFxRevaluationSide,
    GlFxRevaluationStatus,
    GlPeriod,
    GlPeriodStatus,
    JournalEntry,
    JournalEntryStatus,
    JournalLine,
    RealizedFxEvent,
    RealizedFxSide,
    ReceiptStatus,
    TaxInvoice,
    TaxCreditLink,
    TaxInvoiceStatus,
    TaxRate,
    TaxRateStatus,
    TenantReceiptPspPolicy,
    TenantTaxAuthorityPolicy,
    TreasuryTransfer,
    TreasuryTransferStatus,
)
from noventi.finance.service import (
    ARInvoiceSnapshot,
    FinanceService,
)

T = TypeVar("T")


class FinanceBase(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class ARReceiptRecord(FinanceBase):
    """DB FKs to crm.* are owned by Alembic; omit ORM FKs (cross-Base metadata)."""

    __tablename__ = "ar_receipts"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "code"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        UniqueConstraint("tenant_id", "apply_key"),
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint(
            "status IN ('draft','applied')", name="status_valid"
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_finance_ar_receipts_tenant_status", "tenant_id", "status"),
        Index(
            "ix_finance_ar_receipts_tenant_customer",
            "tenant_id",
            "customer_id",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    functional_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    fx_rate: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    functional_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    allocated_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    ar_invoice_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    ar_invoice_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    apply_key: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    applied_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    psp_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    psp_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class ARReceiptAllocationRecord(FinanceBase):
    __tablename__ = "ar_receipt_allocations"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "allocation_key"),
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "ix_finance_ar_receipt_allocations_tenant_receipt",
            "tenant_id",
            "receipt_id",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    receipt_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    ar_invoice_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    allocation_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class RealizedFxEventRecord(FinanceBase):
    __tablename__ = "realized_fx_events"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "source_type", "source_id"),
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint("side IN ('gain','loss')", name="side_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "ix_finance_realized_fx_events_tenant_receipt",
            "tenant_id",
            "receipt_id",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    side: Mapped[str] = mapped_column(String(8), nullable=False)
    receipt_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    invoice_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class ARWriteOffRecord(FinanceBase):
    __tablename__ = "ar_write_offs"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_finance_ar_write_offs_tenant_invoice", "tenant_id", "ar_invoice_id"),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    ar_invoice_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class TenantReceiptPspPolicyRecord(FinanceBase):
    __tablename__ = "tenant_receipt_policies"
    __table_args__ = (
        CheckConstraint("version > 0", name="version_positive"),
        {"schema": "finance"},
    )

    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    receipt_psp_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )


class TenantTaxAuthorityPolicyRecord(FinanceBase):
    __tablename__ = "tenant_tax_authority_policies"
    __table_args__ = (
        CheckConstraint("version > 0", name="version_positive"),
        {"schema": "finance"},
    )

    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tax_authority_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )


class TaxRateRecord(FinanceBase):
    __tablename__ = "tax_rates"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "tax_code"),
        CheckConstraint("rate_percent >= 0", name="rate_percent_non_negative"),
        CheckConstraint(
            "status IN ('active','archived')", name="status_valid"
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_finance_tax_rates_tenant_status", "tenant_id", "status"),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    tax_code: Mapped[str] = mapped_column(String(64), nullable=False)
    tax_name: Mapped[str] = mapped_column(String(128), nullable=False)
    rate_percent: Mapped[Decimal] = mapped_column(Numeric(9, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class ARCreditNoteRecord(FinanceBase):
    """DB FKs to crm.* are owned by Alembic; omit ORM FKs (cross-Base metadata)."""

    __tablename__ = "ar_credit_notes"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "code"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        UniqueConstraint("tenant_id", "issue_key"),
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint(
            "status IN ('draft','issued')", name="status_valid"
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "ix_finance_ar_credit_notes_tenant_status",
            "tenant_id",
            "status",
        ),
        Index(
            "ix_finance_ar_credit_notes_tenant_customer",
            "tenant_id",
            "customer_id",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    ar_invoice_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    ar_invoice_version: Mapped[int] = mapped_column(Integer, nullable=False)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    issued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    issue_key: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class ARRefundRecord(FinanceBase):
    __tablename__ = "ar_refunds"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        UniqueConstraint("tenant_id", "post_key"),
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint(
            "status IN ('draft','posted')", name="status_valid"
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_finance_ar_refunds_tenant_status", "tenant_id", "status"),
        Index(
            "ix_finance_ar_refunds_tenant_credit_note",
            "tenant_id",
            "credit_note_id",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    credit_note_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False
    )
    customer_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    posted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    post_key: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class TreasuryTransferRecord(FinanceBase):
    __tablename__ = "treasury_transfers"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        UniqueConstraint("tenant_id", "post_key"),
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint(
            "functional_amount > 0", name="functional_amount_positive"
        ),
        CheckConstraint("fx_rate > 0", name="fx_rate_positive"),
        CheckConstraint(
            "from_account_ref <> to_account_ref", name="accounts_distinct"
        ),
        CheckConstraint(
            "status IN ('draft','posted')", name="status_valid"
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "ix_finance_treasury_transfers_tenant_status",
            "tenant_id",
            "status",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    from_account_ref: Mapped[str] = mapped_column(String(128), nullable=False)
    to_account_ref: Mapped[str] = mapped_column(String(128), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    functional_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    fx_rate: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    functional_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False
    )
    idempotency_key: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    posted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    post_key: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class TaxInvoiceRecord(FinanceBase):
    """DB FKs to crm.* are owned by Alembic; omit ORM FKs (cross-Base metadata)."""

    __tablename__ = "tax_invoices"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "code"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        UniqueConstraint("tenant_id", "issue_key"),
        UniqueConstraint("tenant_id", "void_key"),
        UniqueConstraint("tenant_id", "original_tax_invoice_id"),
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint(
            "status IN ('draft','issued','voided')", name="status_valid"
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "ix_finance_tax_invoices_tenant_status",
            "tenant_id",
            "status",
        ),
        Index(
            "ix_finance_tax_invoices_tenant_customer",
            "tenant_id",
            "customer_id",
        ),
        Index(
            "ix_finance_tax_invoices_tenant_ar_invoice",
            "tenant_id",
            "ar_invoice_id",
        ),
        Index(
            "ix_finance_tax_invoices_tenant_original",
            "tenant_id",
            "original_tax_invoice_id",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    ar_invoice_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    ar_invoice_version: Mapped[int] = mapped_column(Integer, nullable=False)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    issued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    issue_key: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    voided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    void_key: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    void_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tax_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    authority_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    authority_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    original_tax_invoice_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    is_red_credit: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class TaxCreditLinkRecord(FinanceBase):
    __tablename__ = "tax_credit_links"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "tax_invoice_id", "credit_note_id"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        CheckConstraint("status IN ('linked')", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "ix_finance_tax_credit_links_tenant_tax_invoice",
            "tenant_id",
            "tax_invoice_id",
        ),
        Index(
            "ix_finance_tax_credit_links_tenant_credit_note",
            "tenant_id",
            "credit_note_id",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    tax_invoice_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    credit_note_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class GlAccountRecord(FinanceBase):
    __tablename__ = "gl_accounts"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "code"),
        CheckConstraint(
            "account_type IN ('asset','liability','equity','revenue','expense')",
            name="account_type_valid",
        ),
        CheckConstraint(
            "status IN ('active','archived')", name="status_valid"
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_finance_gl_accounts_tenant_status", "tenant_id", "status"),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    account_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class GlPeriodRecord(FinanceBase):
    __tablename__ = "gl_periods"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "code"),
        UniqueConstraint("tenant_id", "close_key"),
        CheckConstraint(
            "status IN ('open','closed')", name="status_valid"
        ),
        CheckConstraint("start_at < end_at", name="start_before_end"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_finance_gl_periods_tenant_status", "tenant_id", "status"),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    start_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    close_key: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class JournalEntryRecord(FinanceBase):
    __tablename__ = "journal_entries"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "code"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        UniqueConstraint("tenant_id", "post_key"),
        CheckConstraint(
            "status IN ('draft','posted')", name="status_valid"
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "ix_finance_journal_entries_tenant_status",
            "tenant_id",
            "status",
        ),
        Index(
            "ix_finance_journal_entries_tenant_period",
            "tenant_id",
            "period_id",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    period_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    memo: Mapped[str | None] = mapped_column(String(500), nullable=True)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    posted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    post_key: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class GlBridgeMapRecord(FinanceBase):
    __tablename__ = "gl_bridge_maps"
    __table_args__ = (
        CheckConstraint("version > 0", name="version_positive"),
        {"schema": "finance"},
    )

    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    ar_control: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    cash: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    revenue: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    tax_payable: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    commission_expense: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False
    )
    commission_payable: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False
    )
    fx_gain: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    fx_loss: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    ap_control: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    ap_expense: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )


class GlBridgePostingRecord(FinanceBase):
    __tablename__ = "gl_bridge_postings"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "source_type", "source_id"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        CheckConstraint(
            "source_type IN ("
            "'ar_invoice','ar_receipt','tax_invoice','commission',"
            "'ap_bill','ap_payment')",
            name="source_type_valid",
        ),
        Index(
            "ix_finance_gl_bridge_postings_tenant_source",
            "tenant_id",
            "source_type",
            "source_id",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    journal_entry_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False
    )
    idempotency_key: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class BankStatementRecord(FinanceBase):
    __tablename__ = "bank_statements"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        CheckConstraint(
            "status IN ('open','reconciled')", name="status_valid"
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "ix_finance_bank_statements_tenant_status",
            "tenant_id",
            "status",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    account_ref: Mapped[str] = mapped_column(String(128), nullable=False)
    statement_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    cleared_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class BankStatementLineRecord(FinanceBase):
    __tablename__ = "bank_statement_lines"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("statement_id", "line_no"),
        CheckConstraint(
            "status IN ('unmatched','matched','cleared')",
            name="status_valid",
        ),
        CheckConstraint("amount != 0", name="amount_nonzero"),
        Index(
            "ix_finance_bank_statement_lines_tenant_statement",
            "tenant_id",
            "statement_id",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    statement_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    matched_journal_line_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    matched_receipt_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    line_no: Mapped[int] = mapped_column(Integer, nullable=False)


class GlFxRevaluationRecord(FinanceBase):
    __tablename__ = "gl_fx_revaluations"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        UniqueConstraint("tenant_id", "post_key"),
        CheckConstraint(
            "status IN ('draft','posted')", name="status_valid"
        ),
        CheckConstraint("side IN ('gain','loss')", name="side_valid"),
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint("rate > 0", name="rate_positive"),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "ix_finance_gl_fx_revaluations_tenant_period",
            "tenant_id",
            "period_id",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    period_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    from_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    to_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    side: Mapped[str] = mapped_column(String(16), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    journal_entry_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    posted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    post_key: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class JournalLineRecord(FinanceBase):
    """DB FKs to journal_entries / gl_accounts are owned by Alembic."""

    __tablename__ = "journal_lines"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        CheckConstraint("debit >= 0", name="debit_non_negative"),
        CheckConstraint("credit >= 0", name="credit_non_negative"),
        CheckConstraint(
            "((debit > 0 AND credit = 0) OR (credit > 0 AND debit = 0))",
            name="debit_xor_credit",
        ),
        Index(
            "ix_finance_journal_lines_tenant_entry",
            "tenant_id",
            "journal_entry_id",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    journal_entry_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False
    )
    account_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    debit: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    credit: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    line_no: Mapped[int] = mapped_column(Integer, nullable=False)


class CommissionEntryRecord(FinanceBase):
    """DB FKs to crm.* / kernel subjects are owned by Alembic."""

    __tablename__ = "commission_entries"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "code"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        UniqueConstraint(
            "tenant_id", "source_invoice_id", "beneficiary_subject_id"
        ),
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint(
            "status IN ('accrued','payable','paid')", name="status_valid"
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "ix_finance_commission_entries_tenant_status",
            "tenant_id",
            "status",
        ),
        {"schema": "finance"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    source_invoice_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False
    )
    beneficiary_subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), nullable=False
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class SQLAlchemyARInvoiceReadAdapter:
    def __init__(self, session: Session, *, tenant_id: UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def get_ar_invoice_snapshot(
        self, invoice_id: UUID
    ) -> ARInvoiceSnapshot | None:
        record = self._session.scalar(
            select(ARInvoiceRecord).where(
                ARInvoiceRecord.id == invoice_id,
                ARInvoiceRecord.tenant_id == self._tenant_id,
            )
        )
        if record is None:
            return None
        return ARInvoiceSnapshot(
            id=record.id,
            tenant_id=record.tenant_id,
            customer_id=record.customer_id,
            currency=record.currency,
            total_amount=record.total_amount,
            status=record.status,
            version=record.version,
            functional_currency=record.functional_currency,
            fx_rate=record.fx_rate,
        )

    def list_ar_invoice_snapshots_for_customer(
        self, customer_id: UUID
    ) -> list[ARInvoiceSnapshot]:
        records = self._session.scalars(
            select(ARInvoiceRecord).where(
                ARInvoiceRecord.customer_id == customer_id,
                ARInvoiceRecord.tenant_id == self._tenant_id,
            )
        ).all()
        return [
            ARInvoiceSnapshot(
                id=record.id,
                tenant_id=record.tenant_id,
                customer_id=record.customer_id,
                currency=record.currency,
                total_amount=record.total_amount,
                status=record.status,
                version=record.version,
                functional_currency=record.functional_currency,
                fx_rate=record.fx_rate,
            )
            for record in records
        ]

    def close_ar_invoice(
        self, *, invoice_id: UUID, expected_version: int
    ) -> None:
        result = self._session.execute(
            update(ARInvoiceRecord)
            .where(
                ARInvoiceRecord.id == invoice_id,
                ARInvoiceRecord.tenant_id == self._tenant_id,
                ARInvoiceRecord.status == "issued",
                ARInvoiceRecord.version == expected_version,
            )
            .values(status="closed", version=expected_version + 1)
        )
        if result.rowcount != 1:
            raise ValueError("AR invoice close conflict")


class SQLAlchemyApBillReadAdapter:
    def __init__(self, session: Session, *, tenant_id: UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def get_ap_bill_snapshot(self, bill_id: UUID):
        from noventi.finance.service import ApBillSnapshot

        record = self._session.scalar(
            select(ApBillRecord).where(
                ApBillRecord.id == bill_id,
                ApBillRecord.tenant_id == self._tenant_id,
            )
        )
        if record is None:
            return None
        return ApBillSnapshot(
            id=record.id,
            tenant_id=record.tenant_id,
            currency=record.currency,
            total_amount=record.total_amount,
            status=record.status,
        )


class SQLAlchemyApPaymentReadAdapter:
    def __init__(self, session: Session, *, tenant_id: UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def get_ap_payment_snapshot(self, payment_id: UUID):
        from noventi.finance.service import ApPaymentSnapshot

        record = self._session.scalar(
            select(ApPaymentRecord).where(
                ApPaymentRecord.id == payment_id,
                ApPaymentRecord.tenant_id == self._tenant_id,
            )
        )
        if record is None:
            return None
        return ApPaymentSnapshot(
            id=record.id,
            tenant_id=record.tenant_id,
            currency=record.currency,
            amount=record.amount,
            status=record.status,
        )


class SQLAlchemyFinanceRepository:
    def __init__(self, session: Session, *, tenant_id: UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def add_receipt(self, receipt: ARReceipt) -> None:
        self._require_tenant(receipt.tenant_id)
        self._session.add(self._receipt_record(receipt))

    def save_receipt(
        self, receipt: ARReceipt, *, expected_version: int
    ) -> None:
        self._require_tenant(receipt.tenant_id)
        result = self._session.execute(
            update(ARReceiptRecord)
            .where(
                ARReceiptRecord.id == receipt.id,
                ARReceiptRecord.tenant_id == self._tenant_id,
                ARReceiptRecord.version == expected_version,
            )
            .values(
                status=receipt.status.value,
                allocated_amount=receipt.allocated_amount,
                ar_invoice_id=receipt.ar_invoice_id,
                ar_invoice_version=receipt.ar_invoice_version,
                apply_key=receipt.apply_key,
                applied_at=receipt.applied_at,
                psp_ref=receipt.psp_ref,
                psp_status=receipt.psp_status,
                version=receipt.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("receipt version conflict")

    def get_receipt(self, receipt_id: UUID) -> ARReceipt | None:
        record = self._session.scalar(
            select(ARReceiptRecord).where(
                ARReceiptRecord.id == receipt_id,
                ARReceiptRecord.tenant_id == self._tenant_id,
            )
        )
        return self._receipt_domain(record) if record is not None else None

    def list_receipts_for_customer(
        self, customer_id: UUID
    ) -> list[ARReceipt]:
        records = self._session.scalars(
            select(ARReceiptRecord)
            .where(
                ARReceiptRecord.customer_id == customer_id,
                ARReceiptRecord.tenant_id == self._tenant_id,
            )
            .order_by(ARReceiptRecord.created_at, ARReceiptRecord.id)
        ).all()
        return [self._receipt_domain(record) for record in records]

    def add_receipt_allocation(self, allocation: ARReceiptAllocation) -> None:
        self._require_tenant(allocation.tenant_id)
        self._session.add(
            ARReceiptAllocationRecord(
                id=allocation.id,
                tenant_id=allocation.tenant_id,
                receipt_id=allocation.receipt_id,
                ar_invoice_id=allocation.ar_invoice_id,
                amount=allocation.amount,
                allocation_key=allocation.allocation_key,
                created_at=allocation.created_at,
                version=allocation.version,
            )
        )

    def get_receipt_allocation_by_key(
        self, allocation_key: UUID
    ) -> ARReceiptAllocation | None:
        record = self._session.scalar(
            select(ARReceiptAllocationRecord).where(
                ARReceiptAllocationRecord.tenant_id == self._tenant_id,
                ARReceiptAllocationRecord.allocation_key == allocation_key,
            )
        )
        return self._receipt_allocation_domain(record) if record else None

    def list_receipt_allocations(
        self, receipt_id: UUID
    ) -> list[ARReceiptAllocation]:
        records = self._session.scalars(
            select(ARReceiptAllocationRecord)
            .where(
                ARReceiptAllocationRecord.tenant_id == self._tenant_id,
                ARReceiptAllocationRecord.receipt_id == receipt_id,
            )
            .order_by(
                ARReceiptAllocationRecord.created_at,
                ARReceiptAllocationRecord.id,
            )
        ).all()
        return [self._receipt_allocation_domain(record) for record in records]

    def add_realized_fx_event(self, event: RealizedFxEvent) -> None:
        self._require_tenant(event.tenant_id)
        self._session.add(
            RealizedFxEventRecord(
                id=event.id,
                tenant_id=event.tenant_id,
                source_type=event.source_type,
                source_id=event.source_id,
                amount=event.amount,
                currency=event.currency,
                side=event.side.value,
                receipt_id=event.receipt_id,
                invoice_id=event.invoice_id,
                created_at=event.created_at,
                version=event.version,
            )
        )

    def get_realized_fx_event(self, event_id: UUID) -> RealizedFxEvent | None:
        record = self._session.get(RealizedFxEventRecord, event_id)
        if record is None or record.tenant_id != self._tenant_id:
            return None
        return self._realized_fx_event_domain(record)

    def get_realized_fx_event_by_source(
        self, source_id: UUID
    ) -> RealizedFxEvent | None:
        record = self._session.scalar(
            select(RealizedFxEventRecord).where(
                RealizedFxEventRecord.tenant_id == self._tenant_id,
                RealizedFxEventRecord.source_type == "allocation",
                RealizedFxEventRecord.source_id == source_id,
            )
        )
        return self._realized_fx_event_domain(record) if record else None

    def add_ar_write_off(self, write_off: ARWriteOff) -> None:
        self._require_tenant(write_off.tenant_id)
        self._session.add(
            ARWriteOffRecord(
                id=write_off.id,
                tenant_id=write_off.tenant_id,
                ar_invoice_id=write_off.ar_invoice_id,
                amount=write_off.amount,
                currency=write_off.currency,
                idempotency_key=write_off.idempotency_key,
                reason=write_off.reason,
                created_at=write_off.created_at,
                version=write_off.version,
            )
        )

    def get_ar_write_off_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ARWriteOff | None:
        record = self._session.scalar(
            select(ARWriteOffRecord).where(
                ARWriteOffRecord.tenant_id == self._tenant_id,
                ARWriteOffRecord.idempotency_key == idempotency_key,
            )
        )
        return self._ar_write_off_domain(record) if record else None

    def list_ar_write_offs(self, invoice_id: UUID) -> list[ARWriteOff]:
        records = self._session.scalars(
            select(ARWriteOffRecord)
            .where(
                ARWriteOffRecord.tenant_id == self._tenant_id,
                ARWriteOffRecord.ar_invoice_id == invoice_id,
            )
            .order_by(ARWriteOffRecord.created_at, ARWriteOffRecord.id)
        ).all()
        return [self._ar_write_off_domain(record) for record in records]

    def get_receipt_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ARReceipt | None:
        record = self._session.scalar(
            select(ARReceiptRecord).where(
                ARReceiptRecord.idempotency_key == idempotency_key,
                ARReceiptRecord.tenant_id == self._tenant_id,
            )
        )
        return self._receipt_domain(record) if record is not None else None

    def get_receipt_psp_policy(self) -> TenantReceiptPspPolicy | None:
        record = self._session.get(
            TenantReceiptPspPolicyRecord, self._tenant_id
        )
        if record is None:
            return None
        return TenantReceiptPspPolicy(
            tenant_id=record.tenant_id,
            receipt_psp_required=record.receipt_psp_required,
            updated_at=record.updated_at,
            version=record.version,
        )

    def save_receipt_psp_policy(
        self,
        policy: TenantReceiptPspPolicy,
        *,
        expected_version: int,
    ) -> None:
        self._require_tenant(policy.tenant_id)
        if expected_version == 0:
            self._session.add(
                TenantReceiptPspPolicyRecord(
                    tenant_id=policy.tenant_id,
                    receipt_psp_required=policy.receipt_psp_required,
                    updated_at=policy.updated_at,
                    version=policy.version,
                )
            )
            return
        result = self._session.execute(
            update(TenantReceiptPspPolicyRecord)
            .where(
                TenantReceiptPspPolicyRecord.tenant_id == self._tenant_id,
                TenantReceiptPspPolicyRecord.version == expected_version,
            )
            .values(
                receipt_psp_required=policy.receipt_psp_required,
                updated_at=policy.updated_at,
                version=policy.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("receipt PSP policy version conflict")

    def get_tax_authority_policy(self) -> TenantTaxAuthorityPolicy | None:
        record = self._session.get(
            TenantTaxAuthorityPolicyRecord, self._tenant_id
        )
        if record is None:
            return None
        return TenantTaxAuthorityPolicy(
            tenant_id=record.tenant_id,
            tax_authority_required=record.tax_authority_required,
            updated_at=record.updated_at,
            version=record.version,
        )

    def save_tax_authority_policy(
        self,
        policy: TenantTaxAuthorityPolicy,
        *,
        expected_version: int,
    ) -> None:
        self._require_tenant(policy.tenant_id)
        if expected_version == 0:
            self._session.add(
                TenantTaxAuthorityPolicyRecord(
                    tenant_id=policy.tenant_id,
                    tax_authority_required=policy.tax_authority_required,
                    updated_at=policy.updated_at,
                    version=policy.version,
                )
            )
            return
        result = self._session.execute(
            update(TenantTaxAuthorityPolicyRecord)
            .where(
                TenantTaxAuthorityPolicyRecord.tenant_id == self._tenant_id,
                TenantTaxAuthorityPolicyRecord.version == expected_version,
            )
            .values(
                tax_authority_required=policy.tax_authority_required,
                updated_at=policy.updated_at,
                version=policy.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("tax authority policy version conflict")

    def add_tax_rate(self, tax_rate: TaxRate) -> None:
        self._require_tenant(tax_rate.tenant_id)
        self._session.add(self._tax_rate_record(tax_rate))

    def save_tax_rate(
        self, tax_rate: TaxRate, *, expected_version: int
    ) -> None:
        self._require_tenant(tax_rate.tenant_id)
        result = self._session.execute(
            update(TaxRateRecord)
            .where(
                TaxRateRecord.id == tax_rate.id,
                TaxRateRecord.tenant_id == self._tenant_id,
                TaxRateRecord.version == expected_version,
            )
            .values(
                tax_name=tax_rate.tax_name,
                rate_percent=tax_rate.rate_percent,
                status=tax_rate.status.value,
                updated_at=tax_rate.updated_at,
                version=tax_rate.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("tax rate version conflict")

    def get_tax_rate(self, tax_rate_id: UUID) -> TaxRate | None:
        record = self._session.scalar(
            select(TaxRateRecord).where(
                TaxRateRecord.id == tax_rate_id,
                TaxRateRecord.tenant_id == self._tenant_id,
            )
        )
        return self._tax_rate_domain(record) if record is not None else None

    def get_tax_rate_by_code(self, tax_code: str) -> TaxRate | None:
        record = self._session.scalar(
            select(TaxRateRecord).where(
                TaxRateRecord.tax_code == tax_code,
                TaxRateRecord.tenant_id == self._tenant_id,
            )
        )
        return self._tax_rate_domain(record) if record is not None else None

    def add_credit_note(self, credit_note: ARCreditNote) -> None:
        self._require_tenant(credit_note.tenant_id)
        self._session.add(self._credit_note_record(credit_note))

    def save_credit_note(
        self, credit_note: ARCreditNote, *, expected_version: int
    ) -> None:
        self._require_tenant(credit_note.tenant_id)
        result = self._session.execute(
            update(ARCreditNoteRecord)
            .where(
                ARCreditNoteRecord.id == credit_note.id,
                ARCreditNoteRecord.tenant_id == self._tenant_id,
                ARCreditNoteRecord.version == expected_version,
            )
            .values(
                status=credit_note.status.value,
                issued_at=credit_note.issued_at,
                issue_key=credit_note.issue_key,
                version=credit_note.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("credit note version conflict")

    def get_credit_note(self, credit_note_id: UUID) -> ARCreditNote | None:
        record = self._session.scalar(
            select(ARCreditNoteRecord).where(
                ARCreditNoteRecord.id == credit_note_id,
                ARCreditNoteRecord.tenant_id == self._tenant_id,
            )
        )
        return self._credit_note_domain(record) if record is not None else None

    def get_credit_note_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ARCreditNote | None:
        record = self._session.scalar(
            select(ARCreditNoteRecord).where(
                ARCreditNoteRecord.idempotency_key == idempotency_key,
                ARCreditNoteRecord.tenant_id == self._tenant_id,
            )
        )
        return self._credit_note_domain(record) if record is not None else None

    def add_ar_refund(self, refund: ARRefund) -> None:
        self._require_tenant(refund.tenant_id)
        self._session.add(self._ar_refund_record(refund))

    def save_ar_refund(
        self, refund: ARRefund, *, expected_version: int
    ) -> None:
        self._require_tenant(refund.tenant_id)
        result = self._session.execute(
            update(ARRefundRecord)
            .where(
                ARRefundRecord.id == refund.id,
                ARRefundRecord.tenant_id == self._tenant_id,
                ARRefundRecord.version == expected_version,
            )
            .values(
                status=refund.status.value,
                posted_at=refund.posted_at,
                post_key=refund.post_key,
                version=refund.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("AR refund version conflict")

    def get_ar_refund(self, refund_id: UUID) -> ARRefund | None:
        record = self._session.scalar(
            select(ARRefundRecord).where(
                ARRefundRecord.id == refund_id,
                ARRefundRecord.tenant_id == self._tenant_id,
            )
        )
        return self._ar_refund_domain(record) if record is not None else None

    def get_ar_refund_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ARRefund | None:
        record = self._session.scalar(
            select(ARRefundRecord).where(
                ARRefundRecord.idempotency_key == idempotency_key,
                ARRefundRecord.tenant_id == self._tenant_id,
            )
        )
        return self._ar_refund_domain(record) if record is not None else None

    def add_treasury_transfer(self, transfer: TreasuryTransfer) -> None:
        self._require_tenant(transfer.tenant_id)
        self._session.add(self._treasury_transfer_record(transfer))

    def save_treasury_transfer(
        self, transfer: TreasuryTransfer, *, expected_version: int
    ) -> None:
        self._require_tenant(transfer.tenant_id)
        result = self._session.execute(
            update(TreasuryTransferRecord)
            .where(
                TreasuryTransferRecord.id == transfer.id,
                TreasuryTransferRecord.tenant_id == self._tenant_id,
                TreasuryTransferRecord.version == expected_version,
            )
            .values(
                status=transfer.status.value,
                posted_at=transfer.posted_at,
                post_key=transfer.post_key,
                version=transfer.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("treasury transfer version conflict")

    def get_treasury_transfer(
        self, transfer_id: UUID
    ) -> TreasuryTransfer | None:
        record = self._session.scalar(
            select(TreasuryTransferRecord).where(
                TreasuryTransferRecord.id == transfer_id,
                TreasuryTransferRecord.tenant_id == self._tenant_id,
            )
        )
        return (
            self._treasury_transfer_domain(record)
            if record is not None
            else None
        )

    def get_treasury_transfer_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> TreasuryTransfer | None:
        record = self._session.scalar(
            select(TreasuryTransferRecord).where(
                TreasuryTransferRecord.idempotency_key == idempotency_key,
                TreasuryTransferRecord.tenant_id == self._tenant_id,
            )
        )
        return (
            self._treasury_transfer_domain(record)
            if record is not None
            else None
        )

    def add_commission(self, entry: CommissionEntry) -> None:
        self._require_tenant(entry.tenant_id)
        self._session.add(self._commission_record(entry))

    def save_commission(
        self, entry: CommissionEntry, *, expected_version: int
    ) -> None:
        self._require_tenant(entry.tenant_id)
        result = self._session.execute(
            update(CommissionEntryRecord)
            .where(
                CommissionEntryRecord.id == entry.id,
                CommissionEntryRecord.tenant_id == self._tenant_id,
                CommissionEntryRecord.version == expected_version,
            )
            .values(status=entry.status.value, version=entry.version)
        )
        if result.rowcount != 1:
            raise ValueError("commission version conflict")

    def get_commission(self, commission_id: UUID) -> CommissionEntry | None:
        record = self._session.scalar(
            select(CommissionEntryRecord).where(
                CommissionEntryRecord.id == commission_id,
                CommissionEntryRecord.tenant_id == self._tenant_id,
            )
        )
        return (
            self._commission_domain(record) if record is not None else None
        )

    def get_commission_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> CommissionEntry | None:
        record = self._session.scalar(
            select(CommissionEntryRecord).where(
                CommissionEntryRecord.idempotency_key == idempotency_key,
                CommissionEntryRecord.tenant_id == self._tenant_id,
            )
        )
        return (
            self._commission_domain(record) if record is not None else None
        )

    def get_commission_by_invoice_beneficiary(
        self, invoice_id: UUID, beneficiary_subject_id: UUID
    ) -> CommissionEntry | None:
        record = self._session.scalar(
            select(CommissionEntryRecord).where(
                CommissionEntryRecord.source_invoice_id == invoice_id,
                CommissionEntryRecord.beneficiary_subject_id
                == beneficiary_subject_id,
                CommissionEntryRecord.tenant_id == self._tenant_id,
            )
        )
        return (
            self._commission_domain(record) if record is not None else None
        )

    def add_tax_invoice(self, tax_invoice: TaxInvoice) -> None:
        self._require_tenant(tax_invoice.tenant_id)
        self._session.add(self._tax_invoice_record(tax_invoice))

    def save_tax_invoice(
        self, tax_invoice: TaxInvoice, *, expected_version: int
    ) -> None:
        self._require_tenant(tax_invoice.tenant_id)
        result = self._session.execute(
            update(TaxInvoiceRecord)
            .where(
                TaxInvoiceRecord.id == tax_invoice.id,
                TaxInvoiceRecord.tenant_id == self._tenant_id,
                TaxInvoiceRecord.version == expected_version,
            )
            .values(
                status=tax_invoice.status.value,
                issued_at=tax_invoice.issued_at,
                issue_key=tax_invoice.issue_key,
                voided_at=tax_invoice.voided_at,
                void_key=tax_invoice.void_key,
                void_reason=tax_invoice.void_reason,
                tax_code=tax_invoice.tax_code,
                authority_ref=tax_invoice.authority_ref,
                authority_status=tax_invoice.authority_status,
                original_tax_invoice_id=tax_invoice.original_tax_invoice_id,
                is_red_credit=tax_invoice.is_red_credit,
                version=tax_invoice.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("tax invoice version conflict")

    def get_tax_invoice(self, tax_invoice_id: UUID) -> TaxInvoice | None:
        record = self._session.scalar(
            select(TaxInvoiceRecord).where(
                TaxInvoiceRecord.id == tax_invoice_id,
                TaxInvoiceRecord.tenant_id == self._tenant_id,
            )
        )
        return self._tax_invoice_domain(record) if record is not None else None

    def get_tax_invoice_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> TaxInvoice | None:
        record = self._session.scalar(
            select(TaxInvoiceRecord).where(
                TaxInvoiceRecord.idempotency_key == idempotency_key,
                TaxInvoiceRecord.tenant_id == self._tenant_id,
            )
        )
        return self._tax_invoice_domain(record) if record is not None else None

    def get_red_credit_by_original_tax_invoice(
        self, original_tax_invoice_id: UUID
    ) -> TaxInvoice | None:
        record = self._session.scalar(
            select(TaxInvoiceRecord).where(
                TaxInvoiceRecord.original_tax_invoice_id
                == original_tax_invoice_id,
                TaxInvoiceRecord.is_red_credit.is_(True),
                TaxInvoiceRecord.tenant_id == self._tenant_id,
            )
        )
        return self._tax_invoice_domain(record) if record is not None else None

    def add_tax_credit_link(self, link: TaxCreditLink) -> None:
        self._require_tenant(link.tenant_id)
        self._session.add(self._tax_credit_link_record(link))

    def get_tax_credit_link(self, link_id: UUID) -> TaxCreditLink | None:
        record = self._session.scalar(
            select(TaxCreditLinkRecord).where(
                TaxCreditLinkRecord.id == link_id,
                TaxCreditLinkRecord.tenant_id == self._tenant_id,
            )
        )
        return self._tax_credit_link_domain(record) if record is not None else None

    def get_tax_credit_link_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> TaxCreditLink | None:
        record = self._session.scalar(
            select(TaxCreditLinkRecord).where(
                TaxCreditLinkRecord.idempotency_key == idempotency_key,
                TaxCreditLinkRecord.tenant_id == self._tenant_id,
            )
        )
        return self._tax_credit_link_domain(record) if record is not None else None

    def add_gl_account(self, account: GlAccount) -> None:
        self._require_tenant(account.tenant_id)
        self._session.add(self._gl_account_record(account))

    def save_gl_account(
        self, account: GlAccount, *, expected_version: int
    ) -> None:
        self._require_tenant(account.tenant_id)
        result = self._session.execute(
            update(GlAccountRecord)
            .where(
                GlAccountRecord.id == account.id,
                GlAccountRecord.tenant_id == self._tenant_id,
                GlAccountRecord.version == expected_version,
            )
            .values(
                name=account.name,
                status=account.status.value,
                version=account.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("gl account version conflict")

    def get_gl_account(self, account_id: UUID) -> GlAccount | None:
        record = self._session.scalar(
            select(GlAccountRecord).where(
                GlAccountRecord.id == account_id,
                GlAccountRecord.tenant_id == self._tenant_id,
            )
        )
        return self._gl_account_domain(record) if record is not None else None

    def get_gl_account_by_code(self, code: str) -> GlAccount | None:
        record = self._session.scalar(
            select(GlAccountRecord).where(
                GlAccountRecord.code == code,
                GlAccountRecord.tenant_id == self._tenant_id,
            )
        )
        return self._gl_account_domain(record) if record is not None else None

    def add_gl_period(self, period: GlPeriod) -> None:
        self._require_tenant(period.tenant_id)
        self._session.add(self._gl_period_record(period))

    def save_gl_period(
        self, period: GlPeriod, *, expected_version: int
    ) -> None:
        self._require_tenant(period.tenant_id)
        result = self._session.execute(
            update(GlPeriodRecord)
            .where(
                GlPeriodRecord.id == period.id,
                GlPeriodRecord.tenant_id == self._tenant_id,
                GlPeriodRecord.version == expected_version,
            )
            .values(
                status=period.status.value,
                closed_at=period.closed_at,
                close_key=period.close_key,
                version=period.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("gl period version conflict")

    def get_gl_period(self, period_id: UUID) -> GlPeriod | None:
        record = self._session.scalar(
            select(GlPeriodRecord).where(
                GlPeriodRecord.id == period_id,
                GlPeriodRecord.tenant_id == self._tenant_id,
            )
        )
        return self._gl_period_domain(record) if record is not None else None

    def get_gl_period_by_code(self, code: str) -> GlPeriod | None:
        record = self._session.scalar(
            select(GlPeriodRecord).where(
                GlPeriodRecord.code == code,
                GlPeriodRecord.tenant_id == self._tenant_id,
            )
        )
        return self._gl_period_domain(record) if record is not None else None

    def list_gl_periods(self) -> list[GlPeriod]:
        records = self._session.scalars(
            select(GlPeriodRecord).where(
                GlPeriodRecord.tenant_id == self._tenant_id
            )
        )
        return [self._gl_period_domain(record) for record in records]

    def add_journal_entry(self, entry: JournalEntry) -> None:
        self._require_tenant(entry.tenant_id)
        self._session.add(self._journal_entry_record(entry))
        for index, line in enumerate(entry.lines, start=1):
            self._session.add(
                JournalLineRecord(
                    id=line.id,
                    tenant_id=entry.tenant_id,
                    journal_entry_id=entry.id,
                    account_id=line.account_id,
                    debit=line.debit,
                    credit=line.credit,
                    line_no=index,
                )
            )

    def save_journal_entry(
        self, entry: JournalEntry, *, expected_version: int
    ) -> None:
        self._require_tenant(entry.tenant_id)
        result = self._session.execute(
            update(JournalEntryRecord)
            .where(
                JournalEntryRecord.id == entry.id,
                JournalEntryRecord.tenant_id == self._tenant_id,
                JournalEntryRecord.version == expected_version,
            )
            .values(
                status=entry.status.value,
                posted_at=entry.posted_at,
                post_key=entry.post_key,
                version=entry.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("journal entry version conflict")

    def get_journal_entry(self, entry_id: UUID) -> JournalEntry | None:
        record = self._session.scalar(
            select(JournalEntryRecord).where(
                JournalEntryRecord.id == entry_id,
                JournalEntryRecord.tenant_id == self._tenant_id,
            )
        )
        if record is None:
            return None
        return self._journal_entry_domain(record, self._journal_lines(entry_id))

    def get_journal_entry_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> JournalEntry | None:
        record = self._session.scalar(
            select(JournalEntryRecord).where(
                JournalEntryRecord.idempotency_key == idempotency_key,
                JournalEntryRecord.tenant_id == self._tenant_id,
            )
        )
        if record is None:
            return None
        return self._journal_entry_domain(
            record, self._journal_lines(record.id)
        )

    def get_journal_line(self, line_id: UUID) -> JournalLine | None:
        record = self._session.scalar(
            select(JournalLineRecord).where(
                JournalLineRecord.id == line_id,
                JournalLineRecord.tenant_id == self._tenant_id,
            )
        )
        if record is None:
            return None
        return JournalLine(
            id=record.id,
            account_id=record.account_id,
            debit=record.debit,
            credit=record.credit,
        )

    def get_gl_bridge_map(self) -> GlBridgeMap | None:
        record = self._session.get(GlBridgeMapRecord, self._tenant_id)
        if record is None:
            return None
        return self._gl_bridge_map_domain(record)

    def save_gl_bridge_map(
        self, bridge_map: GlBridgeMap, *, expected_version: int
    ) -> None:
        self._require_tenant(bridge_map.tenant_id)
        current = self.get_gl_bridge_map()
        if current is None:
            if expected_version != 0:
                raise ValueError("gl bridge map version conflict")
            self._session.add(self._gl_bridge_map_record(bridge_map))
            return
        result = self._session.execute(
            update(GlBridgeMapRecord)
            .where(
                GlBridgeMapRecord.tenant_id == self._tenant_id,
                GlBridgeMapRecord.version == expected_version,
            )
            .values(
                ar_control=bridge_map.ar_control,
                cash=bridge_map.cash,
                revenue=bridge_map.revenue,
                tax_payable=bridge_map.tax_payable,
                commission_expense=bridge_map.commission_expense,
                commission_payable=bridge_map.commission_payable,
                fx_gain=bridge_map.fx_gain,
                fx_loss=bridge_map.fx_loss,
                ap_control=bridge_map.ap_control,
                ap_expense=bridge_map.ap_expense,
                updated_at=bridge_map.updated_at,
                version=bridge_map.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("gl bridge map version conflict")

    def add_gl_bridge_posting(self, posting: GlBridgePosting) -> None:
        self._require_tenant(posting.tenant_id)
        self._session.add(self._gl_bridge_posting_record(posting))

    def get_gl_bridge_posting_by_source(
        self, source_type: GlBridgeSourceType, source_id: UUID
    ) -> GlBridgePosting | None:
        record = self._session.scalar(
            select(GlBridgePostingRecord).where(
                GlBridgePostingRecord.tenant_id == self._tenant_id,
                GlBridgePostingRecord.source_type == source_type.value,
                GlBridgePostingRecord.source_id == source_id,
            )
        )
        return (
            self._gl_bridge_posting_domain(record) if record is not None else None
        )

    def get_gl_bridge_posting_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> GlBridgePosting | None:
        record = self._session.scalar(
            select(GlBridgePostingRecord).where(
                GlBridgePostingRecord.tenant_id == self._tenant_id,
                GlBridgePostingRecord.idempotency_key == idempotency_key,
            )
        )
        return (
            self._gl_bridge_posting_domain(record) if record is not None else None
        )

    def add_gl_fx_revaluation(self, revaluation: GlFxRevaluation) -> None:
        self._require_tenant(revaluation.tenant_id)
        self._session.add(self._gl_fx_revaluation_record(revaluation))

    def save_gl_fx_revaluation(
        self, revaluation: GlFxRevaluation, *, expected_version: int
    ) -> None:
        self._require_tenant(revaluation.tenant_id)
        result = self._session.execute(
            update(GlFxRevaluationRecord)
            .where(
                GlFxRevaluationRecord.id == revaluation.id,
                GlFxRevaluationRecord.tenant_id == self._tenant_id,
                GlFxRevaluationRecord.version == expected_version,
            )
            .values(
                status=revaluation.status.value,
                journal_entry_id=revaluation.journal_entry_id,
                posted_at=revaluation.posted_at,
                post_key=revaluation.post_key,
                version=revaluation.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("gl fx revaluation version conflict")

    def get_gl_fx_revaluation(
        self, revaluation_id: UUID
    ) -> GlFxRevaluation | None:
        record = self._session.scalar(
            select(GlFxRevaluationRecord).where(
                GlFxRevaluationRecord.id == revaluation_id,
                GlFxRevaluationRecord.tenant_id == self._tenant_id,
            )
        )
        return (
            self._gl_fx_revaluation_domain(record)
            if record is not None
            else None
        )

    def get_gl_fx_revaluation_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> GlFxRevaluation | None:
        record = self._session.scalar(
            select(GlFxRevaluationRecord).where(
                GlFxRevaluationRecord.idempotency_key == idempotency_key,
                GlFxRevaluationRecord.tenant_id == self._tenant_id,
            )
        )
        return (
            self._gl_fx_revaluation_domain(record)
            if record is not None
            else None
        )

    def add_bank_statement(self, statement: BankStatement) -> None:
        self._require_tenant(statement.tenant_id)
        self._session.add(self._bank_statement_record(statement))
        for index, line in enumerate(statement.lines, start=1):
            self._session.add(
                BankStatementLineRecord(
                    id=line.id,
                    tenant_id=statement.tenant_id,
                    statement_id=statement.id,
                    amount=line.amount,
                    description=line.description,
                    status=line.status.value,
                    matched_journal_line_id=line.matched_journal_line_id,
                    matched_receipt_id=line.matched_receipt_id,
                    line_no=index,
                )
            )

    def save_bank_statement(
        self, statement: BankStatement, *, expected_version: int
    ) -> None:
        self._require_tenant(statement.tenant_id)
        result = self._session.execute(
            update(BankStatementRecord)
            .where(
                BankStatementRecord.id == statement.id,
                BankStatementRecord.tenant_id == self._tenant_id,
                BankStatementRecord.version == expected_version,
            )
            .values(
                status=statement.status.value,
                cleared_at=statement.cleared_at,
                version=statement.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("bank statement version conflict")
        for line in statement.lines:
            line_result = self._session.execute(
                update(BankStatementLineRecord)
                .where(
                    BankStatementLineRecord.id == line.id,
                    BankStatementLineRecord.tenant_id == self._tenant_id,
                    BankStatementLineRecord.statement_id == statement.id,
                )
                .values(
                    status=line.status.value,
                    matched_journal_line_id=line.matched_journal_line_id,
                    matched_receipt_id=line.matched_receipt_id,
                )
            )
            if line_result.rowcount != 1:
                raise ValueError("bank statement line update conflict")

    def get_bank_statement(
        self, statement_id: UUID
    ) -> BankStatement | None:
        record = self._session.scalar(
            select(BankStatementRecord).where(
                BankStatementRecord.id == statement_id,
                BankStatementRecord.tenant_id == self._tenant_id,
            )
        )
        if record is None:
            return None
        return self._bank_statement_domain(
            record, self._bank_statement_lines(statement_id)
        )

    def _bank_statement_lines(
        self, statement_id: UUID
    ) -> list[BankStatementLine]:
        records = self._session.scalars(
            select(BankStatementLineRecord)
            .where(
                BankStatementLineRecord.statement_id == statement_id,
                BankStatementLineRecord.tenant_id == self._tenant_id,
            )
            .order_by(BankStatementLineRecord.line_no)
        ).all()
        return [
            BankStatementLine(
                id=record.id,
                statement_id=record.statement_id,
                amount=record.amount,
                description=record.description,
                status=BankStatementLineStatus(record.status),
                matched_journal_line_id=record.matched_journal_line_id,
                matched_receipt_id=record.matched_receipt_id,
            )
            for record in records
        ]

    def _journal_lines(self, entry_id: UUID) -> list[JournalLine]:
        records = self._session.scalars(
            select(JournalLineRecord)
            .where(
                JournalLineRecord.journal_entry_id == entry_id,
                JournalLineRecord.tenant_id == self._tenant_id,
            )
            .order_by(JournalLineRecord.line_no, JournalLineRecord.id)
        ).all()
        return [
            JournalLine(
                id=record.id,
                account_id=record.account_id,
                debit=record.debit,
                credit=record.credit,
            )
            for record in records
        ]

    def _require_tenant(self, tenant_id: UUID) -> None:
        if tenant_id != self._tenant_id:
            raise ValueError("Finance record is outside repository tenant")

    @staticmethod
    def _receipt_record(receipt: ARReceipt) -> ARReceiptRecord:
        return ARReceiptRecord(
            id=receipt.id,
            tenant_id=receipt.tenant_id,
            customer_id=receipt.customer_id,
            code=receipt.code,
            currency=receipt.currency,
            amount=receipt.amount,
            functional_currency=receipt.functional_currency,
            fx_rate=receipt.fx_rate,
            functional_amount=receipt.functional_amount,
            allocated_amount=receipt.allocated_amount,
            idempotency_key=receipt.idempotency_key,
            status=receipt.status.value,
            created_at=receipt.created_at,
            ar_invoice_id=receipt.ar_invoice_id,
            ar_invoice_version=receipt.ar_invoice_version,
            apply_key=receipt.apply_key,
            applied_at=receipt.applied_at,
            psp_ref=receipt.psp_ref,
            psp_status=receipt.psp_status,
            version=receipt.version,
        )

    @staticmethod
    def _receipt_domain(record: ARReceiptRecord) -> ARReceipt:
        return ARReceipt(
            id=record.id,
            tenant_id=record.tenant_id,
            customer_id=record.customer_id,
            code=record.code,
            currency=record.currency,
            amount=record.amount,
            functional_currency=record.functional_currency,
            fx_rate=record.fx_rate,
            functional_amount=record.functional_amount,
            allocated_amount=record.allocated_amount,
            idempotency_key=record.idempotency_key,
            status=ReceiptStatus(record.status),
            created_at=record.created_at,
            ar_invoice_id=record.ar_invoice_id,
            ar_invoice_version=record.ar_invoice_version,
            apply_key=record.apply_key,
            applied_at=record.applied_at,
            psp_ref=record.psp_ref,
            psp_status=record.psp_status,
            version=record.version,
        )

    @staticmethod
    def _receipt_allocation_domain(
        record: ARReceiptAllocationRecord,
    ) -> ARReceiptAllocation:
        return ARReceiptAllocation(
            id=record.id,
            tenant_id=record.tenant_id,
            receipt_id=record.receipt_id,
            ar_invoice_id=record.ar_invoice_id,
            amount=record.amount,
            allocation_key=record.allocation_key,
            created_at=record.created_at,
            version=record.version,
        )

    @staticmethod
    def _realized_fx_event_domain(
        record: RealizedFxEventRecord,
    ) -> RealizedFxEvent:
        return RealizedFxEvent(
            id=record.id,
            tenant_id=record.tenant_id,
            source_type=record.source_type,
            source_id=record.source_id,
            amount=record.amount,
            currency=record.currency,
            side=RealizedFxSide(record.side),
            receipt_id=record.receipt_id,
            invoice_id=record.invoice_id,
            created_at=record.created_at,
            version=record.version,
        )

    @staticmethod
    def _ar_write_off_domain(record: ARWriteOffRecord) -> ARWriteOff:
        return ARWriteOff(
            id=record.id,
            tenant_id=record.tenant_id,
            ar_invoice_id=record.ar_invoice_id,
            amount=record.amount,
            currency=record.currency,
            idempotency_key=record.idempotency_key,
            reason=record.reason,
            created_at=record.created_at,
            version=record.version,
        )

    @staticmethod
    def _credit_note_record(credit_note: ARCreditNote) -> ARCreditNoteRecord:
        return ARCreditNoteRecord(
            id=credit_note.id,
            tenant_id=credit_note.tenant_id,
            customer_id=credit_note.customer_id,
            ar_invoice_id=credit_note.ar_invoice_id,
            ar_invoice_version=credit_note.ar_invoice_version,
            code=credit_note.code,
            currency=credit_note.currency,
            amount=credit_note.amount,
            idempotency_key=credit_note.idempotency_key,
            status=credit_note.status.value,
            created_at=credit_note.created_at,
            issued_at=credit_note.issued_at,
            issue_key=credit_note.issue_key,
            version=credit_note.version,
        )

    @staticmethod
    def _credit_note_domain(record: ARCreditNoteRecord) -> ARCreditNote:
        return ARCreditNote(
            id=record.id,
            tenant_id=record.tenant_id,
            customer_id=record.customer_id,
            ar_invoice_id=record.ar_invoice_id,
            ar_invoice_version=record.ar_invoice_version,
            code=record.code,
            currency=record.currency,
            amount=record.amount,
            idempotency_key=record.idempotency_key,
            status=CreditNoteStatus(record.status),
            created_at=record.created_at,
            issued_at=record.issued_at,
            issue_key=record.issue_key,
            version=record.version,
        )

    @staticmethod
    def _ar_refund_record(refund: ARRefund) -> ARRefundRecord:
        return ARRefundRecord(
            id=refund.id,
            tenant_id=refund.tenant_id,
            credit_note_id=refund.credit_note_id,
            customer_id=refund.customer_id,
            currency=refund.currency,
            amount=refund.amount,
            idempotency_key=refund.idempotency_key,
            status=refund.status.value,
            created_at=refund.created_at,
            posted_at=refund.posted_at,
            post_key=refund.post_key,
            version=refund.version,
        )

    @staticmethod
    def _ar_refund_domain(record: ARRefundRecord) -> ARRefund:
        return ARRefund(
            id=record.id,
            tenant_id=record.tenant_id,
            credit_note_id=record.credit_note_id,
            customer_id=record.customer_id,
            currency=record.currency,
            amount=record.amount,
            idempotency_key=record.idempotency_key,
            status=ARRefundStatus(record.status),
            created_at=record.created_at,
            posted_at=record.posted_at,
            post_key=record.post_key,
            version=record.version,
        )

    @staticmethod
    def _treasury_transfer_record(
        transfer: TreasuryTransfer,
    ) -> TreasuryTransferRecord:
        return TreasuryTransferRecord(
            id=transfer.id,
            tenant_id=transfer.tenant_id,
            from_account_ref=transfer.from_account_ref,
            to_account_ref=transfer.to_account_ref,
            currency=transfer.currency,
            amount=transfer.amount,
            functional_currency=transfer.functional_currency,
            fx_rate=transfer.fx_rate,
            functional_amount=transfer.functional_amount,
            idempotency_key=transfer.idempotency_key,
            status=transfer.status.value,
            created_at=transfer.created_at,
            posted_at=transfer.posted_at,
            post_key=transfer.post_key,
            version=transfer.version,
        )

    @staticmethod
    def _treasury_transfer_domain(
        record: TreasuryTransferRecord,
    ) -> TreasuryTransfer:
        return TreasuryTransfer(
            id=record.id,
            tenant_id=record.tenant_id,
            from_account_ref=record.from_account_ref,
            to_account_ref=record.to_account_ref,
            currency=record.currency,
            amount=record.amount,
            functional_currency=record.functional_currency,
            fx_rate=record.fx_rate,
            functional_amount=record.functional_amount,
            idempotency_key=record.idempotency_key,
            status=TreasuryTransferStatus(record.status),
            created_at=record.created_at,
            posted_at=record.posted_at,
            post_key=record.post_key,
            version=record.version,
        )

    @staticmethod
    def _commission_record(entry: CommissionEntry) -> CommissionEntryRecord:
        return CommissionEntryRecord(
            id=entry.id,
            tenant_id=entry.tenant_id,
            source_invoice_id=entry.source_invoice_id,
            beneficiary_subject_id=entry.beneficiary_subject_id,
            code=entry.code,
            currency=entry.currency,
            amount=entry.amount,
            idempotency_key=entry.idempotency_key,
            status=entry.status.value,
            created_at=entry.created_at,
            version=entry.version,
        )

    @staticmethod
    def _commission_domain(record: CommissionEntryRecord) -> CommissionEntry:
        return CommissionEntry(
            id=record.id,
            tenant_id=record.tenant_id,
            source_invoice_id=record.source_invoice_id,
            beneficiary_subject_id=record.beneficiary_subject_id,
            code=record.code,
            currency=record.currency,
            amount=record.amount,
            idempotency_key=record.idempotency_key,
            status=CommissionStatus(record.status),
            created_at=record.created_at,
            version=record.version,
        )

    @staticmethod
    def _tax_rate_record(tax_rate: TaxRate) -> TaxRateRecord:
        return TaxRateRecord(
            id=tax_rate.id,
            tenant_id=tax_rate.tenant_id,
            tax_code=tax_rate.tax_code,
            tax_name=tax_rate.tax_name,
            rate_percent=tax_rate.rate_percent,
            status=tax_rate.status.value,
            created_at=tax_rate.created_at,
            updated_at=tax_rate.updated_at,
            version=tax_rate.version,
        )

    @staticmethod
    def _tax_rate_domain(record: TaxRateRecord) -> TaxRate:
        return TaxRate(
            id=record.id,
            tenant_id=record.tenant_id,
            tax_code=record.tax_code,
            tax_name=record.tax_name,
            rate_percent=record.rate_percent,
            status=TaxRateStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            version=record.version,
        )

    @staticmethod
    def _tax_invoice_record(tax_invoice: TaxInvoice) -> TaxInvoiceRecord:
        return TaxInvoiceRecord(
            id=tax_invoice.id,
            tenant_id=tax_invoice.tenant_id,
            customer_id=tax_invoice.customer_id,
            ar_invoice_id=tax_invoice.ar_invoice_id,
            ar_invoice_version=tax_invoice.ar_invoice_version,
            code=tax_invoice.code,
            currency=tax_invoice.currency,
            amount=tax_invoice.amount,
            idempotency_key=tax_invoice.idempotency_key,
            status=tax_invoice.status.value,
            created_at=tax_invoice.created_at,
            issued_at=tax_invoice.issued_at,
            issue_key=tax_invoice.issue_key,
            voided_at=tax_invoice.voided_at,
            void_key=tax_invoice.void_key,
            void_reason=tax_invoice.void_reason,
            tax_code=tax_invoice.tax_code,
            authority_ref=tax_invoice.authority_ref,
            authority_status=tax_invoice.authority_status,
            version=tax_invoice.version,
        )

    @staticmethod
    def _tax_invoice_domain(record: TaxInvoiceRecord) -> TaxInvoice:
        return TaxInvoice(
            id=record.id,
            tenant_id=record.tenant_id,
            customer_id=record.customer_id,
            ar_invoice_id=record.ar_invoice_id,
            ar_invoice_version=record.ar_invoice_version,
            code=record.code,
            currency=record.currency,
            amount=record.amount,
            idempotency_key=record.idempotency_key,
            status=TaxInvoiceStatus(record.status),
            created_at=record.created_at,
            issued_at=record.issued_at,
            issue_key=record.issue_key,
            voided_at=record.voided_at,
            void_key=record.void_key,
            void_reason=record.void_reason,
            tax_code=record.tax_code,
            authority_ref=record.authority_ref,
            authority_status=record.authority_status,
            original_tax_invoice_id=record.original_tax_invoice_id,
            is_red_credit=record.is_red_credit,
            version=record.version,
        )

    @staticmethod
    def _tax_credit_link_record(link: TaxCreditLink) -> TaxCreditLinkRecord:
        return TaxCreditLinkRecord(
            id=link.id,
            tenant_id=link.tenant_id,
            tax_invoice_id=link.tax_invoice_id,
            credit_note_id=link.credit_note_id,
            status=link.status,
            idempotency_key=link.idempotency_key,
            created_at=link.created_at,
            version=link.version,
        )

    @staticmethod
    def _tax_credit_link_domain(record: TaxCreditLinkRecord) -> TaxCreditLink:
        return TaxCreditLink(
            id=record.id,
            tenant_id=record.tenant_id,
            tax_invoice_id=record.tax_invoice_id,
            credit_note_id=record.credit_note_id,
            status=record.status,
            idempotency_key=record.idempotency_key,
            created_at=record.created_at,
            version=record.version,
        )

    @staticmethod
    def _gl_account_record(account: GlAccount) -> GlAccountRecord:
        return GlAccountRecord(
            id=account.id,
            tenant_id=account.tenant_id,
            code=account.code,
            name=account.name,
            account_type=account.account_type.value,
            status=account.status.value,
            created_at=account.created_at,
            version=account.version,
        )

    @staticmethod
    def _gl_account_domain(record: GlAccountRecord) -> GlAccount:
        return GlAccount(
            id=record.id,
            tenant_id=record.tenant_id,
            code=record.code,
            name=record.name,
            account_type=GlAccountType(record.account_type),
            status=GlAccountStatus(record.status),
            created_at=record.created_at,
            version=record.version,
        )

    @staticmethod
    def _gl_period_record(period: GlPeriod) -> GlPeriodRecord:
        return GlPeriodRecord(
            id=period.id,
            tenant_id=period.tenant_id,
            code=period.code,
            name=period.name,
            start_at=period.start_at,
            end_at=period.end_at,
            status=period.status.value,
            created_at=period.created_at,
            closed_at=period.closed_at,
            close_key=period.close_key,
            version=period.version,
        )

    @staticmethod
    def _gl_period_domain(record: GlPeriodRecord) -> GlPeriod:
        return GlPeriod(
            id=record.id,
            tenant_id=record.tenant_id,
            code=record.code,
            name=record.name,
            start_at=record.start_at,
            end_at=record.end_at,
            status=GlPeriodStatus(record.status),
            created_at=record.created_at,
            closed_at=record.closed_at,
            close_key=record.close_key,
            version=record.version,
        )

    @staticmethod
    def _journal_entry_record(entry: JournalEntry) -> JournalEntryRecord:
        return JournalEntryRecord(
            id=entry.id,
            tenant_id=entry.tenant_id,
            code=entry.code,
            currency=entry.currency,
            period_id=entry.period_id,
            memo=entry.memo,
            idempotency_key=entry.idempotency_key,
            status=entry.status.value,
            created_at=entry.created_at,
            posted_at=entry.posted_at,
            post_key=entry.post_key,
            version=entry.version,
        )

    @staticmethod
    def _journal_entry_domain(
        record: JournalEntryRecord, lines: list[JournalLine]
    ) -> JournalEntry:
        return JournalEntry(
            id=record.id,
            tenant_id=record.tenant_id,
            code=record.code,
            currency=record.currency,
            period_id=record.period_id,
            memo=record.memo,
            idempotency_key=record.idempotency_key,
            status=JournalEntryStatus(record.status),
            created_at=record.created_at,
            posted_at=record.posted_at,
            post_key=record.post_key,
            version=record.version,
            lines=lines,
        )

    @staticmethod
    def _gl_bridge_map_record(bridge_map: GlBridgeMap) -> GlBridgeMapRecord:
        return GlBridgeMapRecord(
            tenant_id=bridge_map.tenant_id,
            ar_control=bridge_map.ar_control,
            cash=bridge_map.cash,
            revenue=bridge_map.revenue,
            tax_payable=bridge_map.tax_payable,
            commission_expense=bridge_map.commission_expense,
            commission_payable=bridge_map.commission_payable,
            fx_gain=bridge_map.fx_gain,
            fx_loss=bridge_map.fx_loss,
            ap_control=bridge_map.ap_control,
            ap_expense=bridge_map.ap_expense,
            updated_at=bridge_map.updated_at,
            version=bridge_map.version,
        )

    @staticmethod
    def _gl_bridge_map_domain(record: GlBridgeMapRecord) -> GlBridgeMap:
        return GlBridgeMap(
            tenant_id=record.tenant_id,
            ar_control=record.ar_control,
            cash=record.cash,
            revenue=record.revenue,
            tax_payable=record.tax_payable,
            commission_expense=record.commission_expense,
            commission_payable=record.commission_payable,
            fx_gain=record.fx_gain,
            fx_loss=record.fx_loss,
            ap_control=record.ap_control,
            ap_expense=record.ap_expense,
            updated_at=record.updated_at,
            version=record.version,
        )

    @staticmethod
    def _gl_bridge_posting_record(
        posting: GlBridgePosting,
    ) -> GlBridgePostingRecord:
        return GlBridgePostingRecord(
            id=posting.id,
            tenant_id=posting.tenant_id,
            source_type=posting.source_type.value,
            source_id=posting.source_id,
            journal_entry_id=posting.journal_entry_id,
            idempotency_key=posting.idempotency_key,
            created_at=posting.created_at,
        )

    @staticmethod
    def _gl_bridge_posting_domain(
        record: GlBridgePostingRecord,
    ) -> GlBridgePosting:
        return GlBridgePosting(
            id=record.id,
            tenant_id=record.tenant_id,
            source_type=GlBridgeSourceType(record.source_type),
            source_id=record.source_id,
            journal_entry_id=record.journal_entry_id,
            idempotency_key=record.idempotency_key,
            created_at=record.created_at,
        )

    @staticmethod
    def _gl_fx_revaluation_record(
        revaluation: GlFxRevaluation,
    ) -> GlFxRevaluationRecord:
        return GlFxRevaluationRecord(
            id=revaluation.id,
            tenant_id=revaluation.tenant_id,
            period_id=revaluation.period_id,
            from_currency=revaluation.from_currency,
            to_currency=revaluation.to_currency,
            rate=revaluation.rate,
            amount=revaluation.amount,
            side=revaluation.side.value,
            idempotency_key=revaluation.idempotency_key,
            status=revaluation.status.value,
            created_at=revaluation.created_at,
            journal_entry_id=revaluation.journal_entry_id,
            posted_at=revaluation.posted_at,
            post_key=revaluation.post_key,
            version=revaluation.version,
        )

    @staticmethod
    def _gl_fx_revaluation_domain(
        record: GlFxRevaluationRecord,
    ) -> GlFxRevaluation:
        return GlFxRevaluation(
            id=record.id,
            tenant_id=record.tenant_id,
            period_id=record.period_id,
            from_currency=record.from_currency,
            to_currency=record.to_currency,
            rate=record.rate,
            amount=record.amount,
            side=GlFxRevaluationSide(record.side),
            idempotency_key=record.idempotency_key,
            status=GlFxRevaluationStatus(record.status),
            created_at=record.created_at,
            journal_entry_id=record.journal_entry_id,
            posted_at=record.posted_at,
            post_key=record.post_key,
            version=record.version,
        )

    @staticmethod
    def _bank_statement_record(statement: BankStatement) -> BankStatementRecord:
        return BankStatementRecord(
            id=statement.id,
            tenant_id=statement.tenant_id,
            account_ref=statement.account_ref,
            statement_date=statement.statement_date,
            currency=statement.currency,
            status=statement.status.value,
            created_at=statement.created_at,
            cleared_at=statement.cleared_at,
            version=statement.version,
        )

    @staticmethod
    def _bank_statement_domain(
        record: BankStatementRecord, lines: list[BankStatementLine]
    ) -> BankStatement:
        return BankStatement(
            id=record.id,
            tenant_id=record.tenant_id,
            account_ref=record.account_ref,
            statement_date=record.statement_date,
            currency=record.currency,
            status=BankStatementStatus(record.status),
            created_at=record.created_at,
            cleared_at=record.cleared_at,
            version=record.version,
            lines=lines,
        )


class TransactionalFinanceService:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        *,
        psp_port=None,
        tax_authority_port=None,
    ) -> None:
        self._session_factory = session_factory
        self._psp_port = psp_port
        self._tax_authority_port = tax_authority_port

    def create_receipt(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ARReceipt]:
        return self._execute(
            ctx, lambda service: service.create_receipt(ctx, **kwargs)
        )

    def apply_receipt_to_invoice(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ARReceipt]:
        return self._execute(
            ctx, lambda service: service.apply_receipt_to_invoice(ctx, **kwargs)
        )

    def get_receipt(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ARReceipt]:
        return self._execute(
            ctx, lambda service: service.get_receipt(ctx, **kwargs)
        )

    def get_customer_balance(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult:
        return self._execute(
            ctx, lambda service: service.get_customer_balance(ctx, **kwargs)
        )

    def create_ar_write_off(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ARWriteOff]:
        return self._execute(
            ctx, lambda service: service.create_ar_write_off(ctx, **kwargs)
        )

    def close_ar_invoice(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ARInvoiceSnapshot]:
        return self._execute(
            ctx, lambda service: service.close_ar_invoice(ctx, **kwargs)
        )

    def get_receipt_psp_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantReceiptPspPolicy]:
        return self._execute(
            ctx, lambda service: service.get_receipt_psp_policy(ctx, **kwargs)
        )

    def set_receipt_psp_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantReceiptPspPolicy]:
        return self._execute(
            ctx, lambda service: service.set_receipt_psp_policy(ctx, **kwargs)
        )

    def get_tax_authority_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantTaxAuthorityPolicy]:
        return self._execute(
            ctx, lambda service: service.get_tax_authority_policy(ctx, **kwargs)
        )

    def set_tax_authority_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantTaxAuthorityPolicy]:
        return self._execute(
            ctx, lambda service: service.set_tax_authority_policy(ctx, **kwargs)
        )

    def create_tax_rate(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TaxRate]:
        return self._execute(
            ctx, lambda service: service.create_tax_rate(ctx, **kwargs)
        )

    def get_tax_rate(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TaxRate]:
        return self._execute(
            ctx, lambda service: service.get_tax_rate(ctx, **kwargs)
        )

    def get_tax_rate_by_code(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TaxRate]:
        return self._execute(
            ctx, lambda service: service.get_tax_rate_by_code(ctx, **kwargs)
        )

    def archive_tax_rate(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TaxRate]:
        return self._execute(
            ctx, lambda service: service.archive_tax_rate(ctx, **kwargs)
        )

    def create_credit_note(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ARCreditNote]:
        return self._execute(
            ctx, lambda service: service.create_credit_note(ctx, **kwargs)
        )

    def issue_credit_note(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ARCreditNote]:
        return self._execute(
            ctx, lambda service: service.issue_credit_note(ctx, **kwargs)
        )

    def get_credit_note(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ARCreditNote]:
        return self._execute(
            ctx, lambda service: service.get_credit_note(ctx, **kwargs)
        )

    def create_ar_refund(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ARRefund]:
        return self._execute(
            ctx, lambda service: service.create_ar_refund(ctx, **kwargs)
        )

    def post_ar_refund(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ARRefund]:
        return self._execute(
            ctx, lambda service: service.post_ar_refund(ctx, **kwargs)
        )

    def create_treasury_transfer(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TreasuryTransfer]:
        return self._execute(
            ctx, lambda service: service.create_treasury_transfer(ctx, **kwargs)
        )

    def get_treasury_transfer(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TreasuryTransfer]:
        return self._execute(
            ctx, lambda service: service.get_treasury_transfer(ctx, **kwargs)
        )

    def post_treasury_transfer(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TreasuryTransfer]:
        return self._execute(
            ctx, lambda service: service.post_treasury_transfer(ctx, **kwargs)
        )

    def create_tax_invoice(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TaxInvoice]:
        return self._execute(
            ctx, lambda service: service.create_tax_invoice(ctx, **kwargs)
        )

    def create_tax_red_credit(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TaxInvoice]:
        return self._execute(
            ctx, lambda service: service.create_tax_red_credit(ctx, **kwargs)
        )

    def issue_tax_invoice(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TaxInvoice]:
        return self._execute(
            ctx, lambda service: service.issue_tax_invoice(ctx, **kwargs)
        )

    def void_tax_invoice(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TaxInvoice]:
        return self._execute(
            ctx, lambda service: service.void_tax_invoice(ctx, **kwargs)
        )

    def get_tax_invoice(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TaxInvoice]:
        return self._execute(
            ctx, lambda service: service.get_tax_invoice(ctx, **kwargs)
        )

    def accrue_commission(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[CommissionEntry]:
        return self._execute(
            ctx, lambda service: service.accrue_commission(ctx, **kwargs)
        )

    def mark_commission_payable(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[CommissionEntry]:
        return self._execute(
            ctx, lambda service: service.mark_commission_payable(ctx, **kwargs)
        )

    def mark_commission_paid(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[CommissionEntry]:
        return self._execute(
            ctx, lambda service: service.mark_commission_paid(ctx, **kwargs)
        )

    def get_commission(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[CommissionEntry]:
        return self._execute(
            ctx, lambda service: service.get_commission(ctx, **kwargs)
        )

    def create_gl_account(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlAccount]:
        return self._execute(
            ctx, lambda service: service.create_gl_account(ctx, **kwargs)
        )

    def get_gl_account(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlAccount]:
        return self._execute(
            ctx, lambda service: service.get_gl_account(ctx, **kwargs)
        )

    def get_gl_account_by_code(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlAccount]:
        return self._execute(
            ctx, lambda service: service.get_gl_account_by_code(ctx, **kwargs)
        )

    def archive_gl_account(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlAccount]:
        return self._execute(
            ctx, lambda service: service.archive_gl_account(ctx, **kwargs)
        )

    def create_gl_period(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlPeriod]:
        return self._execute(
            ctx, lambda service: service.create_gl_period(ctx, **kwargs)
        )

    def get_gl_period(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlPeriod]:
        return self._execute(
            ctx, lambda service: service.get_gl_period(ctx, **kwargs)
        )

    def get_gl_period_by_code(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlPeriod]:
        return self._execute(
            ctx, lambda service: service.get_gl_period_by_code(ctx, **kwargs)
        )

    def close_gl_period(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlPeriod]:
        return self._execute(
            ctx, lambda service: service.close_gl_period(ctx, **kwargs)
        )

    def create_journal_entry(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[JournalEntry]:
        return self._execute(
            ctx, lambda service: service.create_journal_entry(ctx, **kwargs)
        )

    def get_journal_entry(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[JournalEntry]:
        return self._execute(
            ctx, lambda service: service.get_journal_entry(ctx, **kwargs)
        )

    def post_journal_entry(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[JournalEntry]:
        return self._execute(
            ctx, lambda service: service.post_journal_entry(ctx, **kwargs)
        )

    def get_gl_bridge_map(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlBridgeMap]:
        return self._execute(
            ctx, lambda service: service.get_gl_bridge_map(ctx, **kwargs)
        )

    def set_gl_bridge_map(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlBridgeMap]:
        return self._execute(
            ctx, lambda service: service.set_gl_bridge_map(ctx, **kwargs)
        )

    def bridge_ar_invoice_issue(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlBridgePosting]:
        return self._execute(
            ctx, lambda service: service.bridge_ar_invoice_issue(ctx, **kwargs)
        )

    def bridge_ar_receipt_apply(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlBridgePosting]:
        return self._execute(
            ctx, lambda service: service.bridge_ar_receipt_apply(ctx, **kwargs)
        )

    def bridge_ap_bill_post(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlBridgePosting]:
        return self._execute(
            ctx, lambda service: service.bridge_ap_bill_post(ctx, **kwargs)
        )

    def bridge_ap_payment_apply(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlBridgePosting]:
        return self._execute(
            ctx, lambda service: service.bridge_ap_payment_apply(ctx, **kwargs)
        )

    def bridge_tax_invoice_issue(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlBridgePosting]:
        return self._execute(
            ctx, lambda service: service.bridge_tax_invoice_issue(ctx, **kwargs)
        )

    def bridge_commission_accrue(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlBridgePosting]:
        return self._execute(
            ctx, lambda service: service.bridge_commission_accrue(ctx, **kwargs)
        )

    def bridge_realized_fx(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlBridgePosting]:
        return self._execute(
            ctx, lambda service: service.bridge_realized_fx(ctx, **kwargs)
        )

    def create_fx_revaluation(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlFxRevaluation]:
        return self._execute(
            ctx, lambda service: service.create_fx_revaluation(ctx, **kwargs)
        )

    def get_fx_revaluation(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlFxRevaluation]:
        return self._execute(
            ctx, lambda service: service.get_fx_revaluation(ctx, **kwargs)
        )

    def post_fx_revaluation(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[GlFxRevaluation]:
        return self._execute(
            ctx, lambda service: service.post_fx_revaluation(ctx, **kwargs)
        )

    def create_bank_statement(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[BankStatement]:
        return self._execute(
            ctx, lambda service: service.create_bank_statement(ctx, **kwargs)
        )

    def get_bank_statement(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[BankStatement]:
        return self._execute(
            ctx, lambda service: service.get_bank_statement(ctx, **kwargs)
        )

    def match_bank_statement_line(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[BankStatement]:
        return self._execute(
            ctx,
            lambda service: service.match_bank_statement_line(ctx, **kwargs),
        )

    def clear_bank_statement(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[BankStatement]:
        return self._execute(
            ctx, lambda service: service.clear_bank_statement(ctx, **kwargs)
        )

    def _execute(
        self,
        ctx: ExecutionContext,
        operation: Callable[[FinanceService], KernelResult[T]],
    ) -> KernelResult[T]:
        if ctx.tenant_id is None or ctx.platform_scope:
            return KernelResult.failure(
                ErrorCode.CTX_INVALID,
                "Finance requires a tenant data-plane context",
            )
        try:
            with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
                audit = SQLAlchemyAuditLog(
                    unit_of_work.session,
                    tenant_id=ctx.tenant_id,
                )
                eligibility = SQLAlchemyPrincipalEligibility(
                    unit_of_work.session
                )
                permission = PermissionService(
                    repository=SQLAlchemyPermissionRepository(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                    ),
                    audit_log=audit,
                    principal_eligibility=eligibility,
                )
                from noventi.finance.psp_provider_adapter import (
                    resolve_psp_port,
                )
                from noventi.finance.tax_authority_adapter import (
                    resolve_tax_authority_port,
                )

                ar_invoice_adapter = SQLAlchemyARInvoiceReadAdapter(
                    unit_of_work.session, tenant_id=ctx.tenant_id
                )
                service = FinanceService(
                    permission,
                    repository=SQLAlchemyFinanceRepository(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                    ),
                    audit_log=audit,
                    ar_invoice_reader=ar_invoice_adapter,
                    ar_invoice_closer=ar_invoice_adapter,
                    ap_bill_reader=SQLAlchemyApBillReadAdapter(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                    ),
                    ap_payment_reader=SQLAlchemyApPaymentReadAdapter(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                    ),
                    beneficiary_eligibility=eligibility,
                    psp_port=(
                        self._psp_port
                        if self._psp_port is not None
                        else resolve_psp_port()
                    ),
                    tax_authority_port=(
                        self._tax_authority_port
                        if self._tax_authority_port is not None
                        else resolve_tax_authority_port()
                    ),
                    rma_credit_note_link_port=(
                        CRMReturnAuthorizationCreditNoteLinkAdapter(
                            SQLAlchemyCRMRepository(
                                unit_of_work.session,
                                tenant_id=ctx.tenant_id,
                            )
                        )
                    ),
                )
                result = operation(service)
                unit_of_work.commit()
                return result
        except IntegrityError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "Finance persistence conflict"
            )
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL, "Finance persistence unavailable"
            )
