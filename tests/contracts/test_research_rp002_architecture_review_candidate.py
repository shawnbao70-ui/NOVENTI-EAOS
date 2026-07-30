"""NRI RP-002 Architecture Review Candidate Package contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARC = (
    ROOT
    / "docs"
    / "research"
    / "programs"
    / "RP-002-enterprise-dna"
    / "ARCHITECTURE_REVIEW_CANDIDATE-RP-002.md"
)
README = ROOT / "docs" / "research" / "programs" / "RP-002-enterprise-dna" / "README.md"
DELIV = (
    ROOT
    / "docs"
    / "research"
    / "programs"
    / "RP-002-enterprise-dna"
    / "DELIVERABLES-RP-002.md"
)
EVID = ROOT / "docs" / "research" / "programs" / "RP-002-enterprise-dna" / "EVIDENCE_PACK.md"
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
TIP = ROOT / "docs" / "research" / "GENERATION2_TIP_BOARD.md"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"


def test_rp002_arc_candidate_exists_and_awaits_board() -> None:
    assert ARC.is_file()
    text = ARC.read_text(encoding="utf-8")
    assert "NRI-ARC-RP-002" in text
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
    assert "PEER" in text or "Peer" in text or "臻宇" in text
    assert "Promote" in text and "Hold" in text and "Reject" in text
    assert "Brain" in text and "Twin" in text
    assert "DNA" in text and ("grant" in text.casefold() or "DNA≠grant" in text or "DNA != grant" in text)
    assert "constraint" in text.casefold() or "authorization" in text.casefold()
    assert "fail-closed" in text.casefold() or "fail closed" in text.casefold()
    assert "EDNA" in text or "Enterprise DNA" in text
    assert "SC-01" in text or "SC-01…03" in text or "scorecard" in text.casefold()
    assert "Constitution" in text or "Blueprint" in text or "Const" in text
    assert "T1" in text and "T2" in text and "T3" in text
    assert "Research Only" in text or "Classification" in text
    assert "Board decision" in text.casefold() or "Board Decision" in text or "decision block" in text.casefold()
    assert "Hold" in text or "Awaiting" in text
    assert "Remain Research Asset" in text or "Hold for" in text or "Hold" in text
    # Status may be Awaiting Board (pre-session) or Board Decision — Hold (PHX-G159)
    assert (
        "Board Decision — Hold" in text
        or "Candidate Package — Awaiting" in text
        or "Awaiting Architecture Review Board" in text
    )


def test_rp002_arc_linked_in_program_and_registry() -> None:
    readme = README.read_text(encoding="utf-8")
    assert "ARCHITECTURE_REVIEW_CANDIDATE" in readme
    assert "NRI-ARC-RP-002" in readme or "ARCHITECTURE_REVIEW_CANDIDATE" in readme
    assert "Accepted" in readme
    deliv = DELIV.read_text(encoding="utf-8")
    evid = EVID.read_text(encoding="utf-8")
    assert "ARCHITECTURE_REVIEW_CANDIDATE" in deliv or "NRI-ARC-RP-002" in deliv or "Architecture Review Candidate" in deliv
    assert "ARCHITECTURE_REVIEW_CANDIDATE" in evid or "NRI-ARC-RP-002" in evid or "Architecture Review Candidate" in evid
    index = INDEX.read_text(encoding="utf-8")
    library = LIBRARY.read_text(encoding="utf-8")
    assert "NRI-ARC-RP-002" in index
    assert "NRI-ARC-RP-002" in library
    tip = TIP.read_text(encoding="utf-8")
    assert "RP-002" in tip
    assert "Architecture Review" in tip or "AR" in tip
    assert "NRI-ARC-RP-002" in tip or "ARCHITECTURE_REVIEW_CANDIDATE" in tip or "Candidate" in tip
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-U016" in ledger
    assert "RP-002" in ledger or "NRI-ARC-RP-002" in ledger
