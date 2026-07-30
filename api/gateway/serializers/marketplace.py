"""Marketplace HTTP DTO mapping (PHX-G34 technical surface)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from eaos_platform.marketplace.models import MarketplaceListing


from api.gateway.serializers.common import uuid_result as uuid_result


def boolean_result(value: bool, *, audit_id: UUID | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"data": value}
    if audit_id is not None:
        payload["audit_id"] = str(audit_id)
    return payload


def serialize_listing(listing: MarketplaceListing) -> dict[str, Any]:
    return {
        "id": str(listing.id),
        "package_key": listing.package_key,
        "package_version": listing.package_version,
        "status": listing.status.value,
        "signature_ref": listing.signature_ref,
        "data_scope": listing.capability.data_scope,
        "required_permissions": sorted(listing.capability.required_permissions),
        "declared_events": sorted(listing.capability.declared_events),
        "version": listing.version,
    }
