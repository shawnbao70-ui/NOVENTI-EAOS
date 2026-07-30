"""PHX-G192 OpenAPI Identity/Org/Knowledge status body field parity contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g192_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0211-openapi-identity-org-knowledge-status-body-field-parity.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G192_ACCEPTANCE.md").is_file()

def test_g192_status_schemas_match_runtime() -> None:
    cases = [
        ("identity", "/v1/identity/status", "FoundationStatusData"),
        ("organization", "/v1/organization/status", "FoundationStatusData"),
        # Knowledge status nest G293 sample-pack product (DAL-U235).
        ("knowledge", "/v1/knowledge/status", "KnowledgeStatusData"),
    ]
    client = TestClient(app)
    for name, route, schema_name in cases:
        spec = _load(ROOT / "docs" / "api" / f"{name}.openapi.yaml")
        assert str(spec["info"]["version"]).startswith("1.0.")
        schema = spec["components"]["schemas"][schema_name]
        assert schema.get("additionalProperties") is False
        assert schema["properties"]["writable"]["const"] is False
        data = client.get(route).json()["data"]
        assert set(schema["required"]) <= set(data)
        assert data["writable"] is False
        assert len(data["supported_surfaces"]) >= 1
        if name == "knowledge":
            assert data["sample_knowledge_pack_product"]["milestone"] == "PHX-G293"
            assert data["sample_knowledge_pack_product"]["crud"] is False

def test_g192_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g192" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    assert (
        ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"][
            "milestone"
        ]["const"].startswith("PHX-G")
    )

def test_g192_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U065" in ledger
    assert "PHX-G192" in tip and "PHX-G192" in manifest and ("PHX-G2" in status)
