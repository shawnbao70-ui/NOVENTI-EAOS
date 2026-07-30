"""PHX-G415 remediation RC evidence pack contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RC = ROOT / "docs" / "release" / "RC_EVIDENCE_G415.md"
ROADMAP = ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"


def test_g415_rc_evidence_pack_present() -> None:
    assert RC.is_file()
    text = RC.read_text(encoding="utf-8")
    assert "PHX-G415" in text
    assert "0.2.3" in text
    assert "0092" in text
    assert "REMEDIATION RC DECISION" in text
    assert "CONDITIONAL GO" in text or "GO" in text or "NO-GO" in text
    assert "G0" in text and "G1" in text and "G4" in text


def test_g415_roadmap_final_stop_remediation() -> None:
    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "TRACK-G415 COMPLETE" in roadmap
    assert "FINAL STOP TRACK-G415" in roadmap or "REMEDIATION RC" in roadmap
