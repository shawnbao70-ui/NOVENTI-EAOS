"""SQLAlchemy mapping for OIDC refresh bindings (PHX-G63)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from kernel.infrastructure.persistence.metadata import Base


class OidcRefreshBindingRecord(Base):
    __tablename__ = "oidc_refresh_bindings"
    __table_args__ = (
        CheckConstraint(
            "refresh_token IS NOT NULL OR id_token IS NOT NULL",
            name="token_present",
        ),
        Index("ix_oidc_refresh_bindings_updated_at", "updated_at", unique=False),
        {"schema": "kernel"},
    )

    eaos_jti: Mapped[str] = mapped_column(String(128), primary_key=True)
    refresh_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    id_token: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
