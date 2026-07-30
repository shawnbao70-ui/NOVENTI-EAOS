"""PHX-G407 remediation Docker-noventi hygiene contracts."""

from __future__ import annotations

from pathlib import Path

from tests.contracts._baseline import EXPECTED_PACKAGE, EXPECTED_TIP, assert_current_baseline

ROOT = Path(__file__).resolve().parents[2]
ROADMAP = ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"
DOCKERFILE = ROOT / "deploy" / "docker" / "Dockerfile"


def test_g407_tip_package_and_roadmap_alignment() -> None:
    assert_current_baseline()
    assert EXPECTED_TIP == "0092_finance_realized_fx_gl_bridge_g372"
    assert EXPECTED_PACKAGE == "0.2.5"

    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "TRACK-G407 COMPLETE" in roadmap
    assert "TRACK-REMEDIATION-DOCKER-NOVENTI COMPLETE" in roadmap
    assert "COPY noventi ./noventi" in DOCKERFILE.read_text(encoding="utf-8")
