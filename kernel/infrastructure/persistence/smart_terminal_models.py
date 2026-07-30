"""SQLAlchemy mappings for Smart Terminal workspace persistence."""

from __future__ import annotations

from datetime import datetime
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

SESSION_STATUSES = "'open','closed'"
INTENT_STATUSES = "'draft','previewed','cancelled'"
PREVIEW_STATUSES = "'active','invalidated','committed'"
DEVICE_TRUSTS = "'trusted','untrusted'"
EXTENSION_STATUSES = "'registered','active','revoked'"


class TerminalSessionRecord(Base):
    __tablename__ = "terminal_sessions"
    __table_args__ = (
        CheckConstraint(f"status IN ({SESSION_STATUSES})", name="status_valid"),
        CheckConstraint(f"device_trust IN ({DEVICE_TRUSTS})", name="device_trust_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_terminal_sessions_tenant_subject", "tenant_id", "subject_id"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    identity_session_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    correlation_id: Mapped[str] = mapped_column(String(128), nullable=False)
    device_trust: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class TerminalIntentRecord(Base):
    __tablename__ = "terminal_intents"
    __table_args__ = (
        CheckConstraint(f"status IN ({INTENT_STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_terminal_intents_tenant_session", "tenant_id", "terminal_session_id"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    terminal_session_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.terminal_sessions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class TerminalPreviewRecord(Base):
    __tablename__ = "terminal_previews"
    __table_args__ = (
        CheckConstraint(f"status IN ({PREVIEW_STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_terminal_previews_tenant_intent", "tenant_id", "intent_id"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    intent_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.terminal_intents.id", ondelete="RESTRICT"),
        nullable=False,
    )
    terminal_session_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.terminal_sessions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    action: Mapped[str] = mapped_column(String(256), nullable=False)
    resource_ref: Mapped[str] = mapped_column(String(512), nullable=False)
    plan_version: Mapped[str] = mapped_column(String(128), nullable=False)
    scope: Mapped[str] = mapped_column(String(256), nullable=False)
    impact_summary: Mapped[str] = mapped_column(String(2000), nullable=False)
    high_impact: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    approval_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class TerminalExtensionRecord(Base):
    __tablename__ = "terminal_extensions"
    __table_args__ = (
        CheckConstraint(f"status IN ({EXTENSION_STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "ix_terminal_extensions_tenant_key",
            "tenant_id",
            text("lower(extension_key)"),
            "extension_version",
        ),
        Index("ix_terminal_extensions_tenant_status", "tenant_id", "status"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    extension_key: Mapped[str] = mapped_column(String(256), nullable=False)
    extension_version: Mapped[str] = mapped_column(String(64), nullable=False)
    signature_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    declared_capabilities_json: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    declared_actions_json: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    allowed_surfaces_json: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    data_scope: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
