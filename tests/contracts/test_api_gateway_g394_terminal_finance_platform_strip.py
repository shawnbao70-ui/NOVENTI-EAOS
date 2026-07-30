"""PHX-G394 Terminal finance/platform status strip contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.finance import FinanceStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
FINANCE_OPENAPI = ROOT / "docs" / "api" / "finance.openapi.yaml"
TERMINAL_JS = ROOT / "smart_terminal" / "ui" / "app.js"
TERMINAL_HTML = ROOT / "smart_terminal" / "ui" / "index.html"


def _client() -> TestClient:
    return TestClient(create_app())


def _load_openapi() -> dict[str, Any]:
    loaded = yaml.safe_load(FINANCE_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_g394_finance_status_honesty() -> None:
    response = _client().get("/v1/finance/status")
    assert response.status_code == 200, response.text
    FinanceStatusEnvelope.model_validate(response.json())
    data = response.json()["data"]
    assert data["writable"] is False
    assert data["commercial_auto_write"] is False
    assert data["holds_business_truth"] is True
    assert data["terminal_holds_business_truth"] is False


def test_g394_platform_thin_statuses_live() -> None:
    client = _client()
    digital = client.get("/v1/platform/digital-employee/status").json()["data"]
    assert digital["execution_authority"] == "none"
    assert digital["commercial_auto_write"] is False
    industry = client.get("/v1/platform/industry-package/status").json()["data"]
    assert industry["execution_authority"] == "none"
    assert industry["industry_package_runtime"] is False
    workforce = client.get("/v1/platform/ai-workforce/status").json()["data"]
    assert workforce["execution_authority"] == "none"
    assert workforce["commercial_auto_write"] is False


def test_g394_terminal_strip_wired() -> None:
    js = TERMINAL_JS.read_text(encoding="utf-8")
    html = TERMINAL_HTML.read_text(encoding="utf-8")
    assert 'financeStatus: "/v1/finance/status"' in js
    assert "async function loadFinancePlatformStatus" in js
    assert 'bind("btnAdminFinancePlatformStatus"' in js
    assert 'id="btnAdminFinancePlatformStatus"' in html
    assert 'id="financePlatformStatus"' in html


def test_g394_finance_openapi_documents_status() -> None:
    spec = _load_openapi()
    path = spec["paths"]["/finance/status"]["get"]
    assert path["operationId"] == "getFinanceStatus"
    props = spec["components"]["schemas"]["FinanceStatusData"]["properties"]
    assert props["terminal_holds_business_truth"]["const"] is False
    assert props["commercial_auto_write"]["const"] is False
