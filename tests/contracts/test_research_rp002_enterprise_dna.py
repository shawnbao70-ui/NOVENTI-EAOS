"""NRI Research Track — RP-002 Enterprise DNA Model contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RP002 = ROOT / "docs" / "research" / "programs" / "RP-002-enterprise-dna"
EDNA = RP002 / "ENTERPRISE_DNA_MODEL.md"
EVID = RP002 / "EVIDENCE_PACK.md"
DELIV = RP002 / "DELIVERABLES-RP-002.md"
README = RP002 / "README.md"
SC_DIR = RP002 / "scorecards"
SC_FILES = (
    SC_DIR / "SC-01-wt01-mfg.md",
    SC_DIR / "SC-02-wt02-svc.md",
    SC_DIR / "SC-03-wt03-contrast.md",
)
PEER_ASSIGN = ROOT / "docs" / "research" / "WAVE1_PEER_ASSIGNMENT.md"
PEER_ASSIGN_W2 = ROOT / "docs" / "research" / "WAVE2_PEER_ASSIGNMENT.md"
PEER_PKG = RP002 / "PEER_REVIEW_PACKAGE.md"
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"


def test_rp002_edna_artifacts_exist() -> None:
    assert EDNA.is_file()
    assert EVID.is_file()
    assert DELIV.is_file()


def test_rp002_edna_axes_and_non_authorization() -> None:
    text = EDNA.read_text(encoding="utf-8")
    assert "NRI-RP-002-EDNA" in text
    assert "Research Draft" in text
    for axis in ("DX-01", "DX-02", "DX-03", "DX-04", "DX-05", "DX-06", "DX-07", "DX-08"):
        assert axis in text
    assert "never" in text.casefold() and "authorization" in text.casefold()
    assert "Permission" in text
    assert "V-DNA-01" in text
    assert "SC-01" in EVID.read_text(encoding="utf-8")


def test_rp002_status_research_and_registry() -> None:
    readme = README.read_text(encoding="utf-8")
    assert "**Status:** Research" in readme
    assert "ENTERPRISE_DNA_MODEL.md" in readme
    library = LIBRARY.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert "NRI-RP-002-EDNA" in library
    assert "NRI-RP-002-EVID" in library
    assert "Enterprise DNA Model" in index
    assert "RP-002" in status
    assert "Wave 2" in status or "EDNA" in status or "DNA" in status or "SC-01" in status


def test_rp002_scorecards_complete_and_non_authorizing() -> None:
    assert (SC_DIR / "README.md").is_file()
    for path in SC_FILES:
        text = path.read_text(encoding="utf-8")
        assert "Synthetic Complete" in text
        assert "authorization_input: never" in text
        assert "DX-01" in text and "DX-08" in text
    evid = EVID.read_text(encoding="utf-8")
    assert "Synthetic Complete" in evid
    assert "≥3 synthetic scorecards | **Yes**" in evid or (
        "synthetic scorecards" in evid and "**Yes**" in evid
    )
    library = LIBRARY.read_text(encoding="utf-8")
    assert "NRI-RP-002-SC-01" in library


def test_rp002_industry_and_risk_drafts() -> None:
    ind = RP002 / "INDUSTRY_ANALYSIS.md"
    risk = RP002 / "RISK_ANALYSIS.md"
    assert ind.is_file() and risk.is_file()
    assert "NRI-RP-002-IND" in ind.read_text(encoding="utf-8")
    assert "P-DNA-01" in ind.read_text(encoding="utf-8")
    assert "NRI-RP-002-RISK" in risk.read_text(encoding="utf-8")
    assert "R-DNA-01" in risk.read_text(encoding="utf-8")
    deliv = DELIV.read_text(encoding="utf-8")
    assert "Industry Analysis" in deliv and "INDUSTRY_ANALYSIS.md" in deliv
    assert "Risk Analysis" in deliv and "RISK_ANALYSIS.md" in deliv
    assert "Draft" in deliv
    library = LIBRARY.read_text(encoding="utf-8")
    assert "NRI-RP-002-IND" in library
    assert "NRI-RP-002-RISK" in library


def test_wave1_peer_assignment_rejects_placeholder_name() -> None:
    assert PEER_ASSIGN.is_file()
    text = PEER_ASSIGN.read_text(encoding="utf-8")
    assert "not** a valid" in text or "not a valid" in text.casefold()
    assert "`<name>`" in text or "<name>" in text
    assert "placeholder" in text.casefold() or "真实" in STATUS.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert "拒绝" in status or "rejected" in status.casefold() or "真实姓名" in status
    assert "Pass" in text and "WP Draft Allowed" in text


def test_rp002_peer_pass_zhenyu_wp_draft() -> None:
    assert PEER_PKG.is_file()
    assert PEER_ASSIGN_W2.is_file()
    peer = PEER_PKG.read_text(encoding="utf-8")
    assert "NRI-RP-002-PEER" in peer
    assert "臻宇" in peer
    assert "Pass — WP Draft Allowed" in peer
    assert "PR-DNA-08" in peer and "**Yes / Pass**" in peer
    assert "PR-DNA-09" in peer and "PR-DNA-10" in peer
    assert "Selected outcome:** **Pass → WP Draft Allowed**" in peer or (
        "Selected outcome:" in peer and "Pass → WP Draft Allowed" in peer
    )
    assert "authorization" in peer.casefold()
    wp = RP002 / "WHITE_PAPER-RP-002.md"
    assert wp.is_file()
    wp_text = wp.read_text(encoding="utf-8")
    assert "NRI-WP-RP-002" in wp_text
    assert "**Status:** Accepted White Paper" in wp_text
    assert "Approval:** Accepted" in wp_text or "**Approval:** Accepted" in wp_text
    assert "never" in wp_text.casefold() or "authorization" in wp_text.casefold()
    w2 = PEER_ASSIGN_W2.read_text(encoding="utf-8")
    assert "臻宇" in w2
    assert "Pass" in w2 and "WP Draft Allowed" in w2
    library = LIBRARY.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert "NRI-RP-002-PEER" in library
    assert "NRI-WP-RP-002" in library
    assert "WHITE_PAPER-RP-002" in index or "RP-002 White Paper" in index
    assert "WHITE_PAPER-RP-002" in status or "WP Draft" in status
