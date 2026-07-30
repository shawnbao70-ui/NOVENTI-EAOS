"""Package Platform HTTP DTO mapping (PHX-G27)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from eaos_platform.package.models import (
    ActionDeclaration,
    DeclaredPermission,
    PackageManifest,
    ResolvedAction,
    SurfaceDeclaration,
)


from api.gateway.serializers.common import uuid_result as uuid_result


def boolean_result(value: bool, *, audit_id: UUID | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"data": value}
    if audit_id is not None:
        payload["audit_id"] = str(audit_id)
    return payload


def serialize_surface(surface: SurfaceDeclaration) -> dict[str, Any]:
    return {
        "surface_key": surface.surface_key,
        "title": surface.title,
        "description": surface.description,
    }


def serialize_action(action: ActionDeclaration) -> dict[str, Any]:
    return {
        "action_key": action.action_key,
        "resource_type": action.resource_type,
        "permission_action": action.permission_action,
        "high_impact": action.high_impact,
        "surface_key": action.surface_key,
        "description": action.description,
    }


def serialize_declared_permission(item: DeclaredPermission) -> dict[str, Any]:
    return {
        "resource_type": item.resource_type,
        "actions": sorted(item.actions),
    }


def serialize_manifest(manifest: PackageManifest) -> dict[str, Any]:
    return {
        "id": str(manifest.id),
        "package_key": manifest.package_key,
        "version": manifest.version,
        "package_type": manifest.package_type.value,
        "status": manifest.status.value,
        "surfaces": [serialize_surface(item) for item in manifest.surfaces],
        "actions": [serialize_action(item) for item in manifest.actions],
        "required_permissions": [
            serialize_declared_permission(item) for item in manifest.required_permissions
        ],
        "declared_events": list(manifest.declared_events),
    }


def serialize_resolved_action(resolved: ResolvedAction) -> dict[str, Any]:
    return {
        "package_key": resolved.package_key,
        "manifest_version": resolved.manifest_version,
        "action_key": resolved.action_key,
        "resource_type": resolved.resource_type,
        "permission_action": resolved.permission_action,
        "high_impact": resolved.high_impact,
        "surface_key": resolved.surface_key,
        "installation_id": str(resolved.installation_id),
        "source": resolved.source,
    }
