"""PHX-G225 Terminal OpenAPI inventory named success envelopes status deepen."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]

def test_g225_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0244-terminal-openapi-inventory-named-success-envelopes-status-deepen.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G225_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G225_ARCHITECTURE_GATE.md").is_file()

def test_g225_terminal_ui_wired() -> None:
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    assert "function loadOpenapiInventoryProductPosture" in js
    assert ("PHX-G28" in js or "OpenAPI inventory posture" in js)
    assert "named_success_envelopes" in js
    assert "named success envelopes honest" in js
    assert 'id="btnAdminOpenapiInventoryStatus"' in html
    assert "G28" in html
    assert "loadOpenapiInventoryProductPosture({ quiet: true })" in js

def test_g225_inventory_still_semantic_partial() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert posture["milestone"].startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["full_openapi_http_complete"] is False
    assert meta["milestone"].startswith("PHX-G")

def test_g225_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U098" in ledger
    assert "PHX-G2" in tip and "PHX-G2" in manifest and "PHX-G2" in status
