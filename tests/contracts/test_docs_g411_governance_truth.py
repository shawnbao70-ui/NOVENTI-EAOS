"""PHX-G411 governance truth + package layout parity contracts."""

from __future__ import annotations

from pathlib import Path

import yaml

from tests.contracts._baseline import EXPECTED_PACKAGE, EXPECTED_TIP, assert_current_baseline

ROOT = Path(__file__).resolve().parents[2]
STATUS = ROOT / "docs" / "project" / "PROJECT_STATUS.md"
ENG_TIP = ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md"
DAL = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
ROADMAP = ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"
LAYOUT = ROOT / "docs" / "project" / "RUNTIME_PACKAGE_LAYOUT.md"
PACKAGES_README = ROOT / "packages" / "README.md"
MANIFEST = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"


def test_g411_tip_surfaces_agree_on_current_baseline() -> None:
    assert_current_baseline()
    status = STATUS.read_text(encoding="utf-8")
    tip = ENG_TIP.read_text(encoding="utf-8")
    dal = DAL.read_text(encoding="utf-8")
    roadmap = ROADMAP.read_text(encoding="utf-8")
    for text in (status, tip, dal, roadmap):
        assert EXPECTED_PACKAGE in text
        assert "0092" in text
    assert "FINAL STOP TRACK-G405" in status or "FINAL STOP TRACK-G405" in roadmap
    assert "0.2.3" in dal and "0092" in dal
    assert "historical" in dal.casefold() or "Historical" in dal


def test_g411_manifest_inventory_honesty_and_layout() -> None:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["version"] == EXPECTED_PACKAGE
    assert manifest["alembic_head"] == EXPECTED_TIP
    assert "milestone_inventory_note" in manifest
    ids = {m["id"] for m in manifest.get("milestones", [])}
    assert "PHX-G293" in ids
    assert "PHX-G415" in ids
    layout = LAYOUT.read_text(encoding="utf-8")
    assert "packages/*" in layout and "noventi/*" in layout
    assert "declarations" in layout.casefold()
    assert "runtime" in layout.casefold()
    packages = PACKAGES_README.read_text(encoding="utf-8")
    assert "declarations" in packages.casefold()
    assert "noventi" in packages
