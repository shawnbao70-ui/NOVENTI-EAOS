"""NRI Research Track — RP-010 Future Enterprise Operating Model contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RP010 = ROOT / "docs" / "research" / "programs" / "RP-010-future-enterprise-operating-model"
FEOM = RP010 / "FUTURE_ENTERPRISE_OPERATING_MODEL.md"
EVID = RP010 / "EVIDENCE_PACK.md"
DELIV = RP010 / "DELIVERABLES-RP-010.md"
README = RP010 / "README.md"
SA_DIR = RP010 / "audits"
SA_FILES = (
    SA_DIR / "SA-01-executive-narrative.md",
    SA_DIR / "SA-02-plant-services-contrast.md",
)
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"
ROADMAP = ROOT / "docs" / "research" / "RESEARCH_ROADMAP.md"
WAVE3 = ROOT / "docs" / "research" / "WAVE3_PEER_ASSIGNMENT.md"


def test_rp010_feom_artifacts_exist() -> None:
    assert FEOM.is_file()
    assert EVID.is_file()
    assert DELIV.is_file()


def test_rp010_feom_spine_and_invariants() -> None:
    text = FEOM.read_text(encoding="utf-8")
    assert "NRI-RP-010-FEOM" in text
    assert "Research Draft" in text
    assert "ES-01" in text and "ES-07" in text
    assert "E0" in text and "E4" in text
    assert "V-EOM-01" in text
    assert "execution_authority" in text or "never Act" in text or "Brain" in text
    assert "Dual-Track" in text or "ADR-0162" in text
    assert "Cap" in text or "capability" in text.casefold()


def test_rp010_status_research_and_registry() -> None:
    readme = README.read_text(encoding="utf-8")
    assert "**Status:** Research" in readme
    assert "FUTURE_ENTERPRISE_OPERATING_MODEL.md" in readme
    library = LIBRARY.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "NRI-RP-010-FEOM" in library
    assert "NRI-RP-010-EVID" in library
    assert "Future Enterprise Operating Model" in index or "FEOM" in index
    assert "RP-010" in status
    assert "FEOM" in status or "SA-01" in status or "WHITE_PAPER-RP-010" in status
    assert "FEOM" in roadmap or "RP-010" in roadmap


def test_rp010_peer_pass_zhenyu_wp_draft() -> None:
    assert (SA_DIR / "README.md").is_file()
    for path in SA_FILES:
        text = path.read_text(encoding="utf-8")
        assert "Synthetic Complete" in text
        assert "constitution_rewrite: never" in text
        assert "execution_authority: none" in text
    evid = EVID.read_text(encoding="utf-8")
    assert "C-EOM-01" in evid
    assert "SA-01" in evid and "SA-02" in evid
    assert "Synthetic Complete" in evid
    assert "constitution_rewrite" in evid.casefold() or "execution_authority" in evid.casefold()
    assert "≥2 synthesis audits** | **Yes**" in evid or (
        "synthesis audits" in evid.casefold() and "**Yes**" in evid
    )
    ind = RP010 / "INDUSTRY_ANALYSIS.md"
    risk = RP010 / "RISK_ANALYSIS.md"
    peer = RP010 / "PEER_REVIEW_PACKAGE.md"
    assert ind.is_file() and risk.is_file() and peer.is_file()
    assert "NRI-RP-010-IND" in ind.read_text(encoding="utf-8")
    assert "P-EOM-01" in ind.read_text(encoding="utf-8")
    assert "NRI-RP-010-RISK" in risk.read_text(encoding="utf-8")
    assert "R-EOM-01" in risk.read_text(encoding="utf-8")
    peer_text = peer.read_text(encoding="utf-8")
    assert "NRI-RP-010-PEER" in peer_text
    assert "臻宇" in peer_text
    assert "Pass — WP Draft Allowed" in peer_text
    assert "PR-EOM-01" in peer_text and "PR-EOM-12" in peer_text
    assert "**Yes / Pass**" in peer_text
    assert "Selected outcome:** **Pass → WP Draft Allowed**" in peer_text or (
        "Selected outcome:" in peer_text and "Pass → WP Draft Allowed" in peer_text
    )
    assert "RP-010 peer = 臻宇" in peer_text
    assert "constitution_rewrite: never" in peer_text
    assert "execution_authority: none" in peer_text
    wp = RP010 / "WHITE_PAPER-RP-010.md"
    assert wp.is_file()
    wp_text = wp.read_text(encoding="utf-8")
    assert "NRI-WP-RP-010" in wp_text
    assert "**Status:** Accepted White Paper" in wp_text
    assert "Approval:** Accepted" in wp_text or "**Approval:** Accepted" in wp_text
    assert "constitution_rewrite" in wp_text.casefold() or "never" in wp_text.casefold()
    assert "execution_authority" in wp_text.casefold() or "none" in wp_text.casefold()
    assert "ES-01" in wp_text and "ES-07" in wp_text
    assert "Research Only — Not Normative for Implementation" in wp_text
    deliv = DELIV.read_text(encoding="utf-8")
    assert "INDUSTRY_ANALYSIS.md" in deliv and "RISK_ANALYSIS.md" in deliv
    assert "WHITE_PAPER-RP-010" in deliv
    library = LIBRARY.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert WAVE3.is_file()
    w3 = WAVE3.read_text(encoding="utf-8")
    assert "NRI-RP-010-SA-01" in library
    assert "NRI-RP-010-IND" in library and "NRI-RP-010-PEER" in library
    assert "NRI-WP-RP-010" in library
    assert "臻宇" in library
    assert "SA-01" in index or "Synthesis Audits" in index
    assert "WHITE_PAPER-RP-010" in index or "RP-010 White Paper" in index
    assert "臻宇" in status and "RP-010" in status
    assert "WHITE_PAPER-RP-010" in status or "WP-010" in status or "WP Draft" in status
    assert "FEOM" in status or "SA-01" in status
    assert "RP-010 peer = 臻宇" in w3 or "臻宇" in w3
    assert "Pass" in w3 and "WP Draft Allowed" in w3
    assert "RP-010" in w3
