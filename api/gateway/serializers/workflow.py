"""Workflow HTTP DTO mapping."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from kernel.workflow.models import WorkflowInstance, WorkflowStatus, WorkflowTask


from api.gateway.serializers.common import uuid_result as uuid_result


def ok_response(*, audit_id: UUID | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"ok": True}
    if audit_id is not None:
        payload["audit_id"] = str(audit_id)
    return payload


def serialize_start(
    data: dict[str, Any],
    *,
    audit_id: UUID | None = None,
) -> dict[str, Any]:
    status = data.get("status")
    status_value = status.value if isinstance(status, WorkflowStatus) else str(status)
    payload: dict[str, Any] = {
        "instance_id": str(data["instance_id"]),
        "status": status_value,
        "task_id": str(data["task_id"]) if data.get("task_id") is not None else None,
    }
    if audit_id is not None:
        payload["audit_id"] = str(audit_id)
    return payload


def serialize_status(
    status: WorkflowStatus,
    *,
    audit_id: UUID | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"status": status.value}
    if audit_id is not None:
        payload["audit_id"] = str(audit_id)
    return payload


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    return value.isoformat().replace("+00:00", "Z")


def serialize_instance(instance: WorkflowInstance) -> dict[str, Any]:
    return {
        "id": str(instance.id),
        "definition_id": str(instance.definition_id),
        "business_key": instance.business_key,
        "status": instance.status.value,
        "payload": dict(instance.payload),
        "current_task_id": (
            str(instance.current_task_id)
            if instance.current_task_id is not None
            else None
        ),
        "approval_principal_id": (
            str(instance.approval_principal_subject_id)
            if instance.approval_principal_subject_id is not None
            else None
        ),
        "approval_action": instance.approval_action,
        "approval_resource_ref": instance.approval_resource_ref,
        "approval_plan_version": instance.approval_plan_version,
        "approval_scope": instance.approval_scope,
        "approval_expires_at": _iso(instance.approval_expires_at),
        "version": instance.version,
        "created_at": _iso(instance.created_at),
        "updated_at": _iso(instance.updated_at),
    }


def serialize_task(task: WorkflowTask) -> dict[str, Any]:
    return {
        "id": str(task.id),
        "instance_id": str(task.instance_id),
        "assignee_subject_id": str(task.assignee_subject_id),
        "status": task.status.value,
        "decision_comment": task.decision_comment,
        "due_at": _iso(task.due_at),
        "version": task.version,
        "created_at": _iso(task.created_at),
        "updated_at": _iso(task.updated_at),
    }
