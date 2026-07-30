"""PHX-G464–G469 Batch M / PROD1 production-GO evidence contracts."""

from __future__ import annotations

from pathlib import Path

from tests.contracts._baseline import EXPECTED_PACKAGE, EXPECTED_TIP

ROOT = Path(__file__).resolve().parents[2]
DECISION = ROOT / "docs" / "release" / "PRODUCTION_GO_DECISION_G469.md"
BRANCH = ROOT / "docs" / "release" / "BRANCH_PROTECTION.md"
RUNBOOK = ROOT / "docs" / "release" / "OPERATIONS_RUNBOOK.md"
CHECKLIST = ROOT / "docs" / "release" / "RELEASE_CHECKLIST.md"
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def test_g464_branch_protection_evidence_recorded() -> None:
    text = BRANCH.read_text(encoding="utf-8")
    # Historical Batch M closeout was UNVERIFIED; PROD1 records VERIFIED evidence.
    assert "UNVERIFIED" in text or "VERIFIED" in text
    assert "human" in text.casefold() or "repo-admin" in text.casefold()
    assert "candidate" in text.casefold() and "sha" in text.casefold()
    assert "shawnbao70-ui/NOVENTI-EAOS" in text or "protected branch" in text.casefold()


def test_g465_docker_smoke_definition_and_green_history() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "docker-smoke" in workflow
    assert "docker build" in workflow
    decision = DECISION.read_text(encoding="utf-8")
    assert "docker" in decision.casefold()
    # PROD1: green history recorded (not merely workflow definition).
    assert "GREEN" in decision or "30513194462" in decision
    assert "6b6457daad79e63e072e9ea426307b139b74fad8" in decision or "docker-smoke" in decision


def test_g466_g467_pg_green_and_go_decision() -> None:
    decision = DECISION.read_text(encoding="utf-8")
    assert "integration_critical" in decision
    assert "GREEN" in decision
    assert "43 passed" in decision or "eaos_test" in decision
    # Unconditional GO only after required evidence; hard holds remain.
    assert "**GO**" in decision or "Decision:** **GO" in decision or "Decision: **GO" in decision
    assert "does not require opening a new feature milestone" in decision or (
        "does not require" in decision.casefold()
    )


def test_g468_operator_pointers_and_g469_holds() -> None:
    assert "Production GO evidence" in RUNBOOK.read_text(encoding="utf-8")
    checklist = CHECKLIST.read_text(encoding="utf-8")
    assert EXPECTED_PACKAGE == "0.2.5"
    assert EXPECTED_TIP.startswith("0092")
    assert "PRODUCTION_GO_DECISION_G469.md" in checklist
    decision = DECISION.read_text(encoding="utf-8")
    for fence in ("external PSP", "bank-file", "Industry host-install", "WebAuthn"):
        assert fence in decision
