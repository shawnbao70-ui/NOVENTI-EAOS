"""Brain request DTOs — runtime parity with docs/api/brain.openapi.yaml."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PublishInsightRequest(_ClosedModel):
    kind: Literal["insight", "recommendation", "simulation"]
    summary: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    source_ref: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    bias_notes: str = ""
    twin_ref: UUID | None = None
    knowledge_refs: list[str] | None = None
    details: dict[str, Any] | None = None
    advisory: bool = True


class BrainInsightResponse(_ClosedModel):
    id: UUID
    kind: Literal["insight", "recommendation", "simulation"]
    summary: str
    confidence: float = Field(ge=0, le=1)
    source_ref: str
    reason: str
    advisory: Literal[True] = True
    bias_notes: str = ""
    twin_ref: UUID | None = None
    knowledge_refs: list[str] = Field(default_factory=list)
    version: int = Field(ge=0)
