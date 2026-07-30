"""NRI Research Track — RP-008 Smart Factory Specialization Model contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RP008 = ROOT / "docs" / "research" / "programs" / "RP-008-smart-factory"
SFSM = RP008 / "SMART_FACTORY_SPECIALIZATION_MODEL.md"
EVID = RP008 / "EVIDENCE_PACK.md"
DELIV = RP008 / "DELIVERABLES-RP-008.md"
README = RP008 / "README.md"
PW_DIR = RP008 / "walkthroughs"
PW_FILES = (
    PW_DIR / "PW-01-discrete-cell.md",
    PW_DIR / "PW-02-line-terminal-ot.md",
)
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"
ROADMAP = ROOT / "docs" / "research" / "RESEARCH_ROADMAP.md"
WAVE3 = ROOT / "docs" / "research" / "WAVE3_PEER_ASSIGNMENT.md"


def test_rp008_sfsm_artifacts_exist() -> None:
    assert SFSM.is_file()
    assert EVID.is_file()
    assert DELIV.is_file()


def test_rp008_sfsm_domains_and_non_mes_fork() -> None:
    text = SFSM.read_text(encoding="utf-8")
    assert "NRI-RP-008-SFSM" in text
    assert "Research Draft" in text
    assert "SF-01" in text and "SF-08" in text
    assert "PR0" in text and "PR4" in text
    assert "V-SF-01" in text
    assert "MES" in text or "mes" in text.casefold()
    assert "never" in text.casefold() or "fork" in text.casefold()
    assert "Brain" in text
    assert "machine" in text.casefold() or "Robot" in text


def test_rp008_status_research_and_registry() -> None:
    readme = README.read_text(encoding="utf-8")
    assert "**Status:** Research" in readme
    assert "SMART_FACTORY_SPECIALIZATION_MODEL.md" in readme
    library = LIBRARY.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "NRI-RP-008-SFSM" in library
    assert "NRI-RP-008-EVID" in library
    assert "Smart Factory Specialization Model" in index or "SFSM" in index
    assert "RP-008" in status
    assert "SFSM" in status or "PW-01" in status
    assert "SFSM" in roadmap or "RP-008" in roadmap


def test_rp008_peer_pass_zhenyu_wp_draft() -> None:
    assert (PW_DIR / "README.md").is_file()
    for path in PW_FILES:
        text = path.read_text(encoding="utf-8")
        assert "Synthetic Complete" in text
        assert "mes_kernelization: never" in text
        assert "machine_control_from_brain: never" in text
    evid = EVID.read_text(encoding="utf-8")
    assert "C-SF-01" in evid
    assert "PW-01" in evid and "PW-02" in evid
    assert "Synthetic Complete" in evid
    assert "mes_kernelization" in evid.casefold() or "MES" in evid
    assert "≥2 synthetic plant overlays** | **Yes**" in evid or (
        "plant overlays" in evid.casefold() and "**Yes**" in evid
    )
    ind = RP008 / "INDUSTRY_ANALYSIS.md"
    risk = RP008 / "RISK_ANALYSIS.md"
    peer = RP008 / "PEER_REVIEW_PACKAGE.md"
    assert ind.is_file() and risk.is_file() and peer.is_file()
    assert "NRI-RP-008-IND" in ind.read_text(encoding="utf-8")
    assert "P-SF-01" in ind.read_text(encoding="utf-8")
    assert "NRI-RP-008-RISK" in risk.read_text(encoding="utf-8")
    assert "R-SF-01" in risk.read_text(encoding="utf-8")
    peer_text = peer.read_text(encoding="utf-8")
    assert "NRI-RP-008-PEER" in peer_text
    assert "臻宇" in peer_text
    assert "Pass — WP Draft Allowed" in peer_text
    assert "PR-SF-01" in peer_text and "PR-SF-12" in peer_text
    assert "**Yes / Pass**" in peer_text
    assert "Selected outcome:** **Pass → WP Draft Allowed**" in peer_text or (
        "Selected outcome:" in peer_text and "Pass → WP Draft Allowed" in peer_text
    )
    assert "mes_kernelization: never" in peer_text
    assert "machine_control_from_brain: never" in peer_text
    wp = RP008 / "WHITE_PAPER-RP-008.md"
    assert wp.is_file()
    wp_text = wp.read_text(encoding="utf-8")
    assert "NRI-WP-RP-008" in wp_text
    assert "**Status:** Accepted White Paper" in wp_text
    assert "Approval:** Accepted" in wp_text or "**Approval:** Accepted" in wp_text
    assert "mes_kernelization" in wp_text.casefold() or "never" in wp_text.casefold()
    assert "machine_control_from_brain" in wp_text.casefold() or "never" in wp_text.casefold()
    deliv = DELIV.read_text(encoding="utf-8")
    assert "INDUSTRY_ANALYSIS.md" in deliv and "RISK_ANALYSIS.md" in deliv
    assert "WHITE_PAPER-RP-008" in deliv
    library = LIBRARY.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert WAVE3.is_file()
    w3 = WAVE3.read_text(encoding="utf-8")
    assert "NRI-RP-008-PW-01" in library
    assert "NRI-RP-008-IND" in library and "NRI-RP-008-PEER" in library
    assert "NRI-WP-RP-008" in library
    assert "臻宇" in library
    assert "PW-01" in index or "Plant Walkthroughs" in index
    assert "WHITE_PAPER-RP-008" in index or "RP-008 White Paper" in index
    assert "臻宇" in status and "RP-008" in status
    assert "WHITE_PAPER-RP-008" in status or "WP-008" in status or "WP Draft" in status
    assert "SFSM" in status or "PW-01" in status
    assert "RP-008 peer = 臻宇" in w3 or "臻宇" in w3
    assert "Pass" in w3 and "WP Draft Allowed" in w3
    assert "WHITE_PAPER-RP-008" in w3 or "RP-008" in w3
