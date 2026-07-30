"""Knowledge domain models (PHX-K10 / Shared Platform Capability)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Optional
from uuid import UUID


class KnowledgeLayer(StrEnum):
    CANONICAL = "canonical"
    OPERATIONAL = "operational"
    DOCUMENTARY = "documentary"
    DERIVED = "derived"


class KnowledgeStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass(slots=True)
class KnowledgeEntity:
    id: UUID
    tenant_id: UUID
    entity_type: str
    name: str
    layer: KnowledgeLayer
    status: KnowledgeStatus
    created_at: datetime
    updated_at: datetime
    attributes: dict[str, Any] = field(default_factory=dict)
    labels: frozenset[str] = field(default_factory=frozenset)
    retain_until: Optional[datetime] = None
    shared_with_subject_ids: frozenset[UUID] = field(default_factory=frozenset)
    version: int = 1


@dataclass(slots=True)
class KnowledgeLink:
    id: UUID
    tenant_id: UUID
    from_entity_id: UUID
    to_entity_id: UUID
    relation_type: str
    status: KnowledgeStatus
    created_at: datetime
    updated_at: datetime
    attributes: dict[str, Any] = field(default_factory=dict)
    version: int = 1


@dataclass(slots=True)
class ProvenanceRecord:
    id: UUID
    tenant_id: UUID
    subject_kind: str
    subject_id: UUID
    actor_subject_id: UUID
    source_ref: str
    reason: str
    derived: bool
    recorded_at: datetime
    details: dict[str, Any] = field(default_factory=dict)
