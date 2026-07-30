"""PHX-G150 Autonomous Execution Directive documentation contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0169-autonomous-execution-directive.md"
AED = ROOT / "docs" / "project" / "AUTONOMOUS_EXECUTION_DIRECTIVE.md"
GATE = ROOT / "docs" / "project" / "PHX-G150_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G150_ACCEPTANCE.md"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
PLAYBOOK = ROOT / "docs" / "project" / "DUAL_TRACK_GOVERNANCE.md"
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"
CHANGELOG = ROOT / "docs" / "project" / "CHANGELOG.md"


def test_g150_artifacts_exist() -> None:
    for path in (ADR, AED, GATE, ACCEPTANCE, LEDGER, PLAYBOOK, STATUS, CHANGELOG):
        assert path.is_file(), path


def test_g150_adr_accepted() -> None:
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "PHX-G150" in adr
    assert "AUTONOMOUS_EXECUTION_DIRECTIVE" in adr or "Autonomous Execution Directive" in adr
    assert "HARD HOLD" in adr or "HARD HOLDS" in adr
    assert "DAL-G004" in adr
    assert "Constitution" in adr or "Blueprint" in adr


def test_g150_aed_v11_hard_holds_and_rules() -> None:
    aed = AED.read_text(encoding="utf-8")
    assert "1.1" in aed
    assert "HARD HOLD" in aed or "HARD HOLDS" in aed
    assert "暂缓" in aed or "payment" in aed.casefold() or "Opened" in aed or "PHX-G162" in aed
    assert "Brain" in aed and "Twin" in aed
    assert "Cap" in aed or "grant" in aed.casefold()
    assert "Architecture Review" in aed
    assert "self-cert" in aed.casefold() or "自证" in aed or "self-promote" in aed.casefold()
    assert "2026-07-27" in aed
    assert "Usage Log" in aed or "DAL" in aed
    assert "Architectural quality" in aed or "architectural quality" in aed.casefold()
    assert "Architecture Review Candidate" in aed
    assert "WebAuthn" in aed
    assert "OpenAPI" in aed
    assert "Dual-Track" in aed or "DUAL_TRACK" in aed


def test_g150_gate_acceptance_docs_only() -> None:
    gate = GATE.read_text(encoding="utf-8")
    acceptance = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Fully Accepted" in gate
    assert "docs-only" in gate.casefold() or "docs-only" in gate
    assert "0.2.1" in gate or "0029" in gate
    assert "Fully Accepted" in acceptance
    assert "DAL-U012" in acceptance
    assert "0.2.1" in acceptance
    assert "0029" in acceptance
    assert "Brain" in acceptance and "Twin" in acceptance


def test_g150_dal_g004_u012() -> None:
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-G004" in ledger
    assert "DAL-U012" in ledger
    assert "AED" in ledger or "AUTONOMOUS_EXECUTION" in ledger or "Autonomous Execution" in ledger
    assert "PHX-G150" in ledger
    assert "Active" in ledger


def test_g150_dual_track_and_status_link_aed() -> None:
    playbook = PLAYBOOK.read_text(encoding="utf-8")
    status = STATUS.read_text(encoding="utf-8")
    changelog = CHANGELOG.read_text(encoding="utf-8")
    assert "AUTONOMOUS_EXECUTION_DIRECTIVE" in playbook
    assert "AED" in playbook or "1.1" in playbook
    assert "PHX-G150" in status
    assert "AUTONOMOUS_EXECUTION_DIRECTIVE" in status or "AED" in status
    assert "DAL-G004" in status or "DAL-U012" in status
    assert "PHX-G150" in changelog
    assert "AUTONOMOUS_EXECUTION_DIRECTIVE" in changelog or "AED" in changelog
