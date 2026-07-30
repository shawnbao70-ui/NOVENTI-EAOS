"""OIDC amr/acr authentication context gate (PHX-G80 / ADR-0099)."""

from __future__ import annotations

import os
from typing import Any

from fastapi import HTTPException, status

_UNSET = object()
_AMR_OVERRIDE: object = _UNSET
_ACR_OVERRIDE: object = _UNSET


def configure_oidc_amr_acr(
    *,
    amr: list[str] | None | object = _UNSET,
    acr: list[str] | None | object = _UNSET,
) -> None:
    """Test helper — pass list/None to override; omit/_UNSET clears that override."""

    global _AMR_OVERRIDE, _ACR_OVERRIDE
    if amr is not _UNSET:
        _AMR_OVERRIDE = amr
    if acr is not _UNSET:
        _ACR_OVERRIDE = acr


def reset_oidc_amr_acr() -> None:
    global _AMR_OVERRIDE, _ACR_OVERRIDE
    _AMR_OVERRIDE = _UNSET
    _ACR_OVERRIDE = _UNSET


def oidc_required_amr() -> list[str]:
    if _AMR_OVERRIDE is not _UNSET:
        if _AMR_OVERRIDE is None:
            return []
        return [str(item).strip() for item in _AMR_OVERRIDE if str(item).strip()]  # type: ignore[union-attr]
    raw = (os.environ.get("EAOS_OIDC_REQUIRED_AMR") or "").strip()
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def oidc_required_acr() -> list[str]:
    if _ACR_OVERRIDE is not _UNSET:
        if _ACR_OVERRIDE is None:
            return []
        return [str(item).strip() for item in _ACR_OVERRIDE if str(item).strip()]  # type: ignore[union-attr]
    raw = (os.environ.get("EAOS_OIDC_REQUIRED_ACR") or "").strip()
    if not raw:
        return []
    return [part.strip() for part in raw.split(",") if part.strip()]


def oidc_required_amr_enabled() -> bool:
    return bool(oidc_required_amr())


def oidc_required_acr_enabled() -> bool:
    return bool(oidc_required_acr())


def assert_oidc_amr_acr(id_claims: dict[str, Any]) -> None:
    """Fail-closed when configured amr/acr requirements are not met."""

    from api.gateway.oidc_mfa_enrollment import mfa_enrollment_detail_fields

    required_amr = oidc_required_amr()
    if required_amr:
        present = _normalize_amr(id_claims.get("amr"))
        if not any(item in present for item in required_amr):
            details: dict[str, Any] = {
                "required_amr": required_amr,
                "present_amr": sorted(present),
            }
            details.update(mfa_enrollment_detail_fields())
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "GATEWAY_OIDC_AMR_REQUIRED",
                    "message": "OIDC id_token amr does not satisfy required authentication methods",
                    "details": details,
                },
            )

    required_acr = oidc_required_acr()
    if required_acr:
        acr_value = id_claims.get("acr")
        acr_text = str(acr_value).strip() if acr_value is not None else ""
        if not acr_text or acr_text not in required_acr:
            details = {
                "required_acr": required_acr,
                "present_acr": acr_text or None,
            }
            details.update(mfa_enrollment_detail_fields())
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "GATEWAY_OIDC_ACR_REQUIRED",
                    "message": "OIDC id_token acr does not satisfy required authentication context",
                    "details": details,
                },
            )


def _normalize_amr(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, str):
        text = value.strip()
        return {text} if text else set()
    if isinstance(value, (list, tuple, set)):
        return {str(item).strip() for item in value if str(item).strip()}
    text = str(value).strip()
    return {text} if text else set()
