"""SQLAlchemy mappings for Identity persistence."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from kernel.infrastructure.persistence.metadata import Base

SUBJECT_TYPES = "'human','ai_employee','service','device','application','plugin'"
ENTITY_STATUSES = "'active','archived','revoked','ended'"
ASSIGNMENT_MODES = "'assign','reassign','inherit','archive'"


class SubjectRecord(Base):
    __tablename__ = "subjects"
    __table_args__ = (
        CheckConstraint(
            f"subject_type IN ({SUBJECT_TYPES})",
            name="subject_type_valid",
        ),
        CheckConstraint(
            f"status IN ({ENTITY_STATUSES})",
            name="status_valid",
        ),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_subjects_tenant_status", "tenant_id", "status"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    subject_type: Mapped[str] = mapped_column(String(32), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default=text("'active'"),
    )
    is_platform_managed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )


class AIEmployeeProfileRecord(Base):
    __tablename__ = "ai_employee_profiles"
    __table_args__ = (
        CheckConstraint("version > 0", name="version_positive"),
        {"schema": "kernel"},
    )

    ai_subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        primary_key=True,
    )
    capabilities_profile_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_policy_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)


class SubjectExternalRefRecord(Base):
    __tablename__ = "subject_external_refs"
    __table_args__ = (
        UniqueConstraint("system", "external_id"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="CASCADE"),
        nullable=False,
    )
    system: Mapped[str] = mapped_column(String(100), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CredentialRecord(Base):
    __tablename__ = "credentials"
    __table_args__ = (
        CheckConstraint(
            f"status IN ({ENTITY_STATUSES})",
            name="status_valid",
        ),
        Index("ix_credentials_tenant_subject", "tenant_id", "subject_id"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    credential_kind: Mapped[str] = mapped_column(String(64), nullable=False)
    secret_handle: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default=text("'active'"),
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class SessionRecord(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        Index("ix_sessions_tenant_subject", "tenant_id", "subject_id"),
        Index("ix_sessions_tenant_expires", "tenant_id", "expires_at"),
        Index("ix_sessions_tenant_credential", "tenant_id", "credential_id"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    credential_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.credentials.id", ondelete="RESTRICT"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    correlation_id_at_issue: Mapped[str] = mapped_column(String(128), nullable=False)


class AIAssignmentRecord(Base):
    __tablename__ = "ai_assignments"
    __table_args__ = (
        CheckConstraint(
            f"mode IN ({ASSIGNMENT_MODES})",
            name="mode_valid",
        ),
        CheckConstraint(
            f"status IN ({ENTITY_STATUSES})",
            name="status_valid",
        ),
        Index("ix_ai_assignments_tenant_status", "tenant_id", "status"),
        Index("ix_ai_assignments_ai_status", "ai_subject_id", "status"),
        Index(
            "uq_ai_assignments_ai_active",
            "ai_subject_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
            sqlite_where=text("status = 'active'"),
        ),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    ai_subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    mode: Mapped[str] = mapped_column(String(32), nullable=False)
    management_policy: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    predecessor_assignment_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.ai_assignments.id", ondelete="RESTRICT"),
        nullable=True,
    )
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default=text("'active'"),
    )


class PlatformIdentityGovernorRecord(Base):
    __tablename__ = "platform_identity_governors"
    __table_args__ = (
        CheckConstraint("status IN ('active','revoked')", name="status_valid"),
        Index(
            "uq_platform_identity_governors_subject_active",
            "subject_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
            sqlite_where=text("status = 'active'"),
        ),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    subject_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    granted_by_subject_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    revoked_by_subject_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        nullable=True,
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    revocation_reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)
