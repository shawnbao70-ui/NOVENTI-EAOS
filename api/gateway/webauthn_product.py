"""Foundation MFA / WebAuthn product posture (PHX-G145 → G160).

Read-only helper. Surfaces whether env-gated live registration mint is
enabled (PHX-G160). Default remains disabled. Live enroll via IdP MFA
redirect (G89/G134) remains available independently. Role→grant mint /
payment / Brain execute / Twin authorize stay closed.
"""

from __future__ import annotations

from typing import Any

from api.gateway.oidc_mfa_enrollment import (
    oidc_mfa_enrollment_enabled,
    oidc_mfa_enrollment_url,
)
from api.gateway.webauthn_ceremony import (
    WEBAUTHN_CEREMONY_ROUTES,
    webauthn_live_mint_ready,
    webauthn_registration_enabled,
    webauthn_rp_configured,
)

# Canonical Gateway path for IdP enrollment redirect (OpenAPI /auth prefix).
_MFA_ENROLLMENT_PATH = "/auth/oidc/mfa-enrollment"


def webauthn_product_posture() -> dict[str, Any]:
    """Return desensitized Foundation MFA/WebAuthn product posture."""

    enabled = webauthn_registration_enabled()
    rp_ok = webauthn_rp_configured()
    mint_ready = webauthn_live_mint_ready()
    reasons: list[str] = []
    if not enabled:
        reasons.append("webauthn_registration_enabled_default_false")
        reasons.append("enable_eaos_webauthn_registration_enabled_for_live_mint")
    elif not rp_ok:
        reasons.append("webauthn_rp_id_or_origin_missing")
    else:
        reasons.append("webauthn_live_mint_challenge_bound_g160")
        reasons.append("attestation_crypto_verify_still_deferred")
    reasons.extend(
        [
            "auth_webauthn_register_single_path_absent",
            "role_grant_payment_brain_twin_remain_closed",
        ]
    )
    return {
        "surface": "foundation_mfa_webauthn_product",
        "milestone": "PHX-G160",
        "webauthn_registration_enabled": enabled,
        "registration_enabled": enabled,
        "webauthn_rp_configured": rp_ok,
        "webauthn_live_mint_ready": mint_ready,
        "registration_routes": list(WEBAUTHN_CEREMONY_ROUTES),
        "ceremony_stub_observability": True,
        "registration_default_off": True,
        "attestation_crypto_verified": False,
        "attestation_mode": "challenge_bound" if mint_ready else "disabled",
        "mfa_enrollment_path": _MFA_ENROLLMENT_PATH,
        "mfa_enrollment_enabled": oidc_mfa_enrollment_enabled(),
        "mfa_enrollment_url": oidc_mfa_enrollment_url(),
        "live_enroll_path": (
            "webauthn_challenge_bound_mint_g160" if mint_ready else "idp_redirect_g89_g134"
        ),
        "fail_closed_reasons": reasons,
    }
