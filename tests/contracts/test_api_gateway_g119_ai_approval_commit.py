"""PHX-G119 AI Approval / Commit Thin Probe contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.workflow.service import WorkflowService
from runtime.ai.service import AIRuntimeService

ROOT = Path(__file__).resolve().parents[2]
ADMIN = uuid4()
AI = uuid4()
APPROVER = uuid4()
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


def _ai_headers(subject_id: UUID = AI) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "ai_employee",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }


def _human_headers(subject_id: UUID = ADMIN) -> dict[str, str]:
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


def test_terminal_exposes_ai_approval_commit_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminAiRequestApproval"' in html
    assert 'id="btnAdminAiCommit"' in html
    assert 'id="aiCommitAction"' in html
    assert 'id="aiCommitResourceRef"' in html
    assert "AI approval/commit 薄探针（G119" in html
    assert "AI Runtime Terminal 运维面齐" in html
    assert "aiApprovals" in js
    assert "aiCommits" in js
    assert "adminRequestAiApproval" in js
    assert "adminCommitAiAction" in js
    start = js.index("async function adminRequestAiApproval")
    end = js.index("async function adminRegisterIdentitySubject")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "expected_fail_closed_without_approval" in chunk
    assert 'subjectType: "ai_employee"' in chunk


def test_ai_approval_and_commit_gate_probe_api() -> None:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    workflow = WorkflowService(permission, definition_administrators={ADMIN})
    ai = AIRuntimeService(permission, workflow)
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=AI,
        resource_type="ai_run",
        actions={"create", "read", "request", "commit"},
    ).ok
    client = TestClient(
        create_app(
            permission_service=permission,
            workflow_service=workflow,
            ai_service=ai,
        )
    )

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Request AI approval" in page.text
    assert "Commit AI action" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminRequestAiApproval" in script.text
    assert "adminCommitAiAction" in script.text

    created = client.post(
        "/v1/ai/runs",
        headers=_ai_headers(),
        json={"goal": "G119 draft", "plan_summary": "approval-gated"},
    )
    assert created.status_code == 201
    run_id = created.json()["data"]

    blocked = client.post(
        f"/v1/ai/runs/{run_id}/commits",
        headers=_ai_headers(),
        json={"action": "invoice.adjust", "resource_ref": f"ai_run:{run_id}"},
    )
    assert blocked.status_code == 403
    assert blocked.json()["detail"]["code"] == "AI_APPROVAL_REQUIRED"

    definition = client.post(
        "/v1/workflow/definitions",
        headers=_human_headers(),
        json={
            "name": f"AI-Approval-{uuid4()}",
            "definition_document_ref": "docs/workflows/g119",
            "version": "1.0",
        },
    )
    assert definition.status_code == 201
    definition_id = definition.json()["id"]
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=AI,
        resource_type="workflow_definition",
        resource_id=UUID(definition_id),
        actions={"start"},
    ).ok

    requested = client.post(
        f"/v1/ai/runs/{run_id}/approvals",
        headers=_ai_headers(),
        json={
            "definition_id": definition_id,
            "approval_subject_id": str(APPROVER),
            "action": "invoice.adjust",
            "resource_ref": f"ai_run:{run_id}",
        },
    )
    assert requested.status_code == 201
    assert requested.json()["data"]

    run = client.get(f"/v1/ai/runs/{run_id}", headers=_ai_headers())
    assert run.status_code == 200
    assert run.json()["status"] == "pending_approval"
