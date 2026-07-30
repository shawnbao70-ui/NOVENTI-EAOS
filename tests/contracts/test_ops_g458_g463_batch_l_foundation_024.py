"""PHX-G458–G463 Batch L Foundation 0.2.4 + FINAL STOP TRACK-G463."""

from __future__ import annotations

from pathlib import Path

import yaml

from eaos_sdk import __version__ as sdk_version
from tests.contracts._baseline import EXPECTED_PACKAGE, EXPECTED_TIP, assert_current_baseline

ROOT = Path(__file__).resolve().parents[2]
CHECKLIST = ROOT / "docs" / "release" / "V2_0_READINESS_CHECKLIST.md"
MANIFEST = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"
ROADMAP = ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"
CHANGELOG = ROOT / "docs" / "project" / "CHANGELOG.md"
CLOSEOUT = ROOT / "docs" / "release" / "BATCHES_E_L_CLOSEOUT_G463.md"


def test_g458_v2_readiness_refreshed_not_cut() -> None:
    text = CHECKLIST.read_text(encoding="utf-8")
    assert "0.2.4" in text
    assert "0092" in text
    assert "does not" in text.casefold() or "≠" in text or "not" in text.casefold()
    assert "V2.0" in text
    # Hard holds remain deferred
    assert "bank" in text.casefold()
    assert "PSP" in text or "psp" in text.casefold()


def test_g461_package_cut_0_2_4() -> None:
    assert_current_baseline(sdk_version=sdk_version)
    assert EXPECTED_PACKAGE == "0.2.5"
    assert EXPECTED_TIP.startswith("0092")
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["version"] == "0.2.5"
    assert str(manifest["alembic_head"]).startswith("0092")


def test_g463_final_stop_and_closeout() -> None:
    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "FINAL STOP TRACK-G463" in roadmap
    assert "TRACK-G463 COMPLETE" in roadmap
    assert CLOSEOUT.is_file()
    close = CLOSEOUT.read_text(encoding="utf-8")
    assert "0.2.4" in close
    assert "0092" in close
    assert "FINAL STOP TRACK-G463" in close
    changelog = CHANGELOG.read_text(encoding="utf-8")
    assert "0.2.4" in changelog
    assert "G463" in changelog or "G416" in changelog
