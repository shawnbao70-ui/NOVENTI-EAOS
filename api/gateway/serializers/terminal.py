"""Smart Terminal HTTP DTO mapping (PHX-G30)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from uuid import UUID

from smart_terminal.models import (
    ApprovalPresentation,
    CommitReceipt,
    PlanPreview,
    TerminalExtension,
    TerminalIntent,
    TerminalSession,
)


from api.gateway.serializers.common import uuid_result as uuid_result


def boolean_result(value: bool, *, audit_id: UUID | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"data": value}
    if audit_id is not None:
        payload["audit_id"] = str(audit_id)
    return payload


def serialize_session(session: TerminalSession) -> dict[str, Any]:
    return {
        "id": str(session.id),
        "tenant_id": str(session.tenant_id),
        "subject_id": str(session.subject_id),
        "device_trust": session.device_trust.value,
        "status": session.status.value,
        "correlation_id": session.correlation_id,
        "identity_session_id": (
            str(session.identity_session_id) if session.identity_session_id else None
        ),
        "version": session.version,
    }


def serialize_intent(intent: TerminalIntent) -> dict[str, Any]:
    return {
        "id": str(intent.id),
        "tenant_id": str(intent.tenant_id),
        "subject_id": str(intent.subject_id),
        "terminal_session_id": str(intent.terminal_session_id),
        "text": intent.text,
        "status": intent.status.value,
        "version": intent.version,
    }


def serialize_preview(preview: PlanPreview) -> dict[str, Any]:
    return {
        "id": str(preview.id),
        "intent_id": str(preview.intent_id),
        "action": preview.action,
        "resource_ref": preview.resource_ref,
        "plan_version": preview.plan_version,
        "scope": preview.scope,
        "impact_summary": preview.impact_summary,
        "high_impact": preview.high_impact,
        "status": preview.status.value,
        "approval_ref": preview.approval_ref,
        "version": preview.version,
    }


def serialize_approval(presentation: ApprovalPresentation) -> dict[str, Any]:
    return {
        "preview_id": str(presentation.preview_id),
        "approval_ref": presentation.approval_ref,
        "workflow_status": presentation.workflow_status,
        "approval_action": presentation.approval_action,
        "approval_resource_ref": presentation.approval_resource_ref,
        "approval_plan_version": presentation.approval_plan_version,
        "approval_scope": presentation.approval_scope,
        "source": presentation.source,
    }


def serialize_commit(receipt: CommitReceipt) -> dict[str, Any]:
    return {
        "preview_id": str(receipt.preview_id),
        "action": receipt.action,
        "resource_ref": receipt.resource_ref,
        "plan_version": receipt.plan_version,
        "approved": receipt.approved,
        "verified_against": receipt.verified_against,
        "correlation_id": receipt.correlation_id,
    }


def serialize_extension(extension: TerminalExtension) -> dict[str, Any]:
    return {
        "id": str(extension.id),
        "extension_key": extension.extension_key,
        "version": extension.version,
        "signature_ref": extension.signature_ref,
        "status": extension.status.value,
        "declared_capabilities": sorted(extension.declared_capabilities),
        "declared_actions": sorted(extension.declared_actions),
        "allowed_surfaces": sorted(extension.allowed_surfaces),
        "data_scope": extension.data_scope,
    }


def serialize_extension_list(
    items: list[TerminalExtension],
) -> dict[str, Any]:
    return {"data": [serialize_extension(item) for item in items]}


def serialize_extension_invoke(
    data: Mapping[str, object],
    *,
    audit_id: UUID | None = None,
) -> dict[str, Any]:
    """Closed invoke envelope — declaration-only sandbox (executed=false)."""

    payload: dict[str, Any] = {
        "data": {
            "extension_id": str(data["extension_id"]),
            "action": str(data["action"]),
            "surface": str(data["surface"]),
            "status": str(data["status"]),
            "executed": bool(data["executed"]),
        }
    }
    if audit_id is not None:
        payload["audit_id"] = str(audit_id)
    return payload
