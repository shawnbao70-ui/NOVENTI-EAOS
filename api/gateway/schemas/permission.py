"""Permission request DTOs — runtime parity with docs/api/permission.openapi.yaml."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


ScopeLevelLiteral = Literal["tenant", "enterprise", "org_unit", "resource"]
EffectLiteral = Literal["allow", "deny"]


class PolicyRuleBody(_ClosedModel):
    effect: EffectLiteral
    resource_type: str = Field(min_length=1)
    actions: list[str] = Field(min_length=1)
    scope_level: ScopeLevelLiteral
    scope_ref_id: UUID | None = None
    condition_ref: str | None = None


class RoleCatalogSourceCounts(_ClosedModel):
    catalog: int = Field(ge=0)
    oidc_map: int = Field(ge=0)
    grant_map: int = Field(ge=0)


class RoleGrantProductPosture(_ClosedModel):
    surface: Literal["foundation_role_grant_product"] = "foundation_role_grant_product"
    milestone: Literal["PHX-G161"] = "PHX-G161"
    auto_grant_from_role_enabled: bool
    role_grant_map_configured: bool
    role_grant_live_mint_ready: bool
    auto_write_routes: list[str] = Field(min_length=1)
    auto_write_stub_observability: bool
    auto_write_default_off: Literal[True] = True
    manual_grant_relatives: Literal["g128_g129"] = "g128_g129"
    evaluate_only_relative: Literal["g83_role_grant_map"] = "g83_role_grant_map"
    fail_closed_reasons: list[str] = Field(min_length=1)


class RoleCatalogStatusData(_ClosedModel):
    catalog_store: Literal["process_memory", "sql"]
    catalog_enabled: bool
    role_count: int = Field(ge=0)
    grant_map_enabled: bool
    grant_map_role_count: int = Field(ge=0)
    source_counts: RoleCatalogSourceCounts
    role_grant_product: RoleGrantProductPosture


class RoleCatalogStatusEnvelope(_ClosedModel):
    data: RoleCatalogStatusData


class PermissionRoleGrantPair(_ClosedModel):
    resource_type: str = Field(min_length=1)
    action: str = Field(min_length=1)


class PermissionRoleCatalogEntry(_ClosedModel):
    name: str = Field(min_length=1)
    sources: list[Literal["catalog", "oidc_map", "grant_map"]]
    grants: list[PermissionRoleGrantPair] | None = None


class PermissionRoleCatalogResponse(_ClosedModel):
    enabled: bool
    roles: list[PermissionRoleCatalogEntry]


class CreatePolicyRequest(_ClosedModel):
    name: str = Field(min_length=1, max_length=255)
    rules: list[PolicyRuleBody] = Field(min_length=1)
    policy_version: str | None = None


class VersionedReasonRequest(_ClosedModel):
    reason: str = Field(min_length=1)
    expected_version: int = Field(ge=1)


class ExpectedVersionRequest(_ClosedModel):
    """Activate historically accepted expected_version without reason."""

    expected_version: int | None = None
    reason: str | None = None


class GrantRequest(_ClosedModel):
    principal_id: UUID
    resource_type: str = Field(min_length=1, max_length=128)
    scope_level: ScopeLevelLiteral
    actions: list[str] = Field(min_length=1)
    resource_id: UUID | None = None
    scope_ref_id: UUID | None = None
    conditions_ref: str | None = None
    expires_at: datetime | None = None
    delegable: bool = False
    delegation_depth: int = Field(default=0, ge=0)


class CapGrantRequest(_ClosedModel):
    """PHX-G345 explicit Cap→grant request; only tenant scope is available."""

    principal_subject_id: UUID
    capability: str = Field(min_length=1, max_length=255)
    resource_type: str = Field(min_length=1, max_length=128)
    actions: list[str] = Field(min_length=1)
    scope_level: Literal["tenant"] = "tenant"
    idempotency_key: str | None = Field(default=None, min_length=1, max_length=255)


class CapGrantRevokeRequest(_ClosedModel):
    reason: str = Field(default="capability grant revoked", min_length=1)
    expected_version: int = Field(default=1, ge=1)


class DelegateRequest(_ClosedModel):
    delegatee_principal_id: UUID
    scope_level: ScopeLevelLiteral
    actions: list[str] = Field(min_length=1)
    expected_version: int = Field(ge=1)
    resource_type: str | None = Field(default=None, max_length=128)
    resource_id: UUID | None = None
    scope_ref_id: UUID | None = None
    expires_at: datetime | None = None
    delegable: bool = False


class EvaluateRequest(_ClosedModel):
    action: str = Field(min_length=1, max_length=128)
    resource_type: str = Field(min_length=1, max_length=128)
    resource_id: UUID | None = None


class RoleGrantAutoWriteRequest(_ClosedModel):
    """Role→grant auto-write mint body (PHX-G161); Cap≠grant."""

    principal_id: UUID
    roles: list[str] = Field(min_length=1)
    scope_level: ScopeLevelLiteral = "tenant"
    scope_ref_id: UUID | None = None
    resource_id: UUID | None = None
    expires_at: datetime | None = None
    delegable: bool = False
    delegation_depth: int = Field(default=0, ge=0)
    conditions_ref: str | None = None


class RoleGrantMintedGrant(_ClosedModel):
    id: UUID
    resource_type: str = Field(min_length=1)
    actions: list[str]
    roles: list[str]


class RoleGrantAutoWriteMintResponse(_ClosedModel):
    auto_write_step: Literal["role_grants"] = "role_grants"
    grant_minted: Literal[True] = True
    cap_is_grant: Literal[False] = False
    title_is_permission: Literal[False] = False
    milestone: Literal["PHX-G161"] = "PHX-G161"
    principal_id: UUID
    roles_applied: list[str]
    grants: list[RoleGrantMintedGrant]
    grant_count: int = Field(ge=0)
    audit_id: UUID | str | None = None


class EvaluateResult(_ClosedModel):
    """Closed evaluate response — runtime policy_version is string (joined versions)."""

    decision_id: UUID
    effect: EffectLiteral
    reason_code: str
    policy_version: str
    audit_id: UUID | str | None = None


class DecisionExplanation(_ClosedModel):
    decision_id: UUID
    effect: EffectLiteral
    reason_code: str
    policy_version: str
    evidence_summary: str
    matched_policy_ids: list[str] = Field(default_factory=list)
    matched_grant_ids: list[str] = Field(default_factory=list)
    matched_roles: list[str] = Field(default_factory=list)
    scope_trace: list[str] = Field(default_factory=list)
    condition_outcomes: list[str] = Field(default_factory=list)


class EffectivePermission(_ClosedModel):
    grant_id: UUID
    resource_type: str = Field(min_length=1)
    scope_level: ScopeLevelLiteral
    actions: list[str]
    effect: EffectLiteral
    resource_id: UUID | None = None
    scope_ref_id: UUID | None = None
