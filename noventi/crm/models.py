"""Customer and Contact models owned by the ``noventi.crm`` package."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Generic, TypeVar
from uuid import UUID

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Page(Generic[T]):
    items: list[T]
    next_cursor: str | None


class CustomerStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class ContactStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class OpportunityStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class RequirementStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class QuoteStatus(StrEnum):
    DRAFT = "draft"
    ISSUED = "issued"
    ARCHIVED = "archived"


class ConversionStatus(StrEnum):
    READY = "ready"
    CONSUMED = "consumed"


class SalesOrderStatus(StrEnum):
    CREATED = "created"
    CONFIRMED = "confirmed"
    PARTIALLY_SHIPPED = "partially_shipped"
    SHIPPED = "shipped"


class QuoteLineStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class DeliveryOrderStatus(StrEnum):
    DRAFT = "draft"
    RELEASED = "released"
    SHIPPED = "shipped"


class DeliveryOrderLineStatus(StrEnum):
    OPEN = "open"
    SHIPPED = "shipped"


class ARInvoiceStatus(StrEnum):
    DRAFT = "draft"
    ISSUED = "issued"
    CLOSED = "closed"
    VOIDED = "voided"


class ReturnAuthorizationStatus(StrEnum):
    DRAFT = "draft"
    RESTOCKED = "restocked"


@dataclass(slots=True)
class Customer:
    id: UUID
    tenant_id: UUID
    code: str
    display_name: str
    owner_subject_id: UUID | None
    status: CustomerStatus
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None
    commercial_hold: bool = False
    version: int = 1


@dataclass(slots=True)
class Contact:
    id: UUID
    tenant_id: UUID
    customer_id: UUID
    display_name: str
    title: str | None
    email: str | None
    phone: str | None
    status: ContactStatus
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None
    version: int = 1


@dataclass(slots=True)
class Opportunity:
    id: UUID
    tenant_id: UUID
    customer_id: UUID
    code: str
    title: str
    owner_subject_id: UUID | None
    status: OpportunityStatus
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None
    version: int = 1


@dataclass(slots=True)
class Requirement:
    id: UUID
    tenant_id: UUID
    opportunity_id: UUID
    code: str
    title: str
    description: str | None
    status: RequirementStatus
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None
    version: int = 1


@dataclass(slots=True)
class Quote:
    id: UUID
    tenant_id: UUID
    requirement_id: UUID
    code: str
    currency: str
    notes: str | None
    status: QuoteStatus
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None
    issued_at: datetime | None = None
    issue_key: UUID | None = None
    version: int = 1
    functional_currency: str | None = None
    fx_rate: Decimal | None = None


@dataclass(slots=True)
class QuoteConversion:
    id: UUID
    tenant_id: UUID
    quote_id: UUID
    requirement_id: UUID
    quote_version: int
    currency: str
    idempotency_key: UUID
    status: ConversionStatus
    created_at: datetime
    updated_at: datetime
    consumed_at: datetime | None = None
    version: int = 1
    functional_currency: str | None = None
    fx_rate: Decimal | None = None
    functional_total: Decimal | None = None


@dataclass(slots=True)
class SalesOrder:
    id: UUID
    tenant_id: UUID
    conversion_id: UUID
    quote_id: UUID
    requirement_id: UUID
    code: str
    currency: str
    idempotency_key: UUID
    status: SalesOrderStatus
    created_at: datetime
    total_amount: Decimal = Decimal("0.00")
    ordered_quantity: Decimal = Decimal("0.000")
    confirmed_at: datetime | None = None
    confirmation_key: UUID | None = None
    shipped_quantity: Decimal = Decimal("0.000")
    version: int = 1
    functional_currency: str | None = None
    fx_rate: Decimal | None = None
    functional_total: Decimal | None = None


@dataclass(slots=True)
class QuoteLine:
    id: UUID
    tenant_id: UUID
    quote_id: UUID
    line_number: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal
    status: QuoteLineStatus
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None
    version: int = 1


@dataclass(slots=True)
class SalesOrderLine:
    id: UUID
    tenant_id: UUID
    sales_order_id: UUID
    line_number: int
    description: str
    quantity: Decimal
    unit_price: Decimal
    amount: Decimal
    created_at: datetime


@dataclass(slots=True)
class DeliveryOrder:
    id: UUID
    tenant_id: UUID
    sales_order_id: UUID
    sales_order_version: int
    quote_id: UUID
    requirement_id: UUID
    code: str
    currency: str
    total_amount: Decimal
    idempotency_key: UUID
    status: DeliveryOrderStatus
    created_at: datetime
    released_at: datetime | None = None
    release_key: UUID | None = None
    version: int = 1


@dataclass(slots=True)
class DeliveryOrderLine:
    id: UUID
    tenant_id: UUID
    delivery_order_id: UUID
    sales_order_line_id: UUID
    quantity: Decimal
    status: DeliveryOrderLineStatus
    created_at: datetime


@dataclass(slots=True)
class ARInvoice:
    id: UUID
    tenant_id: UUID
    delivery_order_id: UUID
    delivery_order_version: int
    sales_order_id: UUID
    sales_order_version: int
    customer_id: UUID
    code: str
    currency: str
    total_amount: Decimal
    idempotency_key: UUID
    status: ARInvoiceStatus
    created_at: datetime
    issued_at: datetime | None = None
    issue_key: UUID | None = None
    voided_at: datetime | None = None
    void_key: UUID | None = None
    void_reason: str | None = None
    version: int = 1
    functional_currency: str | None = None
    fx_rate: Decimal | None = None
    functional_total: Decimal | None = None


@dataclass(slots=True)
class ReturnAuthorization:
    id: UUID
    tenant_id: UUID
    delivery_order_id: UUID
    code: str
    reason: str
    idempotency_key: UUID
    status: ReturnAuthorizationStatus
    created_at: datetime
    invoice_id: UUID | None = None
    credit_note_id: UUID | None = None
    credit_note_key: UUID | None = None
    restocked_at: datetime | None = None
    restock_key: UUID | None = None
    credit_note_issued_at: datetime | None = None
    version: int = 1


@dataclass(slots=True)
class TenantConfirmPolicy:
    tenant_id: UUID
    confirm_approval_required: bool
    quote_issue_approval_required: bool
    quote_convert_approval_required: bool
    so_confirm_workflow_approval_required: bool
    do_ship_approval_required: bool
    do_release_approval_required: bool
    updated_at: datetime
    version: int = 1
