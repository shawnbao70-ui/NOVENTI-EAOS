"""PHX-G401 Marketplace billing record internal shell (≠ external PSP)."""

from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.marketplace import MarketplaceStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
MARKET = ROOT / "docs" / "api" / "marketplace.openapi.yaml"


def test_g401_billing_record_shell_honesty() -> None:
    data = TestClient(create_app()).get("/v1/marketplace/status").json()["data"]
    MarketplaceStatusEnvelope.model_validate({"data": data})
    billing = data["billing_record_product"]
    assert billing["milestone"] == "PHX-G401"
    assert billing["posture"] == "internal_invoice_shell"
    assert billing["external_psp"] is False
    assert billing["enable_psp_network_default"] == "off"
    assert billing["bank_file_import"] == "deferred"
    assert billing["finance_ar_invoice_separate"] is True
    assert data["payment_clearing_product"]["external_psp"] is False
    assert "billing_record_shell" in data["supported_surfaces"]


def test_g401_openapi_documents_billing_shell() -> None:
    spec = yaml.safe_load(MARKET.read_text(encoding="utf-8"))
    props = spec["components"]["schemas"]["BillingRecordProduct"]["properties"]
    assert props["external_psp"]["const"] is False
    assert props["bank_file_import"]["const"] == "deferred"
    assert props["enable_psp_network_default"]["const"] == "off"
