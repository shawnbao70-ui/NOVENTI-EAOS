"""PHX-G117 AI Runtime Status / Run Thin Probe contracts."""

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


def _headers(subject_id: UUID = AI) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "ai_employee",
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


def test_terminal_exposes_ai_probe_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminAiStatus"' in html
    assert 'id="btnAdminAiCreateRun"' in html
    assert 'id="btnAdminAiGetRun"' in html
    assert 'id="aiRunId"' in html
    assert 'id="aiRunGoal"' in html
    assert "AI Runtime 状态/run 薄探针（G117" in html
    assert 'aiStatus: "/v1/ai/status"' in js
    assert 'aiRuns: "/v1/ai/runs"' in js
    assert "adminCreateAiRun" in js
    assert "adminGetAiRun" in js
    assert 'subjectType: "ai_employee"' in js
    start = js.index("async function adminCreateAiRun")
    end = js.index("async function adminRegisterAiTool")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "/tools" not in chunk
    assert "/memory" not in chunk
    assert "/approvals" not in chunk
    assert "/commits" not in chunk


def test_ai_status_and_probe_api() -> None:
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
        actions={"create", "read"},
    ).ok
    client = TestClient(
        create_app(
            permission_service=permission,
            workflow_service=workflow,
            ai_service=ai,
        )
    )

    status = client.get("/v1/ai/status")
    assert status.status_code == 200
    data = status.json()["data"]
    assert data["writable"] is False
    assert data["ai_subject_required"] is True
    assert data["commit_requires_approval"] is True
    assert "run_create" in data["supported_surfaces"]
    assert "run_get" in data["supported_surfaces"]

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "AI Runtime status" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminCreateAiRun" in script.text
    assert 'subjectType: "ai_employee"' in script.text

    created = client.post(
        "/v1/ai/runs",
        headers=_headers(),
        json={"goal": "G117 draft", "plan_summary": "probe"},
    )
    assert created.status_code == 201
    run_id = created.json()["data"]

    fetched = client.get(f"/v1/ai/runs/{run_id}", headers=_headers())
    assert fetched.status_code == 200
    assert fetched.json()["goal"] == "G117 draft"
    assert fetched.json()["status"] == "planned"

    human_denied = client.post(
        "/v1/ai/runs",
        headers={
            "X-EAOS-Subject-Id": str(AI),
            "X-EAOS-Subject-Type": "human",
            "X-EAOS-Tenant-Id": str(TENANT),
            "X-Correlation-Id": CORR,
        },
        json={"goal": "should fail"},
    )
    assert human_denied.status_code == 403
    assert human_denied.json()["detail"]["code"] == "AI_RUNTIME_REQUIRED"
