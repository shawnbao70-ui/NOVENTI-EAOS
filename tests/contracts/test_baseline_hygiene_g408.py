"""PHX-G408 remediation contract-shards hygiene contracts."""

from __future__ import annotations

from pathlib import Path

from tests.contracts._baseline import EXPECTED_PACKAGE, EXPECTED_TIP, assert_current_baseline

ROOT = Path(__file__).resolve().parents[2]
ROADMAP = ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"
SHARDS = ROOT / "tests" / "contracts" / "shards.yaml"


def test_g408_tip_package_and_roadmap_alignment() -> None:
    assert_current_baseline()
    assert EXPECTED_TIP == "0092_finance_realized_fx_gl_bridge_g372"
    assert EXPECTED_PACKAGE == "0.2.5"

    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "TRACK-G408 COMPLETE" in roadmap
    assert "TRACK-REMEDIATION-CONTRACT-SHARDS COMPLETE" in roadmap
    assert SHARDS.is_file()
    assert "pr_required" in SHARDS.read_text(encoding="utf-8")
