"""PHX-G184 Terminal OpenAPI inventory posture deepen contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]

def test_g184_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0203-terminal-openapi-inventory-posture-deepen.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G184_ACCEPTANCE.md").is_file()

def test_g184_terminal_ui_wired() -> None:
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    assert ("PHX-G28" in js or "OpenAPI inventory posture" in js)
    assert "t0188_status" in js
    assert "product.milestone" in js
    assert 'id="btnOpenapiInventoryRefresh"' in html
    assert "btnOpenapiInventoryRefresh" in js

def test_g184_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U057" in ledger
    assert "PHX-G184" in tip
    assert "PHX-G184" in manifest
    assert "PHX-G184" in status or "PHX-G18" in status
