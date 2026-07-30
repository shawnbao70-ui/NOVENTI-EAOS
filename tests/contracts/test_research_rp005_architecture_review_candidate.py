"""NRI RP-005 Architecture Review Candidate Package contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARC = (
    ROOT
    / "docs"
    / "research"
    / "programs"
    / "RP-005-ai-workforce-transformation"
    / "ARCHITECTURE_REVIEW_CANDIDATE-RP-005.md"
)
README = ROOT / "docs" / "research" / "programs" / "RP-005-ai-workforce-transformation" / "README.md"
DELIV = (
    ROOT
    / "docs"
    / "research"
    / "programs"
    / "RP-005-ai-workforce-transformation"
    / "DELIVERABLES-RP-005.md"
)
EVID = ROOT / "docs" / "research" / "programs" / "RP-005-ai-workforce-transformation" / "EVIDENCE_PACK.md"
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
TIP = ROOT / "docs" / "research" / "GENERATION2_TIP_BOARD.md"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"


def test_rp005_arc_candidate_exists_and_awaits_board() -> None:
    assert ARC.is_file()
    text = ARC.read_text(encoding="utf-8")
    assert "NRI-ARC-RP-005" in text
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
    assert "PEER" in text or "Peer" in text or "包锦昱" in text
    assert "Promote" in text and "Hold" in text and "Reject" in text
    assert "Brain" in text and "Twin" in text
    assert "Constitution" in text or "Blueprint" in text or "Const" in text
    assert "T1" in text and "T2" in text and "T3" in text
    assert "Research Only" in text or "Classification" in text
    assert "Board decision" in text.casefold() or "Board Decision" in text or "decision block" in text.casefold()
    assert "Hold" in text or "Awaiting" in text
    assert "Title" in text or "title" in text or "Permission" in text
    assert "auto_grant_minted" in text or "Role→grant" in text or "grant mint" in text.casefold()
    assert "legal person" in text.casefold() or "Digital Human" in text or "duty bearer" in text.casefold()
    assert "ANRF" in text or "AI_NATIVE" in text or "Role Framework" in text
    assert "RI-01" in text or "RI-02" in text or "inventor" in text.casefold()
    # Status may be Awaiting Board (pre-session) or Board Decision — Hold (PHX-G159)
    assert (
        "Board Decision — Hold" in text
        or "Candidate Package — Awaiting" in text
        or "Awaiting Architecture Review Board" in text
    )


def test_rp005_arc_linked_in_program_and_registry() -> None:
    readme = README.read_text(encoding="utf-8")
    assert "ARCHITECTURE_REVIEW_CANDIDATE" in readme
    assert "NRI-ARC-RP-005" in readme or "ARCHITECTURE_REVIEW_CANDIDATE" in readme
    assert "Accepted" in readme
    deliv = DELIV.read_text(encoding="utf-8")
    evid = EVID.read_text(encoding="utf-8")
    assert "ARCHITECTURE_REVIEW_CANDIDATE" in deliv or "NRI-ARC-RP-005" in deliv or "Architecture Review Candidate" in deliv
    assert "ARCHITECTURE_REVIEW_CANDIDATE" in evid or "NRI-ARC-RP-005" in evid or "Architecture Review Candidate" in evid
    index = INDEX.read_text(encoding="utf-8")
    library = LIBRARY.read_text(encoding="utf-8")
    assert "NRI-ARC-RP-005" in index
    assert "NRI-ARC-RP-005" in library
    tip = TIP.read_text(encoding="utf-8")
    assert "RP-005" in tip
    assert "Architecture Review" in tip or "AR" in tip
    assert "NRI-ARC-RP-005" in tip or "ARCHITECTURE_REVIEW_CANDIDATE" in tip or "Candidate" in tip
    assert "NRI-ARC-RP-001" in tip and "NRI-ARC-RP-007" in tip  # Wave 1 AR set
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-U015" in ledger
    assert "RP-005" in ledger or "NRI-ARC-RP-005" in ledger
