"""PHX-G210 OpenAPI OIDC details per-code shapes honesty contracts."""

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
AUTH = API / "auth.openapi.yaml"
OPS = API / "ops.openapi.yaml"

OIDC_SCHEMAS = (
    "OidcRequiredClaimMissingDetails",
    "OidcRoleRequiredDetails",
    "OidcAmrRequiredDetails",
    "OidcAcrRequiredDetails",
)

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g210_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0229-openapi-oidc-details-code-shapes-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G210_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G210_ARCHITECTURE_GATE.md").is_file()

def test_g210_auth_oidc_details_schemas() -> None:
    spec = _load(AUTH)
    assert spec["info"]["version"].startswith("1.3.")
    schemas = spec["components"]["schemas"]
    for name in OIDC_SCHEMAS:
        assert name in schemas
    claim = schemas["OidcRequiredClaimMissingDetails"]
    assert claim["required"] == ["claims"]
    assert claim.get("additionalProperties") is False
    role = schemas["OidcRoleRequiredDetails"]
    assert set(role["required"]) == {"role_claim", "mapped_roles"}
    amr = schemas["OidcAmrRequiredDetails"]
    assert set(amr["required"]) == {"required_amr", "present_amr"}
    assert amr.get("additionalProperties") is False  # closed G244
    acr = schemas["OidcAcrRequiredDetails"]
    assert "required_acr" in acr["required"]
    details = schemas["ErrorResponse"]["properties"]["details"]
    refs = {
        item.get("$ref", "").rsplit("/", 1)[-1]
        for item in (details.get("anyOf") or [])
        if isinstance(item, dict)
    }
    for name in (
        "OidcRequiredClaimMissingDetails",
        "OidcRoleRequiredDetails",
        "OidcAmrRequiredDetails",
        "OidcAcrRequiredDetails",
    ):
        assert name in refs or name in schemas
    # Known keys remain on named schemas (G210); G218 may move flat catalog to anyOf.
    for name, keys in (
        ("OidcRequiredClaimMissingDetails", ("claims",)),
        ("OidcRoleRequiredDetails", ("role_claim", "mapped_roles")),
        ("OidcAmrRequiredDetails", ("required_amr", "present_amr")),
        ("OidcAcrRequiredDetails", ("required_acr", "present_acr")),
    ):
        props = schemas[name]["properties"]
        for key in keys:
            assert key in props

def test_g210_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g210" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g210_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U083" in ledger
    assert ("PHX-G210" in tip or "PHX-G211" in tip or "PHX-G212" in tip) and (
        "PHX-G210" in manifest or "PHX-G211" in manifest or "PHX-G212" in manifest
    ) and ("PHX-G2" in status)