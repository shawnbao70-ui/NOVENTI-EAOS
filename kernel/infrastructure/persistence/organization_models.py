"""SQLAlchemy mappings for Organization persistence."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
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
from sqlalchemy.orm import Mapped, mapped_column

from kernel.infrastructure.persistence.metadata import Base

ORG_STATUSES = "'active','suspended','closed','inactive','ended'"
UNIT_TYPES = "'hq','group','branch','department','other'"


class TenantRecord(Base):
    __tablename__ = "tenants"
    __table_args__ = (
        CheckConstraint(f"status IN ({ORG_STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("uq_tenants_legal_name_ci", text("lower(legal_name)"), unique=True),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    region_policy_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class EnterpriseRecord(Base):
    __tablename__ = "enterprises"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id"),
        CheckConstraint(f"status IN ({ORG_STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index(
            "uq_enterprises_tenant_legal_name_ci",
            "tenant_id",
            text("lower(legal_name)"),
            unique=True,
        ),
        Index(
            "uq_enterprises_primary_per_tenant",
            "tenant_id",
            unique=True,
            postgresql_where=text("is_primary"),
            sqlite_where=text("is_primary = 1"),
        ),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class OrganizationUnitRecord(Base):
    __tablename__ = "org_units"
    __table_args__ = (
        ForeignKeyConstraint(
            ["parent_unit_id", "tenant_id"],
            ["kernel.org_units.id", "kernel.org_units.tenant_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["parent_unit_id", "tenant_id", "enterprise_id"],
            [
                "kernel.org_units.id",
                "kernel.org_units.tenant_id",
                "kernel.org_units.enterprise_id",
            ],
            ondelete="RESTRICT",
            name="fk_org_units_parent_tenant_enterprise",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "tenant_id"],
            ["kernel.enterprises.id", "kernel.enterprises.tenant_id"],
            ondelete="RESTRICT",
        ),
        UniqueConstraint("id", "tenant_id"),
        UniqueConstraint(
            "id",
            "tenant_id",
            "enterprise_id",
            name="uq_org_units_id_tenant_enterprise",
        ),
        CheckConstraint(f"unit_type IN ({UNIT_TYPES})", name="unit_type_valid"),
        CheckConstraint(f"status IN ({ORG_STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_org_units_tenant_parent", "tenant_id", "parent_unit_id"),
        Index("ix_org_units_tenant_enterprise", "tenant_id", "enterprise_id"),
        Index("ix_org_units_tenant_status", "tenant_id", "status"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    parent_unit_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    enterprise_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    unit_type: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class MembershipRecord(Base):
    __tablename__ = "memberships"
    __table_args__ = (
        ForeignKeyConstraint(
            ["org_unit_id", "tenant_id"],
            ["kernel.org_units.id", "kernel.org_units.tenant_id"],
            ondelete="RESTRICT",
        ),
        ForeignKeyConstraint(
            ["org_unit_id", "tenant_id", "enterprise_id"],
            [
                "kernel.org_units.id",
                "kernel.org_units.tenant_id",
                "kernel.org_units.enterprise_id",
            ],
            ondelete="RESTRICT",
            name="fk_memberships_unit_tenant_enterprise",
        ),
        ForeignKeyConstraint(
            ["enterprise_id", "tenant_id"],
            ["kernel.enterprises.id", "kernel.enterprises.tenant_id"],
            ondelete="RESTRICT",
        ),
        CheckConstraint(f"status IN ({ORG_STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        Index("ix_memberships_tenant_subject", "tenant_id", "subject_id"),
        Index("ix_memberships_tenant_unit", "tenant_id", "org_unit_id"),
        Index("ix_memberships_tenant_enterprise", "tenant_id", "enterprise_id"),
        Index(
            "uq_memberships_active_unit",
            "tenant_id",
            "enterprise_id",
            "subject_id",
            "org_unit_id",
            unique=True,
            postgresql_where=text("status = 'active' AND org_unit_id IS NOT NULL"),
            sqlite_where=text("status = 'active' AND org_unit_id IS NOT NULL"),
        ),
        Index(
            "uq_memberships_active_no_unit",
            "tenant_id",
            "enterprise_id",
            "subject_id",
            unique=True,
            postgresql_where=text("status = 'active' AND org_unit_id IS NULL"),
            sqlite_where=text("status = 'active' AND org_unit_id IS NULL"),
        ),
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
    org_unit_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    enterprise_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    membership_role_label: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
