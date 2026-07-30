"""PHX-G488–G493 Batch Q Marketplace economy residual contracts."""

from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.marketplace import MarketplaceStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
OPENAPI = ROOT / "docs" / "api" / "marketplace.openapi.yaml"
TERMINAL = ROOT / "smart_terminal" / "ui" / "app.js"


def test_g488_g491_marketplace_residual_honesty() -> None:
    response = TestClient(create_app()).get("/v1/marketplace/status")
    MarketplaceStatusEnvelope.model_validate(response.json())
    data = response.json()["data"]
    assert data["economy_residual_reviewed"] is True
    assert data["external_commercial_services"] == "fail_closed"
    assert data["host_acquire_not_package_install"] is True
    assert data["billing_record_product"]["external_psp"] is False
    assert data["billing_record_product"]["bank_file_import"] == "deferred"
    assert data["dispute_arbitration_product"]["external_arbitration_invent"] is False


def test_g488_g491_marketplace_openapi_parity() -> None:
    spec = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
    props = spec["components"]["schemas"]["FoundationStatusData"]["properties"]
    assert props["economy_residual_reviewed"]["const"] is True
    assert props["external_commercial_services"]["const"] == "fail_closed"
    assert props["host_acquire_not_package_install"]["const"] is True


def test_g492_terminal_marketplace_residual_strip() -> None:
    js = TERMINAL.read_text(encoding="utf-8")
    assert "economy_reviewed=" in js
    assert "host_acquire_not_install=" in js
