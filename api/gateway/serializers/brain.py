"""Enterprise Brain HTTP DTO mapping (PHX-G28)."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from eaos_platform.brain.models import BrainInsight


from api.gateway.serializers.common import uuid_result as uuid_result


def serialize_insight(insight: BrainInsight) -> dict[str, Any]:
    return {
        "id": str(insight.id),
        "kind": insight.kind.value,
        "summary": insight.summary,
        "confidence": insight.confidence,
        "source_ref": insight.source_ref,
        "reason": insight.reason,
        "advisory": insight.advisory,
        "bias_notes": insight.bias_notes,
        "twin_ref": str(insight.twin_ref) if insight.twin_ref else None,
        "knowledge_refs": list(insight.knowledge_refs),
        "version": insight.version,
    }
