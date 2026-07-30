"""PHX-G266 OpenAPI AI AgentRun/MemoryEntry schemas closed honesty."""

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

def test_g266_docs_present() -> None:
    assert (
        ROOT / "docs" / "decisions" / "ADR-0285-openapi-ai-agent-memory-schemas-closed.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G266_ACCEPTANCE.md").is_file()

def test_g266_ai_schemas_closed() -> None:
    ai = _load(API / "ai.openapi.yaml")
    assert ai["info"]["version"].startswith("1.0.")
    schemas = ai["components"]["schemas"]
    for name in ("AgentRun", "MemoryEntry"):
        assert schemas[name].get("additionalProperties") is False, name
    assert schemas["MemoryEntry"]["properties"]["value"].get("additionalProperties") is True

def test_g266_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g266" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g266_baseline() -> None:
    assert sdk_version == "0.2.5"
    assert_current_baseline()
    assert "DAL-U139" in (
        ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
    ).read_text(encoding="utf-8")
