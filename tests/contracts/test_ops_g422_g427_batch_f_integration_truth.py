"""PHX-G422–G427 Batch F integration tip / suite truth contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESET = ROOT / "tests" / "integration" / "_db_reset.py"
SHARDS = ROOT / "docs" / "release" / "CONTRACT_SHARDS.md"
ROADMAP = ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"
BASELINE = ROOT / "tests" / "contracts" / "_baseline.py"


def test_g422_migration_forward_only_posture() -> None:
    reset = RESET.read_text(encoding="utf-8")
    assert "reset_eaos_test_database" in reset
    assert "DROP SCHEMA" in reset
    # Mid-chain downgrade remains deferred / skipped — not claimed green.
    assert "alembic_current_head" in BASELINE.read_text(encoding="utf-8")


def test_g423_g426_integration_critical_shard_present() -> None:
    shards_yaml = (ROOT / "tests" / "contracts" / "shards.yaml").read_text(encoding="utf-8")
    assert "integration_critical" in shards_yaml
    assert "EAOS_RUN_INTEGRATION_CRITICAL" in (
        ROOT / "tests" / "contracts" / "test_ops_g414_pg_integration_subset.py"
    ).read_text(encoding="utf-8")


def test_g427_duration_published() -> None:
    text = SHARDS.read_text(encoding="utf-8")
    assert "integration_critical" in text.casefold() or "DURATION" in text
    assert "0.2.4" in text or "EXPECTED" in text or "0092" in text


def test_g422_g427_roadmap_markers() -> None:
    roadmap = ROADMAP.read_text(encoding="utf-8")
    for marker in (
        "TRACK-G422 COMPLETE",
        "TRACK-G427 COMPLETE",
        "TRACK-BATCH-F-DURATION-PUBLISH COMPLETE",
    ):
        assert marker in roadmap
