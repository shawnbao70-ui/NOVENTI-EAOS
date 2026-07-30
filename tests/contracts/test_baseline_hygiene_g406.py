"""PHX-G406 remediation tip-helper hygiene contracts."""

from __future__ import annotations

from pathlib import Path

from tests.contracts._baseline import EXPECTED_PACKAGE, EXPECTED_TIP, assert_current_baseline

ROOT = Path(__file__).resolve().parents[2]
ROADMAP = ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"


def test_g406_tip_package_and_roadmap_alignment() -> None:
    assert_current_baseline()
    assert EXPECTED_TIP == "0092_finance_realized_fx_gl_bridge_g372"
    assert EXPECTED_PACKAGE == "0.2.5"

    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert EXPECTED_TIP in roadmap
    assert "TRACK-G406 COMPLETE" in roadmap
    assert "TRACK-REMEDIATION-TIP-HELPER COMPLETE" in roadmap
    assert "REPAIR FREEZE" in roadmap
    assert "PHX-G407" in roadmap
