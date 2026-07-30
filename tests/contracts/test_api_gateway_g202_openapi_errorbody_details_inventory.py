"""PHX-G202 OpenAPI ErrorBody/ErrorResponse details inventory contracts."""

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

GAP_SPECS = {
    "auth.openapi.yaml": {"1.3.14", "1.3.15", "1.3.16", "1.3.17", "1.3.18", "1.3.19"},
    "permission.openapi.yaml": {"1.1.10", "1.1.11", "1.1.12", "1.1.13", "1.1.14"},
    "organization.openapi.yaml": {"1.0.4", "1.0.5", "1.0.6", "1.0.7", "1.0.8", "1.0.9"},
    "workflow.openapi.yaml": {"1.0.6", "1.0.7", "1.0.8", "1.0.9"},
    "platform.openapi.yaml": {"1.0.3", "1.0.4", "1.0.5", "1.0.6"},
}

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g202_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0221-openapi-cross-domain-errorbody-details-inventory.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G202_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G202_ARCHITECTURE_GATE.md").is_file()

def test_g202_gap_domains_have_errorresponse_details() -> None:
    for name, versions in GAP_SPECS.items():
        spec = _load(API / name)
        ver = str(spec["info"]["version"])
        prefix = next(iter(versions)).rsplit(".", 1)[0] + "."
        assert ver.startswith(prefix) or ver in versions
        err = spec["components"]["schemas"]["ErrorResponse"]
        assert "details" in err["properties"]
        details = err["properties"]["details"]
        assert details.get("type") == "object" or "anyOf" in details

def test_g202_catalog_error_schemas_document_details() -> None:
    missing: list[str] = []
    for path in sorted(API.glob("*.openapi.yaml")):
        schemas = _load(path).get("components", {}).get("schemas", {})
        for name in ("ErrorBody", "ErrorResponse"):
            schema = schemas.get(name)
            if not isinstance(schema, dict):
                continue
            props = schema.get("properties") or {}
            if "details" not in props:
                missing.append(f"{path.name}:{name}")
    assert missing == []

def test_g202_elevation_emit_includes_details() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/context/echo",
        headers={
            "X-EAOS-Subject-Id": str(uuid4()),
            "X-EAOS-Subject-Type": "human",
            "X-EAOS-Tenant-Id": str(uuid4()),
            "X-Correlation-ID": "g202-echo",
        },
        json={"tenant_id": str(uuid4()), "roles": ["admin"]},
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "TERMINAL_CONTEXT_ELEVATION_DENIED"
    assert "details" in detail
    assert "fields" in detail["details"]

def test_g202_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g202" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g202_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U075" in ledger
    assert ("PHX-G202" in tip or "PHX-G203" in tip or "PHX-G204" in tip) and (
        "PHX-G202" in manifest or "PHX-G203" in manifest or "PHX-G204" in manifest
    ) and ("PHX-G2" in status)
