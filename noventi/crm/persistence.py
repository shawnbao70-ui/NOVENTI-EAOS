"""SQLAlchemy persistence and transactional composition for CRM C1."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy import (
    and_,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    MetaData,
    Numeric,
    or_,
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

from kernel.event_bus.domain_emit import DomainEventEmitter
from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
from kernel.infrastructure.persistence.event_repository import SQLAlchemyOutboxWriter
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
from noventi.crm.approval import (
    ConfirmApprovalGate,
    DeliveryOrderReleaseApprovalGate,
    QuoteConvertApprovalGate,
    QuoteIssueApprovalGate,
    SalesOrderConfirmApprovalGate,
)
from noventi.crm.models import (
    ARInvoice,
    ARInvoiceStatus,
    Contact,
    ContactStatus,
    ConversionStatus,
    Customer,
    CustomerStatus,
    DeliveryOrder,
    DeliveryOrderLine,
    DeliveryOrderLineStatus,
    DeliveryOrderStatus,
    Opportunity,
    OpportunityStatus,
    Quote,
    QuoteConversion,
    QuoteLine,
    QuoteLineStatus,
    QuoteStatus,
    Requirement,
    RequirementStatus,
    ReturnAuthorization,
    ReturnAuthorizationStatus,
    SalesOrder,
    SalesOrderLine,
    SalesOrderStatus,
    TenantConfirmPolicy,
)
from noventi.crm.service import CRMService

T = TypeVar("T")
CRM_STATUSES = "'active','archived'"
QUOTE_STATUSES = "'draft','issued','archived'"
CONVERSION_STATUSES = "'ready','consumed'"
SALES_ORDER_STATUSES = "'created','confirmed','partially_shipped','shipped'"


class CRMBase(DeclarativeBase):
    """Keep business-package mappings out of Kernel metadata."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class CustomerRecord(CRMBase):
    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        CheckConstraint(f"status IN ({CRM_STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "uq_crm_customers_tenant_code_ci",
            "tenant_id",
            text("lower(code)"),
            unique=True,
        ),
        Index("ix_crm_customers_tenant_status", "tenant_id", "status"),
        {"schema": "crm"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_subject_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    commercial_hold: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class ContactRecord(CRMBase):
    __tablename__ = "contacts"
    __table_args__ = (
        ForeignKeyConstraint(
            ["customer_id", "tenant_id"],
            ["crm.customers.id", "crm.customers.tenant_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "tenant_id"),
        CheckConstraint(f"status IN ({CRM_STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_crm_contacts_tenant_customer", "tenant_id", "customer_id"),
        Index("ix_crm_contacts_tenant_status", "tenant_id", "status"),
        {"schema": "crm"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str | None] = mapped_column(String(128), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class OpportunityRecord(CRMBase):
    __tablename__ = "opportunities"
    __table_args__ = (
        ForeignKeyConstraint(
            ["customer_id", "tenant_id"],
            ["crm.customers.id", "crm.customers.tenant_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "code"),
        CheckConstraint(f"status IN ({CRM_STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_crm_opportunities_tenant_customer", "tenant_id", "customer_id"),
        Index("ix_crm_opportunities_tenant_status", "tenant_id", "status"),
        {"schema": "crm"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    customer_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_subject_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class RequirementRecord(CRMBase):
    __tablename__ = "requirements"
    __table_args__ = (
        ForeignKeyConstraint(
            ["opportunity_id", "tenant_id"],
            ["crm.opportunities.id", "crm.opportunities.tenant_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "code"),
        CheckConstraint(f"status IN ({CRM_STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_crm_requirements_tenant_opportunity", "tenant_id", "opportunity_id"),
        Index("ix_crm_requirements_tenant_status", "tenant_id", "status"),
        {"schema": "crm"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    opportunity_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class QuoteRecord(CRMBase):
    __tablename__ = "quotes"
    __table_args__ = (
        ForeignKeyConstraint(
            ["requirement_id", "tenant_id"],
            ["crm.requirements.id", "crm.requirements.tenant_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "code"),
        UniqueConstraint("tenant_id", "issue_key"),
        CheckConstraint(f"status IN ({QUOTE_STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_crm_quotes_tenant_requirement", "tenant_id", "requirement_id"),
        Index("ix_crm_quotes_tenant_status", "tenant_id", "status"),
        {"schema": "crm"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    requirement_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    functional_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    fx_rate: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    issued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    issue_key: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class QuoteLineRecord(CRMBase):
    __tablename__ = "quote_lines"
    __table_args__ = (
        ForeignKeyConstraint(
            ["quote_id", "tenant_id"],
            ["crm.quotes.id", "crm.quotes.tenant_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "quote_id", "line_number"),
        CheckConstraint(f"status IN ({CRM_STATUSES})", name="status_valid"),
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("unit_price >= 0", name="unit_price_non_negative"),
        CheckConstraint("amount >= 0", name="amount_non_negative"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_crm_quote_lines_tenant_quote", "tenant_id", "quote_id"),
        {"schema": "crm"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    quote_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class QuoteConversionRecord(CRMBase):
    __tablename__ = "quote_conversions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["quote_id", "tenant_id"],
            ["crm.quotes.id", "crm.quotes.tenant_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "quote_id"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        CheckConstraint(
            f"status IN ({CONVERSION_STATUSES})", name="status_valid"
        ),
        CheckConstraint("quote_version > 0", name="quote_version_positive"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_crm_quote_conversions_tenant_status", "tenant_id", "status"),
        {"schema": "crm"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    quote_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    requirement_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    quote_version: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    functional_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    fx_rate: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    functional_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class SalesOrderRecord(CRMBase):
    __tablename__ = "sales_orders"
    __table_args__ = (
        ForeignKeyConstraint(
            ["conversion_id", "tenant_id"],
            ["crm.quote_conversions.id", "crm.quote_conversions.tenant_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["quote_id", "tenant_id"],
            ["crm.quotes.id", "crm.quotes.tenant_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["requirement_id", "tenant_id"],
            ["crm.requirements.id", "crm.requirements.tenant_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "conversion_id"),
        UniqueConstraint("tenant_id", "quote_id"),
        UniqueConstraint("tenant_id", "code"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        UniqueConstraint("tenant_id", "confirmation_key"),
        CheckConstraint(
            f"status IN ({SALES_ORDER_STATUSES})", name="status_valid"
        ),
        CheckConstraint("total_amount >= 0", name="total_amount_non_negative"),
        CheckConstraint("functional_total >= 0", name="functional_total_non_negative"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_crm_sales_orders_tenant_status", "tenant_id", "status"),
        {"schema": "crm"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    conversion_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    quote_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    requirement_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    functional_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    fx_rate: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    functional_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    ordered_quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 3), nullable=False, server_default=text("0")
    )
    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    shipped_quantity: Mapped[Decimal] = mapped_column(
        Numeric(18, 3), nullable=False, server_default=text("0")
    )
    confirmation_key: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class SalesOrderLineRecord(CRMBase):
    __tablename__ = "sales_order_lines"
    __table_args__ = (
        ForeignKeyConstraint(
            ["sales_order_id", "tenant_id"],
            ["crm.sales_orders.id", "crm.sales_orders.tenant_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "sales_order_id", "line_number"),
        CheckConstraint("line_number > 0", name="line_number_positive"),
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("unit_price >= 0", name="unit_price_non_negative"),
        CheckConstraint("amount >= 0", name="amount_non_negative"),
        Index(
            "ix_crm_sales_order_lines_tenant_order",
            "tenant_id",
            "sales_order_id",
        ),
        {"schema": "crm"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    sales_order_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DeliveryOrderRecord(CRMBase):
    __tablename__ = "delivery_orders"
    __table_args__ = (
        ForeignKeyConstraint(
            ["sales_order_id", "tenant_id"],
            ["crm.sales_orders.id", "crm.sales_orders.tenant_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["quote_id", "tenant_id"],
            ["crm.quotes.id", "crm.quotes.tenant_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["requirement_id", "tenant_id"],
            ["crm.requirements.id", "crm.requirements.tenant_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "code"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        UniqueConstraint("tenant_id", "release_key"),
        CheckConstraint("sales_order_version > 0", name="so_version_positive"),
        CheckConstraint("total_amount >= 0", name="total_amount_non_negative"),
        CheckConstraint(
            "status IN ('draft','released','shipped')", name="status_valid"
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_crm_delivery_orders_tenant_status", "tenant_id", "status"),
        {"schema": "crm"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    sales_order_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    sales_order_version: Mapped[int] = mapped_column(Integer, nullable=False)
    quote_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    requirement_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    released_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    release_key: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class DeliveryOrderLineRecord(CRMBase):
    __tablename__ = "delivery_order_lines"
    __table_args__ = (
        ForeignKeyConstraint(
            ["delivery_order_id", "tenant_id"],
            ["crm.delivery_orders.id", "crm.delivery_orders.tenant_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["sales_order_line_id", "tenant_id"],
            ["crm.sales_order_lines.id", "crm.sales_order_lines.tenant_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "delivery_order_id", "sales_order_line_id"),
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("status IN ('open','shipped')", name="status_valid"),
        Index(
            "ix_crm_delivery_order_lines_tenant_do",
            "tenant_id",
            "delivery_order_id",
        ),
        {"schema": "crm"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    delivery_order_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    sales_order_line_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ARInvoiceRecord(CRMBase):
    __tablename__ = "ar_invoices"
    __table_args__ = (
        ForeignKeyConstraint(
            ["delivery_order_id", "tenant_id"],
            ["crm.delivery_orders.id", "crm.delivery_orders.tenant_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["sales_order_id", "tenant_id"],
            ["crm.sales_orders.id", "crm.sales_orders.tenant_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["customer_id", "tenant_id"],
            ["crm.customers.id", "crm.customers.tenant_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "delivery_order_id"),
        UniqueConstraint("tenant_id", "sales_order_id"),
        UniqueConstraint("tenant_id", "code"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        UniqueConstraint("tenant_id", "issue_key"),
        UniqueConstraint("tenant_id", "void_key"),
        CheckConstraint("delivery_order_version > 0", name="do_version_positive"),
        CheckConstraint("sales_order_version > 0", name="so_version_positive"),
        CheckConstraint("total_amount >= 0", name="total_amount_non_negative"),
        CheckConstraint("functional_total >= 0", name="functional_total_non_negative"),
        CheckConstraint(
            "status IN ('draft','issued','closed','voided')", name="status_valid"
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_crm_ar_invoices_tenant_status", "tenant_id", "status"),
        {"schema": "crm"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    delivery_order_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    delivery_order_version: Mapped[int] = mapped_column(Integer, nullable=False)
    sales_order_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    sales_order_version: Mapped[int] = mapped_column(Integer, nullable=False)
    customer_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    functional_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    fx_rate: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    functional_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    issued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    issue_key: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    voided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    void_key: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    void_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class ReturnAuthorizationRecord(CRMBase):
    __tablename__ = "return_authorizations"
    __table_args__ = (
        ForeignKeyConstraint(
            ["delivery_order_id", "tenant_id"],
            ["crm.delivery_orders.id", "crm.delivery_orders.tenant_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["invoice_id", "tenant_id"],
            ["crm.ar_invoices.id", "crm.ar_invoices.tenant_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["credit_note_id", "tenant_id"],
            ["finance.ar_credit_notes.id", "finance.ar_credit_notes.tenant_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint("tenant_id", "delivery_order_id"),
        UniqueConstraint("tenant_id", "code"),
        UniqueConstraint("tenant_id", "idempotency_key"),
        UniqueConstraint("tenant_id", "credit_note_id"),
        UniqueConstraint("tenant_id", "credit_note_key"),
        CheckConstraint(
            "status IN ('draft','restocked')", name="status_valid"
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_crm_return_authorizations_tenant_status", "tenant_id", "status"),
        {"schema": "crm"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    delivery_order_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    invoice_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    credit_note_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    credit_note_key: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[str] = mapped_column(String(500), nullable=False)
    idempotency_key: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    restocked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    restock_key: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    credit_note_issued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class TenantConfirmPolicyRecord(CRMBase):
    __tablename__ = "tenant_confirm_policies"
    __table_args__ = (
        CheckConstraint("version > 0", name="version_positive"),
        {"schema": "crm"},
    )

    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    confirm_approval_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    quote_issue_approval_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    quote_convert_approval_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    so_confirm_workflow_approval_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    do_ship_approval_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    do_release_approval_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )


class SQLAlchemyCRMRepository:
    def __init__(self, session: Session, *, tenant_id: UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def add_customer(self, customer: Customer) -> None:
        self._require_tenant(customer.tenant_id)
        self._session.add(self._customer_record(customer))

    def get_customer(self, customer_id: UUID) -> Customer | None:
        record = self._session.scalar(
            select(CustomerRecord).where(
                CustomerRecord.id == customer_id,
                CustomerRecord.tenant_id == self._tenant_id,
            )
        )
        return self._customer_domain(record) if record is not None else None

    def list_customers(
        self, *, limit: int, after: tuple[datetime, UUID] | None = None
    ) -> list[Customer]:
        conditions = [
            CustomerRecord.tenant_id == self._tenant_id,
            CustomerRecord.status == CustomerStatus.ACTIVE.value,
        ]
        if after is not None:
            conditions.append(
                or_(
                    CustomerRecord.updated_at < after[0],
                    and_(
                        CustomerRecord.updated_at == after[0],
                        CustomerRecord.id < after[1],
                    ),
                )
            )
        records = self._session.scalars(
            select(CustomerRecord)
            .where(*conditions)
            .order_by(CustomerRecord.updated_at.desc(), CustomerRecord.id.desc())
            .limit(limit)
        ).all()
        return [self._customer_domain(record) for record in records]

    def save_customer(self, customer: Customer, *, expected_version: int) -> None:
        self._require_tenant(customer.tenant_id)
        result = self._session.execute(
            update(CustomerRecord)
            .where(
                CustomerRecord.id == customer.id,
                CustomerRecord.tenant_id == self._tenant_id,
                CustomerRecord.version == expected_version,
            )
            .values(
                display_name=customer.display_name,
                owner_subject_id=customer.owner_subject_id,
                status=customer.status.value,
                commercial_hold=customer.commercial_hold,
                updated_at=customer.updated_at,
                archived_at=customer.archived_at,
                version=customer.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("customer version conflict")

    def add_contact(self, contact: Contact) -> None:
        self._require_tenant(contact.tenant_id)
        self._session.add(self._contact_record(contact))

    def get_contact(self, customer_id: UUID, contact_id: UUID) -> Contact | None:
        record = self._session.scalar(
            select(ContactRecord).where(
                ContactRecord.id == contact_id,
                ContactRecord.customer_id == customer_id,
                ContactRecord.tenant_id == self._tenant_id,
            )
        )
        return self._contact_domain(record) if record is not None else None

    def list_contacts(
        self,
        customer_id: UUID,
        *,
        limit: int,
        after: tuple[datetime, UUID] | None = None,
    ) -> list[Contact]:
        conditions = [
            ContactRecord.tenant_id == self._tenant_id,
            ContactRecord.customer_id == customer_id,
            ContactRecord.status == ContactStatus.ACTIVE.value,
        ]
        if after is not None:
            conditions.append(
                or_(
                    ContactRecord.updated_at < after[0],
                    and_(
                        ContactRecord.updated_at == after[0],
                        ContactRecord.id < after[1],
                    ),
                )
            )
        records = self._session.scalars(
            select(ContactRecord)
            .where(*conditions)
            .order_by(ContactRecord.updated_at.desc(), ContactRecord.id.desc())
            .limit(limit)
        ).all()
        return [self._contact_domain(record) for record in records]

    def save_contact(self, contact: Contact, *, expected_version: int) -> None:
        self._require_tenant(contact.tenant_id)
        result = self._session.execute(
            update(ContactRecord)
            .where(
                ContactRecord.id == contact.id,
                ContactRecord.customer_id == contact.customer_id,
                ContactRecord.tenant_id == self._tenant_id,
                ContactRecord.version == expected_version,
            )
            .values(
                display_name=contact.display_name,
                title=contact.title,
                email=contact.email,
                phone=contact.phone,
                status=contact.status.value,
                updated_at=contact.updated_at,
                archived_at=contact.archived_at,
                version=contact.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("contact version conflict")

    def add_opportunity(self, opportunity: Opportunity) -> None:
        self._require_tenant(opportunity.tenant_id)
        self._session.add(self._opportunity_record(opportunity))

    def get_opportunity(self, opportunity_id: UUID) -> Opportunity | None:
        record = self._session.scalar(
            select(OpportunityRecord).where(
                OpportunityRecord.id == opportunity_id,
                OpportunityRecord.tenant_id == self._tenant_id,
            )
        )
        return self._opportunity_domain(record) if record is not None else None

    def list_opportunities(
        self, *, limit: int, after: tuple[datetime, UUID] | None = None
    ) -> list[Opportunity]:
        conditions = [
            OpportunityRecord.tenant_id == self._tenant_id,
            OpportunityRecord.status == OpportunityStatus.ACTIVE.value,
        ]
        if after is not None:
            conditions.append(
                or_(
                    OpportunityRecord.updated_at < after[0],
                    and_(
                        OpportunityRecord.updated_at == after[0],
                        OpportunityRecord.id < after[1],
                    ),
                )
            )
        records = self._session.scalars(
            select(OpportunityRecord)
            .where(*conditions)
            .order_by(OpportunityRecord.updated_at.desc(), OpportunityRecord.id.desc())
            .limit(limit)
        ).all()
        return [self._opportunity_domain(record) for record in records]

    def save_opportunity(
        self, opportunity: Opportunity, *, expected_version: int
    ) -> None:
        self._require_tenant(opportunity.tenant_id)
        result = self._session.execute(
            update(OpportunityRecord)
            .where(
                OpportunityRecord.id == opportunity.id,
                OpportunityRecord.tenant_id == self._tenant_id,
                OpportunityRecord.version == expected_version,
            )
            .values(
                title=opportunity.title,
                owner_subject_id=opportunity.owner_subject_id,
                status=opportunity.status.value,
                updated_at=opportunity.updated_at,
                archived_at=opportunity.archived_at,
                version=opportunity.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("opportunity version conflict")

    def add_requirement(self, requirement: Requirement) -> None:
        self._require_tenant(requirement.tenant_id)
        self._session.add(self._requirement_record(requirement))

    def get_requirement(self, requirement_id: UUID) -> Requirement | None:
        record = self._session.scalar(
            select(RequirementRecord).where(
                RequirementRecord.id == requirement_id,
                RequirementRecord.tenant_id == self._tenant_id,
            )
        )
        return self._requirement_domain(record) if record is not None else None

    def list_requirements(
        self, *, limit: int, after: tuple[datetime, UUID] | None = None
    ) -> list[Requirement]:
        conditions = [
            RequirementRecord.tenant_id == self._tenant_id,
            RequirementRecord.status == RequirementStatus.ACTIVE.value,
        ]
        if after is not None:
            conditions.append(
                or_(
                    RequirementRecord.updated_at < after[0],
                    and_(
                        RequirementRecord.updated_at == after[0],
                        RequirementRecord.id < after[1],
                    ),
                )
            )
        records = self._session.scalars(
            select(RequirementRecord)
            .where(*conditions)
            .order_by(RequirementRecord.updated_at.desc(), RequirementRecord.id.desc())
            .limit(limit)
        ).all()
        return [self._requirement_domain(record) for record in records]

    def save_requirement(
        self, requirement: Requirement, *, expected_version: int
    ) -> None:
        self._require_tenant(requirement.tenant_id)
        result = self._session.execute(
            update(RequirementRecord)
            .where(
                RequirementRecord.id == requirement.id,
                RequirementRecord.tenant_id == self._tenant_id,
                RequirementRecord.version == expected_version,
            )
            .values(
                title=requirement.title,
                description=requirement.description,
                status=requirement.status.value,
                updated_at=requirement.updated_at,
                archived_at=requirement.archived_at,
                version=requirement.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("requirement version conflict")

    def add_quote(self, quote: Quote) -> None:
        self._require_tenant(quote.tenant_id)
        self._session.add(self._quote_record(quote))

    def get_quote(self, quote_id: UUID) -> Quote | None:
        record = self._session.scalar(
            select(QuoteRecord).where(
                QuoteRecord.id == quote_id,
                QuoteRecord.tenant_id == self._tenant_id,
            )
        )
        return self._quote_domain(record) if record is not None else None

    def list_quotes(
        self, *, limit: int, after: tuple[datetime, UUID] | None = None
    ) -> list[Quote]:
        conditions = [
            QuoteRecord.tenant_id == self._tenant_id,
            QuoteRecord.status != QuoteStatus.ARCHIVED.value,
        ]
        if after is not None:
            conditions.append(
                or_(
                    QuoteRecord.updated_at < after[0],
                    and_(
                        QuoteRecord.updated_at == after[0],
                        QuoteRecord.id < after[1],
                    ),
                )
            )
        records = self._session.scalars(
            select(QuoteRecord)
            .where(*conditions)
            .order_by(QuoteRecord.updated_at.desc(), QuoteRecord.id.desc())
            .limit(limit)
        ).all()
        return [self._quote_domain(record) for record in records]

    def save_quote(self, quote: Quote, *, expected_version: int) -> None:
        self._require_tenant(quote.tenant_id)
        result = self._session.execute(
            update(QuoteRecord)
            .where(
                QuoteRecord.id == quote.id,
                QuoteRecord.tenant_id == self._tenant_id,
                QuoteRecord.version == expected_version,
            )
            .values(
                currency=quote.currency,
                functional_currency=quote.functional_currency,
                fx_rate=quote.fx_rate,
                notes=quote.notes,
                status=quote.status.value,
                updated_at=quote.updated_at,
                archived_at=quote.archived_at,
                issued_at=quote.issued_at,
                issue_key=quote.issue_key,
                version=quote.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("quote version conflict")

    def next_quote_line_number(self, quote_id: UUID) -> int:
        current = self._session.scalar(
            select(func.max(QuoteLineRecord.line_number)).where(
                QuoteLineRecord.quote_id == quote_id,
                QuoteLineRecord.tenant_id == self._tenant_id,
            )
        )
        return int(current or 0) + 1

    def add_quote_line(self, quote_line: QuoteLine) -> None:
        self._require_tenant(quote_line.tenant_id)
        self._session.add(self._quote_line_record(quote_line))

    def get_quote_line(
        self, quote_id: UUID, quote_line_id: UUID
    ) -> QuoteLine | None:
        record = self._session.scalar(
            select(QuoteLineRecord).where(
                QuoteLineRecord.id == quote_line_id,
                QuoteLineRecord.quote_id == quote_id,
                QuoteLineRecord.tenant_id == self._tenant_id,
            )
        )
        return self._quote_line_domain(record) if record is not None else None

    def list_quote_lines(self, quote_id: UUID) -> list[QuoteLine]:
        records = self._session.scalars(
            select(QuoteLineRecord)
            .where(
                QuoteLineRecord.quote_id == quote_id,
                QuoteLineRecord.tenant_id == self._tenant_id,
            )
            .order_by(QuoteLineRecord.line_number)
        ).all()
        return [self._quote_line_domain(record) for record in records]

    def save_quote_line(
        self, quote_line: QuoteLine, *, expected_version: int
    ) -> None:
        self._require_tenant(quote_line.tenant_id)
        result = self._session.execute(
            update(QuoteLineRecord)
            .where(
                QuoteLineRecord.id == quote_line.id,
                QuoteLineRecord.quote_id == quote_line.quote_id,
                QuoteLineRecord.tenant_id == self._tenant_id,
                QuoteLineRecord.version == expected_version,
            )
            .values(
                description=quote_line.description,
                quantity=quote_line.quantity,
                unit_price=quote_line.unit_price,
                amount=quote_line.amount,
                status=quote_line.status.value,
                updated_at=quote_line.updated_at,
                archived_at=quote_line.archived_at,
                version=quote_line.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("quote line version conflict")

    def add_conversion(self, conversion: QuoteConversion) -> None:
        self._require_tenant(conversion.tenant_id)
        self._session.add(self._conversion_record(conversion))

    def get_conversion(self, conversion_id: UUID) -> QuoteConversion | None:
        record = self._session.scalar(
            select(QuoteConversionRecord).where(
                QuoteConversionRecord.id == conversion_id,
                QuoteConversionRecord.tenant_id == self._tenant_id,
            )
        )
        return self._conversion_domain(record) if record is not None else None

    def get_conversion_by_quote(self, quote_id: UUID) -> QuoteConversion | None:
        record = self._session.scalar(
            select(QuoteConversionRecord).where(
                QuoteConversionRecord.quote_id == quote_id,
                QuoteConversionRecord.tenant_id == self._tenant_id,
            )
        )
        return self._conversion_domain(record) if record is not None else None

    def save_conversion(
        self, conversion: QuoteConversion, *, expected_version: int
    ) -> None:
        self._require_tenant(conversion.tenant_id)
        result = self._session.execute(
            update(QuoteConversionRecord)
            .where(
                QuoteConversionRecord.id == conversion.id,
                QuoteConversionRecord.tenant_id == self._tenant_id,
                QuoteConversionRecord.version == expected_version,
            )
            .values(
                status=conversion.status.value,
                updated_at=conversion.updated_at,
                consumed_at=conversion.consumed_at,
                version=conversion.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("conversion version conflict")

    def add_sales_order(self, sales_order: SalesOrder) -> None:
        self._require_tenant(sales_order.tenant_id)
        self._session.add(self._sales_order_record(sales_order))

    def get_sales_order(self, sales_order_id: UUID) -> SalesOrder | None:
        record = self._session.scalar(
            select(SalesOrderRecord).where(
                SalesOrderRecord.id == sales_order_id,
                SalesOrderRecord.tenant_id == self._tenant_id,
            )
        )
        return self._sales_order_domain(record) if record is not None else None

    def list_sales_orders(
        self, *, limit: int, after: tuple[datetime, UUID] | None = None
    ) -> list[SalesOrder]:
        conditions = [SalesOrderRecord.tenant_id == self._tenant_id]
        if after is not None:
            conditions.append(
                or_(
                    SalesOrderRecord.created_at < after[0],
                    and_(
                        SalesOrderRecord.created_at == after[0],
                        SalesOrderRecord.id < after[1],
                    ),
                )
            )
        records = self._session.scalars(
            select(SalesOrderRecord)
            .where(*conditions)
            .order_by(SalesOrderRecord.created_at.desc(), SalesOrderRecord.id.desc())
            .limit(limit)
        ).all()
        return [self._sales_order_domain(record) for record in records]

    def get_sales_order_by_conversion(
        self, conversion_id: UUID
    ) -> SalesOrder | None:
        record = self._session.scalar(
            select(SalesOrderRecord).where(
                SalesOrderRecord.conversion_id == conversion_id,
                SalesOrderRecord.tenant_id == self._tenant_id,
            )
        )
        return self._sales_order_domain(record) if record is not None else None

    def save_sales_order(
        self, sales_order: SalesOrder, *, expected_version: int
    ) -> None:
        self._require_tenant(sales_order.tenant_id)
        result = self._session.execute(
            update(SalesOrderRecord)
            .where(
                SalesOrderRecord.id == sales_order.id,
                SalesOrderRecord.tenant_id == self._tenant_id,
                SalesOrderRecord.version == expected_version,
            )
            .values(
                status=sales_order.status.value,
                total_amount=sales_order.total_amount,
                ordered_quantity=sales_order.ordered_quantity,
                confirmed_at=sales_order.confirmed_at,
                shipped_quantity=sales_order.shipped_quantity,
                confirmation_key=sales_order.confirmation_key,
                version=sales_order.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("sales order version conflict")

    def add_sales_order_lines(
        self, sales_order_lines: list[SalesOrderLine]
    ) -> None:
        for sales_order_line in sales_order_lines:
            self._require_tenant(sales_order_line.tenant_id)
            self._session.add(self._sales_order_line_record(sales_order_line))

    def list_sales_order_lines(
        self, sales_order_id: UUID
    ) -> list[SalesOrderLine]:
        records = self._session.scalars(
            select(SalesOrderLineRecord)
            .where(
                SalesOrderLineRecord.sales_order_id == sales_order_id,
                SalesOrderLineRecord.tenant_id == self._tenant_id,
            )
            .order_by(SalesOrderLineRecord.line_number)
        ).all()
        return [self._sales_order_line_domain(record) for record in records]

    def add_delivery_order(self, delivery_order: DeliveryOrder) -> None:
        self._require_tenant(delivery_order.tenant_id)
        self._session.add(self._delivery_order_record(delivery_order))
        # Composite FK on delivery_order_lines needs the header row present first.
        self._session.flush()

    def add_delivery_order_lines(
        self, delivery_order_lines: list[DeliveryOrderLine]
    ) -> None:
        for line in delivery_order_lines:
            self._require_tenant(line.tenant_id)
            self._session.add(self._delivery_order_line_record(line))

    def list_delivery_order_lines(
        self, delivery_order_id: UUID
    ) -> list[DeliveryOrderLine]:
        records = self._session.scalars(
            select(DeliveryOrderLineRecord)
            .where(
                DeliveryOrderLineRecord.delivery_order_id == delivery_order_id,
                DeliveryOrderLineRecord.tenant_id == self._tenant_id,
            )
            .order_by(DeliveryOrderLineRecord.sales_order_line_id)
        ).all()
        return [self._delivery_order_line_domain(record) for record in records]

    def save_delivery_order_lines(
        self, delivery_order_lines: list[DeliveryOrderLine]
    ) -> None:
        for line in delivery_order_lines:
            self._require_tenant(line.tenant_id)
            result = self._session.execute(
                update(DeliveryOrderLineRecord)
                .where(
                    DeliveryOrderLineRecord.id == line.id,
                    DeliveryOrderLineRecord.tenant_id == self._tenant_id,
                )
                .values(status=line.status.value)
            )
            if result.rowcount != 1:
                raise ValueError("delivery order line conflict")

    def save_delivery_order(
        self, delivery_order: DeliveryOrder, *, expected_version: int
    ) -> None:
        self._require_tenant(delivery_order.tenant_id)
        result = self._session.execute(
            update(DeliveryOrderRecord)
            .where(
                DeliveryOrderRecord.id == delivery_order.id,
                DeliveryOrderRecord.tenant_id == self._tenant_id,
                DeliveryOrderRecord.version == expected_version,
            )
            .values(
                status=delivery_order.status.value,
                released_at=delivery_order.released_at,
                release_key=delivery_order.release_key,
                version=delivery_order.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("delivery order version conflict")

    def get_delivery_order(
        self, delivery_order_id: UUID
    ) -> DeliveryOrder | None:
        record = self._session.scalar(
            select(DeliveryOrderRecord).where(
                DeliveryOrderRecord.id == delivery_order_id,
                DeliveryOrderRecord.tenant_id == self._tenant_id,
            )
        )
        return self._delivery_order_domain(record) if record is not None else None

    def get_delivery_order_by_sales_order(
        self, sales_order_id: UUID
    ) -> DeliveryOrder | None:
        record = self._session.scalar(
            select(DeliveryOrderRecord).where(
                DeliveryOrderRecord.sales_order_id == sales_order_id,
                DeliveryOrderRecord.tenant_id == self._tenant_id,
            )
        )
        return self._delivery_order_domain(record) if record is not None else None

    def get_delivery_order_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> DeliveryOrder | None:
        record = self._session.scalar(
            select(DeliveryOrderRecord).where(
                DeliveryOrderRecord.idempotency_key == idempotency_key,
                DeliveryOrderRecord.tenant_id == self._tenant_id,
            )
        )
        return self._delivery_order_domain(record) if record is not None else None

    def list_delivery_orders_by_sales_order(
        self, sales_order_id: UUID
    ) -> list[DeliveryOrder]:
        records = self._session.scalars(
            select(DeliveryOrderRecord).where(
                DeliveryOrderRecord.sales_order_id == sales_order_id,
                DeliveryOrderRecord.tenant_id == self._tenant_id,
            )
        ).all()
        return [self._delivery_order_domain(record) for record in records]

    def add_ar_invoice(self, invoice: ARInvoice) -> None:
        self._require_tenant(invoice.tenant_id)
        self._session.add(self._ar_invoice_record(invoice))

    def save_ar_invoice(
        self, invoice: ARInvoice, *, expected_version: int
    ) -> None:
        self._require_tenant(invoice.tenant_id)
        result = self._session.execute(
            update(ARInvoiceRecord)
            .where(
                ARInvoiceRecord.id == invoice.id,
                ARInvoiceRecord.tenant_id == self._tenant_id,
                ARInvoiceRecord.version == expected_version,
            )
            .values(
                status=invoice.status.value,
                issued_at=invoice.issued_at,
                issue_key=invoice.issue_key,
                voided_at=invoice.voided_at,
                void_key=invoice.void_key,
                void_reason=invoice.void_reason,
                version=invoice.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("AR invoice version conflict")

    def get_ar_invoice(self, invoice_id: UUID) -> ARInvoice | None:
        record = self._session.scalar(
            select(ARInvoiceRecord).where(
                ARInvoiceRecord.id == invoice_id,
                ARInvoiceRecord.tenant_id == self._tenant_id,
            )
        )
        return self._ar_invoice_domain(record) if record is not None else None

    def get_ar_invoice_by_delivery_order(
        self, delivery_order_id: UUID
    ) -> ARInvoice | None:
        record = self._session.scalar(
            select(ARInvoiceRecord).where(
                ARInvoiceRecord.delivery_order_id == delivery_order_id,
                ARInvoiceRecord.tenant_id == self._tenant_id,
            )
        )
        return self._ar_invoice_domain(record) if record is not None else None

    def add_return_authorization(
        self, authorization: ReturnAuthorization
    ) -> None:
        self._require_tenant(authorization.tenant_id)
        self._session.add(self._return_authorization_record(authorization))

    def get_return_authorization(
        self, return_authorization_id: UUID
    ) -> ReturnAuthorization | None:
        record = self._session.scalar(
            select(ReturnAuthorizationRecord).where(
                ReturnAuthorizationRecord.id == return_authorization_id,
                ReturnAuthorizationRecord.tenant_id == self._tenant_id,
            )
        )
        return (
            self._return_authorization_domain(record)
            if record is not None
            else None
        )

    def get_return_authorization_by_credit_note_id(
        self, credit_note_id: UUID
    ) -> ReturnAuthorization | None:
        record = self._session.scalar(
            select(ReturnAuthorizationRecord).where(
                ReturnAuthorizationRecord.credit_note_id == credit_note_id,
                ReturnAuthorizationRecord.tenant_id == self._tenant_id,
            )
        )
        return (
            self._return_authorization_domain(record)
            if record is not None
            else None
        )

    def get_return_authorization_by_delivery_order(
        self, delivery_order_id: UUID
    ) -> ReturnAuthorization | None:
        record = self._session.scalar(
            select(ReturnAuthorizationRecord).where(
                ReturnAuthorizationRecord.delivery_order_id == delivery_order_id,
                ReturnAuthorizationRecord.tenant_id == self._tenant_id,
            )
        )
        return (
            self._return_authorization_domain(record)
            if record is not None
            else None
        )

    def get_return_authorization_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ReturnAuthorization | None:
        record = self._session.scalar(
            select(ReturnAuthorizationRecord).where(
                ReturnAuthorizationRecord.idempotency_key == idempotency_key,
                ReturnAuthorizationRecord.tenant_id == self._tenant_id,
            )
        )
        return (
            self._return_authorization_domain(record)
            if record is not None
            else None
        )

    def save_return_authorization(
        self, authorization: ReturnAuthorization, *, expected_version: int
    ) -> None:
        self._require_tenant(authorization.tenant_id)
        result = self._session.execute(
            update(ReturnAuthorizationRecord)
            .where(
                ReturnAuthorizationRecord.id == authorization.id,
                ReturnAuthorizationRecord.tenant_id == self._tenant_id,
                ReturnAuthorizationRecord.version == expected_version,
            )
            .values(
                status=authorization.status.value,
                credit_note_id=authorization.credit_note_id,
                credit_note_key=authorization.credit_note_key,
                restocked_at=authorization.restocked_at,
                restock_key=authorization.restock_key,
                credit_note_issued_at=authorization.credit_note_issued_at,
                version=authorization.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("return authorization version conflict")

    def get_confirm_policy(self) -> TenantConfirmPolicy | None:
        record = self._session.scalar(
            select(TenantConfirmPolicyRecord).where(
                TenantConfirmPolicyRecord.tenant_id == self._tenant_id
            )
        )
        return self._confirm_policy_domain(record) if record is not None else None

    def save_confirm_policy(
        self, policy: TenantConfirmPolicy, *, expected_version: int
    ) -> None:
        self._require_tenant(policy.tenant_id)
        current = self.get_confirm_policy()
        if current is None:
            if expected_version != 0:
                raise ValueError("confirm policy version conflict")
            self._session.add(self._confirm_policy_record(policy))
            return
        result = self._session.execute(
            update(TenantConfirmPolicyRecord)
            .where(
                TenantConfirmPolicyRecord.tenant_id == policy.tenant_id,
                TenantConfirmPolicyRecord.version == expected_version,
            )
            .values(
                confirm_approval_required=policy.confirm_approval_required,
                quote_issue_approval_required=policy.quote_issue_approval_required,
                quote_convert_approval_required=policy.quote_convert_approval_required,
                so_confirm_workflow_approval_required=(
                    policy.so_confirm_workflow_approval_required
                ),
                do_ship_approval_required=policy.do_ship_approval_required,
                do_release_approval_required=policy.do_release_approval_required,
                updated_at=policy.updated_at,
                version=policy.version,
            )
        )
        if result.rowcount != 1:
            raise ValueError("confirm policy version conflict")

    def _require_tenant(self, tenant_id: UUID) -> None:
        if tenant_id != self._tenant_id:
            raise ValueError("CRM record is outside repository tenant")

    @staticmethod
    def _customer_record(customer: Customer) -> CustomerRecord:
        return CustomerRecord(
            id=customer.id,
            tenant_id=customer.tenant_id,
            code=customer.code,
            display_name=customer.display_name,
            owner_subject_id=customer.owner_subject_id,
            status=customer.status.value,
            commercial_hold=customer.commercial_hold,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
            archived_at=customer.archived_at,
            version=customer.version,
        )

    @staticmethod
    def _contact_record(contact: Contact) -> ContactRecord:
        return ContactRecord(
            id=contact.id,
            tenant_id=contact.tenant_id,
            customer_id=contact.customer_id,
            display_name=contact.display_name,
            title=contact.title,
            email=contact.email,
            phone=contact.phone,
            status=contact.status.value,
            created_at=contact.created_at,
            updated_at=contact.updated_at,
            archived_at=contact.archived_at,
            version=contact.version,
        )

    @staticmethod
    def _opportunity_record(opportunity: Opportunity) -> OpportunityRecord:
        return OpportunityRecord(
            id=opportunity.id,
            tenant_id=opportunity.tenant_id,
            customer_id=opportunity.customer_id,
            code=opportunity.code,
            title=opportunity.title,
            owner_subject_id=opportunity.owner_subject_id,
            status=opportunity.status.value,
            created_at=opportunity.created_at,
            updated_at=opportunity.updated_at,
            archived_at=opportunity.archived_at,
            version=opportunity.version,
        )

    @staticmethod
    def _requirement_record(requirement: Requirement) -> RequirementRecord:
        return RequirementRecord(
            id=requirement.id,
            tenant_id=requirement.tenant_id,
            opportunity_id=requirement.opportunity_id,
            code=requirement.code,
            title=requirement.title,
            description=requirement.description,
            status=requirement.status.value,
            created_at=requirement.created_at,
            updated_at=requirement.updated_at,
            archived_at=requirement.archived_at,
            version=requirement.version,
        )

    @staticmethod
    def _quote_record(quote: Quote) -> QuoteRecord:
        return QuoteRecord(
            id=quote.id,
            tenant_id=quote.tenant_id,
            requirement_id=quote.requirement_id,
            code=quote.code,
            currency=quote.currency,
            functional_currency=quote.functional_currency,
            fx_rate=quote.fx_rate,
            notes=quote.notes,
            status=quote.status.value,
            created_at=quote.created_at,
            updated_at=quote.updated_at,
            archived_at=quote.archived_at,
            issued_at=quote.issued_at,
            issue_key=quote.issue_key,
            version=quote.version,
        )

    @staticmethod
    def _quote_line_record(quote_line: QuoteLine) -> QuoteLineRecord:
        return QuoteLineRecord(
            id=quote_line.id,
            tenant_id=quote_line.tenant_id,
            quote_id=quote_line.quote_id,
            line_number=quote_line.line_number,
            description=quote_line.description,
            quantity=quote_line.quantity,
            unit_price=quote_line.unit_price,
            amount=quote_line.amount,
            status=quote_line.status.value,
            created_at=quote_line.created_at,
            updated_at=quote_line.updated_at,
            archived_at=quote_line.archived_at,
            version=quote_line.version,
        )

    @staticmethod
    def _conversion_record(conversion: QuoteConversion) -> QuoteConversionRecord:
        return QuoteConversionRecord(
            id=conversion.id,
            tenant_id=conversion.tenant_id,
            quote_id=conversion.quote_id,
            requirement_id=conversion.requirement_id,
            quote_version=conversion.quote_version,
            currency=conversion.currency,
            functional_currency=conversion.functional_currency,
            fx_rate=conversion.fx_rate,
            functional_total=conversion.functional_total,
            idempotency_key=conversion.idempotency_key,
            status=conversion.status.value,
            created_at=conversion.created_at,
            updated_at=conversion.updated_at,
            consumed_at=conversion.consumed_at,
            version=conversion.version,
        )

    @staticmethod
    def _sales_order_record(sales_order: SalesOrder) -> SalesOrderRecord:
        return SalesOrderRecord(
            id=sales_order.id,
            tenant_id=sales_order.tenant_id,
            conversion_id=sales_order.conversion_id,
            quote_id=sales_order.quote_id,
            requirement_id=sales_order.requirement_id,
            code=sales_order.code,
            currency=sales_order.currency,
            functional_currency=sales_order.functional_currency,
            fx_rate=sales_order.fx_rate,
            functional_total=sales_order.functional_total,
            idempotency_key=sales_order.idempotency_key,
            status=sales_order.status.value,
            created_at=sales_order.created_at,
            total_amount=sales_order.total_amount,
            ordered_quantity=sales_order.ordered_quantity,
            confirmed_at=sales_order.confirmed_at,
            shipped_quantity=sales_order.shipped_quantity,
            confirmation_key=sales_order.confirmation_key,
            version=sales_order.version,
        )

    @staticmethod
    def _sales_order_line_record(
        sales_order_line: SalesOrderLine,
    ) -> SalesOrderLineRecord:
        return SalesOrderLineRecord(
            id=sales_order_line.id,
            tenant_id=sales_order_line.tenant_id,
            sales_order_id=sales_order_line.sales_order_id,
            line_number=sales_order_line.line_number,
            description=sales_order_line.description,
            quantity=sales_order_line.quantity,
            unit_price=sales_order_line.unit_price,
            amount=sales_order_line.amount,
            created_at=sales_order_line.created_at,
        )

    @staticmethod
    def _delivery_order_record(
        delivery_order: DeliveryOrder,
    ) -> DeliveryOrderRecord:
        return DeliveryOrderRecord(
            id=delivery_order.id,
            tenant_id=delivery_order.tenant_id,
            sales_order_id=delivery_order.sales_order_id,
            sales_order_version=delivery_order.sales_order_version,
            quote_id=delivery_order.quote_id,
            requirement_id=delivery_order.requirement_id,
            code=delivery_order.code,
            currency=delivery_order.currency,
            total_amount=delivery_order.total_amount,
            idempotency_key=delivery_order.idempotency_key,
            status=delivery_order.status.value,
            created_at=delivery_order.created_at,
            released_at=delivery_order.released_at,
            release_key=delivery_order.release_key,
            version=delivery_order.version,
        )

    @staticmethod
    def _delivery_order_line_record(
        line: DeliveryOrderLine,
    ) -> DeliveryOrderLineRecord:
        return DeliveryOrderLineRecord(
            id=line.id,
            tenant_id=line.tenant_id,
            delivery_order_id=line.delivery_order_id,
            sales_order_line_id=line.sales_order_line_id,
            quantity=line.quantity,
            status=line.status.value,
            created_at=line.created_at,
        )

    @staticmethod
    def _ar_invoice_record(invoice: ARInvoice) -> ARInvoiceRecord:
        return ARInvoiceRecord(
            id=invoice.id,
            tenant_id=invoice.tenant_id,
            delivery_order_id=invoice.delivery_order_id,
            delivery_order_version=invoice.delivery_order_version,
            sales_order_id=invoice.sales_order_id,
            sales_order_version=invoice.sales_order_version,
            customer_id=invoice.customer_id,
            code=invoice.code,
            currency=invoice.currency,
            functional_currency=invoice.functional_currency,
            fx_rate=invoice.fx_rate,
            total_amount=invoice.total_amount,
            functional_total=invoice.functional_total,
            idempotency_key=invoice.idempotency_key,
            status=invoice.status.value,
            created_at=invoice.created_at,
            issued_at=invoice.issued_at,
            issue_key=invoice.issue_key,
            voided_at=invoice.voided_at,
            void_key=invoice.void_key,
            void_reason=invoice.void_reason,
            version=invoice.version,
        )

    @staticmethod
    def _return_authorization_record(
        authorization: ReturnAuthorization,
    ) -> ReturnAuthorizationRecord:
        return ReturnAuthorizationRecord(
            id=authorization.id,
            tenant_id=authorization.tenant_id,
            delivery_order_id=authorization.delivery_order_id,
            invoice_id=authorization.invoice_id,
            credit_note_id=authorization.credit_note_id,
            credit_note_key=authorization.credit_note_key,
            code=authorization.code,
            reason=authorization.reason,
            idempotency_key=authorization.idempotency_key,
            status=authorization.status.value,
            created_at=authorization.created_at,
            restocked_at=authorization.restocked_at,
            restock_key=authorization.restock_key,
            credit_note_issued_at=authorization.credit_note_issued_at,
            version=authorization.version,
        )

    @staticmethod
    def _customer_domain(record: CustomerRecord) -> Customer:
        return Customer(
            id=record.id,
            tenant_id=record.tenant_id,
            code=record.code,
            display_name=record.display_name,
            owner_subject_id=record.owner_subject_id,
            status=CustomerStatus(record.status),
            commercial_hold=bool(record.commercial_hold),
            created_at=record.created_at,
            updated_at=record.updated_at,
            archived_at=record.archived_at,
            version=record.version,
        )

    @staticmethod
    def _contact_domain(record: ContactRecord) -> Contact:
        return Contact(
            id=record.id,
            tenant_id=record.tenant_id,
            customer_id=record.customer_id,
            display_name=record.display_name,
            title=record.title,
            email=record.email,
            phone=record.phone,
            status=ContactStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            archived_at=record.archived_at,
            version=record.version,
        )

    @staticmethod
    def _opportunity_domain(record: OpportunityRecord) -> Opportunity:
        return Opportunity(
            id=record.id,
            tenant_id=record.tenant_id,
            customer_id=record.customer_id,
            code=record.code,
            title=record.title,
            owner_subject_id=record.owner_subject_id,
            status=OpportunityStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            archived_at=record.archived_at,
            version=record.version,
        )

    @staticmethod
    def _requirement_domain(record: RequirementRecord) -> Requirement:
        return Requirement(
            id=record.id,
            tenant_id=record.tenant_id,
            opportunity_id=record.opportunity_id,
            code=record.code,
            title=record.title,
            description=record.description,
            status=RequirementStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            archived_at=record.archived_at,
            version=record.version,
        )

    @staticmethod
    def _quote_domain(record: QuoteRecord) -> Quote:
        return Quote(
            id=record.id,
            tenant_id=record.tenant_id,
            requirement_id=record.requirement_id,
            code=record.code,
            currency=record.currency,
            functional_currency=record.functional_currency,
            fx_rate=record.fx_rate,
            notes=record.notes,
            status=QuoteStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            archived_at=record.archived_at,
            issued_at=record.issued_at,
            issue_key=record.issue_key,
            version=record.version,
        )

    @staticmethod
    def _quote_line_domain(record: QuoteLineRecord) -> QuoteLine:
        return QuoteLine(
            id=record.id,
            tenant_id=record.tenant_id,
            quote_id=record.quote_id,
            line_number=record.line_number,
            description=record.description,
            quantity=record.quantity,
            unit_price=record.unit_price,
            amount=record.amount,
            status=QuoteLineStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            archived_at=record.archived_at,
            version=record.version,
        )

    @staticmethod
    def _conversion_domain(record: QuoteConversionRecord) -> QuoteConversion:
        return QuoteConversion(
            id=record.id,
            tenant_id=record.tenant_id,
            quote_id=record.quote_id,
            requirement_id=record.requirement_id,
            quote_version=record.quote_version,
            currency=record.currency,
            functional_currency=record.functional_currency,
            fx_rate=record.fx_rate,
            functional_total=record.functional_total,
            idempotency_key=record.idempotency_key,
            status=ConversionStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            consumed_at=record.consumed_at,
            version=record.version,
        )

    @staticmethod
    def _sales_order_domain(record: SalesOrderRecord) -> SalesOrder:
        return SalesOrder(
            id=record.id,
            tenant_id=record.tenant_id,
            conversion_id=record.conversion_id,
            quote_id=record.quote_id,
            requirement_id=record.requirement_id,
            code=record.code,
            currency=record.currency,
            functional_currency=record.functional_currency,
            fx_rate=record.fx_rate,
            functional_total=record.functional_total,
            idempotency_key=record.idempotency_key,
            status=SalesOrderStatus(record.status),
            created_at=record.created_at,
            total_amount=record.total_amount,
            ordered_quantity=record.ordered_quantity,
            confirmed_at=record.confirmed_at,
            shipped_quantity=record.shipped_quantity,
            confirmation_key=record.confirmation_key,
            version=record.version,
        )

    @staticmethod
    def _sales_order_line_domain(
        record: SalesOrderLineRecord,
    ) -> SalesOrderLine:
        return SalesOrderLine(
            id=record.id,
            tenant_id=record.tenant_id,
            sales_order_id=record.sales_order_id,
            line_number=record.line_number,
            description=record.description,
            quantity=record.quantity,
            unit_price=record.unit_price,
            amount=record.amount,
            created_at=record.created_at,
        )

    @staticmethod
    def _delivery_order_domain(record: DeliveryOrderRecord) -> DeliveryOrder:
        return DeliveryOrder(
            id=record.id,
            tenant_id=record.tenant_id,
            sales_order_id=record.sales_order_id,
            sales_order_version=record.sales_order_version,
            quote_id=record.quote_id,
            requirement_id=record.requirement_id,
            code=record.code,
            currency=record.currency,
            total_amount=record.total_amount,
            idempotency_key=record.idempotency_key,
            status=DeliveryOrderStatus(record.status),
            created_at=record.created_at,
            released_at=record.released_at,
            release_key=record.release_key,
            version=record.version,
        )

    @staticmethod
    def _delivery_order_line_domain(
        record: DeliveryOrderLineRecord,
    ) -> DeliveryOrderLine:
        return DeliveryOrderLine(
            id=record.id,
            tenant_id=record.tenant_id,
            delivery_order_id=record.delivery_order_id,
            sales_order_line_id=record.sales_order_line_id,
            quantity=record.quantity,
            status=DeliveryOrderLineStatus(record.status),
            created_at=record.created_at,
        )

    @staticmethod
    def _ar_invoice_domain(record: ARInvoiceRecord) -> ARInvoice:
        return ARInvoice(
            id=record.id,
            tenant_id=record.tenant_id,
            delivery_order_id=record.delivery_order_id,
            delivery_order_version=record.delivery_order_version,
            sales_order_id=record.sales_order_id,
            sales_order_version=record.sales_order_version,
            customer_id=record.customer_id,
            code=record.code,
            currency=record.currency,
            functional_currency=record.functional_currency,
            fx_rate=record.fx_rate,
            total_amount=record.total_amount,
            functional_total=record.functional_total,
            idempotency_key=record.idempotency_key,
            status=ARInvoiceStatus(record.status),
            created_at=record.created_at,
            issued_at=record.issued_at,
            issue_key=record.issue_key,
            voided_at=record.voided_at,
            void_key=record.void_key,
            void_reason=record.void_reason,
            version=record.version,
        )

    @staticmethod
    def _return_authorization_domain(
        record: ReturnAuthorizationRecord,
    ) -> ReturnAuthorization:
        return ReturnAuthorization(
            id=record.id,
            tenant_id=record.tenant_id,
            delivery_order_id=record.delivery_order_id,
            invoice_id=record.invoice_id,
            credit_note_id=record.credit_note_id,
            credit_note_key=record.credit_note_key,
            code=record.code,
            reason=record.reason,
            idempotency_key=record.idempotency_key,
            status=ReturnAuthorizationStatus(record.status),
            created_at=record.created_at,
            restocked_at=record.restocked_at,
            restock_key=record.restock_key,
            credit_note_issued_at=record.credit_note_issued_at,
            version=record.version,
        )

    @staticmethod
    def _confirm_policy_record(
        policy: TenantConfirmPolicy,
    ) -> TenantConfirmPolicyRecord:
        return TenantConfirmPolicyRecord(
            tenant_id=policy.tenant_id,
            confirm_approval_required=policy.confirm_approval_required,
            quote_issue_approval_required=policy.quote_issue_approval_required,
            quote_convert_approval_required=policy.quote_convert_approval_required,
            so_confirm_workflow_approval_required=(
                policy.so_confirm_workflow_approval_required
            ),
            do_ship_approval_required=policy.do_ship_approval_required,
            do_release_approval_required=policy.do_release_approval_required,
            updated_at=policy.updated_at,
            version=policy.version,
        )

    @staticmethod
    def _confirm_policy_domain(
        record: TenantConfirmPolicyRecord,
    ) -> TenantConfirmPolicy:
        return TenantConfirmPolicy(
            tenant_id=record.tenant_id,
            confirm_approval_required=bool(record.confirm_approval_required),
            quote_issue_approval_required=bool(record.quote_issue_approval_required),
            quote_convert_approval_required=bool(
                record.quote_convert_approval_required
            ),
            so_confirm_workflow_approval_required=bool(
                record.so_confirm_workflow_approval_required
            ),
            do_ship_approval_required=bool(record.do_ship_approval_required),
            do_release_approval_required=bool(record.do_release_approval_required),
            updated_at=record.updated_at,
            version=record.version,
        )


class _FinanceCreditNoteCreateAdapter:
    """Keeps the CRM→Finance command inside the current SQL transaction."""

    def __init__(self, finance_service: Any) -> None:
        self._finance_service = finance_service

    def create_credit_note(
        self,
        ctx: ExecutionContext,
        *,
        invoice_id: UUID,
        amount: Decimal,
        idempotency_key: UUID,
    ) -> KernelResult[UUID]:
        result = self._finance_service.create_credit_note(
            ctx,
            invoice_id=invoice_id,
            amount=amount,
            idempotency_key=idempotency_key,
        )
        if not result.ok:
            return result
        if result.data is None:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL,
                "Finance returned no credit note",
            )
        return KernelResult.success(result.data.id, audit_id=result.audit_id)


class TransactionalCRMService:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        *,
        confirm_approval_gate: ConfirmApprovalGate | None = None,
        quote_issue_approval_gate: QuoteIssueApprovalGate | None = None,
        quote_convert_approval_gate: QuoteConvertApprovalGate | None = None,
        sales_order_confirm_approval_gate: SalesOrderConfirmApprovalGate | None = None,
        delivery_order_release_approval_gate: (
            DeliveryOrderReleaseApprovalGate | None
        ) = None,
    ) -> None:
        self._session_factory = session_factory
        self._confirm_approval_gate = confirm_approval_gate
        self._quote_issue_approval_gate = quote_issue_approval_gate
        self._quote_convert_approval_gate = quote_convert_approval_gate
        self._sales_order_confirm_approval_gate = sales_order_confirm_approval_gate
        self._delivery_order_release_approval_gate = (
            delivery_order_release_approval_gate
        )

    def set_quote_issue_approval_gate(
        self, gate: QuoteIssueApprovalGate | None
    ) -> None:
        self._quote_issue_approval_gate = gate

    def set_quote_convert_approval_gate(
        self, gate: QuoteConvertApprovalGate | None
    ) -> None:
        self._quote_convert_approval_gate = gate

    def set_sales_order_confirm_approval_gate(
        self, gate: SalesOrderConfirmApprovalGate | None
    ) -> None:
        self._sales_order_confirm_approval_gate = gate

    def set_delivery_order_release_approval_gate(
        self, gate: DeliveryOrderReleaseApprovalGate | None
    ) -> None:
        self._delivery_order_release_approval_gate = gate

    def create_customer(self, ctx: ExecutionContext, **kwargs) -> KernelResult[Customer]:
        return self._execute(ctx, lambda service: service.create_customer(ctx, **kwargs))

    def get_customer(self, ctx: ExecutionContext, **kwargs) -> KernelResult[Customer]:
        return self._execute(ctx, lambda service: service.get_customer(ctx, **kwargs))

    def list_customers(self, ctx: ExecutionContext, **kwargs) -> KernelResult:
        return self._execute(ctx, lambda service: service.list_customers(ctx, **kwargs))

    def update_customer(self, ctx: ExecutionContext, **kwargs) -> KernelResult[Customer]:
        return self._execute(ctx, lambda service: service.update_customer(ctx, **kwargs))

    def archive_customer(self, ctx: ExecutionContext, **kwargs) -> KernelResult[Customer]:
        return self._execute(ctx, lambda service: service.archive_customer(ctx, **kwargs))

    def set_customer_commercial_hold(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[Customer]:
        return self._execute(
            ctx, lambda service: service.set_customer_commercial_hold(ctx, **kwargs)
        )

    def get_confirm_approval_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantConfirmPolicy]:
        return self._execute(
            ctx, lambda service: service.get_confirm_approval_policy(ctx, **kwargs)
        )

    def set_confirm_approval_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantConfirmPolicy]:
        return self._execute(
            ctx, lambda service: service.set_confirm_approval_policy(ctx, **kwargs)
        )

    def get_quote_issue_approval_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantConfirmPolicy]:
        return self._execute(
            ctx,
            lambda service: service.get_quote_issue_approval_policy(ctx, **kwargs),
        )

    def set_quote_issue_approval_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantConfirmPolicy]:
        return self._execute(
            ctx,
            lambda service: service.set_quote_issue_approval_policy(ctx, **kwargs),
        )

    def get_quote_convert_approval_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantConfirmPolicy]:
        return self._execute(
            ctx,
            lambda service: service.get_quote_convert_approval_policy(ctx, **kwargs),
        )

    def set_quote_convert_approval_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantConfirmPolicy]:
        return self._execute(
            ctx,
            lambda service: service.set_quote_convert_approval_policy(ctx, **kwargs),
        )

    def get_so_confirm_workflow_approval_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantConfirmPolicy]:
        return self._execute(
            ctx,
            lambda service: service.get_so_confirm_workflow_approval_policy(
                ctx, **kwargs
            ),
        )

    def set_so_confirm_workflow_approval_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantConfirmPolicy]:
        return self._execute(
            ctx,
            lambda service: service.set_so_confirm_workflow_approval_policy(
                ctx, **kwargs
            ),
        )

    def get_do_ship_approval_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantConfirmPolicy]:
        return self._execute(
            ctx, lambda service: service.get_do_ship_approval_policy(ctx, **kwargs)
        )

    def set_do_ship_approval_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantConfirmPolicy]:
        return self._execute(
            ctx, lambda service: service.set_do_ship_approval_policy(ctx, **kwargs)
        )

    def get_do_release_approval_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantConfirmPolicy]:
        return self._execute(
            ctx, lambda service: service.get_do_release_approval_policy(ctx, **kwargs)
        )

    def set_do_release_approval_policy(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[TenantConfirmPolicy]:
        return self._execute(
            ctx, lambda service: service.set_do_release_approval_policy(ctx, **kwargs)
        )

    def create_contact(self, ctx: ExecutionContext, **kwargs) -> KernelResult[Contact]:
        return self._execute(ctx, lambda service: service.create_contact(ctx, **kwargs))

    def get_contact(self, ctx: ExecutionContext, **kwargs) -> KernelResult[Contact]:
        return self._execute(ctx, lambda service: service.get_contact(ctx, **kwargs))

    def list_contacts(self, ctx: ExecutionContext, **kwargs) -> KernelResult:
        return self._execute(ctx, lambda service: service.list_contacts(ctx, **kwargs))

    def update_contact(self, ctx: ExecutionContext, **kwargs) -> KernelResult[Contact]:
        return self._execute(ctx, lambda service: service.update_contact(ctx, **kwargs))

    def archive_contact(self, ctx: ExecutionContext, **kwargs) -> KernelResult[Contact]:
        return self._execute(ctx, lambda service: service.archive_contact(ctx, **kwargs))

    def create_opportunity(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[Opportunity]:
        return self._execute(
            ctx, lambda service: service.create_opportunity(ctx, **kwargs)
        )

    def get_opportunity(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[Opportunity]:
        return self._execute(
            ctx, lambda service: service.get_opportunity(ctx, **kwargs)
        )

    def list_opportunities(self, ctx: ExecutionContext, **kwargs) -> KernelResult:
        return self._execute(
            ctx, lambda service: service.list_opportunities(ctx, **kwargs)
        )

    def update_opportunity(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[Opportunity]:
        return self._execute(
            ctx, lambda service: service.update_opportunity(ctx, **kwargs)
        )

    def archive_opportunity(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[Opportunity]:
        return self._execute(
            ctx, lambda service: service.archive_opportunity(ctx, **kwargs)
        )

    def create_requirement(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[Requirement]:
        return self._execute(
            ctx, lambda service: service.create_requirement(ctx, **kwargs)
        )

    def get_requirement(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[Requirement]:
        return self._execute(
            ctx, lambda service: service.get_requirement(ctx, **kwargs)
        )

    def list_requirements(self, ctx: ExecutionContext, **kwargs) -> KernelResult:
        return self._execute(
            ctx, lambda service: service.list_requirements(ctx, **kwargs)
        )

    def update_requirement(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[Requirement]:
        return self._execute(
            ctx, lambda service: service.update_requirement(ctx, **kwargs)
        )

    def archive_requirement(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[Requirement]:
        return self._execute(
            ctx, lambda service: service.archive_requirement(ctx, **kwargs)
        )

    def create_quote(self, ctx: ExecutionContext, **kwargs) -> KernelResult[Quote]:
        return self._execute(ctx, lambda service: service.create_quote(ctx, **kwargs))

    def get_quote(self, ctx: ExecutionContext, **kwargs) -> KernelResult[Quote]:
        return self._execute(ctx, lambda service: service.get_quote(ctx, **kwargs))

    def list_quotes(self, ctx: ExecutionContext, **kwargs) -> KernelResult:
        return self._execute(ctx, lambda service: service.list_quotes(ctx, **kwargs))

    def update_quote(self, ctx: ExecutionContext, **kwargs) -> KernelResult[Quote]:
        return self._execute(ctx, lambda service: service.update_quote(ctx, **kwargs))

    def archive_quote(self, ctx: ExecutionContext, **kwargs) -> KernelResult[Quote]:
        return self._execute(ctx, lambda service: service.archive_quote(ctx, **kwargs))

    def issue_quote(self, ctx: ExecutionContext, **kwargs) -> KernelResult[Quote]:
        return self._execute(ctx, lambda service: service.issue_quote(ctx, **kwargs))

    def create_quote_line(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[QuoteLine]:
        return self._execute(
            ctx, lambda service: service.create_quote_line(ctx, **kwargs)
        )

    def get_quote_line(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[QuoteLine]:
        return self._execute(
            ctx, lambda service: service.get_quote_line(ctx, **kwargs)
        )

    def list_quote_lines(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[list[QuoteLine]]:
        return self._execute(
            ctx, lambda service: service.list_quote_lines(ctx, **kwargs)
        )

    def update_quote_line(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[QuoteLine]:
        return self._execute(
            ctx, lambda service: service.update_quote_line(ctx, **kwargs)
        )

    def archive_quote_line(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[QuoteLine]:
        return self._execute(
            ctx, lambda service: service.archive_quote_line(ctx, **kwargs)
        )

    def convert_quote(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[QuoteConversion]:
        return self._execute(ctx, lambda service: service.convert_quote(ctx, **kwargs))

    def get_conversion(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[QuoteConversion]:
        return self._execute(
            ctx, lambda service: service.get_conversion(ctx, **kwargs)
        )

    def create_sales_order(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[SalesOrder]:
        return self._execute(
            ctx, lambda service: service.create_sales_order(ctx, **kwargs)
        )

    def get_sales_order(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[SalesOrder]:
        return self._execute(
            ctx, lambda service: service.get_sales_order(ctx, **kwargs)
        )

    def list_sales_orders(self, ctx: ExecutionContext, **kwargs) -> KernelResult:
        return self._execute(
            ctx, lambda service: service.list_sales_orders(ctx, **kwargs)
        )

    def confirm_sales_order(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[SalesOrder]:
        return self._execute(
            ctx, lambda service: service.confirm_sales_order(ctx, **kwargs)
        )

    def list_sales_order_lines(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[list[SalesOrderLine]]:
        return self._execute(
            ctx, lambda service: service.list_sales_order_lines(ctx, **kwargs)
        )

    def create_delivery_order(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[DeliveryOrder]:
        return self._execute(
            ctx, lambda service: service.create_delivery_order(ctx, **kwargs)
        )

    def get_delivery_order(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[DeliveryOrder]:
        return self._execute(
            ctx, lambda service: service.get_delivery_order(ctx, **kwargs)
        )

    def release_delivery_order(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[DeliveryOrder]:
        return self._execute(
            ctx, lambda service: service.release_delivery_order(ctx, **kwargs)
        )

    def create_ar_invoice(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ARInvoice]:
        return self._execute(
            ctx, lambda service: service.create_ar_invoice(ctx, **kwargs)
        )

    def issue_ar_invoice(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ARInvoice]:
        return self._execute(
            ctx, lambda service: service.issue_ar_invoice(ctx, **kwargs)
        )

    def void_ar_invoice(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ARInvoice]:
        return self._execute(
            ctx, lambda service: service.void_ar_invoice(ctx, **kwargs)
        )

    def get_ar_invoice(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ARInvoice]:
        return self._execute(
            ctx, lambda service: service.get_ar_invoice(ctx, **kwargs)
        )

    def create_return_authorization(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ReturnAuthorization]:
        return self._execute(
            ctx,
            lambda service: service.create_return_authorization(ctx, **kwargs),
        )

    def get_return_authorization(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ReturnAuthorization]:
        return self._execute(
            ctx,
            lambda service: service.get_return_authorization(ctx, **kwargs),
        )

    def restock_return_authorization(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ReturnAuthorization]:
        return self._execute(
            ctx,
            lambda service: service.restock_return_authorization(ctx, **kwargs),
        )

    def create_credit_note_from_return_authorization(
        self, ctx: ExecutionContext, **kwargs
    ) -> KernelResult[ReturnAuthorization]:
        return self._execute(
            ctx,
            lambda service: service.create_credit_note_from_return_authorization(
                ctx, **kwargs
            ),
        )

    def _execute(
        self,
        ctx: ExecutionContext,
        operation: Callable[[CRMService], KernelResult[T]],
    ) -> KernelResult[T]:
        if ctx.tenant_id is None or ctx.platform_scope:
            return KernelResult.failure(
                ErrorCode.CTX_INVALID, "CRM requires a tenant data-plane context"
            )
        try:
            from noventi.inventory.persistence import (
                SQLAlchemyInventoryRepository,
            )
            from noventi.inventory.restock_adapter import (
                InventoryReturnRestockAdapter,
            )
            from noventi.finance.persistence import (
                SQLAlchemyARInvoiceReadAdapter,
                SQLAlchemyFinanceRepository,
            )
            from noventi.finance.service import FinanceService

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
                inventory_repo = SQLAlchemyInventoryRepository(
                    unit_of_work.session,
                    tenant_id=ctx.tenant_id,
                )
                finance_service = FinanceService(
                    permission,
                    repository=SQLAlchemyFinanceRepository(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                    ),
                    audit_log=audit,
                    ar_invoice_reader=SQLAlchemyARInvoiceReadAdapter(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                    ),
                )
                service = CRMService(
                    permission,
                    repository=SQLAlchemyCRMRepository(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                    ),
                    audit_log=audit,
                    confirm_approval_gate=self._confirm_approval_gate,
                    quote_issue_approval_gate=self._quote_issue_approval_gate,
                    quote_convert_approval_gate=self._quote_convert_approval_gate,
                    sales_order_confirm_approval_gate=(
                        self._sales_order_confirm_approval_gate
                    ),
                    delivery_order_release_approval_gate=(
                        self._delivery_order_release_approval_gate
                    ),
                    return_restock_port=InventoryReturnRestockAdapter(
                        inventory_repo
                    ),
                    credit_note_create_port=_FinanceCreditNoteCreateAdapter(
                        finance_service
                    ),
                    domain_events=DomainEventEmitter(
                        SQLAlchemyOutboxWriter(unit_of_work.session)
                    ),
                )
                result = operation(service)
                unit_of_work.commit()
                return result
        except IntegrityError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "CRM persistence conflict"
            )
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL, "CRM persistence unavailable"
            )
