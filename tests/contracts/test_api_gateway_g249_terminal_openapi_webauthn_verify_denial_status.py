"""PHX-G249 Terminal OpenAPI inventory WebAuthn verify denial status deepen."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_g249_terminal_ui_wired() -> None:
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    assert "webauthn_verify_denial" in js
    assert "WebAuthn verify denial honest" in js
    assert "G28" in html
    assert (ROOT / "docs" / "project" / "PHX-G249_ACCEPTANCE.md").is_file()
