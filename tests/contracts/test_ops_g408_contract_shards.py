"""PHX-G408 contract shard inventory + required PR budget contracts."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SHARDS = ROOT / "tests" / "contracts" / "shards.yaml"
DOC = ROOT / "docs" / "release" / "CONTRACT_SHARDS.md"
RUNNER = ROOT / "scripts" / "run_contract_shard.py"


def _load() -> dict:
    data = yaml.safe_load(SHARDS.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_g408_shard_manifest_and_docs_exist() -> None:
    assert SHARDS.is_file()
    assert DOC.is_file()
    assert RUNNER.is_file()
    doc = DOC.read_text(encoding="utf-8")
    assert "PHX-G408" in doc
    assert "pr_required" in doc
    assert "≤10" in doc or "600" in doc or "10 minute" in doc.casefold()
    assert "nightly" in doc.casefold()
    assert "ownership" in doc.casefold() or "Ownership" in doc


def test_g408_pr_required_shard_within_budget_definition() -> None:
    data = _load()
    assert data["milestone"] == "PHX-G408"
    assert int(data["budget_seconds_pr_required"]) == 600
    shards = data["shards"]
    assert "pr_required" in shards
    assert "full_contracts" in shards
    pr = shards["pr_required"]
    assert pr["schedule"] == "every_pr"
    assert int(pr["budget_seconds"]) <= 600
    paths = pr["paths"]
    assert paths, "pr_required must list explicit paths"
    for rel in paths:
        path = ROOT / rel
        assert path.is_file(), rel


def test_g408_domain_shards_declare_ownership_and_schedule() -> None:
    shards = _load()["shards"]
    required = {
        "baseline",
        "ops_release",
        "docs",
        "openapi_auth",
        "openapi_terminal",
        "openapi_remainder",
        "domain_runtime",
        "integration_critical",
        "full_contracts",
    }
    assert required <= set(shards)
    for name in required:
        shard = shards[name]
        assert shard.get("ownership"), name
        assert shard.get("schedule") in {
            "nightly",
            "nightly_or_parallel",
            "every_pr",
        }, name


def test_g408_docs_publish_duration_honesty() -> None:
    text = DOC.read_text(encoding="utf-8")
    folded = text.casefold()
    assert "duration" in folded or "wall-clock" in folded
    assert "do not hide" in folded or "publish" in folded
    assert "full" in folded and ("nightly" in folded or "parallel" in folded)
