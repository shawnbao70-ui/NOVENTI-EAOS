"""AI Runtime HTTP DTO mapping (PHX-G29)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from runtime.ai.models import AgentRun, MemoryEntry, ToolInvocationResult


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    return value.isoformat().replace("+00:00", "Z")


def uuid_result(resource_id: UUID, *, audit_id: UUID | None = None) -> dict[str, Any]:
    from api.gateway.serializers.common import uuid_result as _uuid_result

    return _uuid_result(resource_id, audit_id=audit_id, ok=True)


def ok_response(*, audit_id: UUID | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"ok": True, "data": True}
    if audit_id is not None:
        payload["audit_id"] = str(audit_id)
    return payload


def serialize_run(run: AgentRun) -> dict[str, Any]:
    return {
        "id": str(run.id),
        "goal": run.goal,
        "plan_summary": run.plan_summary,
        "status": run.status.value,
        "approval_ref": run.approval_ref,
        "version": run.version,
        "created_at": _iso(run.created_at),
        "updated_at": _iso(run.updated_at),
    }


def serialize_memory(entry: MemoryEntry) -> dict[str, Any]:
    return {
        "id": str(entry.id),
        "key": entry.key,
        "value": dict(entry.value),
        "version": entry.version,
    }


def serialize_tool_invocation(
    result: ToolInvocationResult,
    *,
    audit_id: UUID | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": True,
        "data": {
            "tool_name": result.tool_name,
            "high_impact": result.high_impact,
            "output": dict(result.output),
        },
    }
    if audit_id is not None:
        payload["audit_id"] = str(audit_id)
    return payload
