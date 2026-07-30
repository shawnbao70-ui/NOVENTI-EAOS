"""Normative PHX-G135 Platform OpenAPI contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT / "docs" / "api" / "platform.openapi.yaml"


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


def test_platform_openapi_is_versioned_and_complete() -> None:
    spec = _spec()
    assert spec["openapi"] == "3.1.0"
    assert spec["servers"] == [{"url": "/v1"}]
    assert spec["security"] == [{"bearerAuth": []}]
    assert spec["info"]["version"] == "1.0.13"
    required = {
        "/platform/roles",
        "/platform/roles/{roleId}/disable",
        "/platform/idp/issuers",
        "/platform/idp/issuers/{issuerId}/disable",
        "/platform/idp/discovery/sync",
        "/platform/idp/federation/matrix",
        "/platform/idp/federation/tenants/{tenantId}/bindings",
        "/platform/idp/federation/bindings/{bindingId}/unbind",
        "/platform/idp/federation/bindings/{bindingId}/priority",
        "/platform/digital-employee/status",
        "/platform/industry-package/status",
        "/platform/ai-workforce/status",
    }
    assert required <= set(spec["paths"])
    description = spec["info"].get("description") or ""
    assert "Role→grant" in description or "Role->grant" in description


def test_platform_openapi_references_resolve() -> None:
    spec = _spec()
    for node in _walk(spec):
        ref = node.get("$ref")
        if ref is not None:
            _resolve_ref(spec, ref)


def test_platform_idp_responses_never_expose_jwks_plaintext() -> None:
    spec = _spec()
    issuer = _resolve_ref(spec, "#/components/schemas/IdpIssuer")
    props = set(issuer["properties"])
    assert "has_jwks_json" in props
    assert "jwks_json" not in props
    body = OPENAPI_PATH.read_text(encoding="utf-8")
    assert "jwks_json" in body  # accepted on write only
    # Response schema block must not list jwks_json as a returned property
    assert '"jwks_json"' not in yaml.dump(issuer)
