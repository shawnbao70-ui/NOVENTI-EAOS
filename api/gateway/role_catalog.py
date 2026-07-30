"""Read-only EAOS roles catalog (PHX-G88/G90/G93 / ADR-0107/0109/0112)."""

from __future__ import annotations

import os
from typing import Any

from api.gateway.oidc_claim_role import oidc_role_map
from api.gateway.role_catalog_store import (
    active_declared_role_names,
    role_catalog_store_label,
)
from api.gateway.role_grant_product import role_grant_product_posture
from kernel.permission.role_grant_map import (
    permission_role_grant_map,
    permission_role_grant_map_enabled,
)

_UNSET = object()
_CATALOG_OVERRIDE: object = _UNSET


def configure_role_catalog(
    roles: list[str] | None | object = _UNSET,
) -> None:
    """Test helper — pass list/None to override env-declared catalog roles."""

    global _CATALOG_OVERRIDE
    if roles is not _UNSET:
        _CATALOG_OVERRIDE = roles


def reset_role_catalog() -> None:
    global _CATALOG_OVERRIDE
    _CATALOG_OVERRIDE = _UNSET


def _env_declared_roles() -> list[str]:
    if _CATALOG_OVERRIDE is not _UNSET:
        if _CATALOG_OVERRIDE is None:
            return []
        return sorted(
            {
                str(item).strip()
                for item in _CATALOG_OVERRIDE  # type: ignore[union-attr]
                if str(item).strip()
            }
        )
    raw = (os.environ.get("EAOS_ROLE_CATALOG") or "").strip()
    if not raw:
        return []
    return sorted({part.strip() for part in raw.split(",") if part.strip()})


def declared_role_catalog() -> list[str]:
    """Env declared roles ∪ active store rows (PHX-G90)."""

    names = set(_env_declared_roles())
    names.update(active_declared_role_names())
    return sorted(names)


def build_role_catalog() -> list[dict[str, Any]]:
    """Aggregate roles from OIDC map targets, grant map keys, and declared catalog."""

    oidc_targets = {
        str(value).strip()
        for value in oidc_role_map().values()
        if str(value).strip()
    }
    grant_map = permission_role_grant_map()
    grant_roles = set(grant_map.keys())
    declared = set(declared_role_catalog())
    names = sorted(oidc_targets | grant_roles | declared)
    rows: list[dict[str, Any]] = []
    for name in names:
        sources: list[str] = []
        if name in declared:
            sources.append("catalog")
        if name in oidc_targets:
            sources.append("oidc_map")
        if name in grant_roles:
            sources.append("grant_map")
        row: dict[str, Any] = {
            "name": name,
            "sources": sources,
        }
        pairs = grant_map.get(name)
        if pairs:
            row["grants"] = [
                {"resource_type": resource_type, "action": action}
                for resource_type, action in sorted(pairs)
            ]
        rows.append(row)
    return rows


def role_catalog_enabled() -> bool:
    return bool(build_role_catalog())


def build_role_catalog_status() -> dict[str, Any]:
    """Lightweight observability for roles catalog + grant map (PHX-G93/G146)."""

    roles = build_role_catalog()
    source_counts = {"catalog": 0, "oidc_map": 0, "grant_map": 0}
    for row in roles:
        for source in row.get("sources") or []:
            key = str(source)
            if key in source_counts:
                source_counts[key] += 1
    grant_map = permission_role_grant_map()
    return {
        "catalog_store": role_catalog_store_label(),
        "catalog_enabled": bool(roles),
        "role_count": len(roles),
        "grant_map_enabled": permission_role_grant_map_enabled(),
        "grant_map_role_count": len(grant_map),
        "source_counts": source_counts,
        "role_grant_product": role_grant_product_posture(),
    }
