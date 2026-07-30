"""Minimal auditable side-effect log for Kernel foundation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional, Protocol, runtime_checkable
from uuid import UUID, uuid4

from kernel.shared.context import ExecutionContext


@dataclass(slots=True)
class AuditEvent:
    id: UUID
    action: str
    correlation_id: str
    subject_id: UUID
    tenant_id: Optional[UUID]
    resource: str
    result: str
    timestamp: datetime
    details: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class AuditLog(Protocol):
    def record(
        self,
        ctx: ExecutionContext,
        *,
        action: str,
        resource: str,
        result: str,
        details: dict[str, Any] | None = None,
    ) -> AuditEvent: ...

    def list_events(self) -> list[AuditEvent]: ...


class InMemoryAuditLog:
    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def record(
        self,
        ctx: ExecutionContext,
        *,
        action: str,
        resource: str,
        result: str,
        details: dict[str, Any] | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            id=uuid4(),
            action=action,
            correlation_id=ctx.correlation_id,
            subject_id=ctx.subject_id,
            tenant_id=ctx.tenant_id,
            resource=resource,
            result=result,
            timestamp=datetime.now(timezone.utc),
            details=details or {},
        )
        self._events.append(event)
        return event

    def list_events(self) -> list[AuditEvent]:
        return list(self._events)
