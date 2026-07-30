"""PHX-G244 OpenAPI OIDC Amr/Acr details closed honesty."""

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

def test_g244_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0263-openapi-oidc-amr-acr-details-closed.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G244_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G244_ARCHITECTURE_GATE.md").is_file()

def test_g244_amr_acr_details_closed() -> None:
    auth = _load(API / "auth.openapi.yaml")
    assert str(auth["info"]["version"]).startswith("1.3.")
    schemas = auth["components"]["schemas"]
    amr = schemas["OidcAmrRequiredDetails"]
    acr = schemas["OidcAcrRequiredDetails"]
    assert amr.get("additionalProperties") is False
    assert acr.get("additionalProperties") is False
    assert set(amr["required"]) == {"required_amr", "present_amr"}
    assert "required_acr" in acr["required"]
    assert "mfa_enrollment_url" in amr["properties"]
    assert "mfa_enrollment_url" in acr["properties"]

def test_g244_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"] .startswith("mount_parity_complete")
    assert "g244" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert str(props["milestone"].get("const", "")).startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g244_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U117" in ledger
    assert ("PHX-G244" in tip or "PHX-G245" in tip) and (
        "PHX-G244" in manifest or "PHX-G245" in manifest
    ) and ("PHX-G2" in status)
