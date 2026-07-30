"""PHX-G143 Dual-Track Governance formalization documentation contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0162-dual-track-governance.md"
PLAYBOOK = ROOT / "docs" / "project" / "DUAL_TRACK_GOVERNANCE.md"
GATE = ROOT / "docs" / "project" / "PHX-G143_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G143_ACCEPTANCE.md"
MASTER = ROOT / "docs" / "project" / "MASTER_PLAN.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"
ROADMAP = ROOT / "docs" / "project" / "ROADMAP.md"
NRI_README = ROOT / "docs" / "research" / "README.md"
NRI_CHARTER = ROOT / "docs" / "research" / "RESEARCH_GOVERNANCE_CHARTER.md"
NRI_PROMO = ROOT / "docs" / "research" / "RESEARCH_PROMOTION_RULES.md"


def test_g143_dual_track_artifacts_exist() -> None:
    for path in (ADR, PLAYBOOK, GATE, ACCEPTANCE, MASTER, STATUS, ROADMAP, NRI_README):
        assert path.is_file(), path


def test_g143_adr_accepts_dual_track() -> None:
    text = ADR.read_text(encoding="utf-8")
    assert "Accepted" in text
    assert "Dual-Track" in text
    assert "Engineering Track" in text
    assert "Research Track" in text
    assert "Constitution" in text
    assert "Kernel" in text and "Runtime" in text
    assert "不" in text and "修改" in text and "Constitution" in text


def test_g143_playbook_defines_bridge_and_no_auto_ingest() -> None:
    text = PLAYBOOK.read_text(encoding="utf-8")
    assert "No auto-ingest" in text or "no auto-ingest" in text.casefold()
    assert "Architecture Review" in text
    assert "fail-closed" in text.casefold() or "fail-closed" in text
    assert "NRI" in text
    assert "PHX-G143" in text


def test_g143_status_and_master_declare_dual_track() -> None:
    master = MASTER.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "Dual-Track" in master
    assert "PHX-G143" in status
    assert "Dual-Track" in status
    assert "Dual-Track" in roadmap


def test_g143_nri_remains_hard_bounded() -> None:
    charter = NRI_CHARTER.read_text(encoding="utf-8")
    promo = NRI_PROMO.read_text(encoding="utf-8")
    nri = NRI_README.read_text(encoding="utf-8")
    assert "shall **not** directly modify" in charter or "shall not directly modify" in charter.casefold()
    assert "Runtime" in charter and "Kernel" in charter
    assert "Promotion is optional" in promo or "promotion is optional" in promo.casefold()
    assert "Dual-Track" in nri
    assert "ADR-0162" in nri or "DUAL_TRACK" in nri
