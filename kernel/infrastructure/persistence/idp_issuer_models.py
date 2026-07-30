"""SQLAlchemy mapping for platform IdP issuer bindings (PHX-G57)."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    Index,
    Integer,
    String,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from kernel.infrastructure.persistence.metadata import Base

STATUSES = "'active','disabled'"


class IdpIssuerBindingRecord(Base):
    __tablename__ = "idp_issuer_bindings"
    __table_args__ = (
        CheckConstraint(f"status IN ({STATUSES})", name="status_valid"),
        CheckConstraint("version > 0", name="version_positive"),
        CheckConstraint(
            "jwks_url IS NOT NULL OR jwks_json IS NOT NULL",
            name="jwks_present",
        ),
        Index(
            "ix_idp_issuer_bindings_issuer_lower",
            text("lower(issuer)"),
            unique=True,
        ),
        Index("ix_idp_issuer_bindings_status", "status", unique=False),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    issuer: Mapped[str] = mapped_column(String(512), nullable=False)
    jwks_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    jwks_json: Mapped[dict[str, Any] | list[Any] | None] = mapped_column(
        JSON().with_variant(JSONB(astext_type=String()), "postgresql"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
