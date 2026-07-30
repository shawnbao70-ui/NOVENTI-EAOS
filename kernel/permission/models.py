"""Permission domain models (DM-KERNEL-001 / PHX-K08)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID


class GrantStatus(StrEnum):
    ACTIVE = "active"
    REVOKED = "revoked"


class PermissionEffect(StrEnum):
    ALLOW = "allow"
    DENY = "deny"


class PolicyStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"


class ScopeLevel(StrEnum):
    RESOURCE = "resource"
    ORG_UNIT = "org_unit"
    ENTERPRISE = "enterprise"
    TENANT = "tenant"


SCOPE_RANK = {
    ScopeLevel.RESOURCE: 0,
    ScopeLevel.ORG_UNIT: 1,
    ScopeLevel.ENTERPRISE: 2,
    ScopeLevel.TENANT: 3,
}


@dataclass(frozen=True, slots=True)
class Resource:
    tenant_id: UUID
    resource_type: str
    resource_id: Optional[UUID] = None
    enterprise_id: Optional[UUID] = None
    org_unit_id: Optional[UUID] = None


@dataclass(slots=True)
class Grant:
    id: UUID
    tenant_id: UUID
    principal_subject_id: UUID
    resource_type: str
    actions: frozenset[str]
    status: GrantStatus
    created_at: datetime
    updated_at: datetime
    scope_level: ScopeLevel = ScopeLevel.RESOURCE
    resource_id: Optional[UUID] = None
    enterprise_id: Optional[UUID] = None
    org_unit_id: Optional[UUID] = None
    expires_at: Optional[datetime] = None
    conditions_ref: Optional[str] = None
    parent_grant_id: Optional[UUID] = None
    delegator_subject_id: Optional[UUID] = None
    remaining_depth: int = 0
    delegable: bool = False
    version: int = 1


@dataclass(slots=True)
class PolicyRule:
    id: UUID
    effect: PermissionEffect
    resource_type: str
    actions: frozenset[str]
    scope_level: ScopeLevel
    enterprise_id: Optional[UUID] = None
    org_unit_id: Optional[UUID] = None
    conditions_ref: Optional[str] = None


@dataclass(slots=True)
class Policy:
    id: UUID
    tenant_id: UUID
    name: str
    policy_version: str
    status: PolicyStatus
    rules: list[PolicyRule]
    created_at: datetime
    updated_at: datetime
    version: int = 1


@dataclass(slots=True)
class DecisionEvidence:
    matched_grant_ids: list[UUID] = field(default_factory=list)
    matched_policy_ids: list[UUID] = field(default_factory=list)
    matched_rule_ids: list[UUID] = field(default_factory=list)
    scope_trace: list[str] = field(default_factory=list)
    condition_outcomes: list[str] = field(default_factory=list)
    # Opt-in EAOS_PERMISSION_ROLE_GRANT_MAP hits (PHX-G83); not DB grants.
    matched_roles: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PermissionDecision:
    id: UUID
    tenant_id: UUID
    principal_subject_id: UUID
    action: str
    resource_type: str
    effect: PermissionEffect
    reason_code: str
    policy_version: str
    correlation_id: str
    decided_at: datetime
    resource_id: Optional[UUID] = None
    evidence: Optional[DecisionEvidence] = None
