"""Outbox, dead-letter, and delivery observability models (PHX-P11)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping
from uuid import UUID


class OutboxStatus(StrEnum):
    PENDING = "pending"
    LEASED = "leased"
    DISPATCHED = "dispatched"
    DEAD = "dead"


@dataclass(slots=True)
class OutboxEntry:
    id: UUID
    tenant_id: UUID
    event_id: UUID
    event_name: str
    schema_version: str
    producer: str
    payload: Mapping[str, Any]
    correlation_id: str
    status: OutboxStatus
    attempt_count: int
    available_at: datetime
    created_at: datetime
    leased_until: datetime | None = None
    leased_by: str | None = None
    last_error_code: str | None = None


@dataclass(slots=True)
class DeadLetterEntry:
    id: UUID
    tenant_id: UUID
    event_id: UUID
    subscriber_id: str
    reason: str
    attempt_count: int
    created_at: datetime
    replayed_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class DeliveryStats:
    pending_outbox: int
    leased_outbox: int
    failed_deliveries: int
    dead_letter_depth: int


@dataclass(frozen=True, slots=True)
class DispatchReport:
    outbox_dispatched: int
    outbox_failed: int
    deliveries_retried: int
    deliveries_dead_lettered: int
