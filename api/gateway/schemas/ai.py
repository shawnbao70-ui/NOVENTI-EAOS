"""AI Runtime request/response DTOs — runtime parity with docs/api/ai.openapi.yaml."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreateAgentRunRequest(_ClosedModel):
    goal: str = Field(min_length=1)
    plan_summary: str = ""


class RegisterToolRequest(_ClosedModel):
    name: str = Field(min_length=1)
    description: str = ""
    high_impact: bool = False


class InvokeToolRequest(_ClosedModel):
    tool_name: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    plan_version: str | None = None
    scope: str | None = None


class WriteMemoryRequest(_ClosedModel):
    key: str = Field(min_length=1)
    value: dict[str, Any]


class RequestAIApprovalRequest(_ClosedModel):
    definition_id: UUID
    approval_subject_id: UUID
    action: str = Field(min_length=1)
    resource_ref: str = Field(min_length=1)
    plan_version: str | None = None
    scope: str | None = None


class CommitActionRequest(_ClosedModel):
    action: str = Field(min_length=1)
    resource_ref: str = Field(min_length=1)
    plan_version: str | None = None
    scope: str | None = None


class AgentRunResponse(_ClosedModel):
    id: UUID
    goal: str
    plan_summary: str
    status: str = Field(min_length=1)
    approval_ref: str | None = None
    version: int = Field(ge=0)
    created_at: str | None = None
    updated_at: str | None = None


class MemoryEntryResponse(_ClosedModel):
    id: UUID
    key: str = Field(min_length=1)
    value: dict[str, Any]
    version: int = Field(ge=0)


class ToolInvocationPayload(_ClosedModel):
    tool_name: str = Field(min_length=1)
    high_impact: bool
    output: dict[str, Any] = Field(default_factory=dict)


class ToolInvocationResult(_ClosedModel):
    ok: Literal[True] = True
    data: ToolInvocationPayload
    audit_id: UUID | str | None = None
