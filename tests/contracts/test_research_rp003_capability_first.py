"""NRI Research Track — RP-003 Capability First Model contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RP003 = ROOT / "docs" / "research" / "programs" / "RP-003-capability-first"
CFM = RP003 / "CAPABILITY_FIRST_MODEL.md"
EVID = RP003 / "EVIDENCE_PACK.md"
DELIV = RP003 / "DELIVERABLES-RP-003.md"
README = RP003 / "README.md"
GRAPH_DIR = RP003 / "graphs"
CG_FILES = (
    GRAPH_DIR / "CG-01-wt01-mfg.md",
    GRAPH_DIR / "CG-02-wt02-svc.md",
)
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"


def test_rp003_cfm_artifacts_exist() -> None:
    assert CFM.is_file()
    assert EVID.is_file()
    assert DELIV.is_file()


def test_rp003_cfm_metamodel_and_non_permission() -> None:
    text = CFM.read_text(encoding="utf-8")
    assert "NRI-RP-003-CFM" in text
    assert "Research Draft" in text
    assert "Cap≠Org" in text or "Cap!=Org" in text
    assert "Permission" in text
    assert "V-CAP-01" in text
    assert "L0" in text and "L4" in text
    assert "A0" in text and "A4" in text
    assert "never" in text.casefold() or "must not" in text.casefold()
    assert "grant" in text.casefold() or "authorization" in text.casefold()


def test_rp003_status_research_and_registry() -> None:
    readme = README.read_text(encoding="utf-8")
    assert "**Status:** Research" in readme
    assert "CAPABILITY_FIRST_MODEL.md" in readme
    library = LIBRARY.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert "NRI-RP-003-CFM" in library
    assert "NRI-RP-003-EVID" in library
    assert "Capability First Model" in index or "CFM" in index
    assert "RP-003" in status


def test_rp003_peer_pass_zhenyu_wp_draft() -> None:
    ind = RP003 / "INDUSTRY_ANALYSIS.md"
    risk = RP003 / "RISK_ANALYSIS.md"
    peer = RP003 / "PEER_REVIEW_PACKAGE.md"
    assert ind.is_file() and risk.is_file() and peer.is_file()
    assert "NRI-RP-003-IND" in ind.read_text(encoding="utf-8")
    assert "P-CAP-01" in ind.read_text(encoding="utf-8")
    assert "NRI-RP-003-RISK" in risk.read_text(encoding="utf-8")
    assert "R-CAP-01" in risk.read_text(encoding="utf-8")
    peer_text = peer.read_text(encoding="utf-8")
    assert "NRI-RP-003-PEER" in peer_text
    assert "臻宇" in peer_text
    assert "Pass — WP Draft Allowed" in peer_text
    assert "PR-CAP-01" in peer_text and "PR-CAP-12" in peer_text
    assert "**Yes / Pass**" in peer_text
    assert "Selected outcome:** **Pass → WP Draft Allowed**" in peer_text or (
        "Selected outcome:" in peer_text and "Pass → WP Draft Allowed" in peer_text
    )
    assert "grant" in peer_text.casefold() or "Permission" in peer_text
    wp = RP003 / "WHITE_PAPER-RP-003.md"
    assert wp.is_file()
    wp_text = wp.read_text(encoding="utf-8")
    assert "NRI-WP-RP-003" in wp_text
    assert "**Status:** Accepted White Paper" in wp_text
    assert "Approval:** Accepted" in wp_text or "**Approval:** Accepted" in wp_text
    assert "never" in wp_text.casefold() or "grant" in wp_text.casefold()
    deliv = DELIV.read_text(encoding="utf-8")
    assert "INDUSTRY_ANALYSIS.md" in deliv and "RISK_ANALYSIS.md" in deliv
    assert "WHITE_PAPER-RP-003" in deliv
    library = LIBRARY.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert "NRI-RP-003-IND" in library and "NRI-RP-003-PEER" in library
    assert "NRI-WP-RP-003" in library
    assert "臻宇" in library
    assert "WHITE_PAPER-RP-003" in index or "RP-003 White Paper" in index
    assert "WHITE_PAPER-RP-003" in status or "WP Draft" in status
    w2 = (ROOT / "docs" / "research" / "WAVE2_PEER_ASSIGNMENT.md").read_text(encoding="utf-8")
    assert "RP-003 peer = 臻宇" in w2 or "臻宇" in w2
    assert "Pass" in w2 and "WP Draft Allowed" in w2


def test_rp003_synthetic_graphs_complete_and_non_granting() -> None:
    assert (GRAPH_DIR / "README.md").is_file()
    for path in CG_FILES:
        text = path.read_text(encoding="utf-8")
        assert "Synthetic Complete" in text
        assert "auto_grant_minted: never" in text
        assert "cap_org_separated: yes" in text
        assert "capability_id" in text or "CAP-" in text
    evid = EVID.read_text(encoding="utf-8")
    assert "C-CAP-01" in evid
    assert "Synthetic Complete" in evid
    assert "≥2 synthetic capability graphs** | **Yes**" in evid or (
        "synthetic capability graphs" in evid and "**Yes**" in evid
    )
    assert "Role→grant" in evid or "Role->grant" in evid or "grant" in evid.casefold()
    library = LIBRARY.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert "NRI-RP-003-CG-01" in library
    assert "NRI-RP-003-CG-02" in library
    assert "CG-01" in index or "Capability Graphs" in index
    assert "CG-01" in status or "CG-01…02" in status or "CG-01" in status
