"""SQLAlchemy mappings for Workflow persistence."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from kernel.infrastructure.persistence.metadata import Base

WORKFLOW_STATUSES = (
    "'running','pending_approval','approved','rejected','cancelled',"
    "'completed','compensating','compensated'"
)
TASK_STATUSES = "'pending','approved','rejected','cancelled'"


class WorkflowDefinitionRecord(Base):
    __tablename__ = "workflow_definitions"
    __table_args__ = (
        CheckConstraint("status IN ('active','deprecated')", name="status_valid"),
        Index(
            "uq_workflow_definitions_tenant_name_version",
            "tenant_id",
            text("lower(name)"),
            "version",
            unique=True,
            postgresql_where=text("tenant_id IS NOT NULL"),
            sqlite_where=text("tenant_id IS NOT NULL"),
        ),
        Index(
            "uq_workflow_definitions_platform_name_version",
            text("lower(name)"),
            "version",
            unique=True,
            postgresql_where=text("tenant_id IS NULL"),
            sqlite_where=text("tenant_id IS NULL"),
        ),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    document_ref: Mapped[str] = mapped_column(String(512), nullable=False)
    version: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class WorkflowInstanceRecord(Base):
    __tablename__ = "workflow_instances"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        CheckConstraint(f"status IN ({WORKFLOW_STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_workflow_instances_tenant_status", "tenant_id", "status"),
        Index("ix_workflow_instances_tenant_business", "tenant_id", "business_key"),
        Index(
            "uq_workflow_instances_active_business_key",
            "tenant_id",
            "business_key",
            unique=True,
            postgresql_where=text(
                "business_key IS NOT NULL AND status IN "
                "('running','pending_approval','approved','compensating')"
            ),
            sqlite_where=text(
                "business_key IS NOT NULL AND status IN "
                "('running','pending_approval','approved','compensating')"
            ),
        ),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    definition_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.workflow_definitions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    initiator_subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    business_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_task_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    approval_principal_subject_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=True,
    )
    approval_action: Mapped[str | None] = mapped_column(String(128), nullable=True)
    approval_resource_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    approval_plan_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    approval_scope: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approval_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class WorkflowTaskRecord(Base):
    __tablename__ = "workflow_tasks"
    __table_args__ = (
        ForeignKeyConstraint(
            ["instance_id", "tenant_id"],
            ["kernel.workflow_instances.id", "kernel.workflow_instances.tenant_id"],
            ondelete="CASCADE",
        ),
        CheckConstraint(f"status IN ({TASK_STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_workflow_tasks_tenant_assignee", "tenant_id", "assignee_subject_id"),
        Index("ix_workflow_tasks_tenant_status", "tenant_id", "status"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    instance_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    assignee_subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    decision_comment: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    escalated_from_subject_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=True,
    )
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class WorkflowHistoryRecord(Base):
    __tablename__ = "workflow_history"
    __table_args__ = (
        ForeignKeyConstraint(
            ["instance_id", "tenant_id"],
            ["kernel.workflow_instances.id", "kernel.workflow_instances.tenant_id"],
            ondelete="CASCADE",
        ),
        Index("ix_workflow_history_instance_time", "instance_id", "timestamp"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    instance_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    correlation_id: Mapped[str] = mapped_column(String(128), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )


class WorkflowSignalReceiptRecord(Base):
    __tablename__ = "workflow_signal_receipts"
    __table_args__ = (
        ForeignKeyConstraint(
            ["instance_id", "tenant_id"],
            ["kernel.workflow_instances.id", "kernel.workflow_instances.tenant_id"],
            ondelete="CASCADE",
        ),
        CheckConstraint(f"resulting_status IN ({WORKFLOW_STATUSES})", name="status_valid"),
        {"schema": "kernel"},
    )

    instance_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    idempotency_key: Mapped[str] = mapped_column(String(255), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    request_fingerprint: Mapped[str] = mapped_column(String(64), nullable=False)
    resulting_status: Mapped[str] = mapped_column(String(32), nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
