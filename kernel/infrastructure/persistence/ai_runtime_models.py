"""SQLAlchemy mappings for AI Runtime persistence."""

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

RUN_STATUSES = (
    "'planned','running','pending_approval','completed','failed','cancelled'"
)


class AIAgentRunRecord(Base):
    __tablename__ = "ai_agent_runs"
    __table_args__ = (
        CheckConstraint(f"status IN ({RUN_STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_ai_agent_runs_tenant_subject", "tenant_id", "subject_id"),
        Index("ix_ai_agent_runs_tenant_status", "tenant_id", "status"),
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
    goal: Mapped[str] = mapped_column(String(1000), nullable=False)
    plan_summary: Mapped[str] = mapped_column(String(2000), nullable=False, server_default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    approval_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class AIToolDeclarationRecord(Base):
    __tablename__ = "ai_tool_declarations"
    __table_args__ = (
        Index(
            "uq_ai_tool_declarations_tenant_name",
            "tenant_id",
            text("lower(name)"),
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
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    high_impact: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AIMemoryEntryRecord(Base):
    __tablename__ = "ai_memory_entries"
    __table_args__ = (
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "uq_ai_memory_entries_run_key",
            "tenant_id",
            "run_id",
            text("lower(key)"),
            unique=True,
        ),
        Index("ix_ai_memory_entries_run", "tenant_id", "run_id"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    run_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.ai_agent_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    key: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
