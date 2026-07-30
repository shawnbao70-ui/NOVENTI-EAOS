"""Workflow request/response DTOs — runtime parity with docs/api/workflow.openapi.yaml."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


WorkflowStatusLiteral = Literal[
    "running",
    "pending_approval",
    "approved",
    "rejected",
    "cancelled",
    "completed",
    "compensating",
    "compensated",
]


class CreateDefinitionRequest(_ClosedModel):
    name: str = Field(min_length=1, max_length=255)
    definition_document_ref: str = Field(min_length=1, max_length=512)
    version: str = Field(min_length=1, max_length=64)


class StartInstanceRequest(_ClosedModel):
    definition_id: UUID
    payload: dict[str, Any]
    business_key: str | None = Field(default=None, max_length=255)
    approval_principal_id: UUID | None = None
    approval_action: str | None = Field(default=None, min_length=1, max_length=128)
    approval_resource_ref: str | None = Field(default=None, min_length=1, max_length=512)
    approval_plan_version: str | None = Field(default=None, max_length=64)
    approval_scope: str | None = Field(default=None, max_length=255)
    approval_expires_at: datetime | None = None
    approval_subject_id: UUID | None = None
    due_at: datetime | None = None


class SignalRequest(_ClosedModel):
    signal_name: str = Field(min_length=1, max_length=128)
    idempotency_key: str = Field(min_length=1, max_length=255)
    expected_version: int = Field(ge=1)
    payload: dict[str, Any] | None = None


class CancelInstanceRequest(_ClosedModel):
    reason: str = Field(min_length=1)
    expected_version: int = Field(ge=1)


class CompensateInstanceRequest(_ClosedModel):
    reason: str = Field(min_length=1)
    expected_version: int = Field(ge=1)


class TaskApprovalRequest(_ClosedModel):
    expected_instance_version: int = Field(ge=1)
    expected_task_version: int = Field(ge=1)
    comment: str | None = Field(default=None, max_length=1000)


class TaskRejectionRequest(_ClosedModel):
    reason: str = Field(min_length=1)
    expected_instance_version: int = Field(ge=1)
    expected_task_version: int = Field(ge=1)


class TaskEscalationRequest(_ClosedModel):
    to_subject_id: UUID
    reason: str = Field(min_length=1)
    expected_instance_version: int = Field(ge=1)
    expected_task_version: int = Field(ge=1)


class StartInstanceResult(_ClosedModel):
    instance_id: UUID
    status: WorkflowStatusLiteral
    task_id: UUID | None = None
    audit_id: UUID | str | None = None


class InstanceStatusResult(_ClosedModel):
    status: WorkflowStatusLiteral
    audit_id: UUID | str | None = None


class WorkflowInstanceResponse(_ClosedModel):
    id: UUID
    definition_id: UUID
    status: WorkflowStatusLiteral
    payload: dict[str, Any]
    version: int = Field(ge=0)
    created_at: str | None = None
    updated_at: str | None = None
    business_key: str | None = None
    current_task_id: UUID | None = None
    approval_principal_id: UUID | None = None
    approval_action: str | None = None
    approval_resource_ref: str | None = None
    approval_plan_version: str | None = None
    approval_scope: str | None = None
    approval_expires_at: str | None = None


TaskStatusLiteral = Literal["pending", "approved", "rejected", "cancelled"]


class WorkflowTaskResponse(_ClosedModel):
    id: UUID
    instance_id: UUID
    assignee_subject_id: UUID
    status: TaskStatusLiteral
    version: int = Field(ge=1)
    created_at: str | None = None
    updated_at: str | None = None
    decision_comment: str | None = None
    due_at: str | None = None
