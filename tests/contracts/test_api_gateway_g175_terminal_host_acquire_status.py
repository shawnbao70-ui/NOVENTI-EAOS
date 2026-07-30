"""PHX-G175 Terminal host-acquire status surface contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_g175_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0194-terminal-host-acquire-status-surface.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G175_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G175_ARCHITECTURE_GATE.md").is_file()


def test_g175_terminal_ui_wired() -> None:
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    assert "function loadHostAcquireStatus" in js
    assert "PHX-G175" in js
    assert 'id="btnAdminHostAcquireStatus"' in html
    assert 'id="hostAcquireStatus"' in html
    assert "loadHostAcquireStatus({ quiet: true })" in js


def test_g175_ledger_tip_manifest() -> None:
    ledger = (ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md").read_text(
        encoding="utf-8"
    )
    tip = (ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md").read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    status = (ROOT / "docs" / "project" / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "DAL-U048" in ledger
    assert "PHX-G175" in tip
    assert "PHX-G175" in manifest
    assert "PHX-G175" in status or "PHX-G18" in status
