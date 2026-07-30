"""PHX-G269 Terminal OpenAPI inventory Event envelope status deepen."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]


def test_g269_terminal_ui_wired() -> None:
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    assert "event_envelope_dead_letter_schemas_closed" in js
    assert "Event envelope/dead-letter schemas closed" in js
    assert "G28" in html
    assert (ROOT / "docs" / "project" / "PHX-G269_ACCEPTANCE.md").is_file()
    assert "DAL-U142" in (
        ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
    ).read_text(encoding="utf-8")
    tip = (ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md").read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    assert "PHX-G269" in tip and "PHX-G269" in manifest
    assert sdk_version == "0.2.5"
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")
