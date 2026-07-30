"""PHX-G387 baseline / release hygiene contracts (historical TRACK freeze)."""

from __future__ import annotations

from pathlib import Path

import yaml
from alembic.config import Config
from alembic.script import ScriptDirectory

ROOT = Path(__file__).resolve().parents[2]
ROADMAP = ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"
MANIFEST = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"
EXPECTED_TIP = "0092_finance_realized_fx_gl_bridge_g372"


def test_g387_tip_and_roadmap_track_freeze() -> None:
    """Historical hygiene: tip + TRACK markers only (package may advance)."""

    scripts = ScriptDirectory.from_config(Config(str(ROOT / "alembic.ini")))
    assert scripts.get_current_head() == EXPECTED_TIP

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["alembic_head"] == EXPECTED_TIP

    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert EXPECTED_TIP in roadmap
    assert "TRACK-G387 COMPLETE" in roadmap
    assert "TRACK-BASELINE-HYGIENE-G387 COMPLETE" in roadmap
