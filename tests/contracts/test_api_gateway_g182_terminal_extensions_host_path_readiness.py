"""PHX-G182 Terminal Extensions demo host-path readiness contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

from fastapi.testclient import TestClient

from api.gateway.demo import create_demo_app
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]

def test_g182_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0201-terminal-extensions-host-path-readiness.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G182_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G182_ARCHITECTURE_GATE.md").is_file()

def test_g182_terminal_ui_wired() -> None:
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    assert "function loadExtHostPathReadiness" in js
    assert "function extAcquireListingToHost" in js
    assert "PHX-G182" in js
    assert 'id="btnExtHostAcquire"' in html
    assert 'id="extHostPathReadiness"' in html
    assert 'id="extHostActions"' in html
    assert "loadExtHostPathReadiness({ quiet: true })" in js

def test_g182_demo_bootstrap_milestone_and_host_actions() -> None:
    client = TestClient(create_demo_app())
    response = client.get("/v1/demo/bootstrap")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["available"] is True
    assert data["milestone"] == "PHX-G182"
    assert data.get("listing_id")
    assert data.get("extension_id")
    assert data.get("host_actions") == ["panel.render"]

def test_g182_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U055" in ledger
    assert "PHX-G182" in tip
    assert "PHX-G182" in manifest
    assert "PHX-G182" in status or "PHX-G18" in status
