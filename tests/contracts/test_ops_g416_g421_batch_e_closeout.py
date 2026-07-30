"""PHX-G416–G421 Batch E RC HOLD closeout contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CI = ROOT / ".github" / "workflows" / "ci.yml"
CLOSEOUT = ROOT / "docs" / "release" / "RC_HOLD_CLOSEOUT_BATCH_E.md"
RESET = ROOT / "tests" / "integration" / "_db_reset.py"
ROADMAP = ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"
BRANCH_DOC = ROOT / "docs" / "release" / "BRANCH_PROTECTION.md"


def test_g416_g417_ci_docker_smoke_path() -> None:
    wf = CI.read_text(encoding="utf-8")
    assert "docker-smoke" in wf
    assert "smoke_imports.py" in wf
    assert CLOSEOUT.is_file()
    text = CLOSEOUT.read_text(encoding="utf-8")
    assert "CI-PATH READY" in text
    assert "Docker CLI" in text or "docker" in text.casefold()


def test_g418_g419_integration_reset_and_tip_helper() -> None:
    assert RESET.is_file()
    reset = RESET.read_text(encoding="utf-8")
    assert "reset_eaos_test_database" in reset
    assert "DROP SCHEMA" in reset
    # Tip pins must not claim 0049 as current alembic_version in integration
    offenders = []
    for path in (ROOT / "tests" / "integration").glob("test_*.py"):
        text = path.read_text(encoding="utf-8")
        if '== "0049_finance_commission_ledger_g314"' in text:
            offenders.append(path.name)
    assert offenders == []


def test_g420_branch_protection_doc() -> None:
    assert BRANCH_DOC.is_file()
    text = BRANCH_DOC.read_text(encoding="utf-8")
    assert "required" in text.casefold()
    assert "contracts-pr" in text or "pr_required" in text
    assert "human" in text.casefold() or "PO" in text


def test_g421_repair_freeze_lifted_for_feature_batches() -> None:
    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "TRACK-G421 COMPLETE" in roadmap
    assert "REPAIR FREEZE lifted" in roadmap or "REPAIR FREEZE： lifted" in roadmap
    assert "Batch F" in roadmap or "G422" in roadmap
