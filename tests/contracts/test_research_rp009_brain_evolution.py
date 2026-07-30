"""NRI Research Track — RP-009 Brain Evolution Model contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RP009 = ROOT / "docs" / "research" / "programs" / "RP-009-enterprise-brain-evolution"
BEM = RP009 / "BRAIN_EVOLUTION_MODEL.md"
EVID = RP009 / "EVIDENCE_PACK.md"
DELIV = RP009 / "DELIVERABLES-RP-009.md"
README = RP009 / "README.md"
RED_TEAM = RP009 / "red-team"
AE_FILES = (
    RED_TEAM / "AE-01-quiet-analytics-trigger.md",
    RED_TEAM / "AE-02-accept-on-behalf.md",
    RED_TEAM / "AE-03-twin-authorize-leak.md",
)
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"
WAVE2 = ROOT / "docs" / "research" / "WAVE2_PEER_ASSIGNMENT.md"


def test_rp009_bem_artifacts_exist() -> None:
    assert BEM.is_file()
    assert EVID.is_file()
    assert DELIV.is_file()


def test_rp009_bem_advisory_never_act() -> None:
    text = BEM.read_text(encoding="utf-8")
    assert "NRI-RP-009-BEM" in text
    assert "Research Draft" in text
    assert "IC-01" in text and "IC-06" in text
    assert "Never" in text or "never" in text
    assert "execution_authority" in text
    assert "V-BE-01" in text
    assert "ADR-0030" in text
    assert "Act" in text


def test_rp009_status_research_and_registry() -> None:
    readme = README.read_text(encoding="utf-8")
    assert "**Status:** Research" in readme
    assert "BRAIN_EVOLUTION_MODEL.md" in readme
    assert "臻宇" in readme
    library = LIBRARY.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert "NRI-RP-009-BEM" in library
    assert "NRI-RP-009-EVID" in library
    assert "臻宇" in library
    assert "Brain Evolution Model" in index or "BEM" in index
    assert "RP-009" in status
    assert "臻宇" in status


def test_rp009_peer_pass_zhenyu_wp_draft() -> None:
    assert (RED_TEAM / "README.md").is_file()
    for path in AE_FILES:
        text = path.read_text(encoding="utf-8")
        assert "Synthetic Complete" in text
        assert "execution_authority: none" in text
        assert "fail_closed" in text or "fail closed" in text.casefold()
    evid = EVID.read_text(encoding="utf-8")
    assert "C-BE-01" in evid
    assert "AE-01" in evid and "AE-03" in evid
    assert "Synthetic Complete" in evid
    assert "execution_authority" in evid or "Brain execute" in evid
    assert "Twin authorize" in evid or "authorize" in evid.casefold()
    ind = RP009 / "INDUSTRY_ANALYSIS.md"
    risk = RP009 / "RISK_ANALYSIS.md"
    peer = RP009 / "PEER_REVIEW_PACKAGE.md"
    assert ind.is_file() and risk.is_file() and peer.is_file()
    assert "NRI-RP-009-IND" in ind.read_text(encoding="utf-8")
    assert "P-BE-01" in ind.read_text(encoding="utf-8")
    assert "NRI-RP-009-RISK" in risk.read_text(encoding="utf-8")
    assert "R-BE-01" in risk.read_text(encoding="utf-8")
    peer_text = peer.read_text(encoding="utf-8")
    assert "NRI-RP-009-PEER" in peer_text
    assert "臻宇" in peer_text
    assert "Pass — WP Draft Allowed" in peer_text
    assert "PR-BE-01" in peer_text and "PR-BE-12" in peer_text
    assert "**Yes / Pass**" in peer_text
    assert "Selected outcome:** **Pass → WP Draft Allowed**" in peer_text or (
        "Selected outcome:" in peer_text and "Pass → WP Draft Allowed" in peer_text
    )
    wp = RP009 / "WHITE_PAPER-RP-009.md"
    assert wp.is_file()
    wp_text = wp.read_text(encoding="utf-8")
    assert "NRI-WP-RP-009" in wp_text
    assert "**Status:** Accepted White Paper" in wp_text
    assert "Approval:** Accepted" in wp_text or "**Approval:** Accepted" in wp_text
    assert "execution_authority" in wp_text.casefold() or "never" in wp_text.casefold()
    deliv = DELIV.read_text(encoding="utf-8")
    assert "INDUSTRY_ANALYSIS.md" in deliv and "RISK_ANALYSIS.md" in deliv
    assert "WHITE_PAPER-RP-009" in deliv
    library = LIBRARY.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    w2 = WAVE2.read_text(encoding="utf-8")
    assert "NRI-RP-009-AE-01" in library
    assert "NRI-RP-009-IND" in library and "NRI-RP-009-PEER" in library
    assert "NRI-WP-RP-009" in library
    assert "WHITE_PAPER-RP-009" in index or "RP-009 White Paper" in index
    assert "WHITE_PAPER-RP-009" in status or "WP-009" in status or "WP Draft" in status
    assert "AE-01" in status or "Pass" in status
    assert "RP-009 peer = 臻宇" in w2 or "臻宇" in w2
    assert "Pass" in w2 and "WP Draft Allowed" in w2
