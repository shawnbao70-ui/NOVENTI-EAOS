"""NRI RP-001 Architecture Review Candidate Package contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARC = (
    ROOT
    / "docs"
    / "research"
    / "programs"
    / "RP-001-enterprise-discovery"
    / "ARCHITECTURE_REVIEW_CANDIDATE-RP-001.md"
)
README = ROOT / "docs" / "research" / "programs" / "RP-001-enterprise-discovery" / "README.md"
DELIV = (
    ROOT
    / "docs"
    / "research"
    / "programs"
    / "RP-001-enterprise-discovery"
    / "DELIVERABLES-RP-001.md"
)
EVID = ROOT / "docs" / "research" / "programs" / "RP-001-enterprise-discovery" / "EVIDENCE_PACK.md"
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
TIP = ROOT / "docs" / "research" / "GENERATION2_TIP_BOARD.md"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"


def test_rp001_arc_candidate_exists_and_awaits_board() -> None:
    assert ARC.is_file()
    text = ARC.read_text(encoding="utf-8")
    assert "NRI-ARC-RP-001" in text
    assert (
        "Board Decision — Hold" in text
        or "Awaiting Architecture Review Board" in text
        or "Awaiting" in text
    )
    assert "Candidate Package" in text
    assert "NOT" in text.upper() or "Not Accepted" in text or "not self" in text.casefold()
    assert "Accepted" in text  # WP Accepted linked
    assert "WHITE_PAPER" in text or "White Paper" in text
    assert "EVIDENCE" in text or "Evidence" in text
    assert "PEER" in text or "Peer" in text
    assert "Promote" in text and "Hold" in text and "Reject" in text
    assert "Brain" in text and "Twin" in text
    assert "Constitution" in text or "Blueprint" in text or "Const" in text
    assert "T1" in text and "T2" in text and "T3" in text
    assert "Research Only" in text or "Classification" in text
    assert "Board decision" in text.casefold() or "Board Decision" in text or "decision block" in text.casefold()
    assert "Hold" in text or "Awaiting" in text
    # Status may be Awaiting Board (pre-session) or Board Decision — Hold (PHX-G159)
    assert (
        "Board Decision — Hold" in text
        or "Candidate Package — Awaiting" in text
        or "Awaiting Architecture Review Board" in text
    )


def test_rp001_arc_linked_in_program_and_registry() -> None:
    assert "ARCHITECTURE_REVIEW_CANDIDATE" in README.read_text(encoding="utf-8")
    assert "NRI-ARC-RP-001" in README.read_text(encoding="utf-8") or "ARCHITECTURE_REVIEW_CANDIDATE" in README.read_text(
        encoding="utf-8"
    )
    deliv = DELIV.read_text(encoding="utf-8")
    evid = EVID.read_text(encoding="utf-8")
    assert "ARCHITECTURE_REVIEW_CANDIDATE" in deliv or "NRI-ARC-RP-001" in deliv or "Architecture Review Candidate" in deliv
    assert "ARCHITECTURE_REVIEW_CANDIDATE" in evid or "NRI-ARC-RP-001" in evid or "Architecture Review Candidate" in evid
    index = INDEX.read_text(encoding="utf-8")
    library = LIBRARY.read_text(encoding="utf-8")
    assert "NRI-ARC-RP-001" in index
    assert "NRI-ARC-RP-001" in library
    tip = TIP.read_text(encoding="utf-8")
    assert "RP-001" in tip
    assert "Architecture Review" in tip or "AR" in tip
    assert "NRI-ARC-RP-001" in tip or "ARCHITECTURE_REVIEW_CANDIDATE" in tip or "Candidate" in tip
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-U013" in ledger
    assert "RP-001" in ledger or "NRI-ARC-RP-001" in ledger
