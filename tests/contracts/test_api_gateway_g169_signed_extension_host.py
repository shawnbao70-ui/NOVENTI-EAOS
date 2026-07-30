"""PHX-G169 signed extension host productization contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_g169_docs_present() -> None:
    assert (
        ROOT / "docs" / "decisions" / "ADR-0188-signed-extension-host-productization.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G169_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G169_ARCHITECTURE_GATE.md").is_file()


def test_g169_terminal_hydrate_path() -> None:
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    assert "hydrateSignedExtensionHost" in js
    assert "PHX-G169" in js
    assert 'id="btnExtHydrate"' in html
    assert 'id="extHostStatus"' in html
    assert "Hydrate signed" in html
    # Closed: no Marketplace arbitrary remote script loader.
    assert "eval(" not in js
    assert "importScripts(" not in js


def test_g169_ledger_tip_manifest() -> None:
    ledger = (ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md").read_text(
        encoding="utf-8"
    )
    tip = (ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md").read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    status = (ROOT / "docs" / "project" / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "DAL-U042" in ledger
    assert "PHX-G169" in tip
    assert "PHX-G169" in manifest
    assert "PHX-G169" in status
