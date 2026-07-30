"""PHX-G149 Eng soft-queue tip hygiene documentation contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0168-eng-soft-queue-tip-board.md"
GATE = ROOT / "docs" / "project" / "PHX-G149_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G149_ACCEPTANCE.md"
TIP = ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
TASKS = ROOT / "docs" / "project" / "TASKS.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"
CHANGELOG = ROOT / "docs" / "project" / "CHANGELOG.md"
ROADMAP = ROOT / "docs" / "project" / "ROADMAP.md"
PLAYBOOK = ROOT / "docs" / "project" / "DUAL_TRACK_GOVERNANCE.md"


def test_g149_artifacts_exist() -> None:
    for path in (ADR, GATE, ACCEPTANCE, TIP, LEDGER, TASKS, STATUS, CHANGELOG, ROADMAP):
        assert path.is_file(), path


def test_g149_adr_gate_acceptance() -> None:
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "PHX-G149" in adr
    assert "ENG_SOFT_QUEUE_TIP" in adr
    assert "DAL-U010" in adr or "DAL-G003" in adr
    gate = GATE.read_text(encoding="utf-8")
    assert "Fully Accepted" in gate
    assert "docs-only" in gate.casefold() or "docs-only" in gate
    assert "DAL-U010" in gate or "DAL-G003" in gate
    acceptance = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Fully Accepted" in acceptance
    assert "DAL-U010" in acceptance
    assert "0.2.1" in acceptance
    assert "Brain" in acceptance and "Twin" in acceptance


def test_g149_tip_board_done_held_next() -> None:
    tip = TIP.read_text(encoding="utf-8")
    assert "PHX-G144" in tip
    assert "PHX-G145" in tip
    assert "PHX-G146" in tip
    assert "PHX-G147" in tip
    assert "PHX-G148" in tip
    assert "支付" in tip or "payment" in tip.casefold()
    assert "暂缓" in tip or "deferred" in tip.casefold()
    assert "Brain" in tip and "Twin" in tip
    assert "WebAuthn" in tip or "ceremony" in tip.casefold()
    assert "Role" in tip or "grant" in tip.casefold()
    assert "## Next (gated)" in tip
    assert "further Eng invent" in tip


def test_g149_tasks_t0199_t0204_complete() -> None:
    tasks = TASKS.read_text(encoding="utf-8")
    t0199 = [line for line in tasks.splitlines() if "T-0199" in line][0]
    t0204 = [line for line in tasks.splitlines() if "T-0204" in line][0]
    assert "延后" not in t0199
    assert "完成" in t0199
    assert "G138" in t0199
    assert "延后" not in t0204
    assert "完成" in t0204
    assert "G25" in t0204 and "G127" in t0204
    assert "T-0729" in tasks
    assert "PHX-G149" in tasks


def test_g149_dal_u010_recorded() -> None:
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-U010" in ledger
    assert "PHX-G149" in ledger
    assert "ENG_SOFT_QUEUE_TIP" in ledger
    assert "DAL-G003" in ledger


def test_g149_status_changelog_roadmap_point_to_tip() -> None:
    status = STATUS.read_text(encoding="utf-8")
    changelog = CHANGELOG.read_text(encoding="utf-8")
    roadmap = ROADMAP.read_text(encoding="utf-8")
    playbook = PLAYBOOK.read_text(encoding="utf-8")
    assert "PHX-G149" in status
    assert "ENG_SOFT_QUEUE_TIP" in status
    assert "DAL-U010" in status
    assert "PHX-G149" in changelog
    assert "ENG_SOFT_QUEUE_TIP" in changelog
    assert "ENG_SOFT_QUEUE_TIP" in roadmap
    assert "PHX-G149" in roadmap
    assert "ENG_SOFT_QUEUE_TIP" in playbook
