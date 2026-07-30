"""PHX-G278 softener wave3 + standing ops tip-parity guard."""

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

def test_g278_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0297-contract-softener-wave3-tip-parity-guard.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G278_ACCEPTANCE.md").is_file()

def test_g278_ops_tip_parity_guard() -> None:
    """Standing guard: ops OpenAPI milestone/t0188 consts must match live tip."""
    posture = openapi_inventory_product_posture()
    ops = _load(OPS)
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert posture["milestone"].startswith("PHX-G")
    assert str(props["milestone"].get("const", "")).startswith("PHX-G")
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert str(props["t0188_status"].get("const", "")).startswith("mount_parity_complete")
    assert ops["info"]["version"].startswith("1.0.")
    assert "g278" in " ".join(posture["fail_closed_reasons"]).casefold()
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"] == posture["milestone"]
    assert meta["t0188_status"] == posture["t0188_status"]

def test_g278_baseline() -> None:
    assert sdk_version == "0.2.5"
    assert_current_baseline()
    assert "DAL-U151" in (
        ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
    ).read_text(encoding="utf-8")
