"""PHX-G434–G439 Batch H Workflow / Approval deepen."""

from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.foundation_status import WorkflowStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / "docs" / "api" / "workflow.openapi.yaml"
ROADMAP = ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"


def test_g434_g437_workflow_status_deepen_live() -> None:
    response = TestClient(create_app()).get("/v1/workflow/status")
    assert response.status_code == 200, response.text
    WorkflowStatusEnvelope.model_validate(response.json())
    data = response.json()["data"]
    assert data["multi_step_executable"] is True
    assert data["escalation_fail_closed"] is True
    assert data["compensation_engine_invent"] is False
    assert data["sla_engine_invent"] is False
    assert data["commercial_auto_write"] is False


def test_g434_g437_workflow_openapi_parity() -> None:
    spec = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    props = spec["components"]["schemas"]["FoundationStatusData"]["properties"]
    assert props["escalation_fail_closed"]["const"] is True
    assert props["compensation_engine_invent"]["const"] is False
    assert props["sla_engine_invent"]["const"] is False


def test_g439_workflow_hygiene_roadmap() -> None:
    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "TRACK-G434 COMPLETE" in roadmap
    assert "TRACK-G439 COMPLETE" in roadmap
