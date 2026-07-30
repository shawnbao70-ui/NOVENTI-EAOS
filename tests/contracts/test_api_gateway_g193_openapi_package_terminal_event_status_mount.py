"""PHX-G193 Package/Terminal/Event status mount parity contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]

def _load(name: str) -> dict:
    return yaml.safe_load((ROOT / "docs" / "api" / name).read_text(encoding="utf-8"))

def test_g193_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0212-openapi-package-terminal-event-status-mount-parity.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G193_ACCEPTANCE.md").is_file()

def test_g193_status_mounts_and_schemas() -> None:
    cases = [
        (
            "package.openapi.yaml",
            {"1.0.4", "1.0.5", "1.0.6", "1.0.7", "1.0.8", "1.0.9", "1.0.10", "1.0.12"},
            "/packages/status",
            "/v1/packages/status",
            "PackageStatusData",
        ),
        (
            "terminal.openapi.yaml",
            "1.1.5",
            "/terminal/status",
            "/v1/terminal/status",
            "TerminalStatusData",
        ),
        (
            "event.openapi.yaml",
            {"1.0.4", "1.0.5", "1.0.6", "1.0.12"},
            "/events/status",
            "/v1/events/status",
            "EventStatusData",
        ),
    ]
    client = TestClient(app)
    for filename, version, openapi_path, http_path, schema_name in cases:
        spec = _load(filename)
        ver = str(spec["info"]["version"])
        if isinstance(version, set):
            prefix = next(iter(version)).rsplit(".", 1)[0] + "."
            assert ver.startswith(prefix) or ver in version
        else:
            prefix = str(version).rsplit(".", 1)[0] + "."
            assert ver.startswith(prefix) or ver == version
        assert openapi_path in spec["paths"]
        schema = spec["components"]["schemas"][schema_name]
        assert schema.get("additionalProperties") is False
        data = client.get(http_path).json()["data"]
        assert data["writable"] is False
        assert set(schema["required"]) <= set(data)
        assert len(data["supported_surfaces"]) >= 1

def test_g193_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g193" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load("ops.openapi.yaml")
    assert ops["info"]["version"].startswith("1.0.")
    assert (
        ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"][
            "milestone"
        ]["const"].startswith("PHX-G")
    )

def test_g193_ledger_tip_manifest_baseline() -> None:
    assert sdk_version == "0.2.5"
    assert_current_baseline()
    ledger = (ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md").read_text(
        encoding="utf-8"
    )
    tip = (ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md").read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    status = (ROOT / "docs" / "project" / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "DAL-U066" in ledger
    assert ("PHX-G193" in tip or "PHX-G194" in tip or "PHX-G195" in tip) and ("PHX-G193" in manifest or "PHX-G194" in manifest or "PHX-G195" in manifest) and ("PHX-G2" in status)
