"""PHX-G155 T2/T3 Evidence Readiness Board contracts."""

from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from eaos_sdk.catalog import load_release_manifest

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0174-t2-t3-evidence-readiness-board.md"
GATE = ROOT / "docs" / "project" / "PHX-G155_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G155_ACCEPTANCE.md"
BOARD = ROOT / "docs" / "research" / "T2_T3_EVIDENCE_READINESS.md"
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
TIP = ROOT / "docs" / "research" / "GENERATION2_TIP_BOARD.md"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"


def test_g155_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "NRI-T2-T3-EVID" in adr or "T2_T3_EVIDENCE_READINESS" in adr
    assert "0.2.1" in adr
    assert "T1" in adr


def test_g155_board_affirms_t1_floor_no_live_upgrade() -> None:
    assert BOARD.is_file()
    text = BOARD.read_text(encoding="utf-8")
    assert "NRI-T2-T3-EVID" in text
    assert "T1" in text and "T2" in text and "T3" in text
    assert "0 / 10" in text or "0/10" in text
    assert "Current floor" in text or "current floor" in text.casefold()
    for rp in range(1, 11):
        assert f"RP-{rp:03d}" in text
    folded = text.casefold()
    assert "does not" in folded or "not" in folded
    assert "brain" in folded and "twin" in folded
    assert "synthetic" in folded or "T1" in text
    # must not claim live T2/T3 complete for the board aggregate
    assert "none registered as Complete" in text or "0 / 10" in text
    assert "DAL-U027" in text
    assert "PHX-G155" in text


def test_g155_registry_and_tips() -> None:
    assert "T2_T3_EVIDENCE_READINESS" in INDEX.read_text(encoding="utf-8") or "NRI-T2-T3-EVID" in INDEX.read_text(
        encoding="utf-8"
    )
    assert "NRI-T2-T3-EVID" in LIBRARY.read_text(encoding="utf-8")
    tip = TIP.read_text(encoding="utf-8")
    assert "T2_T3_EVIDENCE_READINESS" in tip or "NRI-T2-T3-EVID" in tip
    assert "DAL-U027" in LEDGER.read_text(encoding="utf-8")
    assert "PHX-G155" in STATUS.read_text(encoding="utf-8")


def test_g155_manifest_and_baseline() -> None:
    manifest = load_release_manifest()
    assert manifest["version"] == "0.2.5"
    assert manifest["alembic_head"] == "0092_finance_realized_fx_gl_bridge_g372"
    by_id = {m["id"]: m for m in manifest["milestones"]}
    assert "PHX-G155" in by_id
    assert by_id["PHX-G155"]["status"] == "fully_accepted"
    scripts = ScriptDirectory.from_config(Config(str(ROOT / "alembic.ini")))
    assert scripts.get_current_head() == "0092_finance_realized_fx_gl_bridge_g372"
