"""PHX-G183 Terminal payment-clearing status surface contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]

def test_g183_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0202-terminal-payment-clearing-status-surface.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G183_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G183_ARCHITECTURE_GATE.md").is_file()

def test_g183_terminal_ui_wired() -> None:
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    assert "function loadPaymentClearingStatus" in js
    assert "PHX-G183" in js
    assert 'id="btnAdminPaymentClearingStatus"' in html
    assert 'id="paymentClearingStatus"' in html
    assert "loadPaymentClearingStatus({ quiet: true })" in js
    assert "external_psp" in js

def test_g183_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U056" in ledger
    assert "PHX-G183" in tip
    assert "PHX-G183" in manifest
    assert "PHX-G183" in status or "PHX-G18" in status
