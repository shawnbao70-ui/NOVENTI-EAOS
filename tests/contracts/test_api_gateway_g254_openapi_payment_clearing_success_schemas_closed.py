"""PHX-G254 OpenAPI PaymentClearing success schemas closed honesty."""

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
OPS = API / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g254_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0273-openapi-payment-clearing-success-schemas-closed.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G254_ACCEPTANCE.md").is_file()

def test_g254_success_schemas_closed() -> None:
    market = _load(API / "marketplace.openapi.yaml")
    assert str(market["info"]["version"]).startswith("1.2.")
    schemas = market["components"]["schemas"]
    for name in ("PaymentClearingRequest", "PaymentClearingEnvelope", "PaymentClearingResult"):
        assert schemas[name].get("additionalProperties") is False
    result = schemas["PaymentClearingResult"]
    assert result["properties"]["payment_cleared"].get("const") is True
    assert result["properties"]["external_psp"].get("const") is False
    assert result["properties"]["audit_id"]["type"] == ["string", "null"]

def test_g254_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert (
        posture["t0188_status"]
        .startswith("mount_parity_complete")
    )
    assert "g254" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g254_baseline() -> None:
    assert sdk_version == "0.2.5"
    assert_current_baseline()
    assert "DAL-U127" in (
        ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
    ).read_text(encoding="utf-8")
