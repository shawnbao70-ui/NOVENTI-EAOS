"""Marketplace domain models (PHX-M16 technical foundation)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID


class ListingStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"
    REVOKED = "revoked"


@dataclass(frozen=True, slots=True)
class CapabilityDeclaration:
    required_permissions: frozenset[str]
    declared_events: frozenset[str]
    data_scope: str


@dataclass(slots=True)
class MarketplaceListing:
    id: UUID
    tenant_id: UUID
    package_key: str
    package_version: str
    publisher_subject_id: UUID
    status: ListingStatus
    capability: CapabilityDeclaration
    created_at: datetime
    updated_at: datetime
    signature_ref: Optional[str] = None
    review_notes: str = ""
    version: int = 1


@dataclass(slots=True)
class MarketplaceAcquisition:
    id: UUID
    tenant_id: UUID
    listing_id: UUID
    package_key: str
    package_version: str
    acquired_by_subject_id: UUID
    created_at: datetime
    version: int = 1


class InvoiceStatus(StrEnum):
    ISSUED = "issued"
    VOID = "void"


class DisputeStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"


@dataclass(slots=True)
class ListingPricing:
    listing_id: UUID
    tenant_id: UUID
    pricing_model: str
    amount: str
    currency: str
    updated_at: datetime
    version: int = 1


@dataclass(slots=True)
class ListingRevenueShare:
    listing_id: UUID
    tenant_id: UUID
    platform_share_bps: int
    updated_at: datetime
    version: int = 1


@dataclass(slots=True)
class MarketplaceInvoice:
    id: UUID
    tenant_id: UUID
    listing_id: UUID
    amount: str
    currency: str
    billing_cycle: str
    status: InvoiceStatus
    issued_by_subject_id: UUID
    created_at: datetime
    version: int = 1


@dataclass(slots=True)
class MarketplaceDispute:
    id: UUID
    tenant_id: UUID
    listing_id: UUID
    reason: str
    status: DisputeStatus
    opened_by_subject_id: UUID
    created_at: datetime
    resolution: str = ""
    resolved_by_subject_id: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    version: int = 1
