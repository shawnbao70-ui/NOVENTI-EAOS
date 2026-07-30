"""Normative PHX-G131/G132 Auth OpenAPI contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT / "docs" / "api" / "auth.openapi.yaml"


def _spec() -> dict[str, Any]:
    loaded = yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _resolve_ref(spec: dict[str, Any], ref: str) -> Any:
    assert ref.startswith("#/")
    value: Any = spec
    for segment in ref[2:].split("/"):
        value = value[segment]
    return value


def _walk(value: Any):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def test_auth_openapi_is_versioned_and_complete() -> None:
    spec = _spec()
    assert spec["openapi"] == "3.1.0"
    assert spec["servers"] == [{"url": "/v1"}]
    assert spec["security"] == []
    assert {
        "/auth/oidc/status",
        "/auth/idp/status",
        "/auth/jwt/status",
        "/auth/oidc/providers",
        "/auth/oidc/mfa-enrollment",
        "/auth/oidc/login",
        "/auth/oidc/callback",
        "/auth/oidc/refresh",
        "/auth/oidc/logout",
        "/auth/webauthn/register/options",
        "/auth/webauthn/register/verify",
    } <= set(spec["paths"])
    assert "/auth/webauthn/register" not in spec["paths"]
    assert spec["info"]["version"] == "1.3.27"


def test_auth_openapi_references_resolve() -> None:
    spec = _spec()
    for node in _walk(spec):
        ref = node.get("$ref")
        if ref is not None:
            _resolve_ref(spec, ref)


def test_auth_status_operations_are_public_and_desensitized() -> None:
    spec = _spec()
    expected = {
        "/auth/oidc/status": "OidcStatusEnvelope",
        "/auth/idp/status": "IdpStatusEnvelope",
        "/auth/jwt/status": "JwtStatusEnvelope",
    }
    for path, envelope in expected.items():
        operation = spec["paths"][path]["get"]
        assert operation.get("security") == []
        assert operation.get("operationId")
        schema_ref = operation["responses"]["200"]["content"]["application/json"][
            "schema"
        ]["$ref"]
        assert schema_ref.endswith(envelope)
