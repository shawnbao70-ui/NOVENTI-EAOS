"""PHX-G212 OpenAPI host-acquire details per-code shape honesty contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "docs" / "api"
MARKET = API / "marketplace.openapi.yaml"
OPS = API / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g212_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0231-openapi-host-acquire-details-code-shape-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G212_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G212_ARCHITECTURE_GATE.md").is_file()

def test_g212_marketplace_host_acquire_details_schema() -> None:
    spec = _load(MARKET)
    assert str(spec["info"]["version"]).startswith("1.2.")
    schema = spec["components"]["schemas"]["HostAcquireAllowlistDenialDetails"]
    assert schema.get("additionalProperties") is False
    assert schema["required"] == ["package_key"]
    assert schema["properties"]["package_key"]["type"] == "string"
    details = spec["components"]["schemas"]["ErrorBody"]["properties"]["details"]
    refs = {
        item.get("$ref", "").rsplit("/", 1)[-1]
        for item in (details.get("anyOf") or [])
        if isinstance(item, dict)
    }
    assert "HostAcquireAllowlistDenialDetails" in refs or "package_key" in (
        details.get("properties") or {}
    )

def test_g212_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g212" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g212_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U085" in ledger
    assert ("PHX-G212" in tip or "PHX-G213" in tip or "PHX-G214" in tip) and (
        "PHX-G212" in manifest or "PHX-G213" in manifest or "PHX-G214" in manifest
    ) and ("PHX-G2" in status)