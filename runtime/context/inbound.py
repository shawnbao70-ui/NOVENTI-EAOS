"""Trusted inbound adapter for the shared ExecutionContext."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from kernel.shared.context import ExecutionContext, SubjectType, require_context
from kernel.shared.errors import ErrorCode, KernelError


@dataclass(frozen=True, slots=True)
class InboundContextSpec:
    subject_id: UUID | str
    subject_type: SubjectType | str
    correlation_id: str
    request_time: datetime | str
    tenant_id: UUID | str | None = None
    platform_scope: bool = False
    session_id: UUID | str | None = None
    package_id: str | None = None
    locale: str | None = None
    trace_id: str | None = None
    approval_ref: str | None = None


class InboundContextBuilder:
    @staticmethod
    def build(
        spec: InboundContextSpec,
        *,
        tenant_data_plane: bool = True,
    ) -> ExecutionContext:
        if not spec.subject_id:
            raise KernelError(
                ErrorCode.CTX_MISSING_SUBJECT,
                "subject_id is required",
            )
        try:
            context = ExecutionContext(
                subject_id=InboundContextBuilder._uuid(spec.subject_id),
                subject_type=SubjectType(spec.subject_type),
                correlation_id=spec.correlation_id,
                request_time=InboundContextBuilder._datetime(spec.request_time),
                tenant_id=(
                    InboundContextBuilder._uuid(spec.tenant_id)
                    if spec.tenant_id is not None
                    else None
                ),
                platform_scope=spec.platform_scope,
                session_id=(
                    InboundContextBuilder._uuid(spec.session_id)
                    if spec.session_id is not None
                    else None
                ),
                package_id=InboundContextBuilder._optional_text(spec.package_id),
                locale=InboundContextBuilder._optional_text(spec.locale),
                trace_id=InboundContextBuilder._optional_text(spec.trace_id),
                approval_ref=InboundContextBuilder._optional_text(spec.approval_ref),
            )
        except (AttributeError, TypeError, ValueError) as exc:
            raise KernelError(ErrorCode.CTX_INVALID, "invalid inbound context") from exc
        require_context(context, tenant_data_plane=tenant_data_plane)
        return context

    @staticmethod
    def _uuid(value: UUID | str) -> UUID:
        return value if isinstance(value, UUID) else UUID(value)

    @staticmethod
    def _datetime(value: datetime | str) -> datetime:
        parsed = value if isinstance(value, datetime) else datetime.fromisoformat(value)
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("request_time must include a timezone")
        return parsed

    @staticmethod
    def _optional_text(value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        if not normalized:
            raise ValueError("optional context text cannot be blank")
        return normalized
