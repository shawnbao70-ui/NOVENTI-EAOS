"""Trusted domain → outbox emission (PHX-E19 / ADR-0034)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping, Protocol
from uuid import UUID, uuid4

from kernel.event_bus.models import EVENT_NAME_PATTERN, SCHEMA_VERSION_PATTERN, deep_freeze
from kernel.event_bus.outbox import OutboxEntry, OutboxStatus
from kernel.shared.context import ExecutionContext
from kernel.shared.errors import ErrorCode, KernelError


class OutboxWriter(Protocol):
    def add_outbox(self, entry: OutboxEntry) -> None: ...


class DomainEventEmitter:
    """Write catalog facts to outbox without requiring event_stream:publish."""

    def __init__(self, writer: OutboxWriter) -> None:
        self._writer = writer

    def enqueue_fact(
        self,
        ctx: ExecutionContext,
        *,
        event_name: str,
        producer: str,
        payload: Mapping[str, Any],
        tenant_id: UUID | None = None,
        schema_version: str = "1",
    ) -> UUID:
        resolved_tenant = tenant_id if tenant_id is not None else ctx.tenant_id
        if resolved_tenant is None:
            raise KernelError(
                ErrorCode.CTX_MISSING_TENANT,
                "tenant_id is required for domain event emission",
            )
        if not ctx.correlation_id or not str(ctx.correlation_id).strip():
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
                "schema_version is invalid",
            )
        normalized_producer = producer.strip()
        if not normalized_producer:
            raise KernelError(
                ErrorCode.EVENT_ENVELOPE_INVALID,
                "producer is required",
            )
        frozen_payload = deep_freeze(dict(payload))
        now = datetime.now(timezone.utc)
        event_id = uuid4()
        entry = OutboxEntry(
            id=uuid4(),
            tenant_id=resolved_tenant,
            event_id=event_id,
            event_name=normalized_name,
            schema_version=normalized_version,
            producer=normalized_producer,
            payload=dict(frozen_payload),
            correlation_id=ctx.correlation_id.strip(),
            status=OutboxStatus.PENDING,
            attempt_count=0,
            available_at=now,
            created_at=now,
        )
        self._writer.add_outbox(entry)
        return event_id
