"""SQLAlchemy mappings for Package Platform persistence."""

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
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from kernel.infrastructure.persistence.metadata import Base

MANIFEST_STATUSES = "'draft','published','deprecated'"
INSTALL_STATUSES = "'installed','disabled'"
PACKAGE_TYPES = "'industry','business','ai','integration'"


class PackageManifestRecord(Base):
    __tablename__ = "package_manifests"
    __table_args__ = (
        CheckConstraint(f"status IN ({MANIFEST_STATUSES})", name="status_valid"),
        CheckConstraint(f"package_type IN ({PACKAGE_TYPES})", name="package_type_valid"),
        CheckConstraint("version_number > 0", name="version_positive"),
        Index(
            "uq_package_manifests_tenant_key_version",
            "tenant_id",
            text("lower(package_key)"),
            "version",
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
    package_key: Mapped[str] = mapped_column(String(256), nullable=False)
    version: Mapped[str] = mapped_column(String(64), nullable=False)
    package_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    surfaces_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    actions_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    required_permissions_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    declared_events_json: Mapped[list[str]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")


class PackageInstallationRecord(Base):
    __tablename__ = "package_installations"
    __table_args__ = (
        CheckConstraint(f"status IN ({INSTALL_STATUSES})", name="status_valid"),
        CheckConstraint("version_number > 0", name="version_positive"),
        Index("ix_package_installations_tenant_key", "tenant_id", "package_key"),
        Index("ix_package_installations_tenant_status", "tenant_id", "status"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    manifest_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.package_manifests.id", ondelete="RESTRICT"),
        nullable=False,
    )
    package_key: Mapped[str] = mapped_column(String(256), nullable=False)
    manifest_version: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
