"""PHX-G133 OIDC Refresh / Logout OpenAPI contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
AUTH_OPENAPI = ROOT / "docs" / "api" / "auth.openapi.yaml"


def _spec() -> dict[str, Any]:
    loaded = yaml.safe_load(AUTH_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _resolve_ref(spec: dict[str, Any], ref: str) -> Any:
    assert ref.startswith("#/")
    value: Any = spec
    for segment in ref[2:].split("/"):
        value = value[segment]
    return value


def test_auth_openapi_documents_oidc_refresh_logout() -> None:
    spec = _spec()
    assert spec["info"]["version"].startswith("1.")
    assert "bearerAuth" in spec["components"]["securitySchemes"]
    for path in ("/auth/oidc/refresh", "/auth/oidc/logout"):
        operation = spec["paths"][path]["post"]
        assert operation.get("security") == [{"bearerAuth": []}]
        assert operation.get("operationId")


def test_oidc_refresh_logout_schemas_are_desensitized() -> None:
    spec = _spec()
    refresh = spec["paths"]["/auth/oidc/refresh"]["post"]
    refresh_ref = refresh["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ]
    assert refresh_ref.endswith("OidcTokenEnvelope")
    envelope = _resolve_ref(spec, refresh_ref)
    payload = _resolve_ref(spec, envelope["properties"]["data"]["$ref"])
    assert "refresh_token" not in payload["properties"]
    assert "client_secret" not in payload["properties"]

    logout = spec["paths"]["/auth/oidc/logout"]["post"]
    logout_ref = logout["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ]
    logout_envelope = _resolve_ref(spec, logout_ref)
    logout_payload = _resolve_ref(
        spec, logout_envelope["properties"]["data"]["$ref"]
    )
    props = set(logout_payload["properties"])
    assert {"revoked", "jti", "rp_logout"} <= props
    assert "refresh_token" not in props
    assert "id_token" not in props
