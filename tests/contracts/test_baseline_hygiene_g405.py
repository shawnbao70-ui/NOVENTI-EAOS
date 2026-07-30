"""PHX-G405 baseline / V2.0 readiness hygiene contracts (historical TRACK freeze)."""

from __future__ import annotations

from pathlib import Path

import yaml
from alembic.config import Config
from alembic.script import ScriptDirectory

ROOT = Path(__file__).resolve().parents[2]
ROADMAP = ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"
MANIFEST = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"
CHECKLIST = ROOT / "docs" / "release" / "V2_0_READINESS_CHECKLIST.md"
EXPECTED_TIP = "0092_finance_realized_fx_gl_bridge_g372"


def test_g405_tip_package_and_roadmap_track_freeze() -> None:
    """G405 freeze: tip/package/TRACK + V2.0 checklist (queue may advance for repair)."""

    scripts = ScriptDirectory.from_config(Config(str(ROOT / "alembic.ini")))
    assert scripts.get_current_head() == EXPECTED_TIP

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["version"] == "0.2.5"
    assert manifest["alembic_head"] == EXPECTED_TIP

    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert EXPECTED_TIP in roadmap
    assert "TRACK-G405 COMPLETE" in roadmap
    assert "TRACK-BASELINE-HYGIENE-G405 COMPLETE" in roadmap
    assert "FINAL STOP TRACK-G405" in roadmap
    assert "G400–G405 COMPLETE" in roadmap

    assert CHECKLIST.is_file()
    checklist = CHECKLIST.read_text(encoding="utf-8")
    assert "0.2.3" in checklist
    assert EXPECTED_TIP in checklist
    assert "does not" in checklist.casefold() or "≠" in checklist
    assert "external PSP" in checklist or "External PSP" in checklist
