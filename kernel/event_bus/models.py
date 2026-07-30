"""Immutable event envelope models (ADR-0006)."""

from __future__ import annotations

import re
from math import isfinite
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID, uuid4

from kernel.shared.context import ExecutionContext
from kernel.shared.errors import ErrorCode, KernelError

EVENT_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$")
SCHEMA_VERSION_PATTERN = re.compile(r"^[1-9][0-9]*(?:\.[0-9]+){0,2}$")


def deep_freeze(value: Any) -> Any:
    """Recursively freeze event data so published facts cannot be mutated."""

    if isinstance(value, Mapping):
        if not all(isinstance(key, str) for key in value):
            raise KernelError(
                ErrorCode.EVENT_ENVELOPE_INVALID,
                "payload mapping keys must be strings",
            )
        return MappingProxyType({key: deep_freeze(item) for key, item in value.items()})
    if isinstance(value, list | tuple):
        return tuple(deep_freeze(item) for item in value)
    if value is None or isinstance(value, str | bool | int):
        return value
    if isinstance(value, float) and isfinite(value):
        return value
    raise KernelError(
        ErrorCode.EVENT_ENVELOPE_INVALID,
        "payload must contain JSON-safe values only",
    )


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    event_id: UUID
    event_name: str
    schema_version: str
    tenant_id: UUID
    correlation_id: str
    timestamp: datetime
    producer: str
    payload: Mapping[str, Any]

    @classmethod
    def create(
        cls,
        ctx: ExecutionContext,
        *,
        event_name: str,
        schema_version: str,
        producer: str,
        payload: Mapping[str, Any],
        event_id: UUID | None = None,
        timestamp: datetime | None = None,
    ) -> EventEnvelope:
        if ctx.tenant_id is None:
            raise KernelError(ErrorCode.CTX_MISSING_TENANT, "tenant_id is required")
        if not ctx.correlation_id.strip():
            raise KernelError(
                ErrorCode.CTX_MISSING_CORRELATION,
                "correlation_id is required",
            )
        normalized_name = event_name.strip()
        if not EVENT_NAME_PATTERN.fullmatch(normalized_name):
            raise KernelError(
                ErrorCode.EVENT_ENVELOPE_INVALID,
                "event_name must match domain.entity.action",
            )
        normalized_version = schema_version.strip()
        if not SCHEMA_VERSION_PATTERN.fullmatch(normalized_version):
            raise KernelError(
                ErrorCode.EVENT_ENVELOPE_INVALID,
                "schema_version must be numeric, for example 1 or 1.0",
            )
        normalized_producer = producer.strip()
        if not normalized_producer:
            raise KernelError(
                ErrorCode.EVENT_ENVELOPE_INVALID,
                "producer is required",
            )
        if not isinstance(payload, Mapping):
            raise KernelError(
                ErrorCode.EVENT_ENVELOPE_INVALID,
                "payload must be a mapping",
            )
        return cls(
            event_id=event_id or uuid4(),
            event_name=normalized_name,
            schema_version=normalized_version,
            tenant_id=ctx.tenant_id,
            correlation_id=ctx.correlation_id,
            timestamp=timestamp or datetime.now(timezone.utc),
            producer=normalized_producer,
            payload=deep_freeze(payload),
        )


@dataclass(frozen=True, slots=True)
class DeliveryReport:
    event_id: UUID
    delivered_count: int
    skipped_count: int
    failed_subscribers: tuple[str, ...] = ()
