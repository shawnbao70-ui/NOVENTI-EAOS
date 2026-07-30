"""Organization HTTP DTO mapping."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from kernel.organization.models import Enterprise, Membership, OrganizationUnit, Tenant


def id_response(resource_id: UUID, *, audit_id: UUID | None = None) -> dict[str, Any]:
    """Dual-key UuidResult dialect (id + data) — PHX-G170 / Foundation harden."""

    from api.gateway.serializers.common import uuid_result

    return uuid_result(resource_id, audit_id=audit_id)


def ok_response(*, audit_id: UUID | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"ok": True}
    if audit_id is not None:
        payload["audit_id"] = str(audit_id)
    return payload


def serialize_tenant(tenant: Tenant) -> dict[str, Any]:
    return {
        "id": str(tenant.id),
        "legal_name": tenant.legal_name,
        "status": tenant.status.value,
        "region_policy_ref": tenant.region_policy_ref,
        "version": tenant.version,
    }


def serialize_enterprise(enterprise: Enterprise) -> dict[str, Any]:
    return {
        "id": str(enterprise.id),
        "tenant_id": str(enterprise.tenant_id),
        "legal_name": enterprise.legal_name,
        "status": enterprise.status.value,
        "is_primary": enterprise.is_primary,
        "version": enterprise.version,
    }


def serialize_unit(unit: OrganizationUnit) -> dict[str, Any]:
    return {
        "id": str(unit.id),
        "tenant_id": str(unit.tenant_id),
        "enterprise_id": str(unit.enterprise_id),
        "parent_unit_id": (
            str(unit.parent_unit_id) if unit.parent_unit_id is not None else None
        ),
        "unit_type": unit.unit_type.value,
        "name": unit.name,
        "status": unit.status.value,
        "version": unit.version,
    }


def serialize_membership(membership: Membership) -> dict[str, Any]:
    return {
        "id": str(membership.id),
        "tenant_id": str(membership.tenant_id),
        "enterprise_id": str(membership.enterprise_id),
        "subject_id": str(membership.subject_id),
        "org_unit_id": (
            str(membership.org_unit_id) if membership.org_unit_id is not None else None
        ),
        "membership_role_label": membership.membership_role_label,
        "status": membership.status.value,
        "ended_at": (
            membership.ended_at.isoformat().replace("+00:00", "Z")
            if membership.ended_at is not None
            else None
        ),
        "version": membership.version,
    }
