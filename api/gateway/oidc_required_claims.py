"""OIDC id_token required-claims gate (PHX-G79 / ADR-0098)."""

from __future__ import annotations

import os
from typing import Any

from fastapi import HTTPException, status

_UNSET = object()
_OVERRIDE: object = _UNSET


def configure_oidc_required_claims(claims: list[str] | None | object = _UNSET) -> None:
    """Test helper — pass list/None to override; omit/_UNSET clears override."""

    global _OVERRIDE
    _OVERRIDE = claims


def oidc_required_claims() -> list[str]:
    if _OVERRIDE is not _UNSET:
        if _OVERRIDE is None:
            return []
        return [str(item).strip() for item in _OVERRIDE if str(item).strip()]  # type: ignore[union-attr]
    raw = (os.environ.get("EAOS_OIDC_REQUIRED_CLAIMS") or "").strip()
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def oidc_required_claims_enabled() -> bool:
    return bool(oidc_required_claims())


def assert_oidc_required_claims(id_claims: dict[str, Any]) -> None:
    """Fail-closed when configured claims are missing or empty."""

    required = oidc_required_claims()
    if not required:
        return
    missing: list[str] = []
    for name in required:
        if name not in id_claims or not _claim_present(id_claims.get(name)):
            missing.append(name)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "code": "GATEWAY_OIDC_REQUIRED_CLAIM_MISSING",
                "message": "OIDC id_token missing required claim(s)",
                "details": {"claims": missing},
            },
        )


def _claim_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return True
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0
    return True
