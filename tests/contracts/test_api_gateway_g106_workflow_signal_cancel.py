"""PHX-G106 Workflow Signal / Cancel Thin Probe contracts."""

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


def test_terminal_exposes_signal_cancel_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminWorkflowSignalInstance"' in html
    assert 'id="btnAdminWorkflowCancelInstance"' in html
    assert 'id="workflowSignalName"' in html
    assert 'id="workflowSignalIdempotencyKey"' in html
    assert "Signal workflow instance" in html
    assert "Cancel workflow instance" in html
    assert "Workflow signal/cancel 薄探针（G106" in html
    assert "workflowInstanceSignal" in js
    assert "workflowInstanceCancel" in js
    assert "adminSignalWorkflowInstance" in js
    assert "adminCancelWorkflowInstance" in js
    start = js.index("async function adminSignalWorkflowInstance")
    end = js.index("async function adminCompensateWorkflowInstance")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "/compensation" not in chunk
    assert "/escalation" not in chunk


def test_gateway_serves_signal_cancel_ui_and_api() -> None:
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
    assert "Signal workflow instance" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminSignalWorkflowInstance" in script.text

    created = client.post(
        "/v1/workflow/definitions",
        headers=_headers(ADMIN),
        json={
            "name": f"Flow-{uuid4()}",
            "definition_document_ref": "docs/workflows/g106",
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
        actions={"read", "signal", "cancel"},
        scope_level=ScopeLevel.TENANT,
    ).ok

    started = client.post(
        "/v1/workflow/instances",
        headers=_headers(OPERATOR),
        json={"definition_id": definition_id, "payload": {"k": 1}},
    )
    assert started.status_code == 201
    assert started.json()["status"] == "running"
    instance_id = started.json()["instance_id"]

    completed = client.post(
        f"/v1/workflow/instances/{instance_id}/signals",
        headers=_headers(OPERATOR),
        json={
            "signal_name": "complete",
            "idempotency_key": f"complete-{instance_id}",
            "expected_version": 1,
        },
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"

    started2 = client.post(
        "/v1/workflow/instances",
        headers=_headers(OPERATOR),
        json={"definition_id": definition_id, "payload": {"k": 2}},
    )
    assert started2.status_code == 201
    instance2 = started2.json()["instance_id"]
    cancelled = client.post(
        f"/v1/workflow/instances/{instance2}/cancellation",
        headers=_headers(OPERATOR),
        json={"reason": "g106-abort", "expected_version": 1},
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"
