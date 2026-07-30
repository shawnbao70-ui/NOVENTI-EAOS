"""Versioned JSON snapshot for asynchronous context handoff."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from kernel.shared.context import ExecutionContext, SubjectType, require_context
from kernel.shared.errors import ErrorCode, KernelError

_FIELDS = {
    "approval_ref",
    "correlation_id",
    "locale",
    "package_id",
    "platform_scope",
    "request_time",
    "session_id",
    "subject_id",
    "subject_type",
    "tenant_id",
    "trace_id",
    "version",
}


@dataclass(frozen=True, slots=True)
class ContextSnapshot:
    serialized_json: str

    @classmethod
    def capture(cls, context: ExecutionContext) -> ContextSnapshot:
        payload = {
            "version": 1,
            "subject_id": str(context.subject_id),
            "subject_type": context.subject_type.value,
            "correlation_id": context.correlation_id,
            "request_time": context.request_time.isoformat(),
            "tenant_id": str(context.tenant_id) if context.tenant_id else None,
            "platform_scope": context.platform_scope,
            "session_id": str(context.session_id) if context.session_id else None,
            "package_id": context.package_id,
            "locale": context.locale,
            "trace_id": context.trace_id,
            "approval_ref": context.approval_ref,
        }
        return cls(json.dumps(payload, sort_keys=True, separators=(",", ":")))

    def to_dict(self) -> dict[str, Any]:
        return json.loads(self.serialized_json)

    def restore(self) -> ExecutionContext:
        try:
            payload = self.to_dict()
            if set(payload) != _FIELDS or payload["version"] != 1:
                raise ValueError("unsupported snapshot shape or version")
            request_time = datetime.fromisoformat(payload["request_time"])
            if request_time.tzinfo is None or request_time.utcoffset() is None:
                raise ValueError("snapshot request_time must include timezone")
            context = ExecutionContext(
                subject_id=UUID(payload["subject_id"]),
                subject_type=SubjectType(payload["subject_type"]),
                correlation_id=payload["correlation_id"],
                request_time=request_time,
                tenant_id=UUID(payload["tenant_id"]) if payload["tenant_id"] else None,
                platform_scope=payload["platform_scope"],
                session_id=UUID(payload["session_id"]) if payload["session_id"] else None,
                package_id=payload["package_id"],
                locale=payload["locale"],
                trace_id=payload["trace_id"],
                approval_ref=payload["approval_ref"],
            )
            require_context(
                context,
                tenant_data_plane=not context.platform_scope,
            )
            return context
        except (KeyError, TypeError, ValueError, json.JSONDecodeError, KernelError) as exc:
            raise KernelError(
                ErrorCode.RT_SNAPSHOT_INVALID,
                "invalid execution context snapshot",
            ) from exc
