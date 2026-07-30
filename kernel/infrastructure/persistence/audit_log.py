"""Tenant-bound SQLAlchemy adapter for the AuditLog port."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from kernel.infrastructure.persistence.audit_models import AuditEventRecord
from kernel.shared.audit import AuditEvent
from kernel.shared.context import ExecutionContext
from kernel.shared.errors import ErrorCode, KernelError


class SQLAlchemyAuditLog:
    """Append-only audit sink scoped to one tenant or platform context."""

    def __init__(
        self,
        session: Session,
        *,
        tenant_id: UUID | None,
        platform_scope: bool = False,
    ) -> None:
        if platform_scope == (tenant_id is not None):
            raise ValueError("provide either tenant_id or platform_scope")
        self._session = session
        self._tenant_id = tenant_id
        self._platform_scope = platform_scope

    def record(
        self,
        ctx: ExecutionContext,
        *,
        action: str,
        resource: str,
        result: str,
        details: dict[str, Any] | None = None,
    ) -> AuditEvent:
        self._require_context_scope(ctx)
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
        self._session.add(
            AuditEventRecord(
                id=event.id,
                tenant_id=event.tenant_id,
                subject_id=event.subject_id,
                action=event.action,
                correlation_id=event.correlation_id,
                resource=event.resource,
                result=event.result,
                timestamp=event.timestamp,
                details=event.details,
            )
        )
        return event

    def list_events(self) -> list[AuditEvent]:
        statement = select(AuditEventRecord).order_by(AuditEventRecord.timestamp)
        if not self._platform_scope:
            statement = statement.where(AuditEventRecord.tenant_id == self._tenant_id)
        return [
            AuditEvent(
                id=record.id,
                action=record.action,
                correlation_id=record.correlation_id,
                subject_id=record.subject_id,
                tenant_id=record.tenant_id,
                resource=record.resource,
                result=record.result,
                timestamp=(
                    record.timestamp.replace(tzinfo=timezone.utc)
                    if record.timestamp.tzinfo is None
                    else record.timestamp.astimezone(timezone.utc)
                ),
                details=dict(record.details),
            )
            for record in self._session.scalars(statement).all()
        ]

    def _require_context_scope(self, ctx: ExecutionContext) -> None:
        if self._platform_scope:
            valid = ctx.platform_scope and ctx.tenant_id is None
        else:
            valid = not ctx.platform_scope and ctx.tenant_id == self._tenant_id
        if not valid:
            raise KernelError(
                ErrorCode.CTX_INVALID,
                "audit context is outside repository scope",
            )
