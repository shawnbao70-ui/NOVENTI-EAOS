"""PHX-G208 OpenAPI elevation details per-code shape honesty contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path
from uuid import uuid4

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "docs" / "api"
OPS = API / "ops.openapi.yaml"
TERMINAL = API / "terminal.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g208_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0227-openapi-elevation-details-code-shape-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G208_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G208_ARCHITECTURE_GATE.md").is_file()

def test_g208_elevation_details_schema() -> None:
    for path, prefix in ((TERMINAL, "1.1."), (OPS, "1.0.")):
        spec = _load(path)
        assert str(spec["info"]["version"]).startswith(prefix)
        schema = spec["components"]["schemas"]["ContextElevationDenialDetails"]
        assert schema.get("additionalProperties") is False
        assert schema["required"] == ["fields"]
        assert schema["properties"]["fields"]["type"] == "array"
        assert "TERMINAL_CONTEXT_ELEVATION_DENIED" in schema.get("description", "")

def test_g208_live_elevation_matches_schema() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/context/echo",
        headers={
            "X-EAOS-Subject-Id": str(uuid4()),
            "X-EAOS-Subject-Type": "human",
            "X-EAOS-Tenant-Id": str(uuid4()),
            "X-Correlation-ID": "g208-echo",
        },
        json={"tenant_id": str(uuid4()), "roles": ["admin"]},
    )
    assert response.status_code == 400
    body = response.json()["detail"]
    assert body["code"] == "TERMINAL_CONTEXT_ELEVATION_DENIED"
    fields = body["details"]["fields"]
    assert isinstance(fields, list) and fields == sorted(fields)

def test_g208_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g208" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g208_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U081" in ledger
    assert ("PHX-G208" in tip or "PHX-G209" in tip or "PHX-G210" in tip) and (
        "PHX-G208" in manifest or "PHX-G209" in manifest or "PHX-G210" in manifest
    ) and ("PHX-G2" in status)