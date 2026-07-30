"""AI Runtime domain models (PHX-A12)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Optional
from uuid import UUID


class AgentRunStatus(StrEnum):
    PLANNED = "planned"
    RUNNING = "running"
    PENDING_APPROVAL = "pending_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class AgentRun:
    id: UUID
    tenant_id: UUID
    subject_id: UUID
    goal: str
    status: AgentRunStatus
    created_at: datetime
    updated_at: datetime
    plan_summary: str = ""
    approval_ref: Optional[str] = None
    last_error_code: Optional[str] = None
    version: int = 1


@dataclass(slots=True)
class ToolDeclaration:
    id: UUID
    tenant_id: UUID
    name: str
    description: str
    high_impact: bool
    created_at: datetime


@dataclass(slots=True)
class MemoryEntry:
    id: UUID
    tenant_id: UUID
    run_id: UUID
    key: str
    value: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    version: int = 1


@dataclass(frozen=True, slots=True)
class ToolInvocationResult:
    tool_name: str
    high_impact: bool
    output: dict[str, Any] = field(default_factory=dict)
