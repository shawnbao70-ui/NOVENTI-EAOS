"""NRI Research Track — Wave 1 peer packages (Pass recorded; WP Drafts open)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RP001 = ROOT / "docs" / "research" / "programs" / "RP-001-enterprise-discovery"
RP005 = ROOT / "docs" / "research" / "programs" / "RP-005-ai-workforce-transformation"
RP007 = ROOT / "docs" / "research" / "programs" / "RP-007-enterprise-evolution-engine"
PEER001 = RP001 / "PEER_REVIEW_PACKAGE.md"
PEER005 = RP005 / "PEER_REVIEW_PACKAGE.md"
PEER007 = RP007 / "PEER_REVIEW_PACKAGE.md"
WP001 = RP001 / "WHITE_PAPER-RP-001.md"
WP005 = RP005 / "WHITE_PAPER-RP-005.md"
WP007 = RP007 / "WHITE_PAPER-RP-007.md"
IND005 = RP005 / "INDUSTRY_ANALYSIS.md"
RISK005 = RP005 / "RISK_ANALYSIS.md"
DELIV005 = RP005 / "DELIVERABLES-RP-005.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"
WAVE1 = ROOT / "docs" / "research" / "WAVE1_PEER_ASSIGNMENT.md"


def _assert_peer_pass(path: Path, reviewer: str, research_id: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert research_id in text
    assert reviewer in text
    assert "Pass — WP Draft Allowed" in text
    assert "Selected outcome:** **Pass → WP Draft Allowed**" in text or (
        "Selected outcome:" in text and "Pass → WP Draft Allowed" in text
    )
    assert "Yes / Pass" in text
    assert "Unassigned — Product Owner" not in text
    assert "Unassigned — designate" not in text


def test_rp001_peer_pass_zhenyu() -> None:
    _assert_peer_pass(PEER001, "臻宇", "NRI-RP-001-PEER")


def test_rp005_peer_pass_bao_jinyu() -> None:
    _assert_peer_pass(PEER005, "包锦昱", "NRI-RP-005-PEER")


def test_rp007_peer_pass_mourong() -> None:
    _assert_peer_pass(PEER007, "牟蓉", "NRI-RP-007-PEER")


def test_wave1_white_papers_content_accepted() -> None:
    for path, wid in (
        (WP001, "NRI-WP-RP-001"),
        (WP005, "NRI-WP-RP-005"),
        (WP007, "NRI-WP-RP-007"),
    ):
        assert path.is_file(), path
        text = path.read_text(encoding="utf-8")
        assert wid in text
        assert "**Status:** Accepted White Paper" in text
        assert "Approval:** Accepted" in text or "**Approval:** Accepted" in text
        assert "Content Acceptance:** Accepted" in text or "**Content Acceptance:** Accepted" in text
        assert "Architecture Review" in text  # non-outcome / boundary mention OK
        assert "Not Normative for Implementation" in text


def test_rp005_industry_risk_draft_and_deliverables() -> None:
    assert IND005.is_file() and RISK005.is_file()
    ind = IND005.read_text(encoding="utf-8")
    risk = RISK005.read_text(encoding="utf-8")
    assert "NRI-RP-005-IND" in ind
    assert "P-AW-01" in ind and "P-AW-10" in ind
    assert "NRI-RP-005-RISK" in risk
    assert "R-AW-01" in risk and "R-AW-14" in risk
    deliv = DELIV005.read_text(encoding="utf-8")
    assert "| 2 | Industry Analysis | Draft |" in deliv
    assert "| 15 | Risk Analysis | Draft |" in deliv


def test_wave1_all_three_peers_pass_in_ledger() -> None:
    status = STATUS.read_text(encoding="utf-8")
    library = LIBRARY.read_text(encoding="utf-8")
    wave1 = WAVE1.read_text(encoding="utf-8")
    for name in ("臻宇", "包锦昱", "牟蓉"):
        assert name in status
        assert name in library
        assert name in wave1
    assert "Pass" in wave1 and "WP Draft Allowed" in wave1
    assert "NRI-WP-RP-001" in library
    assert "NRI-WP-RP-005" in library
    assert "NRI-WP-RP-007" in library
    assert "WP Draft" in status or "WHITE_PAPER" in status
