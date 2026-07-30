"""PHX-G395 Terminal event/outbox status strip contracts."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from api.gateway import create_app

ROOT = Path(__file__).resolve().parents[2]
TERMINAL_JS = ROOT / "smart_terminal" / "ui" / "app.js"
TERMINAL_HTML = ROOT / "smart_terminal" / "ui" / "index.html"


def test_g395_event_status_and_catalog_live_for_strip() -> None:
    client = TestClient(create_app())
    status = client.get("/v1/events/status").json()["data"]
    assert status["background_worker_daemon"] is False
    assert status["fail_closed_without_grant"] is True
    catalog = client.get("/v1/events/catalog").json()["data"]
    assert catalog["catalog_id"] == "EVT-COMMERCIAL-001"
    assert len(catalog["events"]) >= 4


def test_g395_terminal_event_outbox_strip_wired() -> None:
    js = TERMINAL_JS.read_text(encoding="utf-8")
    html = TERMINAL_HTML.read_text(encoding="utf-8")
    assert "async function loadEventOutboxStatus" in js
    assert 'bind("btnAdminEventOutboxStatus"' in js
    assert 'id="btnAdminEventOutboxStatus"' in html
    assert 'id="eventOutboxStatus"' in html
    assert "PHX-G395" in js
