"""Foundation OIDC login product posture (PHX-G147 / ADR-0166).

Read-only helper. Composes the existing Authorization Code surface
(G40/G61/G132). Does not introduce a new auth protocol or ceremony.
Unconfigured OIDC remains fail-closed (503 on login/callback).
"""

from __future__ import annotations

from typing import Any

# Canonical Gateway paths for the Auth Code product (OpenAPI /auth prefix).
_LIVE_ROUTES = (
    "/auth/oidc/status",
    "/auth/oidc/login",
    "/auth/oidc/callback",
    "/auth/oidc/providers",
    "/auth/oidc/refresh",
    "/auth/oidc/logout",
)

_FAIL_CLOSED_REASONS = (
    "oidc_unconfigured_returns_503",
    "authorization_code_requires_issuer_client_id_redirect",
    "no_new_auth_protocol_in_this_slice",
    "webauthn_ceremony_role_grant_payment_brain_twin_remain_closed",
)


def _resolve_authorization_code_enabled() -> bool:
    from api.gateway.oidc import OidcSettings

    return bool(OidcSettings.from_env().enabled)


def oidc_login_product_posture(
    *,
    authorization_code_enabled: bool | None = None,
) -> dict[str, Any]:
    """Return desensitized Foundation OIDC login product posture."""

    enabled = (
        bool(authorization_code_enabled)
        if authorization_code_enabled is not None
        else _resolve_authorization_code_enabled()
    )
    return {
        "surface": "foundation_oidc_login_product",
        "milestone": "PHX-G147",
        "protocol": "oauth2_authorization_code",
        "authorization_code_enabled": enabled,
        "live_routes": list(_LIVE_ROUTES),
        "fail_closed_when_unconfigured": True,
        "fail_closed": not enabled,
        "fail_closed_reasons": list(_FAIL_CLOSED_REASONS),
    }
