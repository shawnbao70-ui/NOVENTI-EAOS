"""Workflow domain models for PHX-K09."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Optional
from uuid import UUID


class WorkflowDefinitionStatus(StrEnum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class WorkflowStatus(StrEnum):
    RUNNING = "running"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


class TaskStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class WorkflowDefinition:
    id: UUID
    tenant_id: Optional[UUID]
    name: str
    document_ref: str
    version: str
    status: WorkflowDefinitionStatus
    created_at: datetime


@dataclass(slots=True)
class WorkflowInstance:
    id: UUID
    definition_id: UUID
    tenant_id: UUID
    initiator_subject_id: UUID
    status: WorkflowStatus
    payload: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    business_key: Optional[str] = None
    current_task_id: Optional[UUID] = None
    approval_principal_subject_id: Optional[UUID] = None
    approval_action: Optional[str] = None
    approval_resource_ref: Optional[str] = None
    approval_plan_version: Optional[str] = None
    approval_scope: Optional[str] = None
    approval_expires_at: Optional[datetime] = None
    version: int = 1


@dataclass(slots=True)
class WorkflowTask:
    id: UUID
    instance_id: UUID
    tenant_id: UUID
    assignee_subject_id: UUID
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    decision_comment: Optional[str] = None
    escalated_from_subject_id: Optional[UUID] = None
    due_at: Optional[datetime] = None
    version: int = 1


@dataclass(slots=True)
class WorkflowHistoryEntry:
    id: UUID
    instance_id: UUID
    tenant_id: UUID
    action: str
    subject_id: UUID
    correlation_id: str
    timestamp: datetime
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class SignalReceipt:
    instance_id: UUID
    tenant_id: UUID
    idempotency_key: str
    request_fingerprint: str
    resulting_status: WorkflowStatus
    processed_at: datetime
