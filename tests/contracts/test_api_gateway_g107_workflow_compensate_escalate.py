"""PHX-G107 Workflow Compensate / Escalate Thin Probe contracts."""

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
OPERATOR = uuid4()
APPROVER = uuid4()
ESCALATEE = uuid4()
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


def test_terminal_exposes_compensate_escalate_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminWorkflowCompensateInstance"' in html
    assert 'id="btnAdminWorkflowEscalateTask"' in html
    assert 'id="workflowCompensateReason"' in html
    assert 'id="workflowEscalateToSubjectId"' in html
    assert "Compensate workflow instance" in html
    assert "Escalate workflow task" in html
    assert "Workflow compensate/escalate 薄探针（G107" in html
    assert "Workflow Terminal 运维面齐" in html
    assert "workflowInstanceCompensate" in js
    assert "workflowTaskEscalation" in js
    assert "adminCompensateWorkflowInstance" in js
    assert "adminEscalateWorkflowTask" in js
    start = js.index("async function adminCompensateWorkflowInstance")
    end = js.index("async function adminRegisterPackageManifest")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk


def test_gateway_serves_compensate_and_escalate_ui_and_api() -> None:
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
    assert "Compensate workflow instance" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminCompensateWorkflowInstance" in script.text

    created = client.post(
        "/v1/workflow/definitions",
        headers=_headers(ADMIN),
        json={
            "name": f"Flow-{uuid4()}",
            "definition_document_ref": "docs/workflows/g107",
            "version": "1.0",
        },
    )
    assert created.status_code == 201
    definition_id = created.json()["id"]
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=OPERATOR,
        resource_type="workflow_definition",
        resource_id=UUID(definition_id),
        actions={"start"},
    ).ok
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=OPERATOR,
        resource_type="workflow_instance",
        actions={"read", "signal", "compensate"},
        scope_level=ScopeLevel.TENANT,
    ).ok

    started = client.post(
        "/v1/workflow/instances",
        headers=_headers(OPERATOR),
        json={"definition_id": definition_id, "payload": {"k": 1}},
    )
    assert started.status_code == 201
    instance_id = started.json()["instance_id"]
    assert (
        client.post(
            f"/v1/workflow/instances/{instance_id}/signals",
            headers=_headers(OPERATOR),
            json={
                "signal_name": "complete",
                "idempotency_key": f"complete-{instance_id}",
                "expected_version": 1,
            },
        ).status_code
        == 200
    )
    compensated = client.post(
        f"/v1/workflow/instances/{instance_id}/compensation",
        headers=_headers(OPERATOR),
        json={"reason": "g107-rollback", "expected_version": 2},
    )
    assert compensated.status_code == 200
    assert compensated.json()["status"] == "compensating"

    started_approval = client.post(
        "/v1/workflow/instances",
        headers=_headers(OPERATOR),
        json={
            "definition_id": definition_id,
            "payload": {},
            "approval_subject_id": str(APPROVER),
            "approval_principal_id": str(AI),
            "approval_action": "commit",
            "approval_resource_ref": "ledger:g107",
        },
    )
    assert started_approval.status_code == 201
    esc_instance = started_approval.json()["instance_id"]
    esc_task = started_approval.json()["task_id"]
    assert esc_task
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=APPROVER,
        resource_type="workflow_task",
        resource_id=UUID(esc_task),
        actions={"escalate"},
    ).ok
    escalated = client.post(
        f"/v1/workflow/instances/{esc_instance}/tasks/{esc_task}/escalation",
        headers=_headers(APPROVER),
        json={
            "to_subject_id": str(ESCALATEE),
            "reason": "g107-ooo",
            "expected_instance_version": 1,
            "expected_task_version": 1,
        },
    )
    assert escalated.status_code == 200
    assert escalated.json()["status"] == "pending_approval"
