"""PHX-G118 AI Tools / Memory Thin Probe contracts."""

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


def test_terminal_exposes_ai_tools_memory_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminAiRegisterTool"' in html
    assert 'id="btnAdminAiInvokeTool"' in html
    assert 'id="btnAdminAiWriteMemory"' in html
    assert 'id="btnAdminAiReadMemory"' in html
    assert 'id="aiToolName"' in html
    assert 'id="aiMemoryKey"' in html
    assert "AI tools/memory 薄探针（G118" in html
    assert "aiTools" in js
    assert "aiToolInvocations" in js
    assert "aiMemory" in js
    assert "aiMemoryKey" in js
    assert "adminRegisterAiTool" in js
    assert "adminInvokeAiTool" in js
    assert "adminWriteAiMemory" in js
    assert "adminReadAiMemory" in js
    start = js.index("async function adminRegisterAiTool")
    end = js.index("async function adminRequestAiApproval")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "/approvals" not in chunk
    assert "/commits" not in chunk


def test_ai_tools_memory_probe_api() -> None:
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
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=AI,
        resource_type="ai_memory",
        actions={"read", "write"},
    ).ok
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=AI,
        resource_type="tool",
        actions={"invoke_tool"},
    ).ok
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=ADMIN,
        resource_type="tool",
        actions={"register"},
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
    assert "Register AI tool" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminRegisterAiTool" in script.text
    assert "adminWriteAiMemory" in script.text

    created = client.post(
        "/v1/ai/runs",
        headers=_ai_headers(),
        json={"goal": "G118 draft", "plan_summary": "tool+memory"},
    )
    assert created.status_code == 201
    run_id = created.json()["data"]

    tool = client.post(
        "/v1/ai/tools",
        headers=_human_headers(),
        json={
            "name": "ledger.read",
            "description": "Read ledger",
            "high_impact": False,
        },
    )
    assert tool.status_code == 201

    invoked = client.post(
        f"/v1/ai/runs/{run_id}/tools/invocations",
        headers=_ai_headers(),
        json={"tool_name": "ledger.read", "arguments": {"account": "A-1"}},
    )
    assert invoked.status_code == 200
    assert invoked.json()["data"]["tool_name"] == "ledger.read"

    written = client.post(
        f"/v1/ai/runs/{run_id}/memory",
        headers=_ai_headers(),
        json={"key": "draft", "value": {"amount": 10}},
    )
    assert written.status_code == 200
    assert written.json()["ok"] is True

    memory = client.get(
        f"/v1/ai/runs/{run_id}/memory/draft",
        headers=_ai_headers(),
    )
    assert memory.status_code == 200
    assert memory.json()["value"]["amount"] == 10
