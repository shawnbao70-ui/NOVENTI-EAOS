"""SQLAlchemy mappings for Marketplace persistence."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from kernel.infrastructure.persistence.metadata import Base

LISTING_STATUSES = (
    "'draft','submitted','approved','rejected','published','revoked'"
)


class MarketplaceListingRecord(Base):
    __tablename__ = "marketplace_listings"
    __table_args__ = (
        CheckConstraint(f"status IN ({LISTING_STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "ix_marketplace_listings_tenant_package",
            "tenant_id",
            text("lower(package_key)"),
            "package_version",
        ),
        Index("ix_marketplace_listings_tenant_status", "tenant_id", "status"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    package_key: Mapped[str] = mapped_column(String(256), nullable=False)
    package_version: Mapped[str] = mapped_column(String(64), nullable=False)
    publisher_subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    signature_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    review_notes: Mapped[str] = mapped_column(String(2000), nullable=False, server_default="")
    required_permissions_json: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    declared_events_json: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    data_scope: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class MarketplaceAcquisitionRecord(Base):
    __tablename__ = "marketplace_acquisitions"
    __table_args__ = (
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "uq_marketplace_acquisitions_tenant_listing",
            "tenant_id",
            "listing_id",
            unique=True,
        ),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    listing_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.marketplace_listings.id", ondelete="RESTRICT"),
        nullable=False,
    )
    package_key: Mapped[str] = mapped_column(String(256), nullable=False)
    package_version: Mapped[str] = mapped_column(String(64), nullable=False)
    acquired_by_subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class MarketplacePricingRecord(Base):
    __tablename__ = "marketplace_listing_pricing"
    __table_args__ = (
        CheckConstraint("version > 0", name="version_positive"),
        CheckConstraint("pricing_model = 'fixed'", name="pricing_model_fixed"),
        {"schema": "kernel"},
    )

    listing_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.marketplace_listings.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    pricing_model: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[str] = mapped_column(String(64), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class MarketplaceRevenueShareRecord(Base):
    __tablename__ = "marketplace_listing_revenue_share"
    __table_args__ = (
        CheckConstraint("version > 0", name="version_positive"),
        CheckConstraint(
            "platform_share_bps >= 0 AND platform_share_bps <= 5000",
            name="platform_share_bps_range",
        ),
        {"schema": "kernel"},
    )

    listing_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.marketplace_listings.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    platform_share_bps: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class MarketplaceInvoiceRecord(Base):
    __tablename__ = "marketplace_invoices"
    __table_args__ = (
        CheckConstraint("version > 0", name="version_positive"),
        CheckConstraint("status IN ('issued','void')", name="invoice_status_valid"),
        CheckConstraint("billing_cycle = 'immediate'", name="billing_cycle_immediate"),
        Index("ix_marketplace_invoices_tenant_listing", "tenant_id", "listing_id"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    listing_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.marketplace_listings.id", ondelete="RESTRICT"),
        nullable=False,
    )
    amount: Mapped[str] = mapped_column(String(64), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    billing_cycle: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    issued_by_subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class MarketplaceDisputeRecord(Base):
    __tablename__ = "marketplace_disputes"
    __table_args__ = (
        CheckConstraint("version > 0", name="version_positive"),
        CheckConstraint("status IN ('open','resolved')", name="dispute_status_valid"),
        Index("ix_marketplace_disputes_tenant_listing", "tenant_id", "listing_id"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    listing_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.marketplace_listings.id", ondelete="RESTRICT"),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(String(2000), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    opened_by_subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    resolution: Mapped[str] = mapped_column(String(2000), nullable=False, server_default="")
    resolved_by_subject_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
