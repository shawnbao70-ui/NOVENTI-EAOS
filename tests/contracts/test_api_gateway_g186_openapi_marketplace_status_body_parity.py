"""PHX-G186 OpenAPI Marketplace status body field parity contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from api.gateway.payment_clearing import payment_clearing_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
MARKET = ROOT / "docs" / "api" / "marketplace.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g186_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0205-openapi-marketplace-status-body-field-parity.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G186_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G186_ARCHITECTURE_GATE.md").is_file()

def test_g186_payment_clearing_product_schema_matches_emit() -> None:
    spec = _load(MARKET)
    assert str(spec["info"]["version"]).startswith("1.2.")
    schema = spec["components"]["schemas"]["PaymentClearingProduct"]
    assert schema.get("additionalProperties") is False
    assert schema["properties"]["milestone"]["const"] == "PHX-G162"
    assert (
        schema["properties"]["surface"]["const"]
        == "foundation_marketplace_payment_clearing"
    )
    assert schema["properties"]["external_psp"]["const"] is False
    assert set(schema["properties"]["settlement_rail"]["enum"]) == {'disabled', 'internal_record_only'}
    required = set(schema["required"])
    emit = payment_clearing_product_posture()
    assert required <= set(emit)
    assert set(emit) <= set(schema["properties"])
    for key in required:
        assert key in schema["properties"]

def test_g186_foundation_status_schema_matches_runtime() -> None:
    spec = _load(MARKET)
    schema = spec["components"]["schemas"]["FoundationStatusData"]
    assert schema.get("additionalProperties") is False
    assert schema["properties"]["foundation_commercial_policy"]["const"] == "v1"
    assert set(schema["properties"]["payment_clearing"]["enum"]) == {'fail_closed', 'internal_env_gated'}
    required = set(schema["required"])
    data = TestClient(app).get("/v1/marketplace/status").json()["data"]
    assert required <= set(data)
    assert set(data) <= set(schema["properties"])
    assert data["foundation_commercial_policy"] == "v1"
    assert data["external_arbitration"] == "fail_closed"
    assert data["host_acquire_product"]["external_psp"] is False
    assert data["payment_clearing_product"]["external_psp"] is False

def test_g186_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g186" in " ".join(posture["fail_closed_reasons"]).casefold()

    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    assert (
        props["t0188_status"]["const"].startswith("mount_parity_complete")
    )
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g186_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U059" in ledger
    assert ("PHX-G186" in tip or "PHX-G187" in tip) and ("PHX-G186" in manifest or "PHX-G187" in manifest) and ("PHX-G2" in status)
