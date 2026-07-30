"""PHX-G410 minimum CI + lock strategy contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
CONSTRAINTS = ROOT / "constraints" / "production.txt"
DOC = ROOT / "docs" / "release" / "CI_AND_LOCK.md"
DOCKERFILE = ROOT / "deploy" / "docker" / "Dockerfile"


def test_g410_ci_workflow_and_constraints_exist() -> None:
    assert WORKFLOW.is_file()
    assert CONSTRAINTS.is_file()
    assert DOC.is_file()
    wf = WORKFLOW.read_text(encoding="utf-8")
    assert "python-version" in wf
    assert "3.11" in wf and "3.12" in wf
    assert "pip check" in wf
    assert "run_contract_shard.py pr_required" in wf
    assert "helm lint" in wf
    assert "smoke_imports.py" in wf


def test_g410_constraints_pin_direct_deps() -> None:
    text = CONSTRAINTS.read_text(encoding="utf-8")
    for pin in (
        "fastapi==",
        "httpx==",
        "uvicorn==",
        "alembic==",
        "SQLAlchemy==",
        "psycopg[binary]==",
        "cryptography==",
        "PyYAML==",
        "pytest==",
    ):
        assert pin in text, pin
    assert "-c constraints/production.txt" in DOC.read_text(encoding="utf-8")
    assert "-c /constraints/production.txt" in DOCKERFILE.read_text(encoding="utf-8")
