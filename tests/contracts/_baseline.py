"""Authoritative contract baseline (PHX-G406).

Current tip / package are sourced from Alembic + RELEASE_MANIFEST only.
Do not copy tip/package literals into individual contracts.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from alembic.config import Config
from alembic.script import ScriptDirectory

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"
ALEMBIC_INI = ROOT / "alembic.ini"
HISTORICAL_COMMISSION_LEDGER_REV = "0049_finance_commission_ledger_g314"


@lru_cache(maxsize=1)
def _load_manifest() -> dict:
    data = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise AssertionError("RELEASE_MANIFEST.yaml must parse to a mapping")
    return data


def alembic_current_head() -> str:
    scripts = ScriptDirectory.from_config(Config(str(ALEMBIC_INI)))
    head = scripts.get_current_head()
    assert head is not None, "Alembic head must be defined"
    return head


def manifest_alembic_head() -> str:
    head = _load_manifest().get("alembic_head")
    assert isinstance(head, str) and head, "manifest alembic_head missing"
    return head


def manifest_package_version() -> str:
    version = _load_manifest().get("version")
    assert isinstance(version, str) and version, "manifest version missing"
    return version


def assert_tip_package_aligned() -> tuple[str, str]:
    """Assert Alembic head == manifest alembic_head; return (tip, package)."""

    tip = alembic_current_head()
    manifest_tip = manifest_alembic_head()
    package = manifest_package_version()
    assert tip == manifest_tip, (
        f"Alembic head {tip!r} != RELEASE_MANIFEST alembic_head {manifest_tip!r}"
    )
    return tip, package


# Eager, import-safe constants for contracts that only need the declared baseline.
EXPECTED_TIP, EXPECTED_PACKAGE = assert_tip_package_aligned()


def assert_current_baseline(*, sdk_version: str | None = None) -> None:
    """Assert live Alembic/Manifest(/optional SDK) match the authoritative baseline."""

    tip, package = assert_tip_package_aligned()
    assert tip == EXPECTED_TIP
    assert package == EXPECTED_PACKAGE
    if sdk_version is not None:
        assert sdk_version == EXPECTED_PACKAGE


def assert_revision_exists(revision: str) -> None:
    """Historical freeze: revision exists in the script directory (≠ current head)."""

    scripts = ScriptDirectory.from_config(Config(str(ALEMBIC_INI)))
    rev = scripts.get_revision(revision)
    assert rev is not None, f"expected revision {revision!r} to exist"


def assert_revision_is_ancestor_of_head(revision: str) -> None:
    """Historical freeze: revision is on the path to (or equal) current head."""

    scripts = ScriptDirectory.from_config(Config(str(ALEMBIC_INI)))
    head = scripts.get_current_head()
    assert head is not None
    if revision == head:
        return
    # walk_revisions(base, head): base is older lower bound, head is current tip
    found = any(
        rev.revision == revision for rev in scripts.walk_revisions(revision, head)
    )
    assert found, f"revision {revision!r} is not an ancestor of head {head!r}"
