"""PHX-G409 release version surface parity contracts."""

from __future__ import annotations

from pathlib import Path

import yaml

from eaos_sdk import __version__ as sdk_version
from tests.contracts._baseline import EXPECTED_PACKAGE, assert_current_baseline

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = ROOT / "pyproject.toml"
MANIFEST = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"
CHART = ROOT / "deploy" / "helm" / "eaos" / "Chart.yaml"
VALUES = ROOT / "deploy" / "helm" / "eaos" / "values.yaml"


def test_g409_all_release_version_surfaces_equal_package() -> None:
    assert_current_baseline(sdk_version=sdk_version)
    assert EXPECTED_PACKAGE == "0.2.5"
    assert f'version = "{EXPECTED_PACKAGE}"' in PYPROJECT.read_text(encoding="utf-8")

    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["version"] == EXPECTED_PACKAGE

    chart = yaml.safe_load(CHART.read_text(encoding="utf-8"))
    assert chart["version"] == EXPECTED_PACKAGE
    assert str(chart["appVersion"]) == EXPECTED_PACKAGE

    values = yaml.safe_load(VALUES.read_text(encoding="utf-8"))
    assert str(values["image"]["tag"]) == EXPECTED_PACKAGE
