"""PHX-G414 PostgreSQL critical integration subset inventory contracts."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
INTEGRATION = ROOT / "tests" / "integration"
CRITICAL = (
    "test_postgresql_persistence.py",
    "test_crm_c1_postgresql.py",
    "test_crm_z1_postgresql.py",
    "test_finance_f1_postgresql.py",
    "test_finance_n1_postgresql.py",
    "test_inventory_i1_postgresql.py",
)


def test_g414_critical_pg_suite_files_exist() -> None:
    for name in CRITICAL:
        assert (INTEGRATION / name).is_file(), name
    readme = INTEGRATION / "README.md"
    assert readme.is_file()
    text = readme.read_text(encoding="utf-8")
    assert "EAOS_TEST_DATABASE_URL" in text
    assert "postgresql" in text.casefold()


def test_g414_critical_pg_suite_runs_when_explicitly_opted_in() -> None:
    """Execute critical subset only with explicit opt-in (not every PR).

    Requires both:
    - ``EAOS_TEST_DATABASE_URL`` pointing at dedicated ``eaos_test*``
    - ``EAOS_RUN_INTEGRATION_CRITICAL=1``
    """

    if os.environ.get("EAOS_RUN_INTEGRATION_CRITICAL", "").strip() not in {
        "1",
        "true",
        "TRUE",
        "yes",
        "YES",
    }:
        pytest.skip(
            "EAOS_RUN_INTEGRATION_CRITICAL unset — inventory-only evidence for G414 "
            "(avoids accidental PR coupling to a host DB URL)"
        )
    url = os.environ.get("EAOS_TEST_DATABASE_URL", "").strip()
    if not url:
        pytest.skip("EAOS_TEST_DATABASE_URL unset — inventory-only evidence for G414")
    assert "eaos_test" in url
    import subprocess
    import sys

    paths = [str(INTEGRATION / name) for name in CRITICAL]
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", *paths, "-q", "-m", "postgresql"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
