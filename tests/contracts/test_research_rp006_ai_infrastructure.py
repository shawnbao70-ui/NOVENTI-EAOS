"""NRI Research Track — RP-006 AI Infrastructure Reference Model contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RP006 = ROOT / "docs" / "research" / "programs" / "RP-006-ai-infrastructure-platform"
AIRM = RP006 / "AI_INFRASTRUCTURE_REFERENCE_MODEL.md"
EVID = RP006 / "EVIDENCE_PACK.md"
DELIV = RP006 / "DELIVERABLES-RP-006.md"
README = RP006 / "README.md"
GP_DIR = RP006 / "gap-profiles"
GP_FILES = (
    GP_DIR / "GP-01-cloud-native.md",
    GP_DIR / "GP-02-hybrid-ot.md",
)
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"
ROADMAP = ROOT / "docs" / "research" / "RESEARCH_ROADMAP.md"
WAVE3 = ROOT / "docs" / "research" / "WAVE3_PEER_ASSIGNMENT.md"


def test_rp006_airm_artifacts_exist() -> None:
    assert AIRM.is_file()
    assert EVID.is_file()
    assert DELIV.is_file()


def test_rp006_airm_domains_and_non_bypass() -> None:
    text = AIRM.read_text(encoding="utf-8")
    assert "NRI-RP-006-AIRM" in text
    assert "Research Draft" in text
    assert "ID-01" in text and "ID-08" in text
    assert "I0" in text and "I4" in text
    assert "V-INF-01" in text
    assert "ADR-0027" in text
    assert "never" in text.casefold() or "bypass" in text.casefold()
    assert "Kernel" in text
    assert "Approval" in text or "approval" in text


def test_rp006_status_research_and_registry() -> None:
    readme = README.read_text(encoding="utf-8")
    assert "**Status:** Research" in readme
    assert "AI_INFRASTRUCTURE_REFERENCE_MODEL.md" in readme
    library = LIBRARY.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "NRI-RP-006-AIRM" in library
    assert "NRI-RP-006-EVID" in library
    assert "AI Infrastructure Reference Model" in index or "AIRM" in index
    assert "RP-006" in status
    assert "AIRM" in status or "GP-01" in status
    assert "AIRM" in roadmap or "RP-006" in roadmap


def test_rp006_peer_pass_zhenyu_wp_draft() -> None:
    assert (GP_DIR / "README.md").is_file()
    for path in GP_FILES:
        text = path.read_text(encoding="utf-8")
        assert "Synthetic Complete" in text
        assert "kernel_bypass: never" in text
        assert "ID-01" in text or "ID-04" in text
    evid = EVID.read_text(encoding="utf-8")
    assert "C-INF-01" in evid
    assert "GP-01" in evid and "GP-02" in evid
    assert "Synthetic Complete" in evid
    assert "kernel_bypass" in evid.casefold() or "Kernel" in evid
    assert "≥2 synthetic gap profiles** | **Yes**" in evid or (
        "gap profiles" in evid.casefold() and "**Yes**" in evid
    )
    ind = RP006 / "INDUSTRY_ANALYSIS.md"
    risk = RP006 / "RISK_ANALYSIS.md"
    peer = RP006 / "PEER_REVIEW_PACKAGE.md"
    assert ind.is_file() and risk.is_file() and peer.is_file()
    assert "NRI-RP-006-IND" in ind.read_text(encoding="utf-8")
    assert "P-INF-01" in ind.read_text(encoding="utf-8")
    assert "NRI-RP-006-RISK" in risk.read_text(encoding="utf-8")
    assert "R-INF-01" in risk.read_text(encoding="utf-8")
    peer_text = peer.read_text(encoding="utf-8")
    assert "NRI-RP-006-PEER" in peer_text
    assert "臻宇" in peer_text
    assert "Pass — WP Draft Allowed" in peer_text
    assert "PR-INF-01" in peer_text and "PR-INF-12" in peer_text
    assert "**Yes / Pass**" in peer_text
    assert "Selected outcome:** **Pass → WP Draft Allowed**" in peer_text or (
        "Selected outcome:" in peer_text and "Pass → WP Draft Allowed" in peer_text
    )
    wp = RP006 / "WHITE_PAPER-RP-006.md"
    assert wp.is_file()
    wp_text = wp.read_text(encoding="utf-8")
    assert "NRI-WP-RP-006" in wp_text
    assert "**Status:** Accepted White Paper" in wp_text
    assert "Approval:** Accepted" in wp_text or "**Approval:** Accepted" in wp_text
    assert "kernel_bypass" in wp_text.casefold() or "never" in wp_text.casefold()
    deliv = DELIV.read_text(encoding="utf-8")
    assert "INDUSTRY_ANALYSIS.md" in deliv and "RISK_ANALYSIS.md" in deliv
    assert "WHITE_PAPER-RP-006" in deliv
    library = LIBRARY.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert WAVE3.is_file()
    w3 = WAVE3.read_text(encoding="utf-8")
    assert "NRI-RP-006-GP-01" in library
    assert "NRI-RP-006-IND" in library and "NRI-RP-006-PEER" in library
    assert "NRI-WP-RP-006" in library
    assert "臻宇" in library
    assert "GP-01" in index or "Gap Profiles" in index
    assert "WHITE_PAPER-RP-006" in index or "RP-006 White Paper" in index
    assert "臻宇" in status and "RP-006" in status
    assert "WHITE_PAPER-RP-006" in status or "WP-006" in status or "WP Draft" in status
    assert "AIRM" in status or "GP-01" in status
    assert "RP-006 peer = 臻宇" in w3 or "臻宇" in w3
    assert "Pass" in w3 and "WP Draft Allowed" in w3
