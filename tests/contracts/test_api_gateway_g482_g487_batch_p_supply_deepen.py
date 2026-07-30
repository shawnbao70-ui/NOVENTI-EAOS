"""PHX-G482–G487 Batch P Purchase/Inventory posture contracts."""

from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.finance import FinanceStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
OPENAPI = ROOT / "docs" / "api" / "finance.openapi.yaml"
TERMINAL = ROOT / "smart_terminal" / "ui" / "app.js"


def test_g482_g485_supply_chain_observability() -> None:
    response = TestClient(create_app()).get("/v1/finance/status")
    FinanceStatusEnvelope.model_validate(response.json())
    data = response.json()["data"]
    assert data["purchase_order_observability"] is True
    assert data["inventory_movement_observability"] is True
    assert data["receiving_return_boundary"] == "kernel_records_only"
    assert data["purchase_inventory_cross_contract"] is True
    assert data["commercial_auto_write"] is False


def test_g482_g485_supply_openapi_parity() -> None:
    spec = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
    props = spec["components"]["schemas"]["FinanceStatusData"]["properties"]
    assert props["purchase_order_observability"]["const"] is True
    assert props["inventory_movement_observability"]["const"] is True
    assert props["receiving_return_boundary"]["const"] == "kernel_records_only"
    assert props["purchase_inventory_cross_contract"]["const"] is True


def test_g486_terminal_supply_strip() -> None:
    js = TERMINAL.read_text(encoding="utf-8")
    assert "supply.po=" in js
    assert "supply.inventory=" in js
