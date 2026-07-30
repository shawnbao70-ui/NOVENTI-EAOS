"""Production authentication fail-closed gate (PHX-G412).

When ``EAOS_ENV`` / ``EAOS_PROFILE`` is ``production`` (or ``prod``), the gateway
refuses to start with insecure auth defaults:

- ``EAOS_REQUIRE_JWT`` must be enabled
- ``EAOS_ALLOW_DEV_CONTEXT_HEADERS`` must be disabled
- ``EAOS_JWT_SECRET`` must be non-empty

Dev / unset profiles remain available for local contracts.
"""

from __future__ import annotations

import os

from api.gateway.auth_jwt import JwtSettings


class ProductionAuthError(RuntimeError):
    """Raised when production profile has insecure authentication posture."""


def production_profile_active(environ: dict[str, str] | None = None) -> bool:
    env = environ if environ is not None else os.environ
    raw = (env.get("EAOS_ENV") or env.get("EAOS_PROFILE") or "").strip().casefold()
    return raw in {"production", "prod"}


def validate_production_auth(
    *,
    settings: JwtSettings | None = None,
    environ: dict[str, str] | None = None,
) -> None:
    if not production_profile_active(environ):
        return
    jwt = settings if settings is not None else JwtSettings.from_env()
    errors: list[str] = []
    if not jwt.require_jwt:
        errors.append("EAOS_REQUIRE_JWT must be enabled")
    if jwt.allow_dev_headers:
        errors.append("EAOS_ALLOW_DEV_CONTEXT_HEADERS must be disabled")
    if not jwt.secret:
        errors.append("EAOS_JWT_SECRET must be set")
    if errors:
        raise ProductionAuthError(
            "Production auth fail-closed: " + "; ".join(errors)
        )
