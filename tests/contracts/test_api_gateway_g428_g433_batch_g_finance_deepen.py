"""PHX-G428–G433 Batch G Finance deepen (no bank file / PSP OFF)."""

from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.finance import FinanceStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
FINANCE = ROOT / "docs" / "api" / "finance.openapi.yaml"
ROADMAP = ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"


def test_g428_g430_finance_status_deepen_live() -> None:
    response = TestClient(create_app()).get("/v1/finance/status")
    assert response.status_code == 200, response.text
    FinanceStatusEnvelope.model_validate(response.json())
    data = response.json()["data"]
    assert data["bank_file_import"] == "deferred"
    assert data["external_psp_network_default"] == "off"
    assert data["gl_period_status_surface"] is True
    assert data["party_balance_projection"] is True
    assert data["treasury_transfer_surface"] is True
    assert data["commercial_auto_write"] is False


def test_g428_g430_finance_openapi_parity() -> None:
    spec = yaml.safe_load(FINANCE.read_text(encoding="utf-8"))
    props = spec["components"]["schemas"]["FinanceStatusData"]["properties"]
    assert props["bank_file_import"]["const"] == "deferred"
    assert props["external_psp_network_default"]["const"] == "off"
    assert props["gl_period_status_surface"]["const"] is True
    assert props["party_balance_projection"]["const"] is True
    assert props["treasury_transfer_surface"]["const"] is True


def test_g433_finance_hygiene_roadmap() -> None:
    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "TRACK-G428 COMPLETE" in roadmap
    assert "TRACK-G433 COMPLETE" in roadmap
    assert "TRACK-BATCH-G-TREASURY-NO-BANK-FILE COMPLETE" in roadmap
