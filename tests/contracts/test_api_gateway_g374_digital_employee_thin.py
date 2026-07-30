"""PHX-G374 Digital Employee thin boundary HTTP contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.digital_employee import DigitalEmployeeStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
PLATFORM_OPENAPI = ROOT / "docs" / "api" / "platform.openapi.yaml"


def _client() -> TestClient:
    return TestClient(create_app())


def _load_openapi() -> dict[str, Any]:
    loaded = yaml.safe_load(PLATFORM_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_g374_digital_employee_status_honest_flags() -> None:
    response = _client().get("/v1/platform/digital-employee/status")
    assert response.status_code == 200, response.text
    body = response.json()
    DigitalEmployeeStatusEnvelope.model_validate(body)
    data = body["data"]
    assert data["identity_ai_employee_surface"] is True
    assert data["labor_write"] is False
    assert data["commercial_auto_write"] is False
    assert data["execution_authority"] == "none"


def test_g374_no_workforce_or_commercial_write_routes() -> None:
    client = _client()
    openapi = client.get("/openapi.json").json()
    paths = openapi["paths"]
    assert "/v1/platform/digital-employee/status" in paths
    assert "get" in paths["/v1/platform/digital-employee/status"]
    for path in paths:
        if "digital-employee" in path and path != "/v1/platform/digital-employee/status":
            raise AssertionError(f"unexpected digital-employee invent path: {path}")
        # AI Workforce is a distinct surface (PHX-G379), not under digital-employee
        if "digital-employee" in path:
            assert "workforce" not in path
        assert "/digital-employee/tasks" not in path


def test_g374_platform_openapi_documents_status() -> None:
    spec = _load_openapi()
    path = spec["paths"]["/platform/digital-employee/status"]["get"]
    assert path["operationId"] == "getDigitalEmployeeStatus"
    assert "200" in path["responses"]
    schema = path["responses"]["200"]["content"]["application/json"]["schema"]
    assert schema["$ref"].endswith("DigitalEmployeeStatusEnvelope")
    data = spec["components"]["schemas"]["DigitalEmployeeStatusData"]
    props = data["properties"]
    assert props["identity_ai_employee_surface"]["const"] is True
    assert props["labor_write"]["const"] is False
    assert props["commercial_auto_write"]["const"] is False
    assert props["execution_authority"]["const"] == "none"
