"""PHX-G403 Workflow multi-step executable deepen (narrow domain)."""

from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.foundation_status import WorkflowStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / "docs" / "api" / "workflow.openapi.yaml"


def test_g403_workflow_multi_step_executable_narrow() -> None:
    response = TestClient(create_app()).get("/v1/workflow/status")
    assert response.status_code == 200, response.text
    WorkflowStatusEnvelope.model_validate(response.json())
    data = response.json()["data"]
    assert data["multi_step_executable"] is True
    assert data["multi_step_scope"] == "kernel_task_approve_reject_escalate"
    assert data["legacy_multi_step_implemented"] is False
    assert data["commercial_auto_write"] is False
    assert data["approval_source_of_truth"] == "workflow_kernel"
    for surface in ("task_approval", "task_rejection", "task_escalation", "instance_start"):
        assert surface in data["supported_surfaces"]


def test_g403_openapi_documents_multi_step_flags() -> None:
    spec = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    props = spec["components"]["schemas"]["FoundationStatusData"]["properties"]
    assert props["multi_step_executable"]["const"] is True
    assert props["multi_step_scope"]["const"] == "kernel_task_approve_reject_escalate"
    assert props["legacy_multi_step_implemented"]["const"] is False
