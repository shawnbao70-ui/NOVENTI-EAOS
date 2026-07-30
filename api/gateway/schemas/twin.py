"""Twin request/response DTOs — runtime parity with docs/api/brain.openapi.yaml Twin schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UpsertTwinSnapshotRequest(_ClosedModel):
    entity_ref: str = Field(min_length=1)
    state: dict[str, Any]
    source_ref: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    confidence: float = Field(ge=0, le=1)
    valid_from: datetime | None = None
    valid_until: datetime | None = None


class TwinSnapshotResponse(_ClosedModel):
    id: UUID
    entity_ref: str = Field(min_length=1)
    state: dict[str, Any]
    source_ref: str
    reason: str
    confidence: float = Field(ge=0, le=1)
    status: Literal["active", "superseded", "archived"]
    version: int = Field(ge=0)
