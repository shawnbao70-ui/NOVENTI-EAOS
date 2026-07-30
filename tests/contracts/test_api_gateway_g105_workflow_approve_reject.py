"""PHX-G105 Workflow Task Approve / Reject Thin Probe contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.workflow.service import WorkflowService

ROOT = Path(__file__).resolve().parents[2]
ADMIN = uuid4()
INITIATOR = uuid4()
APPROVER = uuid4()
AI = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


@pytest.fixture(autouse=True)
def _reset() -> None:
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    yield


def _headers(subject_id: UUID) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }


def _admin_ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=CORR,
        request_time=ExecutionContext.utc_now(),
    )


def test_terminal_exposes_approve_reject_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminWorkflowApproveTask"' in html
    assert 'id="btnAdminWorkflowRejectTask"' in html
    assert 'id="workflowTaskId"' in html
    assert "Approve workflow task" in html
    assert "Reject workflow task" in html
    assert "Workflow 任务 approve/reject 薄探针（G105" in html
    assert "workflowTaskApproval" in js
    assert "workflowTaskRejection" in js
    assert "adminApproveWorkflowTask" in js
    assert "adminRejectWorkflowTask" in js
    start = js.index("async function adminApproveWorkflowTask")
    end = js.index("async function adminSignalWorkflowInstance")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "/signals" not in chunk
    assert "/cancellation" not in chunk


def test_gateway_serves_approve_reject_ui_and_api() -> None:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    workflow = WorkflowService(
        permission,
        definition_administrators={ADMIN},
    )
    client = TestClient(
        create_app(permission_service=permission, workflow_service=workflow)
    )

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Approve workflow task" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminApproveWorkflowTask" in script.text

    created = client.post(
        "/v1/workflow/definitions",
        headers=_headers(ADMIN),
        json={
            "name": f"Flow-{uuid4()}",
            "definition_document_ref": "docs/workflows/g105",
            "version": "1.0",
        },
    )
    assert created.status_code == 201
    definition_id = created.json()["id"]
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=INITIATOR,
        resource_type="workflow_definition",
        resource_id=UUID(definition_id),
        actions={"start"},
    ).ok
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=INITIATOR,
        resource_type="workflow_instance",
        actions={"read"},
        scope_level=ScopeLevel.TENANT,
    ).ok

    started = client.post(
        "/v1/workflow/instances",
        headers=_headers(INITIATOR),
        json={
            "definition_id": definition_id,
            "payload": {"action": "g105"},
            "approval_subject_id": str(APPROVER),
            "approval_principal_id": str(AI),
            "approval_action": "commit",
            "approval_resource_ref": "ledger:g105",
        },
    )
    assert started.status_code == 201
    instance_id = started.json()["instance_id"]
    task_id = started.json()["task_id"]
    assert task_id
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=APPROVER,
        resource_type="workflow_task",
        resource_id=UUID(task_id),
        actions={"approve", "reject"},
    ).ok

    approved = client.post(
        f"/v1/workflow/instances/{instance_id}/tasks/{task_id}/approval",
        headers=_headers(APPROVER),
        json={
            "comment": "g105-ok",
            "expected_instance_version": 1,
            "expected_task_version": 1,
        },
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
