"""SQLAlchemy mapping for tenant IdP federation bindings (PHX-G67/G78)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Index, Integer, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from kernel.infrastructure.persistence.metadata import Base

STATUSES = "'active','disabled'"
DEFAULT_PRIORITY = 100


class TenantIdpBindingRecord(Base):
    __tablename__ = "tenant_idp_bindings"
    __table_args__ = (
        CheckConstraint(f"status IN ({STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        CheckConstraint("priority >= 0", name="priority_nonneg"),
        Index(
            "ix_tenant_idp_bindings_tenant_issuer_lower",
            "tenant_id",
            text("lower(issuer)"),
            unique=True,
        ),
        Index(
            "ix_tenant_idp_bindings_tenant_status",
            "tenant_id",
            "status",
            unique=False,
        ),
        Index(
            "ix_tenant_idp_bindings_tenant_priority",
            "tenant_id",
            "priority",
            unique=False,
        ),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    issuer: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    priority: Mapped[int] = mapped_column(
        Integer, nullable=False, default=DEFAULT_PRIORITY
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
