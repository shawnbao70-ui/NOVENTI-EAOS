"""PHX-G246 OpenAPI IdP JWKS document named honesty."""

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

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g246_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0265-openapi-idp-jwks-document-named-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G246_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G246_ARCHITECTURE_GATE.md").is_file()

def test_g246_jwks_document_named() -> None:
    platform = _load(API / "platform.openapi.yaml")
    assert platform["info"]["version"].startswith("1.0.")
    schemas = platform["components"]["schemas"]
    assert "IdpJwksDocument" in schemas and "IdpJwksKey" in schemas
    doc = schemas["IdpJwksDocument"]
    key = schemas["IdpJwksKey"]
    assert doc.get("additionalProperties") is True  # RFC residual open
    assert key.get("additionalProperties") is True
    assert "keys" in doc["properties"]
    assert {"kty", "kid", "n", "e"} <= set(key["properties"])
    jwks = schemas["CreateIdpIssuerRequest"]["properties"]["jwks_json"]
    refs = {
        item.get("$ref", "").rsplit("/", 1)[-1]
        for item in (jwks.get("oneOf") or [])
        if isinstance(item, dict)
    }
    assert "IdpJwksDocument" in refs

def test_g246_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g246" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g246_ledger_tip_manifest_baseline() -> None:
    assert sdk_version == "0.2.5"
    assert_current_baseline()
    ledger = (ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md").read_text(
        encoding="utf-8"
    )
    tip = (ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md").read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    status = (ROOT / "docs" / "project" / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "DAL-U119" in ledger
    assert ("PHX-G246" in tip or "PHX-G247" in tip) and (
        "PHX-G246" in manifest or "PHX-G247" in manifest
    ) and ("PHX-G2" in status)
