"""PHX-G171 Terminal UuidResult dual-key client harden contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_g171_docs_present() -> None:
    assert (
        ROOT / "docs" / "decisions" / "ADR-0190-terminal-uuid-result-client-harden.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G171_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G171_ARCHITECTURE_GATE.md").is_file()


def test_g171_terminal_helper_wired() -> None:
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert "function uuidFromResult" in js
    assert "PHX-G171" in js
    assert "state.sessionId = uuidFromResult(data)" in js
    assert "state.intentId = uuidFromResult(data)" in js
    assert "state.previewId = uuidFromResult(data)" in js
    assert "state.extensionId = uuidFromResult(data)" in js


def test_g171_ledger_tip_manifest() -> None:
    ledger = (ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md").read_text(
        encoding="utf-8"
    )
    tip = (ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md").read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    status = (ROOT / "docs" / "project" / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "DAL-U044" in ledger
    assert "PHX-G171" in tip
    assert "PHX-G171" in manifest
    assert "PHX-G171" in status or "PHX-G18" in status
