"""Enterprise Brain domain models (PHX-E15)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Optional
from uuid import UUID


class InsightKind(StrEnum):
    INSIGHT = "insight"
    RECOMMENDATION = "recommendation"
    SIMULATION = "simulation"


@dataclass(slots=True)
class BrainInsight:
    id: UUID
    tenant_id: UUID
    kind: InsightKind
    summary: str
    confidence: float
    source_ref: str
    reason: str
    advisory: bool
    created_at: datetime
    updated_at: datetime
    bias_notes: str = ""
    twin_ref: Optional[UUID] = None
    knowledge_refs: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
    version: int = 1
