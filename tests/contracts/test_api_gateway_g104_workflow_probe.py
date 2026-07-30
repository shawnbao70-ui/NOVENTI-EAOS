"""PHX-G104 Workflow Status / Definition / Instance Thin Probe contracts."""

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
ACTOR = uuid4()
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


def _headers(subject_id: UUID = ACTOR) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }


def test_terminal_exposes_workflow_probe_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminWorkflowStatus"' in html
    assert 'id="btnAdminWorkflowCreateDefinition"' in html
    assert 'id="btnAdminWorkflowStartInstance"' in html
    assert 'id="btnAdminWorkflowGetInstance"' in html
    assert 'id="btnAdminWorkflowListTasks"' in html
    assert 'id="workflowDefinitionId"' in html
    assert 'id="workflowInstanceId"' in html
    assert "Workflow 状态/定义/实例/任务薄探针（G104" in html
    assert "审批真相仍归 Workflow Kernel" in html
    assert 'workflowStatus: "/v1/workflow/status"' in js
    assert 'workflowDefinitions: "/v1/workflow/definitions"' in js
    assert "adminCreateWorkflowDefinition" in js
    assert "adminStartWorkflowInstance" in js
    assert "adminGetWorkflowInstance" in js
    assert "adminListWorkflowTasks" in js
    start = js.index("async function adminCreateWorkflowDefinition")
    end = js.index("async function adminApproveWorkflowTask")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "/approval" not in chunk
    assert "/rejection" not in chunk


def test_workflow_status_and_probe_api() -> None:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    workflow = WorkflowService(
        permission,
        definition_administrators={ACTOR},
    )
    admin_ctx = ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=CORR,
        request_time=ExecutionContext.utc_now(),
    )
    client = TestClient(
        create_app(permission_service=permission, workflow_service=workflow)
    )

    status = client.get("/v1/workflow/status")
    assert status.status_code == 200
    data = status.json()["data"]
    assert data["writable"] is False
    assert data["approval_source_of_truth"] == "workflow_kernel"
    assert "definition_register" in data["supported_surfaces"]
    assert "instance_start" in data["supported_surfaces"]
    assert "task_list" in data["supported_surfaces"]

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Workflow status" in page.text
    assert "Create workflow definition" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminCreateWorkflowDefinition" in script.text

    created = client.post(
        "/v1/workflow/definitions",
        headers=_headers(),
        json={
            "name": f"Flow-{uuid4()}",
            "definition_document_ref": "docs/workflows/g104",
            "version": "1.0",
        },
    )
    assert created.status_code == 201
    definition_id = created.json()["id"]
    assert permission.grant(
        admin_ctx,
        principal_subject_id=ACTOR,
        resource_type="workflow_definition",
        resource_id=UUID(definition_id),
        actions={"start"},
    ).ok
    assert permission.grant(
        admin_ctx,
        principal_subject_id=ACTOR,
        resource_type="workflow_instance",
        actions={"read"},
        scope_level=ScopeLevel.TENANT,
    ).ok

    started = client.post(
        "/v1/workflow/instances",
        headers=_headers(),
        json={"definition_id": definition_id, "payload": {"action": "probe"}},
    )
    assert started.status_code == 201
    body = started.json()
    assert body["instance_id"]
    assert body["status"] == "running"

    instance = client.get(
        f"/v1/workflow/instances/{body['instance_id']}",
        headers=_headers(),
    )
    assert instance.status_code == 200
    assert instance.json()["id"] == body["instance_id"]
    assert instance.json()["status"] == "running"

    tasks = client.get("/v1/workflow/tasks", headers=_headers())
    assert tasks.status_code == 200
    assert isinstance(tasks.json(), list)
