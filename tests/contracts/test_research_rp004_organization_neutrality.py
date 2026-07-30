"""NRI Research Track — RP-004 Organization Neutrality Model contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RP004 = ROOT / "docs" / "research" / "programs" / "RP-004-organization-neutrality"
ONM = RP004 / "ORGANIZATION_NEUTRALITY_MODEL.md"
EVID = RP004 / "EVIDENCE_PACK.md"
DELIV = RP004 / "DELIVERABLES-RP-004.md"
README = RP004 / "README.md"
AUDIT_DIR = RP004 / "audits"
NA_FILES = (
    AUDIT_DIR / "NA-01-wt01-mfg.md",
    AUDIT_DIR / "NA-02-wt02-svc.md",
)
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"


def test_rp004_onm_artifacts_exist() -> None:
    assert ONM.is_file()
    assert EVID.is_file()
    assert DELIV.is_file()


def test_rp004_onm_principles_and_non_permission() -> None:
    text = ONM.read_text(encoding="utf-8")
    assert "NRI-RP-004-ONM" in text
    assert "Research Draft" in text
    assert "OF-01" in text and "OF-07" in text
    assert "N-01" in text and "N-08" in text
    assert "V-ON-01" in text
    assert "Permission" in text
    assert "never" in text.casefold() or "must not" in text.casefold()
    assert "grant" in text.casefold()


def test_rp004_status_research_and_registry() -> None:
    readme = README.read_text(encoding="utf-8")
    assert "**Status:** Research" in readme
    assert "ORGANIZATION_NEUTRALITY_MODEL.md" in readme
    library = LIBRARY.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert "NRI-RP-004-ONM" in library
    assert "NRI-RP-004-EVID" in library
    assert "Organization Neutrality Model" in index or "ONM" in index
    assert "RP-004" in status


def test_rp004_peer_pass_zhenyu_wp_draft() -> None:
    ind = RP004 / "INDUSTRY_ANALYSIS.md"
    risk = RP004 / "RISK_ANALYSIS.md"
    peer = RP004 / "PEER_REVIEW_PACKAGE.md"
    assert ind.is_file() and risk.is_file() and peer.is_file()
    assert "NRI-RP-004-IND" in ind.read_text(encoding="utf-8")
    assert "P-ON-01" in ind.read_text(encoding="utf-8")
    assert "NRI-RP-004-RISK" in risk.read_text(encoding="utf-8")
    assert "R-ON-01" in risk.read_text(encoding="utf-8")
    peer_text = peer.read_text(encoding="utf-8")
    assert "NRI-RP-004-PEER" in peer_text
    assert "臻宇" in peer_text
    assert "Pass — WP Draft Allowed" in peer_text
    assert "PR-ON-01" in peer_text and "PR-ON-12" in peer_text
    assert "**Yes / Pass**" in peer_text
    assert "Selected outcome:** **Pass → WP Draft Allowed**" in peer_text or (
        "Selected outcome:" in peer_text and "Pass → WP Draft Allowed" in peer_text
    )
    assert "grant" in peer_text.casefold() or "Permission" in peer_text
    wp = RP004 / "WHITE_PAPER-RP-004.md"
    assert wp.is_file()
    wp_text = wp.read_text(encoding="utf-8")
    assert "NRI-WP-RP-004" in wp_text
    assert "**Status:** Accepted White Paper" in wp_text
    assert "Approval:** Accepted" in wp_text or "**Approval:** Accepted" in wp_text
    assert "never" in wp_text.casefold() or "grant" in wp_text.casefold()
    deliv = DELIV.read_text(encoding="utf-8")
    assert "INDUSTRY_ANALYSIS.md" in deliv and "RISK_ANALYSIS.md" in deliv
    assert "WHITE_PAPER-RP-004" in deliv
    library = LIBRARY.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert "NRI-RP-004-IND" in library and "NRI-RP-004-PEER" in library
    assert "NRI-WP-RP-004" in library
    assert "臻宇" in library
    assert "WHITE_PAPER-RP-004" in index or "RP-004 White Paper" in index
    assert "WHITE_PAPER-RP-004" in status or "WP Draft" in status
    assert "臻宇" in status and "RP-004" in status
    w2 = (ROOT / "docs" / "research" / "WAVE2_PEER_ASSIGNMENT.md").read_text(encoding="utf-8")
    assert "RP-004 peer = 臻宇" in w2 or "臻宇" in w2
    assert "Pass" in w2 and "WP Draft Allowed" in w2


def test_rp004_synthetic_audits_complete_and_non_granting() -> None:
    assert (AUDIT_DIR / "README.md").is_file()
    for path in NA_FILES:
        text = path.read_text(encoding="utf-8")
        assert "Synthetic Complete" in text
        assert "org_shape_grant: never" in text
        assert "N-01" in text and "N-08" in text
        assert "cap_ids_stable: yes" in text
    evid = EVID.read_text(encoding="utf-8")
    assert "C-ON-01" in evid
    assert "Synthetic Complete" in evid
    assert "≥2 synthetic neutrality audits** | **Yes**" in evid or (
        "synthetic neutrality audits" in evid and "**Yes**" in evid
    )
    assert "grant" in evid.casefold()
    library = LIBRARY.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert "NRI-RP-004-NA-01" in library
    assert "NRI-RP-004-NA-02" in library
    assert "NA-01" in index or "Neutrality Audits" in index
    assert "NA-01" in status or "NA-01…02" in status
