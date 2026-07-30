"""SQLAlchemy mappings for durable Event Bus state."""

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


class EventRecord(Base):
    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("event_id", "tenant_id"),
        Index("ix_events_tenant_name_time", "tenant_id", "event_name", "timestamp"),
        Index("ix_events_correlation", "correlation_id"),
        {"schema": "kernel"},
    )

    event_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    event_name: Mapped[str] = mapped_column(String(255), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False)
    correlation_id: Mapped[str] = mapped_column(String(128), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    producer: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )


class EventSubscriptionRecord(Base):
    __tablename__ = "event_subscriptions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "subscriber_id", "event_name"),
        Index("ix_event_subscriptions_tenant_name", "tenant_id", "event_name"),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    subscriber_id: Mapped[str] = mapped_column(String(255), nullable=False)
    subscriber_subject_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    event_name: Mapped[str] = mapped_column(String(255), nullable=False)
    delivery_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    signing_secret: Mapped[str | None] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class EventDeliveryRecord(Base):
    __tablename__ = "event_deliveries"
    __table_args__ = (
        ForeignKeyConstraint(
            ["event_id", "tenant_id"],
            ["kernel.events.event_id", "kernel.events.tenant_id"],
            ondelete="CASCADE",
        ),
        CheckConstraint(
            "status IN ('delivered','failed','dead')",
            name="status_valid",
        ),
        CheckConstraint("attempt_count > 0", name="attempt_count_positive"),
        Index("ix_event_deliveries_tenant_status", "tenant_id", "status"),
        {"schema": "kernel"},
    )

    event_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    subscriber_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    attempt_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=text("1"),
    )
    last_attempt_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    last_error_code: Mapped[str | None] = mapped_column(String(128), nullable=True)


class EventOutboxRecord(Base):
    __tablename__ = "event_outbox"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','leased','dispatched','dead')",
            name="status_valid",
        ),
        CheckConstraint("attempt_count >= 0", name="attempt_count_non_negative"),
        Index("ix_event_outbox_claim", "tenant_id", "status", "available_at"),
        Index("ix_event_outbox_event_id", "event_id", unique=True),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("kernel.tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    event_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    event_name: Mapped[str] = mapped_column(String(255), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(32), nullable=False)
    producer: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
    )
    correlation_id: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    leased_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    leased_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(String(128), nullable=True)


class EventDeadLetterRecord(Base):
    __tablename__ = "event_dead_letters"
    __table_args__ = (
        ForeignKeyConstraint(
            ["event_id", "tenant_id"],
            ["kernel.events.event_id", "kernel.events.tenant_id"],
            ondelete="CASCADE",
        ),
        Index("ix_event_dead_letters_tenant", "tenant_id", "created_at"),
        Index(
            "uq_event_dead_letters_open",
            "tenant_id",
            "event_id",
            "subscriber_id",
            unique=True,
            postgresql_where=text("replayed_at IS NULL"),
            sqlite_where=text("replayed_at IS NULL"),
        ),
        {"schema": "kernel"},
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    tenant_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    event_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    subscriber_id: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    replayed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
