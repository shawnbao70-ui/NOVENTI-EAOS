"""Identity domain models (conceptual DM-KERNEL-001)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID


class SubjectKind(StrEnum):
    HUMAN = "human"
    AI_EMPLOYEE = "ai_employee"
    SERVICE = "service"
    DEVICE = "device"
    APPLICATION = "application"
    PLUGIN = "plugin"


class EntityStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    REVOKED = "revoked"
    ENDED = "ended"


class AssignmentMode(StrEnum):
    ASSIGN = "assign"
    REASSIGN = "reassign"
    INHERIT = "inherit"
    ARCHIVE = "archive"


# Non-AI types allowed for RegisterSubject
REGISTERABLE_SUBJECT_KINDS = frozenset(
    {
        SubjectKind.HUMAN,
        SubjectKind.SERVICE,
        SubjectKind.DEVICE,
        SubjectKind.APPLICATION,
        SubjectKind.PLUGIN,
    }
)


@dataclass(slots=True)
class ExternalRef:
    system: str
    external_id: str


@dataclass(slots=True)
class Subject:
    id: UUID
    subject_type: SubjectKind
    display_name: str
    status: EntityStatus
    created_at: datetime
    updated_at: datetime
    is_platform_managed: bool = False
    tenant_id: Optional[UUID] = None
    version: int = 1
    external_refs: list[ExternalRef] = field(default_factory=list)


@dataclass(slots=True)
class AIEmployeeProfile:
    ai_subject_id: UUID
    capabilities_profile_ref: str
    owner_policy_ref: str
    created_at: datetime
    updated_at: datetime
    version: int = 1


@dataclass(slots=True)
class Credential:
    id: UUID
    subject_id: UUID
    tenant_id: UUID
    credential_kind: str
    secret_handle: str
    status: EntityStatus
    created_at: datetime
    expires_at: Optional[datetime] = None


@dataclass(frozen=True, slots=True)
class CredentialValidationView:
    credential_id: UUID
    subject_id: UUID
    tenant_id: UUID
    credential_kind: str
    expires_at: Optional[datetime]


@dataclass(slots=True)
class Session:
    id: UUID
    subject_id: UUID
    tenant_id: UUID
    created_at: datetime
    expires_at: datetime
    credential_id: Optional[UUID] = None
    revoked_at: Optional[datetime] = None
    correlation_id_at_issue: str = ""


@dataclass(frozen=True, slots=True)
class SessionValidationView:
    session_id: UUID
    subject_id: UUID
    tenant_id: UUID
    expires_at: datetime


@dataclass(slots=True)
class PlatformIdentityGovernorGrant:
    id: UUID
    subject_id: UUID
    granted_by_subject_id: UUID
    granted_at: datetime
    status: EntityStatus = EntityStatus.ACTIVE
    revoked_by_subject_id: Optional[UUID] = None
    revoked_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None


@dataclass(slots=True)
class AIAssignment:
    id: UUID
    ai_subject_id: UUID
    tenant_id: UUID
    mode: AssignmentMode
    management_policy: str
    created_at: datetime
    effective_from: datetime
    predecessor_assignment_id: Optional[UUID] = None
    effective_to: Optional[datetime] = None
    status: EntityStatus = EntityStatus.ACTIVE
