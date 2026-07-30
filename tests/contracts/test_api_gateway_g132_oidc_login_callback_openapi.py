"""PHX-G132 OIDC Login / Callback OpenAPI contracts."""

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


def test_auth_openapi_documents_oidc_login_callback_providers() -> None:
    spec = _spec()
    assert spec["info"]["version"].startswith("1.")
    required = {
        "/auth/oidc/login",
        "/auth/oidc/callback",
        "/auth/oidc/providers",
    }
    assert required <= set(spec["paths"])
    for path in required:
        operation = spec["paths"][path]["get"]
        assert operation.get("security") == []
        assert operation.get("operationId")


def test_oidc_callback_json_token_schema_is_desensitized() -> None:
    spec = _spec()
    operation = spec["paths"]["/auth/oidc/callback"]["get"]
    schema_ref = operation["responses"]["200"]["content"]["application/json"]["schema"][
        "$ref"
    ]
    envelope = _resolve_ref(spec, schema_ref)
    payload = _resolve_ref(spec, envelope["properties"]["data"]["$ref"])
    props = set(payload["properties"])
    assert "access_token" in props
    assert "refresh_token" not in props
    assert "client_secret" not in props
    assert "id_token" not in props
    login = spec["paths"]["/auth/oidc/login"]["get"]
    assert "302" in login["responses"]
