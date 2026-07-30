"""PHX-G240 OpenAPI WebAuthn PublicKeyCredentialCreationOptions named honesty."""

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

def test_g240_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0259-openapi-webauthn-public-key-creation-options-named-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G240_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G240_ARCHITECTURE_GATE.md").is_file()

def test_g240_public_key_creation_options_named() -> None:
    auth = _load(API / "auth.openapi.yaml")
    assert str(auth["info"]["version"]).startswith("1.3.")
    schemas = auth["components"]["schemas"]
    assert "PublicKeyCredentialCreationOptions" in schemas
    pk = schemas["PublicKeyCredentialCreationOptions"]
    assert pk.get("additionalProperties") is False
    assert set(pk["required"]) >= {
        "rp",
        "user",
        "challenge",
        "pubKeyCredParams",
        "timeout",
        "attestation",
        "authenticatorSelection",
    }
    resp = schemas["WebauthnRegisterOptionsResponse"]
    assert resp.get("additionalProperties") is False
    assert resp["properties"]["publicKey"]["$ref"].endswith(
        "/PublicKeyCredentialCreationOptions"
    )
    req = schemas["WebauthnRegisterOptionsRequest"]
    assert req.get("additionalProperties") is False
    verify = schemas["WebauthnRegisterVerifyRequest"]
    assert verify["properties"]["credential"]["$ref"].endswith("/WebauthnPublicKeyCredential")
    assert verify["properties"]["response"]["$ref"].endswith(
        "/WebauthnAuthenticatorAttestationResponse"
    )

def test_g240_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert (
        posture["t0188_status"]
        .startswith("mount_parity_complete")
    )
    assert "g240" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert str(props["milestone"].get("const", "")).startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g240_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U113" in ledger
    assert ("PHX-G240" in tip or "PHX-G241" in tip) and (
        "PHX-G240" in manifest or "PHX-G241" in manifest
    ) and ("PHX-G2" in status)
