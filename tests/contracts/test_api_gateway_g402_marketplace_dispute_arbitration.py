"""PHX-G402 Dispute/arbitration fail-closed shell contracts."""

from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.marketplace import MarketplaceStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
MARKET = ROOT / "docs" / "api" / "marketplace.openapi.yaml"


def test_g402_dispute_arbitration_fail_closed_shell() -> None:
    data = TestClient(create_app()).get("/v1/marketplace/status").json()["data"]
    MarketplaceStatusEnvelope.model_validate({"data": data})
    assert data["external_arbitration"] == "fail_closed"
    product = data["dispute_arbitration_product"]
    assert product["milestone"] == "PHX-G402"
    assert product["external_arbitration"] == "fail_closed"
    assert product["external_arbitration_invent"] is False
    assert product["dispute_surface"] == "publisher_tenant_resolve"
    assert "dispute_arbitration_shell" in data["supported_surfaces"]


def test_g402_no_external_arbitration_invent_routes() -> None:
    paths = TestClient(create_app()).get("/openapi.json").json()["paths"]
    for path in paths:
        lowered = path.casefold()
        assert "/external-arbitration" not in lowered
        assert "/arbiter/" not in lowered
        assert "/marketplace/arbitration/submit" not in lowered


def test_g402_openapi_documents_dispute_shell() -> None:
    spec = yaml.safe_load(MARKET.read_text(encoding="utf-8"))
    props = spec["components"]["schemas"]["DisputeArbitrationProduct"]["properties"]
    assert props["external_arbitration"]["const"] == "fail_closed"
    assert props["external_arbitration_invent"]["const"] is False
