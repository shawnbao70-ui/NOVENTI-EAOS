"""OIDC claim → eaos_roles mint gate (PHX-G81 / ADR-0100)."""

from __future__ import annotations

import os
from typing import Any

from fastapi import HTTPException, status

_UNSET = object()
_CLAIM_OVERRIDE: object = _UNSET
_MAP_OVERRIDE: object = _UNSET
_REQUIRE_OVERRIDE: object = _UNSET


def configure_oidc_claim_role(
    *,
    role_claim: str | None | object = _UNSET,
    role_map: dict[str, str] | None | object = _UNSET,
    require_mapped_role: bool | None | object = _UNSET,
) -> None:
    """Test helper — pass values to override; omit/_UNSET leaves that override unchanged."""

    global _CLAIM_OVERRIDE, _MAP_OVERRIDE, _REQUIRE_OVERRIDE
    if role_claim is not _UNSET:
        _CLAIM_OVERRIDE = role_claim
    if role_map is not _UNSET:
        _MAP_OVERRIDE = role_map
    if require_mapped_role is not _UNSET:
        _REQUIRE_OVERRIDE = require_mapped_role


def reset_oidc_claim_role() -> None:
    global _CLAIM_OVERRIDE, _MAP_OVERRIDE, _REQUIRE_OVERRIDE
    _CLAIM_OVERRIDE = _UNSET
    _MAP_OVERRIDE = _UNSET
    _REQUIRE_OVERRIDE = _UNSET


def oidc_role_claim() -> str | None:
    if _CLAIM_OVERRIDE is not _UNSET:
        if _CLAIM_OVERRIDE is None:
            return None
        text = str(_CLAIM_OVERRIDE).strip()
        return text or None
    raw = (os.environ.get("EAOS_OIDC_ROLE_CLAIM") or "").strip()
    return raw or None


def oidc_role_map() -> dict[str, str]:
    if _MAP_OVERRIDE is not _UNSET:
        if _MAP_OVERRIDE is None:
            return {}
        return {
            str(key).strip(): str(value).strip()
            for key, value in dict(_MAP_OVERRIDE).items()  # type: ignore[arg-type]
            if str(key).strip() and str(value).strip()
        }
    raw = (os.environ.get("EAOS_OIDC_ROLE_MAP") or "").strip()
    if not raw:
        return {}
    mapping: dict[str, str] = {}
    for part in raw.split(","):
        piece = part.strip()
        if not piece or "=" not in piece:
            continue
        source, target = piece.split("=", 1)
        source = source.strip()
        target = target.strip()
        if source and target:
            mapping[source] = target
    return mapping


def oidc_role_claim_enabled() -> bool:
    return oidc_role_claim() is not None and bool(oidc_role_map())


def oidc_require_mapped_role() -> bool:
    if _REQUIRE_OVERRIDE is not _UNSET:
        return bool(_REQUIRE_OVERRIDE)
    raw = (os.environ.get("EAOS_OIDC_REQUIRE_MAPPED_ROLE") or "0").strip().lower()
    return raw in ("1", "true", "yes", "on")


def map_oidc_roles(id_claims: dict[str, Any]) -> list[str]:
    """Map IdP claim values to sorted unique eaos_roles; empty when disabled."""

    claim = oidc_role_claim()
    mapping = oidc_role_map()
    if not claim or not mapping:
        return []
    values = _claim_values(id_claims.get(claim))
    roles = {mapping[value] for value in values if value in mapping}
    return sorted(roles)


def assert_oidc_mapped_roles(roles: list[str]) -> None:
    if not oidc_role_claim_enabled():
        return
    if oidc_require_mapped_role() and not roles:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "GATEWAY_OIDC_ROLE_REQUIRED",
                "message": "OIDC id_token produced no mapped eaos_roles",
                "details": {
                    "role_claim": oidc_role_claim(),
                    "mapped_roles": [],
                },
            },
        )


def _claim_values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []
