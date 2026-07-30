"""Digital Twin domain models (PHX-E15)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Optional
from uuid import UUID


class TwinSnapshotStatus(StrEnum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


@dataclass(slots=True)
class TwinSnapshot:
    id: UUID
    tenant_id: UUID
    entity_ref: str
    state: dict[str, Any]
    source_ref: str
    reason: str
    confidence: float
    status: TwinSnapshotStatus
    created_at: datetime
    updated_at: datetime
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    version: int = 1
