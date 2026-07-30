"""Read-only multi-IdP / JWT status aggregation (PHX-G55/G56)."""

from __future__ import annotations

from typing import Any

from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import current_jwt_settings
from api.gateway.idp_registry import merge_registry_issuers, registry_status_view
from api.gateway.oidc import (
    discovery_registry_write_status,
    maybe_wire_discovery_jwks,
    maybe_write_discovery_to_registry,
    oidc_status,
)
from api.gateway.tenant_idp_federation import federation_status_view


def idp_status(*, jwt_settings: JwtSettings | None = None) -> dict[str, Any]:
    """Compose redacted OIDC + JWT issuer status for operators."""

    base = jwt_settings if jwt_settings is not None else current_jwt_settings()
    maybe_write_discovery_to_registry(raise_on_error=False)
    settings = merge_registry_issuers(maybe_wire_discovery_jwks(base))
    issuers = [
        {
            "issuer": binding.issuer,
            "jwks_url": binding.jwks_url,
            "has_jwks_json": bool(binding.jwks_json),
        }
        for binding in settings.issuers
    ]
    registry = registry_status_view()
    registry["discovery_write"] = discovery_registry_write_status()
    return {
        "writable": False,
        "config_source": "environment+registry",
        "oidc": oidc_status(),
        "jwt": {
            "multi_issuer": settings.multi_issuer,
            "issuer": settings.issuer,
            "audience": settings.audience,
            "has_secret": bool(settings.secret),
            "has_jwks_url": bool(settings.jwks_url),
            "has_jwks_json": bool(settings.jwks_json),
            "require_jwt": settings.require_jwt,
            "allow_dev_headers": settings.allow_dev_headers,
            "denylist_enabled": settings.denylist_enabled,
            "issuers": issuers,
        },
        "registry": registry,
        "federation": federation_status_view(),
    }
