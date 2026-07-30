"""Permission HTTP surface — thin transport adapter (PHX-G22)."""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, status

from api.gateway.context import derive_tenant_context, reject_context_override
from api.gateway.deps import PermissionGatewayService, get_permission_service
from api.gateway.errors import raise_for_result
from api.gateway.role_catalog import build_role_catalog, build_role_catalog_status
from api.gateway.schemas.common import OkResponse, UuidResult
from api.gateway.schemas.foundation_status import FoundationStatusEnvelope
from api.gateway.schemas.permission import (
    CapGrantRequest,
    CapGrantRevokeRequest,
    CreatePolicyRequest,
    DecisionExplanation,
    DelegateRequest,
    EffectivePermission,
    EvaluateRequest,
    EvaluateResult,
    ExpectedVersionRequest,
    GrantRequest,
    PolicyRuleBody,
    PermissionRoleCatalogResponse,
    RoleCatalogStatusEnvelope,
    VersionedReasonRequest,
)
from api.gateway.serializers.permission import (
    ok_response,
    serialize_effective_grant,
    serialize_evaluate,
    serialize_explanation,
    uuid_result,
)
from kernel.permission.models import (
    PermissionEffect,
    PolicyRule,
    Resource,
    ScopeLevel,
)
from kernel.shared.context import ExecutionContext

router = APIRouter(prefix="/v1/permission", tags=["Permission"])


def _scope_ids(
    scope_level: ScopeLevel,
    scope_ref_id: UUID | None,
) -> tuple[UUID | None, UUID | None]:
    if scope_level == ScopeLevel.ENTERPRISE:
        return scope_ref_id, None
    if scope_level == ScopeLevel.ORG_UNIT:
        # OpenAPI exposes a single scope_ref_id; map to org_unit_id only.
        # Callers needing enterprise+unit should use Kernel/composition APIs.
        return None, scope_ref_id
    return None, None


def _parse_rules(raw_rules: list[PolicyRuleBody]) -> list[PolicyRule]:
    rules: list[PolicyRule] = []
    for item in raw_rules:
        level = ScopeLevel(item.scope_level)
        enterprise_id, org_unit_id = _scope_ids(level, item.scope_ref_id)
        rules.append(
            PolicyRule(
                id=uuid4(),
                effect=PermissionEffect(item.effect),
                resource_type=item.resource_type,
                actions=frozenset(item.actions),
                scope_level=level,
                enterprise_id=enterprise_id,
                org_unit_id=org_unit_id,
                conditions_ref=item.condition_ref,
            )
        )
    return rules


@router.post("/policies", response_model=UuidResult, status_code=status.HTTP_201_CREATED)
def create_policy(
    body: CreatePolicyRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    permission: PermissionGatewayService = Depends(get_permission_service),
) -> UuidResult:
    reject_context_override(body.model_dump())
    rules = _parse_rules(body.rules)
    result = permission.create_policy(
        ctx,
        name=body.name,
        policy_version=body.policy_version or "1",
        rules=rules,
    )
    raise_for_result(result)
    assert result.data is not None
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.post("/policies/{policy_id}/activation", response_model=OkResponse)
def activate_policy(
    policy_id: UUID,
    body: ExpectedVersionRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    permission: PermissionGatewayService = Depends(get_permission_service),
) -> OkResponse:
    reject_context_override(body.model_dump(exclude_none=True))
    result = permission.activate_policy(
        ctx,
        policy_id=policy_id,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    return OkResponse.model_validate(ok_response(audit_id=result.audit_id))


@router.post("/policies/{policy_id}/deprecation", response_model=OkResponse)
def deprecate_policy(
    policy_id: UUID,
    body: ExpectedVersionRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    permission: PermissionGatewayService = Depends(get_permission_service),
) -> OkResponse:
    reject_context_override(body.model_dump(exclude_none=True))
    result = permission.deprecate_policy(
        ctx,
        policy_id=policy_id,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    return OkResponse.model_validate(ok_response(audit_id=result.audit_id))


@router.post("/grants", response_model=UuidResult, status_code=status.HTTP_201_CREATED)
def create_grant(
    body: GrantRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    permission: PermissionGatewayService = Depends(get_permission_service),
) -> UuidResult:
    reject_context_override(body.model_dump(exclude_none=True))
    level = ScopeLevel(body.scope_level)
    enterprise_id, org_unit_id = _scope_ids(level, body.scope_ref_id)
    result = permission.grant(
        ctx,
        principal_subject_id=body.principal_id,
        resource_type=body.resource_type,
        actions=set(body.actions),
        resource_id=body.resource_id,
        scope_level=level,
        enterprise_id=enterprise_id,
        org_unit_id=org_unit_id,
        conditions_ref=body.conditions_ref,
        expires_at=body.expires_at,
        delegable=body.delegable,
        remaining_depth=body.delegation_depth,
    )
    raise_for_result(result)
    assert result.data is not None
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.post(
    "/cap-grants",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def create_cap_grant(
    body: CapGrantRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    permission: PermissionGatewayService = Depends(get_permission_service),
) -> UuidResult:
    """Explicit PHX-G345 capability-labelled tenant grant; Cap is not a role."""
    reject_context_override(body.model_dump(exclude_none=True))
    result = permission.grant_capability(
        ctx,
        principal_subject_id=body.principal_subject_id,
        capability=body.capability,
        resource_type=body.resource_type,
        actions=set(body.actions),
        idempotency_key=body.idempotency_key,
    )
    raise_for_result(result)
    assert result.data is not None
    return UuidResult.model_validate(uuid_result(result.data, audit_id=result.audit_id))


@router.get("/cap-grants", response_model=list[EffectivePermission])
def list_cap_grants(
    principal_subject_id: UUID | None = None,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    permission: PermissionGatewayService = Depends(get_permission_service),
) -> list[EffectivePermission]:
    result = permission.list_tenant_grants(
        ctx,
        principal_subject_id=principal_subject_id,
    )
    raise_for_result(result)
    assert result.data is not None
    return [
        EffectivePermission.model_validate(serialize_effective_grant(item))
        for item in result.data
    ]


@router.post("/cap-grants/{grant_id}/revoke", response_model=OkResponse)
def revoke_cap_grant(
    grant_id: UUID,
    body: CapGrantRevokeRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    permission: PermissionGatewayService = Depends(get_permission_service),
) -> OkResponse:
    reject_context_override(body.model_dump())
    result = permission.revoke_capability(
        ctx,
        grant_id=grant_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    return OkResponse.model_validate(ok_response(audit_id=result.audit_id))


@router.post("/grants/{grant_id}/revocation", response_model=OkResponse)
def revoke_grant(
    grant_id: UUID,
    body: VersionedReasonRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    permission: PermissionGatewayService = Depends(get_permission_service),
) -> OkResponse:
    reject_context_override(body.model_dump())
    result = permission.revoke(
        ctx,
        grant_id=grant_id,
        reason=body.reason,
        expected_version=body.expected_version,
    )
    raise_for_result(result)
    return OkResponse.model_validate(ok_response(audit_id=result.audit_id))


@router.post(
    "/grants/{grant_id}/delegations",
    response_model=UuidResult,
    status_code=status.HTTP_201_CREATED,
)
def delegate_grant(
    grant_id: UUID,
    body: DelegateRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    permission: PermissionGatewayService = Depends(get_permission_service),
) -> UuidResult:
    reject_context_override(body.model_dump(exclude_none=True))
    level = ScopeLevel(body.scope_level)
    enterprise_id, org_unit_id = _scope_ids(level, body.scope_ref_id)
    result = permission.delegate(
        ctx,
        parent_grant_id=grant_id,
        to_principal_subject_id=body.delegatee_principal_id,
        actions=set(body.actions),
        scope_level=level,
        enterprise_id=enterprise_id,
        org_unit_id=org_unit_id,
        resource_id=body.resource_id,
        expires_at=body.expires_at,
        delegable=body.delegable,
    )
    raise_for_result(result)
    assert result.data is not None
    return UuidResult.model_validate(
        uuid_result(result.data, audit_id=result.audit_id)
    )


@router.post("/evaluations", response_model=EvaluateResult)
def evaluate_permission(
    body: EvaluateRequest,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    permission: PermissionGatewayService = Depends(get_permission_service),
) -> EvaluateResult:
    reject_context_override(body.model_dump(exclude_none=True))
    assert ctx.tenant_id is not None
    # Principal is the trusted header subject — never accept body impersonation.
    result = permission.evaluate(
        ctx,
        principal_subject_id=ctx.subject_id,
        action=body.action,
        resource=Resource(
            tenant_id=ctx.tenant_id,
            resource_type=body.resource_type,
            resource_id=body.resource_id,
        ),
    )
    raise_for_result(result)
    assert result.data is not None
    return EvaluateResult.model_validate(
        serialize_evaluate(result.data, audit_id=result.audit_id)
    )


@router.get(
    "/decisions/{decision_id}/explanation",
    response_model=DecisionExplanation,
)
def explain_decision(
    decision_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    permission: PermissionGatewayService = Depends(get_permission_service),
) -> DecisionExplanation:
    result = permission.explain(ctx, decision_id=decision_id)
    raise_for_result(result)
    assert result.data is not None
    return DecisionExplanation.model_validate(
        serialize_explanation(decision_id, result.data)
    )


@router.get(
    "/principals/{subject_id}/effective-permissions",
    response_model=list[EffectivePermission],
)
def list_effective_permissions(
    subject_id: UUID,
    ctx: ExecutionContext = Depends(derive_tenant_context),
    permission: PermissionGatewayService = Depends(get_permission_service),
) -> list[EffectivePermission]:
    result = permission.list_effective(ctx, principal_subject_id=subject_id)
    raise_for_result(result)
    assert result.data is not None
    return [
        EffectivePermission.model_validate(serialize_effective_grant(item))
        for item in result.data
    ]


@router.get(
    "/roles",
    response_model=PermissionRoleCatalogResponse,
    response_model_exclude_none=True,
)
def list_roles(
    ctx: ExecutionContext = Depends(derive_tenant_context),
) -> PermissionRoleCatalogResponse:
    """Flat catalog payload (not a data envelope) — OpenAPI PermissionRoleCatalogResponse."""

    _ = ctx
    roles = build_role_catalog()
    return PermissionRoleCatalogResponse.model_validate(
        {"enabled": bool(roles), "roles": roles}
    )


@router.get("/roles/status", response_model=RoleCatalogStatusEnvelope)
def roles_status(
    ctx: ExecutionContext = Depends(derive_tenant_context),
) -> RoleCatalogStatusEnvelope:
    _ = ctx
    return RoleCatalogStatusEnvelope.model_validate(
        {"data": build_role_catalog_status()}
    )


@router.get("/status", response_model=FoundationStatusEnvelope)
def get_permission_status() -> FoundationStatusEnvelope:
    return FoundationStatusEnvelope.model_validate(
        {
            "data": {
                "writable": False,
                "supported_surfaces": [
                    "policy_create",
                    "policy_activate",
                    "policy_deprecate",
                    "grant_create",
                    "grant_revoke",
                    "grant_delegate",
                    "evaluate",
                    "explain",
                    "effective_permissions",
                    "role_catalog",
                    "role_grant_auto_write",
                ],
            }
        }
    )
