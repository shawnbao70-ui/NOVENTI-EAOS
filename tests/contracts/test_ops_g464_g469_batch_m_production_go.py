"""PHX-G464–G469 Batch M production-GO evidence decision contracts."""

from __future__ import annotations

from pathlib import Path

from tests.contracts._baseline import EXPECTED_PACKAGE, EXPECTED_TIP

ROOT = Path(__file__).resolve().parents[2]
DECISION = ROOT / "docs" / "release" / "PRODUCTION_GO_DECISION_G469.md"
BRANCH = ROOT / "docs" / "release" / "BRANCH_PROTECTION.md"
RUNBOOK = ROOT / "docs" / "release" / "OPERATIONS_RUNBOOK.md"
CHECKLIST = ROOT / "docs" / "release" / "RELEASE_CHECKLIST.md"
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


def test_g464_branch_protection_requires_human_evidence() -> None:
    text = BRANCH.read_text(encoding="utf-8")
    assert "UNVERIFIED" in text
    assert "human" in text.casefold() or "repo-admin" in text
    assert "candidate commit SHA" in text


def test_g465_docker_smoke_definition_is_not_history() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "docker-smoke" in workflow
    assert "docker build" in workflow
    decision = DECISION.read_text(encoding="utf-8")
    assert "UNVERIFIED HISTORY" in decision
    assert "local Docker" in decision


def test_g466_g467_pg_attempt_and_fail_closed_decision() -> None:
    decision = DECISION.read_text(encoding="utf-8")
    assert "integration_critical" in decision
    assert "BLOCKED" in decision
    assert "NO-GO" in decision
    assert "does not replace" in decision


def test_g468_operator_pointers_and_g469_holds() -> None:
    assert "Production GO evidence" in RUNBOOK.read_text(encoding="utf-8")
    checklist = CHECKLIST.read_text(encoding="utf-8")
    assert EXPECTED_PACKAGE == "0.2.5"
    assert EXPECTED_TIP.startswith("0092")
    assert "PRODUCTION_GO_DECISION_G469.md" in checklist
    decision = DECISION.read_text(encoding="utf-8")
    for fence in ("external PSP", "bank-file", "Industry host-install", "WebAuthn"):
        assert fence in decision
