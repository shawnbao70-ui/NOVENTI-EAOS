"""PHX-G242 OpenAPI WebAuthn RegisterVerifyResponse closed honesty."""

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

def test_g242_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0261-openapi-webauthn-register-verify-response-closed.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G242_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G242_ARCHITECTURE_GATE.md").is_file()

def test_g242_verify_response_closed() -> None:
    auth = _load(API / "auth.openapi.yaml")
    assert str(auth["info"]["version"]).startswith("1.3.")
    resp = auth["components"]["schemas"]["WebauthnRegisterVerifyResponse"]
    assert resp.get("additionalProperties") is False
    assert resp["properties"]["attestation_verified"].get("const") is True
    assert resp["properties"]["next_action"].get("const") == "none"
    assert resp["properties"]["attestation_crypto_verified"].get("const") is False

def test_g242_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert (
        posture["t0188_status"]
        .startswith("mount_parity_complete")
    )
    assert "g242" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert str(props["milestone"].get("const", "")).startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g242_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U115" in ledger
    assert ("PHX-G242" in tip or "PHX-G243" in tip) and (
        "PHX-G242" in manifest or "PHX-G243" in manifest
    ) and ("PHX-G2" in status)
