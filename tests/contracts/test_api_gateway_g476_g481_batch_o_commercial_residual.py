"""PHX-G476–G481 Batch O CRM/commercial residual contracts."""

from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.finance import FinanceStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
OPENAPI = ROOT / "docs" / "api" / "finance.openapi.yaml"
TERMINAL = ROOT / "smart_terminal" / "ui" / "app.js"


def test_g476_g480_commercial_chain_posture() -> None:
    response = TestClient(create_app()).get("/v1/finance/status")
    assert response.status_code == 200
    FinanceStatusEnvelope.model_validate(response.json())
    data = response.json()["data"]
    assert data["crm_quote_so_do_state_consistency"] is True
    assert data["ar_receipt_credit_boundary"] == "internal_records_only"
    assert data["commission_settlement_mode"] == "read_only_status"
    assert data["crm_finance_handoff_audit"] is True
    assert data["commercial_auto_write"] is False
    assert data["bank_file_import"] == "deferred"
    assert data["external_psp_network_default"] == "off"


def test_g476_g479_openapi_parity() -> None:
    spec = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
    props = spec["components"]["schemas"]["FinanceStatusData"]["properties"]
    assert props["crm_quote_so_do_state_consistency"]["const"] is True
    assert props["ar_receipt_credit_boundary"]["const"] == "internal_records_only"
    assert props["commission_settlement_mode"]["const"] == "read_only_status"
    assert props["crm_finance_handoff_audit"]["const"] is True


def test_g480_terminal_commercial_strip() -> None:
    js = TERMINAL.read_text(encoding="utf-8")
    assert "commercial.chain_consistent=" in js
    assert "commercial.commission=" in js
