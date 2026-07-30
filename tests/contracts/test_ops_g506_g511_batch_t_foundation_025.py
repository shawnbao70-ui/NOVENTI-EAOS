"""PHX-G506–G511 Batch T Foundation 0.2.5 final-stop contracts."""

from __future__ import annotations

from pathlib import Path

import yaml

from eaos_sdk import __version__ as sdk_version
from tests.contracts._baseline import EXPECTED_PACKAGE, EXPECTED_TIP, assert_current_baseline

ROOT = Path(__file__).resolve().parents[2]
CHECKLIST = ROOT / "docs" / "release" / "V2_0_READINESS_CHECKLIST.md"
MANIFEST = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"
ROADMAP = ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"
CLOSEOUT = ROOT / "docs" / "release" / "BATCHES_M_T_CLOSEOUT_G511.md"
DECISION = ROOT / "docs" / "release" / "PRODUCTION_GO_DECISION_G469.md"


def test_g506_readiness_is_not_v2_cut() -> None:
    text = CHECKLIST.read_text(encoding="utf-8")
    assert "0.2.5" in text and "0092" in text
    assert "does not" in text.casefold() or "≠" in text
    assert "production" in text.casefold()


def test_g507_g509_release_surfaces_align() -> None:
    assert_current_baseline(sdk_version=sdk_version)
    assert EXPECTED_PACKAGE == "0.2.5"
    assert EXPECTED_TIP.startswith("0092")
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["version"] == "0.2.5"
    ids = {item["id"] for item in manifest["milestones"]}
    assert {"PHX-G469", "PHX-G509", "PHX-G511"} <= ids


def test_g510_g511_final_stop_and_no_go_honesty() -> None:
    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "TRACK-G511 COMPLETE" in roadmap
    assert "FINAL STOP TRACK-G511" in roadmap
    assert "await PO G512+" in roadmap
    closeout = CLOSEOUT.read_text(encoding="utf-8")
    assert "0.2.5" in closeout and "0092" in closeout
    assert "NO-GO" in closeout
    assert "NO-GO" in DECISION.read_text(encoding="utf-8")
