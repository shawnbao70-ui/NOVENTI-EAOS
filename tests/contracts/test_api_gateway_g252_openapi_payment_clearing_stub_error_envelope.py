"""PHX-G252 OpenAPI PaymentClearingStubError envelope honesty."""

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

def test_g252_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0271-openapi-payment-clearing-stub-error-envelope-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G252_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G252_ARCHITECTURE_GATE.md").is_file()

def test_g252_stub_error_envelope() -> None:
    market = _load(API / "marketplace.openapi.yaml")
    assert str(market["info"]["version"]).startswith("1.2.")
    schemas = market["components"]["schemas"]
    assert "PaymentClearingStubError" in schemas
    err = schemas["PaymentClearingStubError"]
    assert err.get("additionalProperties") is False
    assert err["properties"]["detail"]["$ref"].endswith("/PaymentClearingStubDetail")
    detail = schemas["PaymentClearingStubDetail"]
    assert detail.get("additionalProperties") is False
    assert detail["properties"]["external_psp"].get("const") is False
    path = market["paths"]["/marketplace/listings/{listingId}/payment-clearing"]["post"]
    assert path["responses"]["503"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/PaymentClearingStubError"
    )
    assert path["responses"]["400"]["content"]["application/json"]["schema"]["$ref"].endswith(
        "/GatewayDetailError"
    )

def test_g252_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert (
        posture["t0188_status"]
        .startswith("mount_parity_complete")
    )
    assert "g252" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g252_baseline() -> None:
    assert sdk_version == "0.2.5"
    assert_current_baseline()
    assert "DAL-U125" in (
        ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
    ).read_text(encoding="utf-8")
    tip = (ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md").read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    assert "PHX-G252" in tip and "PHX-G252" in manifest
