"""PHX-G340 baseline hygiene contract for the current roadmap tip."""

from __future__ import annotations

import re
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory


ROOT = Path(__file__).resolve().parents[2]
ROADMAP = ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"
VERIFIED_HEAD_CELL = re.compile(
    r"^\|\s*Alembic head（verified）\s*\|\s*`([^`]+)`\s*\|\s*$",
    re.MULTILINE,
)


def test_roadmap_verified_tip_matches_alembic_head() -> None:
    match = VERIFIED_HEAD_CELL.search(ROADMAP.read_text(encoding="utf-8"))
    assert match is not None, "roadmap must declare its verified Alembic head"

    scripts = ScriptDirectory.from_config(Config(str(ROOT / "alembic.ini")))
    assert match.group(1) == scripts.get_current_head()
