"""SQLAlchemy mappings for Enterprise Brain persistence."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from kernel.infrastructure.persistence.metadata import Base

INSIGHT_KINDS = "'insight','recommendation','simulation'"


class BrainInsightRecord(Base):
    __tablename__ = "brain_insights"
    __table_args__ = (
        CheckConstraint(f"kind IN ({INSIGHT_KINDS})", name="kind_valid"),
        CheckConstraint("confidence >= 0 AND confidence <= 1", name="confidence_range"),
        CheckConstraint("advisory = true", name="advisory_required"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_brain_insights_tenant_kind", "tenant_id", "kind"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    kind: Mapped[str] = mapped_column(String(32), nullable=False)
    summary: Mapped[str] = mapped_column(String(2000), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    source_ref: Mapped[str] = mapped_column(String(512), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    advisory: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    bias_notes: Mapped[str] = mapped_column(String(2000), nullable=False, server_default="")
    twin_ref: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.twin_snapshots.id", ondelete="RESTRICT"),
        nullable=True,
    )
    knowledge_refs_json: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    details_json: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
