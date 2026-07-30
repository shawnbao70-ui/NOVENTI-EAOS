"""WebAuthn registration ceremony (PHX-G151/G154 stubs → PHX-G160 live mint).

Default remains fail-closed 503. Under CA-authorized live mint (PHX-G160 /
DAL-G008 / DAL-U037), ``EAOS_WEBAUTHN_REGISTRATION_ENABLED=true`` plus
RP_ID/ORIGIN opens challenge-bound credential mint into
Identity.BindCredential.

Full packed/TPM attestation-statement crypto verify remains Explicit Out
(``attestation_crypto_verified=false``); challenge + origin + type binding
is enforced.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import threading
import time
from typing import Any, Literal
from uuid import UUID

from fastapi import HTTPException, status

from api.gateway.deps import IdentityGatewayService
from api.gateway.errors import raise_for_result
from kernel.shared.context import ExecutionContext

# Canonical OpenAPI /auth-prefix paths for the ceremony routes.
WEBAUTHN_CEREMONY_ROUTES: tuple[str, ...] = (
    "/auth/webauthn/register/options",
    "/auth/webauthn/register/verify",
)
# Back-compat alias for G151/G154 contracts.
WEBAUTHN_CEREMONY_STUB_ROUTES = WEBAUTHN_CEREMONY_ROUTES

GATEWAY_WEBAUTHN_REGISTRATION_DISABLED = "GATEWAY_WEBAUTHN_REGISTRATION_DISABLED"
GATEWAY_WEBAUTHN_RP_CONFIG_REQUIRED = "GATEWAY_WEBAUTHN_RP_CONFIG_REQUIRED"
GATEWAY_WEBAUTHN_CHALLENGE_INVALID = "GATEWAY_WEBAUTHN_CHALLENGE_INVALID"
GATEWAY_WEBAUTHN_ATTESTATION_INVALID = "GATEWAY_WEBAUTHN_ATTESTATION_INVALID"

CeremonyStep = Literal["register_options", "register_verify"]

_CHALLENGE_TTL_SECONDS = 300
_challenge_lock = threading.Lock()
_challenges: dict[str, dict[str, Any]] = {}

_DISABLED_MESSAGE = (
    "WebAuthn registration ceremony is disabled "
    "(set EAOS_WEBAUTHN_REGISTRATION_ENABLED=true after PHX-G160)"
)
_RP_CONFIG_MESSAGE = (
    "WebAuthn live mint requires EAOS_WEBAUTHN_RP_ID and "
    "EAOS_WEBAUTHN_ORIGIN when registration is enabled (PHX-G160)"
)


def _env_flag(name: str, *, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    return str(raw).strip().casefold() in {"1", "true", "yes", "on"}


def webauthn_registration_enabled() -> bool:
    """Honor EAOS_WEBAUTHN_REGISTRATION_ENABLED (default false; PHX-G160)."""

    return _env_flag("EAOS_WEBAUTHN_REGISTRATION_ENABLED", default=False)


def webauthn_rp_id() -> str | None:
    value = (os.environ.get("EAOS_WEBAUTHN_RP_ID") or "").strip()
    return value or None


def webauthn_origin() -> str | None:
    value = (os.environ.get("EAOS_WEBAUTHN_ORIGIN") or "").strip()
    return value or None


def webauthn_rp_name() -> str:
    value = (os.environ.get("EAOS_WEBAUTHN_RP_NAME") or "").strip()
    return value or "NOVENTI EAOS"


def webauthn_rp_configured() -> bool:
    return webauthn_rp_id() is not None and webauthn_origin() is not None


def webauthn_live_mint_ready() -> bool:
    return webauthn_registration_enabled() and webauthn_rp_configured()


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def _purge_expired_challenges(now: float | None = None) -> None:
    cutoff = (now if now is not None else time.time()) - _CHALLENGE_TTL_SECONDS
    expired = [key for key, meta in _challenges.items() if float(meta["created_at"]) < cutoff]
    for key in expired:
        _challenges.pop(key, None)


def clear_webauthn_challenges() -> None:
    """Test helper — drop in-memory ceremony challenges."""

    with _challenge_lock:
        _challenges.clear()


def raise_webauthn_registration_disabled(
    *,
    ceremony_step: CeremonyStep,
) -> None:
    """Raise the canonical 503 when registration env is off."""

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": GATEWAY_WEBAUTHN_REGISTRATION_DISABLED,
            "message": _DISABLED_MESSAGE,
            "ceremony_step": ceremony_step,
            "registration_minted": False,
            "attestation_verified": False,
            "attestation_crypto_verified": False,
            "next_action": "none",
            "milestone": "PHX-G160",
        },
    )


def raise_webauthn_rp_config_required(
    *,
    ceremony_step: CeremonyStep,
) -> None:
    """Raise 503 when mint env is on but RP_ID/ORIGIN are missing."""

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "code": GATEWAY_WEBAUTHN_RP_CONFIG_REQUIRED,
            "message": _RP_CONFIG_MESSAGE,
            "ceremony_step": ceremony_step,
            "registration_minted": False,
            "attestation_verified": False,
            "attestation_crypto_verified": False,
            "next_action": "configure_rp_id_and_origin",
            "milestone": "PHX-G160",
        },
    )


def mint_registration_options(
    ctx: ExecutionContext,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Mint PublicKeyCredentialCreationOptions and store the challenge."""

    if not webauthn_registration_enabled():
        raise_webauthn_registration_disabled(ceremony_step="register_options")
    if not webauthn_rp_configured():
        raise_webauthn_rp_config_required(ceremony_step="register_options")

    payload = body or {}
    rp_id = webauthn_rp_id()
    assert rp_id is not None
    challenge = secrets.token_bytes(32)
    challenge_b64 = _b64url(challenge)
    user_id = str(ctx.subject_id)
    user_name = str(payload.get("user_name") or user_id)
    display_name = str(payload.get("user_display_name") or user_name)

    with _challenge_lock:
        _purge_expired_challenges()
        _challenges[challenge_b64] = {
            "created_at": time.time(),
            "tenant_id": str(ctx.tenant_id),
            "subject_id": str(ctx.subject_id),
            "rp_id": rp_id,
            "origin": webauthn_origin(),
        }

    return {
        "ceremony_step": "register_options",
        "registration_minted": False,
        "attestation_verified": False,
        "attestation_crypto_verified": False,
        "attestation_mode": "challenge_bound",
        "milestone": "PHX-G160",
        "publicKey": {
            "rp": {"id": rp_id, "name": webauthn_rp_name()},
            "user": {
                "id": _b64url(user_id.encode("utf-8")),
                "name": user_name,
                "displayName": display_name,
            },
            "challenge": challenge_b64,
            "pubKeyCredParams": [
                {"type": "public-key", "alg": -7},
                {"type": "public-key", "alg": -257},
            ],
            "timeout": 60000,
            "attestation": "none",
            "authenticatorSelection": {
                "residentKey": "preferred",
                "userVerification": "preferred",
            },
        },
    }


def verify_and_mint_registration(
    ctx: ExecutionContext,
    identity: IdentityGatewayService,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Challenge-bound verify → Identity.BindCredential (kind=webauthn)."""

    if not webauthn_registration_enabled():
        raise_webauthn_registration_disabled(ceremony_step="register_verify")
    if not webauthn_rp_configured():
        raise_webauthn_rp_config_required(ceremony_step="register_verify")

    payload = body or {}
    credential = payload.get("credential") if isinstance(payload.get("credential"), dict) else payload
    if not isinstance(credential, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": GATEWAY_WEBAUTHN_ATTESTATION_INVALID,
                "message": "credential object is required",
                "ceremony_step": "register_verify",
            },
        )

    response = credential.get("response")
    if not isinstance(response, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": GATEWAY_WEBAUTHN_ATTESTATION_INVALID,
                "message": "credential.response is required",
                "ceremony_step": "register_verify",
            },
        )

    client_data_b64 = str(response.get("clientDataJSON") or "").strip()
    attestation_b64 = str(response.get("attestationObject") or "").strip()
    credential_id = str(credential.get("id") or credential.get("rawId") or "").strip()
    if not client_data_b64 or not attestation_b64 or not credential_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": GATEWAY_WEBAUTHN_ATTESTATION_INVALID,
                "message": "id, clientDataJSON, and attestationObject are required",
                "ceremony_step": "register_verify",
            },
        )

    try:
        client_data = json.loads(_b64url_decode(client_data_b64).decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": GATEWAY_WEBAUTHN_ATTESTATION_INVALID,
                "message": "clientDataJSON must be base64url JSON",
                "ceremony_step": "register_verify",
            },
        ) from exc

    if not isinstance(client_data, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": GATEWAY_WEBAUTHN_ATTESTATION_INVALID,
                "message": "clientDataJSON must be an object",
                "ceremony_step": "register_verify",
            },
        )

    if client_data.get("type") != "webauthn.create":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": GATEWAY_WEBAUTHN_CHALLENGE_INVALID,
                "message": "clientDataJSON.type must be webauthn.create",
                "ceremony_step": "register_verify",
            },
        )

    expected_origin = webauthn_origin()
    if client_data.get("origin") != expected_origin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": GATEWAY_WEBAUTHN_CHALLENGE_INVALID,
                "message": "clientDataJSON.origin does not match EAOS_WEBAUTHN_ORIGIN",
                "ceremony_step": "register_verify",
            },
        )

    challenge_b64 = str(client_data.get("challenge") or "").strip()
    with _challenge_lock:
        _purge_expired_challenges()
        meta = _challenges.pop(challenge_b64, None)

    if meta is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": GATEWAY_WEBAUTHN_CHALLENGE_INVALID,
                "message": "challenge is unknown or expired",
                "ceremony_step": "register_verify",
            },
        )

    if meta["subject_id"] != str(ctx.subject_id) or meta["tenant_id"] != str(ctx.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": GATEWAY_WEBAUTHN_CHALLENGE_INVALID,
                "message": "challenge was issued for a different subject/tenant",
                "ceremony_step": "register_verify",
            },
        )

    # Opaque attestation presence check — full statement crypto is Explicit Out.
    try:
        attestation_bytes = _b64url_decode(attestation_b64)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": GATEWAY_WEBAUTHN_ATTESTATION_INVALID,
                "message": "attestationObject must be base64url",
                "ceremony_step": "register_verify",
            },
        ) from exc
    if len(attestation_bytes) < 16:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": GATEWAY_WEBAUTHN_ATTESTATION_INVALID,
                "message": "attestationObject is too short",
                "ceremony_step": "register_verify",
            },
        )

    attestation_digest = hashlib.sha256(attestation_bytes).hexdigest()
    secret_handle = f"webauthn:cred:{credential_id}:att:{attestation_digest[:32]}"

    result = identity.bind_credential(
        ctx,
        subject_id=UUID(str(ctx.subject_id)),
        credential_kind="webauthn",
        secret_handle=secret_handle,
    )
    raise_for_result(result)
    assert result.data is not None

    return {
        "ceremony_step": "register_verify",
        "registration_minted": True,
        "attestation_verified": True,
        "attestation_crypto_verified": False,
        "attestation_mode": "challenge_bound",
        "credential_id": str(result.data),
        "credential_kind": "webauthn",
        "audit_id": result.audit_id,
        "next_action": "none",
        "milestone": "PHX-G160",
    }
