"""PHX-G270 OpenAPI Knowledge entity/provenance schemas closed honesty."""

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

def test_g270_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0289-openapi-knowledge-entity-provenance-schemas-closed.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G270_ACCEPTANCE.md").is_file()

def test_g270_knowledge_schemas_closed() -> None:
    know = _load(API / "knowledge.openapi.yaml")
    assert know["info"]["version"].startswith("1.0.")
    schemas = know["components"]["schemas"]
    for name in ("KnowledgeEntity", "ProvenanceRecord"):
        assert schemas[name].get("additionalProperties") is False, name
    assert schemas["KnowledgeEntity"]["properties"]["attributes"].get(
        "additionalProperties"
    ) is True
    details = schemas["ProvenanceRecord"]["properties"]["details"]
    # details may be free-form object or anyOf including free-form object
    if details.get("additionalProperties") is True:
        pass
    else:
        any_of = details.get("anyOf") or []
        assert any(
            isinstance(item, dict) and item.get("additionalProperties") is True
            for item in any_of
        ), details

def test_g270_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert (
        posture["t0188_status"]
        .startswith("mount_parity_complete")
    )
    assert "g270" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g270_baseline() -> None:
    assert sdk_version == "0.2.5"
    assert_current_baseline()
    assert "DAL-U143" in (
        ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
    ).read_text(encoding="utf-8")
