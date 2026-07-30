"""PHX-G288 OpenAPI outer-close regression guard honesty."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "docs" / "api"
OPS = API / "ops.openapi.yaml"

# Intentional residual / free-form named outers — do NOT invent closes.
INTENTIONAL_OPEN: set[tuple[str, str]] = {
    ("auth.openapi.yaml", "WebauthnAuthenticatorAttestationResponse"),
    ("auth.openapi.yaml", "WebauthnPublicKeyCredential"),
    ("auth.openapi.yaml", "WebauthnRegisterVerifyRequest"),
    ("platform.openapi.yaml", "IdpJwksKey"),
    ("platform.openapi.yaml", "IdpJwksDocument"),
    ("ops.openapi.yaml", "ContextEchoRequest"),
}

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g288_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0307-openapi-outer-close-regression-guard.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G288_ACCEPTANCE.md").is_file()

def test_g288_named_outers_closed_or_allowlisted() -> None:
    seen_open: set[tuple[str, str]] = set()
    for path in sorted(API.glob("*.openapi.yaml")):
        schemas = _load(path).get("components", {}).get("schemas", {})
        for name, schema in schemas.items():
            if not isinstance(schema, dict):
                continue
            if schema.get("type") != "object":
                continue
            if any(k in schema for k in ("allOf", "anyOf", "oneOf", "$ref")):
                continue
            key = (path.name, name)
            ap = schema.get("additionalProperties")
            if ap is True:
                if name == "ValidationErrorItem":
                    continue
                assert key in INTENTIONAL_OPEN, f"unexpected open outer {key}"
                seen_open.add(key)
            else:
                assert ap is False, f"missing/closed AP on {key}: {ap!r}"
    assert seen_open == INTENTIONAL_OPEN

def test_g288_context_echo_request_named() -> None:
    ops = _load(OPS)
    schema = ops["components"]["schemas"]["ContextEchoRequest"]
    assert schema.get("additionalProperties") is True
    ref = (
        ops["paths"]["/context/echo"]["post"]["requestBody"]["content"][
            "application/json"
        ]["schema"].get("$ref", "")
    )
    assert ref.endswith("/ContextEchoRequest")

def test_g288_ops_tip_parity() -> None:
    posture = openapi_inventory_product_posture()
    ops = _load(OPS)
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert posture["milestone"] == "PHX-G288"
    assert props["milestone"].get("const") == "PHX-G288"
    assert posture["t0188_status"] == "mount_parity_complete_outer_close_regression_guard_honest"
    assert props["t0188_status"].get("const") == posture["t0188_status"]
    assert ops["info"]["version"] == "1.0.69"
    assert "g288" in " ".join(posture["fail_closed_reasons"]).casefold()
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"] == "PHX-G288"
    assert posture["full_openapi_http_complete"] is False

def test_g288_baseline() -> None:
    assert sdk_version == "0.2.5"
    assert_current_baseline()
    assert "DAL-U161" in (
        ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
    ).read_text(encoding="utf-8")
