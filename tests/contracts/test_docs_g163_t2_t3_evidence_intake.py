"""PHX-G163 T2/T3 Evidence Intake & Live Capture board contracts."""

from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from eaos_sdk.catalog import load_release_manifest

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0180-t2-t3-evidence-intake-live-capture.md"
GATE = ROOT / "docs" / "project" / "PHX-G163_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G163_ACCEPTANCE.md"
INTAKE = ROOT / "docs" / "research" / "T2_T3_EVIDENCE_INTAKE.md"
TEMPLATE = ROOT / "docs" / "research" / "templates" / "LIVE_EVIDENCE_CAPTURE_TEMPLATE.md"
READINESS = ROOT / "docs" / "research" / "T2_T3_EVIDENCE_READINESS.md"
INDEX = ROOT / "docs" / "research" / "RESEARCH_INDEX.md"
LIBRARY = ROOT / "docs" / "research" / "RESEARCH_LIBRARY.md"
TIP = ROOT / "docs" / "research" / "GENERATION2_TIP_BOARD.md"
ENG_TIP = ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"


def test_g163_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "NRI-T2-T3-INTAKE" in adr or "T2_T3_EVIDENCE_INTAKE" in adr
    assert "0.2.1" in adr
    assert "PHX-G163" in adr
    assert "DAL-U034" in adr
    assert "0" in adr and ("Complete" in adr or "complete" in adr.casefold())


def test_g163_intake_affirms_zero_complete_and_bars() -> None:
    assert INTAKE.is_file()
    assert TEMPLATE.is_file()
    text = INTAKE.read_text(encoding="utf-8")
    assert "NRI-T2-T3-INTAKE" in text
    assert "0 / 10" in text or "0/10" in text
    assert "0 Complete" in text
    assert "T2" in text and "T3" in text
    assert "Intake checklist" in text or "intake checklist" in text.casefold()
    assert "Verification" in text or "verification" in text.casefold()
    assert "Live Capture Registry" in text or "registry" in text.casefold()
    for rp in range(1, 11):
        assert f"RP-{rp:03d}" in text
    folded = text.casefold()
    assert "brain" in folded and "twin" in folded
    assert "does not" in folded or "not" in folded
    assert "DAL-U034" in text
    assert "PHX-G163" in text
    assert "10 Open" in text or "| **Open** |" in text
    tpl = TEMPLATE.read_text(encoding="utf-8")
    assert "mode" in tpl.casefold() and "live" in tpl.casefold()
    assert "I1" in tpl and "V1" in tpl


def test_g163_readiness_still_t1_zero_complete() -> None:
    text = READINESS.read_text(encoding="utf-8")
    assert "NRI-T2-T3-EVID" in text
    assert "0 / 10" in text or "0/10" in text
    assert "T2_T3_EVIDENCE_INTAKE" in text or "NRI-T2-T3-INTAKE" in text
    assert "Current floor" in text or "current floor" in text.casefold()
    assert "**T1**" in text or "| **T1** |" in text


def test_g163_registry_tips_ledger_status() -> None:
    assert "T2_T3_EVIDENCE_INTAKE" in INDEX.read_text(encoding="utf-8") or "NRI-T2-T3-INTAKE" in INDEX.read_text(
        encoding="utf-8"
    )
    assert "NRI-T2-T3-INTAKE" in LIBRARY.read_text(encoding="utf-8")
    tip = TIP.read_text(encoding="utf-8")
    assert "T2_T3_EVIDENCE_INTAKE" in tip or "NRI-T2-T3-INTAKE" in tip
    assert "PHX-G163" in tip
    eng = ENG_TIP.read_text(encoding="utf-8")
    assert "PHX-G163" in eng or "NRI-T2-T3-INTAKE" in eng or "T2_T3_EVIDENCE_INTAKE" in eng
    assert "DAL-U034" in LEDGER.read_text(encoding="utf-8")
    assert "PHX-G163" in STATUS.read_text(encoding="utf-8")


def test_g163_manifest_and_baseline() -> None:
    manifest = load_release_manifest()
    assert manifest["version"] == "0.2.5"
    assert manifest["alembic_head"] == "0092_finance_realized_fx_gl_bridge_g372"
    by_id = {m["id"]: m for m in manifest["milestones"]}
    assert "PHX-G163" in by_id
    assert by_id["PHX-G163"]["status"] == "fully_accepted"
    scripts = ScriptDirectory.from_config(Config(str(ROOT / "alembic.ini")))
    assert scripts.get_current_head() == "0092_finance_realized_fx_gl_bridge_g372"


def test_g163_fail_closed_holds() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (ADR, GATE, ACCEPTANCE, INTAKE)
    )
    folded = combined.casefold()
    assert "brain" in folded and "execute" in folded
    assert "twin" in folded and "authorize" in folded
    assert "payment" in folded or "支付" in combined
