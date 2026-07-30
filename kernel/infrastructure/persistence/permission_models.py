"""SQLAlchemy mappings for Permission persistence."""

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
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from kernel.infrastructure.persistence.metadata import Base


class PolicyRecord(Base):
    __tablename__ = "policies"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft','active','deprecated')",
            name="policy_status_valid",
        ),
        CheckConstraint("version > 0", name="policy_version_positive"),
        Index(
            "uq_policies_tenant_name_version",
            "tenant_id",
            text("lower(name)"),
            "policy_version",
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
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    policy_version: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class PolicyRuleRecord(Base):
    __tablename__ = "policy_rules"
    __table_args__ = (
        CheckConstraint("effect IN ('allow','deny')", name="rule_effect_valid"),
        CheckConstraint(
            "scope_level IN ('resource','org_unit','enterprise','tenant')",
            name="rule_scope_valid",
        ),
        Index("ix_policy_rules_policy", "policy_id"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    policy_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.policies.id", ondelete="CASCADE"),
        nullable=False,
    )
    effect: Mapped[str] = mapped_column(String(16), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(128), nullable=False)
    actions: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    scope_level: Mapped[str] = mapped_column(String(32), nullable=False)
    enterprise_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    org_unit_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    conditions_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)


class GrantRecord(Base):
    __tablename__ = "grants"
    __table_args__ = (
        CheckConstraint("status IN ('active','revoked')", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        CheckConstraint("remaining_depth >= 0", name="remaining_depth_non_negative"),
        CheckConstraint(
            "scope_level IN ('resource','org_unit','enterprise','tenant')",
            name="grant_scope_valid",
        ),
        Index(
            "ix_grants_tenant_principal",
            "tenant_id",
            "principal_subject_id",
        ),
        Index("ix_grants_tenant_resource", "tenant_id", "resource_type", "resource_id"),
        Index(
            "uq_grants_equivalent_active",
            "tenant_id",
            "principal_subject_id",
            "resource_type",
            text("coalesce(resource_id, '00000000-0000-0000-0000-000000000000')"),
            "actions",
            "scope_level",
            text("coalesce(enterprise_id, '00000000-0000-0000-0000-000000000000')"),
            text("coalesce(org_unit_id, '00000000-0000-0000-0000-000000000000')"),
            text("coalesce(parent_grant_id, '00000000-0000-0000-0000-000000000000')"),
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
    principal_subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    resource_type: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    scope_level: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        server_default=text("'resource'"),
    )
    enterprise_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    org_unit_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    actions: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    conditions_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    parent_grant_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.grants.id", ondelete="RESTRICT"),
        nullable=True,
    )
    delegator_subject_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=True,
    )
    remaining_depth: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("0"),
    )
    delegable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class PermissionDecisionRecord(Base):
    __tablename__ = "permission_decisions"
    __table_args__ = (
        CheckConstraint("effect IN ('allow','deny')", name="effect_valid"),
        Index(
            "ix_permission_decisions_tenant_principal",
            "tenant_id",
            "principal_subject_id",
        ),
        Index("ix_permission_decisions_correlation", "correlation_id"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    principal_subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(128), nullable=False)
    resource_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), nullable=True)
    effect: Mapped[str] = mapped_column(String(16), nullable=False)
    reason_code: Mapped[str] = mapped_column(String(128), nullable=False)
    policy_version: Mapped[str] = mapped_column(String(64), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(128), nullable=False)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    evidence_json: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
