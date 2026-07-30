"""PHX-G214 OpenAPI OIDC MFA enrollment details honesty contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from api.gateway.oidc_mfa_enrollment import mfa_enrollment_detail_fields
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "docs" / "api"
AUTH = API / "auth.openapi.yaml"
OPS = API / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g214_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0233-openapi-oidc-mfa-enrollment-details-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G214_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G214_ARCHITECTURE_GATE.md").is_file()

def test_g214_auth_mfa_enrollment_url_documented() -> None:
    spec = _load(AUTH)
    assert spec["info"]["version"].startswith("1.3.")
    schemas = spec["components"]["schemas"]
    for name in ("OidcAmrRequiredDetails", "OidcAcrRequiredDetails"):
        prop = schemas[name]["properties"]["mfa_enrollment_url"]
        assert prop["type"] == "string"
        assert prop.get("format") == "uri"
    details = schemas["ErrorResponse"]["properties"]["details"]
    # G214 documented on named schemas; G218 composes them via anyOf $ref.
    refs = {
        item.get("$ref", "").rsplit("/", 1)[-1]
        for item in (details.get("anyOf") or [])
        if isinstance(item, dict)
    }
    assert "OidcAmrRequiredDetails" in refs and "OidcAcrRequiredDetails" in refs

def test_g214_live_helper_keys_match_schema() -> None:
    # Without env URL the helper returns {}; with URL it returns the documented key.
    empty = mfa_enrollment_detail_fields()
    assert empty == {} or set(empty) <= {"mfa_enrollment_url"}

def test_g214_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g214" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g214_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U087" in ledger
    assert "PHX-G2" in tip and "PHX-G2" in manifest and "PHX-G2" in status
