"""Identity HTTP DTO mapping."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from kernel.identity.models import (
    AIEmployeeProfile,
    CredentialValidationView,
    SessionValidationView,
    Subject,
)


def uuid_created(resource_id: UUID, *, audit_id: UUID | None = None) -> dict[str, Any]:
    """Dual-key UuidResult (id + data) — OpenAPI Identity UuidResult parity."""

    from api.gateway.serializers.common import uuid_result

    return uuid_result(resource_id, audit_id=audit_id)


def serialize_subject(subject: Subject) -> dict[str, Any]:
    return {
        "id": str(subject.id),
        "subject_type": subject.subject_type.value,
        "display_name": subject.display_name,
        "status": subject.status.value,
        "version": subject.version,
    }


def serialize_credential_validation(view: CredentialValidationView) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "credential_id": str(view.credential_id),
        "valid": True,
        "status": "active",
    }
    if view.expires_at is not None:
        payload["expires_at"] = view.expires_at.isoformat().replace("+00:00", "Z")
    else:
        payload["expires_at"] = None
    return payload


def serialize_session_created(
    data: dict[str, Any],
    *,
    audit_id: UUID | None = None,
) -> dict[str, Any]:
    payload = {
        "session_id": str(data["session_id"]),
        "expires_at": data["expires_at"].isoformat().replace("+00:00", "Z"),
    }
    if audit_id is not None:
        payload["audit_id"] = str(audit_id)
    return payload


def serialize_session_validation(view: SessionValidationView) -> dict[str, Any]:
    return {
        "session_id": str(view.session_id),
        "valid": True,
        "status": "active",
        "expires_at": view.expires_at.isoformat().replace("+00:00", "Z"),
    }


def serialize_ai_profile(profile: AIEmployeeProfile) -> dict[str, Any]:
    return {
        "ai_subject_id": str(profile.ai_subject_id),
        "capabilities_profile_ref": profile.capabilities_profile_ref,
        "owner_policy_ref": profile.owner_policy_ref,
        "version": profile.version,
    }
