"""Knowledge HTTP DTO mapping."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from eaos_platform.knowledge.models import KnowledgeEntity, ProvenanceRecord


from api.gateway.serializers.common import uuid_result as uuid_result


def ok_response(*, audit_id: UUID | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"ok": True}
    if audit_id is not None:
        payload["audit_id"] = str(audit_id)
    return payload


def list_envelope(items: list[dict[str, Any]]) -> dict[str, Any]:
    return {"ok": True, "data": items}


def _iso(value: Any) -> str | None:
    if value is None:
        return None
    return value.isoformat().replace("+00:00", "Z")


def serialize_entity(entity: KnowledgeEntity) -> dict[str, Any]:
    return {
        "id": str(entity.id),
        "entity_type": entity.entity_type,
        "name": entity.name,
        "layer": entity.layer.value,
        "status": entity.status.value,
        "attributes": dict(entity.attributes),
        "labels": sorted(entity.labels),
        "shared_with_subject_ids": sorted(str(item) for item in entity.shared_with_subject_ids),
        "retain_until": _iso(entity.retain_until),
        "version": entity.version,
        "created_at": _iso(entity.created_at),
        "updated_at": _iso(entity.updated_at),
    }


def serialize_provenance(record: ProvenanceRecord) -> dict[str, Any]:
    return {
        "id": str(record.id),
        "subject_kind": record.subject_kind,
        "subject_id": str(record.subject_id),
        "actor_subject_id": str(record.actor_subject_id),
        "source_ref": record.source_ref,
        "reason": record.reason,
        "derived": record.derived,
        "recorded_at": _iso(record.recorded_at),
        "details": dict(record.details),
    }
