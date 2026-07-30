"""PHX-G195 OpenAPI RoleCatalogStatus source_counts field parity contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from api.gateway.role_catalog import build_role_catalog_status
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
PERMISSION = ROOT / "docs" / "api" / "permission.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g195_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0214-openapi-role-catalog-status-source-counts-field-parity.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G195_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G195_ARCHITECTURE_GATE.md").is_file()

def test_g195_role_catalog_source_counts_schema_matches_emit() -> None:
    spec = _load(PERMISSION)
    assert str(spec["info"]["version"]).startswith("1.1.")
    status_schema = spec["components"]["schemas"]["RoleCatalogStatus"]
    assert status_schema.get("additionalProperties") is False
    assert status_schema["properties"]["catalog_store"]["enum"] == ["process_memory"]
    assert status_schema["properties"]["source_counts"] == {
        "$ref": "#/components/schemas/RoleCatalogSourceCounts"
    }
    counts = spec["components"]["schemas"]["RoleCatalogSourceCounts"]
    assert counts.get("additionalProperties") is False
    required = set(counts["required"])
    assert required == {'catalog', 'oidc_map', 'grant_map'}
    emit = build_role_catalog_status()
    assert required <= set(emit["source_counts"])
    for key in required:
        assert key in counts["properties"]
        assert isinstance(emit["source_counts"][key], int)
    assert emit["catalog_store"] == "process_memory"

def test_g195_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g195" in " ".join(posture["fail_closed_reasons"]).casefold()

    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    assert (
        props["t0188_status"]["const"].startswith("mount_parity_complete")
    )
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g195_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U068" in ledger
    assert ("PHX-G195" in tip or "PHX-G196" in tip or "PHX-G197" in tip or "PHX-G20" in tip) and ("PHX-G195" in manifest or "PHX-G196" in manifest or "PHX-G197" in manifest or "PHX-G20" in manifest) and ("PHX-G2" in status)
