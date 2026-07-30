"""PHX-G379 AI Workforce thin boundary HTTP contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.ai_workforce import AiWorkforceStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
PLATFORM_OPENAPI = ROOT / "docs" / "api" / "platform.openapi.yaml"


def _client() -> TestClient:
    return TestClient(create_app())


def _load_openapi() -> dict[str, Any]:
    loaded = yaml.safe_load(PLATFORM_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_g379_ai_workforce_status_honest_flags() -> None:
    response = _client().get("/v1/platform/ai-workforce/status")
    assert response.status_code == 200, response.text
    body = response.json()
    AiWorkforceStatusEnvelope.model_validate(body)
    data = body["data"]
    assert data["task_engine"] is False
    assert data["labor_write"] is False
    assert data["commercial_auto_write"] is False
    assert data["execution_authority"] == "none"
    assert data["digital_employee_identity_separate"] is True


def test_g379_distinct_from_digital_employee_status() -> None:
    client = _client()
    aiw = client.get("/v1/platform/ai-workforce/status")
    de = client.get("/v1/platform/digital-employee/status")
    assert aiw.status_code == 200
    assert de.status_code == 200
    assert aiw.json()["data"] != de.json()["data"]
    assert "digital_employee_identity_separate" in aiw.json()["data"]
    assert "identity_ai_employee_surface" in de.json()["data"]


def test_g379_no_task_crud_or_invent_routes() -> None:
    client = _client()
    openapi = client.get("/openapi.json").json()
    paths = openapi["paths"]
    assert "/v1/platform/ai-workforce/status" in paths
    assert "get" in paths["/v1/platform/ai-workforce/status"]
    for path in paths:
        if "ai-workforce" in path and path != "/v1/platform/ai-workforce/status":
            raise AssertionError(f"unexpected ai-workforce invent path: {path}")
        lowered = path.casefold()
        assert "/ai-workforce/tasks" not in lowered
        assert "/ai-workforce/task" not in lowered


def test_g379_platform_openapi_documents_status() -> None:
    spec = _load_openapi()
    assert str(spec["info"]["version"]).startswith("1.0.")
    path = spec["paths"]["/platform/ai-workforce/status"]["get"]
    assert path["operationId"] == "getAiWorkforceStatus"
    assert "200" in path["responses"]
    schema = path["responses"]["200"]["content"]["application/json"]["schema"]
    assert schema["$ref"].endswith("AiWorkforceStatusEnvelope")
    data = spec["components"]["schemas"]["AiWorkforceStatusData"]
    props = data["properties"]
    assert props["task_engine"]["const"] is False
    assert props["labor_write"]["const"] is False
    assert props["commercial_auto_write"]["const"] is False
    assert props["execution_authority"]["const"] == "none"
    assert props["digital_employee_identity_separate"]["const"] is True
    required = set(data["required"])
    assert {
        "task_engine",
        "labor_write",
        "commercial_auto_write",
        "execution_authority",
        "digital_employee_identity_separate",
    } <= required
