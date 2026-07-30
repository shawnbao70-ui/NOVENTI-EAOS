"""Trusted-context helpers for SDK consumers."""

from __future__ import annotations

from uuid import UUID, uuid4

from kernel.shared.context import ExecutionContext, SubjectType


def build_tenant_context(
    *,
    tenant_id: UUID,
    subject_id: UUID,
    subject_type: SubjectType = SubjectType.HUMAN,
    correlation_id: str | None = None,
    session_id: UUID | None = None,
    roles: tuple[str, ...] | list[str] | None = None,
) -> ExecutionContext:
    """Build a tenant data-plane context.

    Callers must obtain tenant_id/subject_id (and roles) from a trusted auth boundary.
    This helper never elevates platform_scope.
    """

    normalized = tuple(sorted({r.strip() for r in (roles or ()) if r and str(r).strip()}))
    return ExecutionContext(
        subject_id=subject_id,
        subject_type=subject_type,
        tenant_id=tenant_id,
        platform_scope=False,
        session_id=session_id,
        correlation_id=correlation_id or str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        roles=normalized,
    )
