"""SQLAlchemy mappings for Knowledge Shared Capability persistence."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
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

KNOWLEDGE_LAYERS = "'canonical','operational','documentary','derived'"
KNOWLEDGE_STATUSES = "'active','archived'"
PROVENANCE_SUBJECT_KINDS = "'entity','link'"


class KnowledgeEntityRecord(Base):
    __tablename__ = "knowledge_entities"
    __table_args__ = (
        CheckConstraint(f"layer IN ({KNOWLEDGE_LAYERS})", name="layer_valid"),
        CheckConstraint(f"status IN ({KNOWLEDGE_STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_knowledge_entities_tenant_type", "tenant_id", "entity_type"),
        Index("ix_knowledge_entities_tenant_status", "tenant_id", "status"),
        Index(
            "uq_knowledge_entities_active_type_name",
            "tenant_id",
            text("lower(entity_type)"),
            text("lower(name)"),
            unique=True,
            postgresql_where=text("status = 'active'"),
            sqlite_where=text("status = 'active'"),
        ),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    entity_type: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    layer: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    attributes: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    labels: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    shared_with_subject_ids: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    retain_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class KnowledgeLinkRecord(Base):
    __tablename__ = "knowledge_links"
    __table_args__ = (
        CheckConstraint(f"status IN ({KNOWLEDGE_STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        CheckConstraint("from_entity_id <> to_entity_id", name="no_self_link"),
        Index("ix_knowledge_links_tenant_from", "tenant_id", "from_entity_id"),
        Index("ix_knowledge_links_tenant_to", "tenant_id", "to_entity_id"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    from_entity_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.knowledge_entities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    to_entity_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.knowledge_entities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    relation_type: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    attributes: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class KnowledgeProvenanceRecord(Base):
    __tablename__ = "knowledge_provenance"
    __table_args__ = (
        CheckConstraint(
            f"subject_kind IN ({PROVENANCE_SUBJECT_KINDS})",
            name="subject_kind_valid",
        ),
        Index(
            "ix_knowledge_provenance_subject",
            "tenant_id",
            "subject_kind",
            "subject_id",
        ),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    subject_kind: Mapped[str] = mapped_column(String(16), nullable=False)
    subject_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    actor_subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    source_ref: Mapped[str] = mapped_column(String(512), nullable=False)
    reason: Mapped[str] = mapped_column(String(1000), nullable=False)
    derived: Mapped[bool] = mapped_column(Boolean, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
