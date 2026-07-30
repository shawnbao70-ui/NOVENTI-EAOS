"""Knowledge request DTOs — runtime parity with docs/api/knowledge.openapi.yaml."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from api.gateway.schemas.ops import SampleKnowledgePackProductPosture


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


KnowledgeLayerLiteral = Literal[
    "canonical", "operational", "documentary", "derived"
]


class KnowledgeStatusData(_ClosedModel):
    """Knowledge status with G377 governance honesty; no graph-write invent."""

    writable: Literal[False] = False
    supported_surfaces: list[str] = Field(min_length=1)
    sample_knowledge_pack_product: SampleKnowledgePackProductPosture
    graph_write_engine: Literal[False] = False
    constitution_rewrite: Literal["never"] = "never"
    sample_pack_is_not_runtime_graph: Literal[True] = True
    sample_pack_not_complete_evidence: Literal[True] = True
    execution_authority: Literal["none"] = "none"


class KnowledgeStatusEnvelope(_ClosedModel):
    data: KnowledgeStatusData


class UpsertEntityRequest(_ClosedModel):
    entity_type: str = Field(min_length=1)
    name: str = Field(min_length=1)
    layer: KnowledgeLayerLiteral
    source_ref: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    entity_id: UUID | None = None
    attributes: dict[str, Any] = Field(default_factory=dict)
    labels: list[str] = Field(default_factory=list)
    retain_until: datetime | None = None
    expected_version: int | None = Field(default=None, ge=1)


class VersionedProvenanceRequest(_ClosedModel):
    source_ref: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    expected_version: int | None = Field(default=None, ge=1)


class ShareEntityRequest(_ClosedModel):
    share_with_subject_id: UUID
    source_ref: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    expected_version: int | None = Field(default=None, ge=1)


class CreateLinkRequest(_ClosedModel):
    from_entity_id: UUID
    to_entity_id: UUID
    relation_type: str = Field(min_length=1)
    source_ref: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    attributes: dict[str, Any] = Field(default_factory=dict)


class KnowledgeEntityResponse(_ClosedModel):
    id: UUID
    entity_type: str = Field(min_length=1)
    name: str
    layer: KnowledgeLayerLiteral
    status: str = Field(min_length=1)
    attributes: dict[str, Any] = Field(default_factory=dict)
    labels: list[str] = Field(default_factory=list)
    shared_with_subject_ids: list[str] = Field(default_factory=list)
    retain_until: str | None = None
    version: int = Field(ge=0)
    created_at: str | None = None
    updated_at: str | None = None


class KnowledgeEntityListEnvelope(_ClosedModel):
    ok: Literal[True] = True
    data: list[KnowledgeEntityResponse]


class ProvenanceRecordResponse(_ClosedModel):
    id: UUID
    subject_kind: str = Field(min_length=1)
    subject_id: UUID
    actor_subject_id: UUID
    source_ref: str
    reason: str
    derived: bool
    recorded_at: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class ProvenanceListEnvelope(_ClosedModel):
    ok: Literal[True] = True
    data: list[ProvenanceRecordResponse]
