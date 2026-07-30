"""NRI Research Track — RP-001 Evidence Pack / Deliverables contracts (Dual-Track)."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RP001 = ROOT / "docs" / "research" / "programs" / "RP-001-enterprise-discovery"
EVID = RP001 / "EVIDENCE_PACK.md"
DELIV = RP001 / "DELIVERABLES-RP-001.md"
EDF = RP001 / "ENTERPRISE_DISCOVERY_FRAMEWORK.md"
WT_DIR = RP001 / "walkthroughs"
WT_FILES = (
    WT_DIR / "WT-01-mid-mfg-synthetic.md",
    WT_DIR / "WT-02-services-synthetic.md",
    WT_DIR / "WT-03-stage-contrast-synthetic.md",
)
IND = RP001 / "INDUSTRY_ANALYSIS.md"
RISK = RP001 / "RISK_ANALYSIS.md"
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"


def test_rp001_evidence_pack_and_deliverables_exist() -> None:
    assert EVID.is_file()
    assert DELIV.is_file()
    assert EDF.is_file()


def test_rp001_evidence_pack_defines_wp_gate_without_promotion() -> None:
    text = EVID.read_text(encoding="utf-8")
    assert "NRI-RP-001-EVID" in text
    assert "Claim Register" in text or "Claim ID" in text
    assert "WT-01" in text and "WT-02" in text and "WT-03" in text
    assert "White Paper" in text
    assert "shall **not**" in text or "shall not" in text.casefold()
    assert "Constitution" in text and "Blueprint" in text
    assert "Kernel" in text and "Runtime" in text
    assert "Research Library" in text


def test_rp001_deliverables_track_charter_sixteen() -> None:
    text = DELIV.read_text(encoding="utf-8")
    assert "NRI-RP-001-DELIV" in text
    for n in range(1, 17):
        assert f"| {n} |" in text or f"|{n}|" in text.replace(" ", "")
    assert "White Paper" in text
    assert "Architecture Review" in text
    assert "No" in text  # Architecture Review not ready


def test_rp001_registry_and_status_point_to_evidence_pack() -> None:
    index = INDEX.read_text(encoding="utf-8")
    library = LIBRARY.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    edf = EDF.read_text(encoding="utf-8")
    assert "EVIDENCE_PACK" in index or "Evidence Pack" in index
    assert "NRI-RP-001-EVID" in library
    assert "NRI-RP-001-DELIV" in library
    assert "Evidence Pack" in status or "EVIDENCE" in status
    assert "EVIDENCE_PACK.md" in edf
    assert "WT-01" in edf or "walkthrough" in edf.casefold()


def test_rp001_synthetic_walkthroughs_complete() -> None:
    assert (WT_DIR / "README.md").is_file()
    for path in WT_FILES:
        assert path.is_file(), path
        text = path.read_text(encoding="utf-8")
        assert "mode: synthetic" in text or "Mode:** synthetic" in text
        assert "domains_completed" in text
        assert "cap_org_separated" in text
        assert "auto_execution_implied: never" in text or "Auto-execution | **never**" in text
        assert "Constitution" in text and "Runtime" in text
    evid = EVID.read_text(encoding="utf-8")
    assert "Synthetic Complete" in evid
    assert "≥3 walkthrough instances completed | **Yes**" in evid.replace(" ", "") or (
        "walkthrough instances completed" in evid and "**Yes**" in evid
    )
    library = LIBRARY.read_text(encoding="utf-8")
    assert "NRI-RP-001-WT-01" in library
    assert "NRI-RP-001-WT-02" in library
    assert "NRI-RP-001-WT-03" in library
    status = STATUS.read_text(encoding="utf-8")
    assert "RP-001" in status
    assert "PEER_REVIEW" in status or "peer" in status.casefold() or "reviewer" in status.casefold()


def test_rp001_industry_and_risk_drafts() -> None:
    assert IND.is_file()
    assert RISK.is_file()
    ind = IND.read_text(encoding="utf-8")
    risk = RISK.read_text(encoding="utf-8")
    assert "NRI-RP-001-IND" in ind
    assert "Status:** Draft" in ind or "**Status:** Draft" in ind
    assert "P1" in ind and "P10" in ind
    assert "license theater" in ind.casefold() or "License theater" in ind
    assert "NRI-RP-001-RISK" in risk
    assert "R-ED-01" in risk and "R-ED-14" in risk
    assert "auto-execution" in risk.casefold() or "Auto-execution" in risk
    assert "Constitution" in risk and "Runtime" in risk
    deliv = DELIV.read_text(encoding="utf-8")
    assert "| 2 | Industry Analysis | Draft |" in deliv
    assert "| 15 | Risk Analysis | Draft |" in deliv
    library = LIBRARY.read_text(encoding="utf-8")
    assert "NRI-RP-001-IND" in library
    assert "NRI-RP-001-RISK" in library
    status = STATUS.read_text(encoding="utf-8")
    assert "RP-001" in status
    assert "PEER_REVIEW" in status or "reviewer" in status.casefold()
