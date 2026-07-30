"""Execution context contract (IF-CTX-001)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Optional
from uuid import UUID

from kernel.shared.errors import ErrorCode, KernelError


class SubjectType(StrEnum):
    HUMAN = "human"
    AI = "ai"
    AI_EMPLOYEE = "ai_employee"
    SERVICE = "service"
    DEVICE = "device"
    APPLICATION = "application"
    PLUGIN = "plugin"


@dataclass(frozen=True, slots=True)
class ExecutionContext:
    """Mandatory call context for Kernel operations."""

    subject_id: UUID
    subject_type: SubjectType
    correlation_id: str
    request_time: datetime
    tenant_id: Optional[UUID] = None
    platform_scope: bool = False
    session_id: Optional[UUID] = None
    package_id: Optional[str] = None
    locale: Optional[str] = None
    trace_id: Optional[str] = None
    approval_ref: Optional[str] = None
    # JWT eaos_roles (PHX-G82); never elevated from request body.
    roles: tuple[str, ...] = ()

    @staticmethod
    def utc_now() -> datetime:
        return datetime.now(timezone.utc)


def require_context(
    ctx: ExecutionContext,
    *,
    tenant_data_plane: bool = True,
) -> None:
    """Validate context; fail closed before any side effect."""

    if not ctx.subject_id:
        raise KernelError(ErrorCode.CTX_MISSING_SUBJECT, "subject_id is required")
    if not ctx.correlation_id or not str(ctx.correlation_id).strip():
        raise KernelError(ErrorCode.CTX_MISSING_CORRELATION, "correlation_id is required")
    if ctx.request_time is None:
        raise KernelError(ErrorCode.CTX_INVALID, "request_time is required")

    if tenant_data_plane:
        if ctx.platform_scope:
            raise KernelError(
                ErrorCode.CTX_INVALID,
                "platform_scope cannot be used on tenant data-plane operations",
            )
        if ctx.tenant_id is None:
            raise KernelError(ErrorCode.CTX_MISSING_TENANT, "tenant_id is required")
    else:
        if not ctx.platform_scope and ctx.tenant_id is None:
            raise KernelError(
                ErrorCode.CTX_MISSING_TENANT,
                "platform_scope=true or tenant_id is required",
            )
