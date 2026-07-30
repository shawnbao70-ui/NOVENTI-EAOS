"""NRI Research Track — RP-007 Evidence Pack / Input Freeze / Trigger Tests."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RP007 = ROOT / "docs" / "research" / "programs" / "RP-007-enterprise-evolution-engine"
EVID = RP007 / "EVIDENCE_PACK.md"
DELIV = RP007 / "DELIVERABLES-RP-007.md"
IFRZ = RP007 / "INPUT_FREEZE.md"
EEM = RP007 / "ENTERPRISE_EVOLUTION_MODEL.md"
TT_DIR = RP007 / "trigger-tests"
TT_FILES = (
    TT_DIR / "TT-01-hold-low-potential.md",
    TT_DIR / "TT-02-assist-not-agentize.md",
    TT_DIR / "TT-03-robot-hold-safety.md",
)
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"


def test_rp007_pack_freeze_and_deliverables_exist() -> None:
    assert EVID.is_file()
    assert DELIV.is_file()
    assert IFRZ.is_file()
    evid = EVID.read_text(encoding="utf-8")
    assert "NRI-RP-007-EVID" in evid
    assert "C-EE-01" in evid and "C-EE-10" in evid
    assert "REC-HOLD" in evid
    assert "execution_authority" in evid
    assert "NRI-RP-007-DELIV" in DELIV.read_text(encoding="utf-8")
    assert "WT-01" in IFRZ.read_text(encoding="utf-8")
    assert "RI-01" in IFRZ.read_text(encoding="utf-8")
    assert "EVIDENCE_PACK.md" in EEM.read_text(encoding="utf-8")


def test_rp007_trigger_tests_hold_and_no_execution() -> None:
    assert (TT_DIR / "README.md").is_file()
    for path in TT_FILES:
        text = path.read_text(encoding="utf-8")
        assert "Synthetic Complete" in text or "status: Synthetic Complete" in text.casefold()
        assert "execution_authority: none" in text
        assert "hold_present: yes" in text
        assert "anti_execution_ok: yes" in text
    evid = EVID.read_text(encoding="utf-8")
    assert "TT-01" in evid and "TT-02" in evid and "TT-03" in evid
    assert "Synthetic Complete" in evid


def test_rp007_registry_and_wave1_status() -> None:
    index = INDEX.read_text(encoding="utf-8")
    library = LIBRARY.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    assert "NRI-RP-007-EVID" in library or "Evolution Engine Evidence Pack" in library
    assert "NRI-RP-007-IFRZ" in library or "Input Freeze" in library
    assert "NRI-RP-007-TT-01" in library
    assert "Trigger Tests" in index or "TT-01" in index
    assert "RP-007" in status
    assert "peer" in status.casefold() or "PEER" in status
