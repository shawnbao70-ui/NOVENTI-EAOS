"""Role→grant auto-write (PHX-G156 stub → PHX-G161 env-gated live mint).

Default remains fail-closed 503. Under explicit PO (PHX-G161 / DAL-G006 /
DAL-U032), ``EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED=true`` plus a configured
``EAOS_PERMISSION_ROLE_GRANT_MAP`` opens Role→grant mint via Permission.grant.

Cap≠grant / title≠permission remain fail-closed. This path never invents
Cap→grant — only expands declared roles through the G83 role→(type,action)
map into ordinary Permission grants (manual-grant relatives G128/G129).
"""

from __future__ import annotations

import os
from typing import Any, Literal
from uuid import UUID

from fastapi import HTTPException, status

from api.gateway.deps import PermissionGatewayService
from api.gateway.errors import raise_for_result
from api.gateway.schemas.permission import RoleGrantAutoWriteRequest
from kernel.permission.models import ScopeLevel
from kernel.permission.role_grant_map import permission_role_grant_map
from kernel.shared.context import ExecutionContext

# Canonical OpenAPI /permission-prefix paths for auto-write routes.
ROLE_GRANT_AUTO_WRITE_STUB_ROUTES: tuple[str, ...] = (
    "/permission/role-grants",
)
# Back-compat alias for G156 contracts.
ROLE_GRANT_AUTO_WRITE_ROUTES = ROLE_GRANT_AUTO_WRITE_STUB_ROUTES

GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED = "GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED"
GATEWAY_ROLE_GRANT_MAP_REQUIRED = "GATEWAY_ROLE_GRANT_MAP_REQUIRED"

AutoWriteStep = Literal["role_grants"]

_DISABLED_MESSAGE = (
    "Role→grant auto-write is disabled "
    "(set EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED=true after PHX-G161 / DAL-G006 / DAL-U032; "
    "Cap≠grant; title≠permission)"
)
_MAP_REQUIRED_MESSAGE = (
    "Role→grant live mint requires a non-empty EAOS_PERMISSION_ROLE_GRANT_MAP "
    "when auto-write is enabled (PHX-G161; Cap≠grant; title≠permission)"
)


def _env_flag(name: str, *, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    return str(raw).strip().casefold() in {"1", "true", "yes", "on"}


def role_grant_auto_write_enabled() -> bool:
    """Honor EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED (default false; PHX-G161)."""

    return _env_flag("EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED", default=False)


def role_grant_map_configured() -> bool:
    return bool(permission_role_grant_map())


def role_grant_live_mint_ready() -> bool:
    return role_grant_auto_write_enabled() and role_grant_map_configured()


def raise_role_grant_auto_write_disabled(
    *,
    auto_write_step: AutoWriteStep = "role_grants",
) -> None:
    """Raise the canonical 503 when auto-write env is off."""

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED,
            "message": _DISABLED_MESSAGE,
            "auto_write_step": auto_write_step,
            "grant_minted": False,
            "cap_is_grant": False,
            "title_is_permission": False,
            "next_action": "none",
            "milestone": "PHX-G161",
        },
    )


def raise_role_grant_map_required(
    *,
    auto_write_step: AutoWriteStep = "role_grants",
) -> None:
    """Raise 503 when mint env is on but role grant map is empty."""

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": GATEWAY_ROLE_GRANT_MAP_REQUIRED,
            "message": _MAP_REQUIRED_MESSAGE,
            "auto_write_step": auto_write_step,
            "grant_minted": False,
            "cap_is_grant": False,
            "title_is_permission": False,
            "next_action": "configure_permission_role_grant_map",
            "milestone": "PHX-G161",
        },
    )


def _scope_ids(
    scope_level: ScopeLevel,
    scope_ref_id: UUID | None,
) -> tuple[UUID | None, UUID | None]:
    if scope_level == ScopeLevel.ENTERPRISE:
        return scope_ref_id, None
    if scope_level == ScopeLevel.ORG_UNIT:
        return None, scope_ref_id
    return None, None


def mint_grants_from_roles(
    ctx: ExecutionContext,
    permission: PermissionGatewayService,
    body: RoleGrantAutoWriteRequest,
) -> dict[str, Any]:
    """Expand roles via G83 map and mint Permission grants (not Cap→grant)."""

    if not role_grant_auto_write_enabled():
        raise_role_grant_auto_write_disabled(auto_write_step="role_grants")
    if not role_grant_map_configured():
        raise_role_grant_map_required(auto_write_step="role_grants")

    principal_id = body.principal_id
    roles = [str(role).strip() for role in body.roles if str(role).strip()]
    if not roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "COMMON_VALIDATION_FAILED",
                "message": "roles is required and must be a non-empty list of role names",
            },
        )

    mapping = permission_role_grant_map()
    # Aggregate actions by resource_type; track which roles contributed.
    by_type: dict[str, set[str]] = {}
    roles_for_type: dict[str, set[str]] = {}
    for role in roles:
        pairs = mapping.get(role, frozenset())
        for resource_type, action in pairs:
            by_type.setdefault(resource_type, set()).add(action)
            roles_for_type.setdefault(resource_type, set()).add(role)

    if not by_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "COMMON_VALIDATION_FAILED",
                "message": (
                    "no grant pairs matched the supplied roles in "
                    "EAOS_PERMISSION_ROLE_GRANT_MAP (Cap≠grant; title≠permission)"
                ),
                "grant_minted": False,
                "cap_is_grant": False,
                "title_is_permission": False,
                "roles": roles,
                "milestone": "PHX-G161",
            },
        )

    level = ScopeLevel(body.scope_level)
    enterprise_id, org_unit_id = _scope_ids(level, body.scope_ref_id)
    minted: list[dict[str, Any]] = []
    audit_id = None
    for resource_type, actions in sorted(by_type.items()):
        result = permission.grant(
            ctx,
            principal_subject_id=principal_id,
            resource_type=resource_type,
            actions=set(actions),
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
        if result.audit_id is not None:
            audit_id = result.audit_id
        minted.append(
            {
                "id": str(result.data),
                "resource_type": resource_type,
                "actions": sorted(actions),
                "roles": sorted(roles_for_type.get(resource_type, set())),
            }
        )

    return {
        "auto_write_step": "role_grants",
        "grant_minted": True,
        "cap_is_grant": False,
        "title_is_permission": False,
        "milestone": "PHX-G161",
        "principal_id": str(principal_id),
        "roles_applied": sorted(set(roles)),
        "grants": minted,
        "grant_count": len(minted),
        "audit_id": str(audit_id) if audit_id is not None else None,
    }
