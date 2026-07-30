"""Opt-in ExecutionContext.roles → evaluate allow map (PHX-G83 / ADR-0102)."""

from __future__ import annotations

import os

_UNSET = object()
_MAP_OVERRIDE: object = _UNSET

# role -> frozenset[(resource_type, action)]
RoleGrantMap = dict[str, frozenset[tuple[str, str]]]


def configure_permission_role_grant_map(
    mapping: RoleGrantMap | None | object = _UNSET,
) -> None:
    """Test helper — pass mapping to override; omit/_UNSET leaves override unchanged."""

    global _MAP_OVERRIDE
    if mapping is not _UNSET:
        _MAP_OVERRIDE = mapping


def reset_permission_role_grant_map() -> None:
    global _MAP_OVERRIDE
    _MAP_OVERRIDE = _UNSET


def parse_role_grant_map(raw: str) -> RoleGrantMap:
    """Parse ``role=type:action|type:action,...`` (empty → {})."""

    text = (raw or "").strip()
    if not text:
        return {}
    mapping: dict[str, set[tuple[str, str]]] = {}
    for part in text.split(","):
        piece = part.strip()
        if not piece or "=" not in piece:
            continue
        role, grants = piece.split("=", 1)
        role = role.strip()
        if not role:
            continue
        pairs: set[tuple[str, str]] = set()
        for grant in grants.split("|"):
            item = grant.strip()
            if not item or ":" not in item:
                continue
            resource_type, action = item.split(":", 1)
            resource_type = resource_type.strip().lower()
            action = action.strip().lower()
            if resource_type and action:
                pairs.add((resource_type, action))
        if pairs:
            mapping.setdefault(role, set()).update(pairs)
    return {role: frozenset(pairs) for role, pairs in mapping.items()}


def permission_role_grant_map() -> RoleGrantMap:
    if _MAP_OVERRIDE is not _UNSET:
        if _MAP_OVERRIDE is None:
            return {}
        return {
            str(role).strip(): frozenset(
                (str(rt).strip().lower(), str(act).strip().lower())
                for rt, act in pairs
                if str(rt).strip() and str(act).strip()
            )
            for role, pairs in dict(_MAP_OVERRIDE).items()  # type: ignore[arg-type]
            if str(role).strip()
        }
    return parse_role_grant_map(os.environ.get("EAOS_PERMISSION_ROLE_GRANT_MAP") or "")


def permission_role_grant_map_enabled() -> bool:
    return bool(permission_role_grant_map())


def match_context_roles(
    *,
    roles: tuple[str, ...] | list[str],
    resource_type: str,
    action: str,
    mapping: RoleGrantMap | None = None,
) -> list[str]:
    """Return sorted unique roles that allow ``(resource_type, action)``."""

    active = mapping if mapping is not None else permission_role_grant_map()
    if not active or not roles:
        return []
    target = (resource_type.strip().lower(), action.strip().lower())
    matched = [
        role
        for role in roles
        if role and target in active.get(role, frozenset())
    ]
    return sorted(set(matched))
