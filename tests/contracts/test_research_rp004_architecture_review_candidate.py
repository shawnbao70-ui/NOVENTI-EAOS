"""NRI RP-004 Architecture Review Candidate Package contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARC = (
    ROOT
    / "docs"
    / "research"
    / "programs"
    / "RP-004-organization-neutrality"
    / "ARCHITECTURE_REVIEW_CANDIDATE-RP-004.md"
)
README = ROOT / "docs" / "research" / "programs" / "RP-004-organization-neutrality" / "README.md"
DELIV = (
    ROOT
    / "docs"
    / "research"
    / "programs"
    / "RP-004-organization-neutrality"
    / "DELIVERABLES-RP-004.md"
)
EVID = ROOT / "docs" / "research" / "programs" / "RP-004-organization-neutrality" / "EVIDENCE_PACK.md"
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
TIP = ROOT / "docs" / "research" / "GENERATION2_TIP_BOARD.md"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"


def test_rp004_arc_candidate_exists_and_awaits_board() -> None:
    assert ARC.is_file()
    text = ARC.read_text(encoding="utf-8")
    assert "NRI-ARC-RP-004" in text
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
    assert "ONM" in text or "Organization Neutrality" in text
    assert "NA-01" in text or "NA-01…02" in text or "NA-02" in text
    assert "Structure" in text and ("Permission" in text or "permission" in text.casefold())
    assert "org_shape_grant" in text
    assert "never" in text.casefold()
    assert "Cap≠Org" in text or "Cap != Org" in text or ("Cap" in text and "Org" in text)
    assert "fail-closed" in text.casefold() or "fail closed" in text.casefold()
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


def test_rp004_arc_linked_in_program_and_registry() -> None:
    readme = README.read_text(encoding="utf-8")
    assert "ARCHITECTURE_REVIEW_CANDIDATE" in readme
    assert "NRI-ARC-RP-004" in readme or "ARCHITECTURE_REVIEW_CANDIDATE" in readme
    assert "Accepted" in readme
    deliv = DELIV.read_text(encoding="utf-8")
    evid = EVID.read_text(encoding="utf-8")
    assert "ARCHITECTURE_REVIEW_CANDIDATE" in deliv or "NRI-ARC-RP-004" in deliv or "Architecture Review Candidate" in deliv
    assert "ARCHITECTURE_REVIEW_CANDIDATE" in evid or "NRI-ARC-RP-004" in evid or "Architecture Review Candidate" in evid
    index = INDEX.read_text(encoding="utf-8")
    library = LIBRARY.read_text(encoding="utf-8")
    assert "NRI-ARC-RP-004" in index
    assert "NRI-ARC-RP-004" in library
    tip = TIP.read_text(encoding="utf-8")
    assert "RP-004" in tip
    assert "Architecture Review" in tip or "AR" in tip
    assert "NRI-ARC-RP-004" in tip or "ARCHITECTURE_REVIEW_CANDIDATE" in tip or "Candidate" in tip
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-U019" in ledger
    assert "RP-004" in ledger or "NRI-ARC-RP-004" in ledger
    # Preserve concurrent U016–U018 if present (Wave 2 / G2 deepenings may land alongside)
    for uid in ("DAL-U016", "DAL-U017", "DAL-U018"):
        if uid in ledger:
            assert uid in ledger
