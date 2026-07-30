"""Digital Twin HTTP DTO mapping (PHX-G28)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from eaos_platform.twin.models import TwinSnapshot


from api.gateway.serializers.common import uuid_result as uuid_result


def serialize_snapshot(snapshot: TwinSnapshot) -> dict[str, Any]:
    return {
        "id": str(snapshot.id),
        "entity_ref": snapshot.entity_ref,
        "state": dict(snapshot.state),
        "source_ref": snapshot.source_ref,
        "reason": snapshot.reason,
        "confidence": snapshot.confidence,
        "status": snapshot.status.value,
        "version": snapshot.version,
    }
