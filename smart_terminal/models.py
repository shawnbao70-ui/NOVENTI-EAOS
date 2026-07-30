"""Smart Terminal domain models (PHX-T13)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID


class DeviceTrust(StrEnum):
    TRUSTED = "trusted"
    UNTRUSTED = "untrusted"


class TerminalSessionStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"


class IntentStatus(StrEnum):
    DRAFT = "draft"
    PREVIEWED = "previewed"
    CANCELLED = "cancelled"


class PreviewStatus(StrEnum):
    ACTIVE = "active"
    INVALIDATED = "invalidated"
    COMMITTED = "committed"


@dataclass(slots=True)
class TerminalSession:
    id: UUID
    tenant_id: UUID
    subject_id: UUID
    correlation_id: str
    device_trust: DeviceTrust
    status: TerminalSessionStatus
    created_at: datetime
    updated_at: datetime
    identity_session_id: Optional[UUID] = None
    version: int = 1


@dataclass(slots=True)
class TerminalIntent:
    id: UUID
    tenant_id: UUID
    subject_id: UUID
    terminal_session_id: UUID
    text: str
    status: IntentStatus
    created_at: datetime
    updated_at: datetime
    version: int = 1


@dataclass(slots=True)
class PlanPreview:
    id: UUID
    tenant_id: UUID
    subject_id: UUID
    intent_id: UUID
    terminal_session_id: UUID
    action: str
    resource_ref: str
    plan_version: str
    scope: str
    impact_summary: str
    high_impact: bool
    status: PreviewStatus
    created_at: datetime
    updated_at: datetime
    approval_ref: Optional[str] = None
    version: int = 1


@dataclass(frozen=True, slots=True)
class ApprovalPresentation:
    preview_id: UUID
    approval_ref: Optional[str]
    workflow_status: Optional[str]
    approval_action: Optional[str]
    approval_resource_ref: Optional[str]
    approval_plan_version: Optional[str]
    approval_scope: Optional[str]
    source: str = "workflow"


@dataclass(frozen=True, slots=True)
class CommitReceipt:
    preview_id: UUID
    action: str
    resource_ref: str
    plan_version: str
    approved: bool
    verified_against: str
    correlation_id: str


class ExtensionStatus(StrEnum):
    REGISTERED = "registered"
    ACTIVE = "active"
    REVOKED = "revoked"


FORBIDDEN_EXTENSION_CAPABILITIES = frozenset(
    {
        "hide_approval",
        "elevate_context",
        "bypass_audit",
        "mutate_shell_controls",
        "network.unrestricted",
    }
)


@dataclass(slots=True)
class TerminalExtension:
    id: UUID
    tenant_id: UUID
    extension_key: str
    version: str
    signature_ref: Optional[str]
    status: ExtensionStatus
    declared_capabilities: frozenset[str]
    declared_actions: frozenset[str]
    allowed_surfaces: frozenset[str]
    data_scope: str
    created_at: datetime
    updated_at: datetime
    version_num: int = 1
