"""PHX-G158 Autonomous Soft-Queue Natural Pause contracts."""

from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

from eaos_sdk.catalog import load_release_manifest

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0177-autonomous-soft-queue-natural-pause.md"
GATE = ROOT / "docs" / "project" / "PHX-G158_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G158_ACCEPTANCE.md"
TIP = ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"


def test_g158_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "0.2.1" in adr
    assert "Pause" in adr or "pause" in adr.casefold()


def test_g158_tip_records_natural_pause() -> None:
    tip = TIP.read_text(encoding="utf-8")
    assert "Natural Pause" in tip or "natural pause" in tip.casefold()
    assert "PHX-G158" in tip
    assert "Board" in tip
    assert "explicit PO" in tip.casefold() or "PO" in tip
    assert "Brain" in tip and "Twin" in tip
    # must not claim invent continues by default
    assert "do not invent" in tip.casefold() or "不" in tip and "invent" in tip.casefold() or "Pause" in tip


def test_g158_status_and_ledger() -> None:
    assert "PHX-G158" in STATUS.read_text(encoding="utf-8")
    assert "DAL-U030" in LEDGER.read_text(encoding="utf-8")
    manifest = load_release_manifest()
    assert manifest["version"] == "0.2.5"
    by_id = {m["id"]: m for m in manifest["milestones"]}
    assert by_id["PHX-G158"]["status"] == "fully_accepted"
    scripts = ScriptDirectory.from_config(Config(str(ROOT / "alembic.ini")))
    assert scripts.get_current_head() == "0092_finance_realized_fx_gl_bridge_g372"
