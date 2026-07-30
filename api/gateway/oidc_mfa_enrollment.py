"""OIDC MFA enrollment URL gate (PHX-G89 / ADR-0108)."""

from __future__ import annotations

import os
from urllib.parse import urlparse

from fastapi import HTTPException, status

_UNSET = object()
_URL_OVERRIDE: object = _UNSET


def configure_oidc_mfa_enrollment(
    url: str | None | object = _UNSET,
) -> None:
    """Test helper — pass URL/None to override; omit/_UNSET leaves override unchanged."""

    global _URL_OVERRIDE
    if url is not _UNSET:
        _URL_OVERRIDE = url


def reset_oidc_mfa_enrollment() -> None:
    global _URL_OVERRIDE
    _URL_OVERRIDE = _UNSET


def _normalize_enrollment_url(raw: str | None) -> str | None:
    text = (raw or "").strip()
    if not text:
        return None
    parsed = urlparse(text)
    scheme = (parsed.scheme or "").casefold()
    host = (parsed.hostname or "").casefold()
    if scheme == "https":
        return text
    if scheme == "http" and host in {"127.0.0.1", "localhost", "::1"}:
        return text
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": "GATEWAY_OIDC_MFA_ENROLLMENT_INVALID",
            "message": (
                "EAOS_OIDC_MFA_ENROLLMENT_URL must be https "
                "(or http loopback for local tests)"
            ),
        },
    )


def oidc_mfa_enrollment_url(*, raise_on_invalid: bool = False) -> str | None:
    if _URL_OVERRIDE is not _UNSET:
        raw = None if _URL_OVERRIDE is None else str(_URL_OVERRIDE)
    else:
        raw = os.environ.get("EAOS_OIDC_MFA_ENROLLMENT_URL")
    try:
        return _normalize_enrollment_url(raw)
    except HTTPException:
        if raise_on_invalid:
            raise
        return None


def oidc_mfa_enrollment_enabled() -> bool:
    return oidc_mfa_enrollment_url() is not None


def mfa_enrollment_detail_fields() -> dict[str, str]:
    """Optional fields attached to amr/acr denial details."""

    url = oidc_mfa_enrollment_url()
    if url is None:
        return {}
    return {"mfa_enrollment_url": url}
