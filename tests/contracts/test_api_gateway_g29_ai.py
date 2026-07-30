"""PHX-G29 Gateway AI Runtime HTTP surface contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.workflow.service import WorkflowService
from runtime.ai.service import AIRuntimeService

ADMIN = uuid4()
AI = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _headers(
    subject_id: UUID = AI,
    *,
    subject_type: str = "ai_employee",
    **extra: str,
) -> dict[str, str]:
    base = {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": subject_type,
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }
    base.update(extra)
    return base


def _admin_ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


@pytest.fixture()
def gateway() -> TestClient:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    workflow = WorkflowService(permission, definition_administrators={ADMIN})
    ai = AIRuntimeService(permission, workflow)
    admin = _admin_ctx()
    assert permission.grant(
        admin,
        principal_subject_id=AI,
        resource_type="ai_run",
        actions={"create", "read", "request", "commit"},
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=AI,
        resource_type="ai_memory",
        actions={"read", "write"},
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=AI,
        resource_type="tool",
        actions={"invoke_tool"},
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=ADMIN,
        resource_type="tool",
        actions={"register"},
    ).ok
    return TestClient(
        create_app(
            permission_service=permission,
            workflow_service=workflow,
            ai_service=ai,
        )
    )


def test_ai_requires_trusted_headers(gateway: TestClient) -> None:
    response = gateway.post("/v1/ai/runs", json={"goal": "x"})
    assert response.status_code == 401


def test_human_subject_cannot_create_run(gateway: TestClient) -> None:
    response = gateway.post(
        "/v1/ai/runs",
        headers=_headers(ADMIN, subject_type="human"),
        json={"goal": "should fail"},
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "AI_RUNTIME_REQUIRED"


def test_create_get_tool_memory_and_commit_requires_approval(
    gateway: TestClient,
) -> None:
    created = gateway.post(
        "/v1/ai/runs",
        headers=_headers(),
        json={"goal": "Draft invoice", "plan_summary": "read then commit"},
    )
    assert created.status_code == 201
    assert created.json()["ok"] is True
    run_id = created.json()["data"]

    fetched = gateway.get(f"/v1/ai/runs/{run_id}", headers=_headers())
    assert fetched.status_code == 200
    assert fetched.json()["goal"] == "Draft invoice"
    assert fetched.json()["status"] == "planned"

    tool = gateway.post(
        "/v1/ai/tools",
        headers=_headers(ADMIN, subject_type="human"),
        json={
            "name": "ledger.read",
            "description": "Read ledger",
            "high_impact": False,
        },
    )
    assert tool.status_code == 201

    invoked = gateway.post(
        f"/v1/ai/runs/{run_id}/tools/invocations",
        headers=_headers(),
        json={"tool_name": "ledger.read", "arguments": {"account": "A-1"}},
    )
    assert invoked.status_code == 200
    assert invoked.json()["data"]["tool_name"] == "ledger.read"

    written = gateway.post(
        f"/v1/ai/runs/{run_id}/memory",
        headers=_headers(),
        json={"key": "draft", "value": {"amount": 10}},
    )
    assert written.status_code == 200
    assert written.json()["ok"] is True

    memory = gateway.get(
        f"/v1/ai/runs/{run_id}/memory/draft",
        headers=_headers(),
    )
    assert memory.status_code == 200
    assert memory.json()["value"]["amount"] == 10

    commit = gateway.post(
        f"/v1/ai/runs/{run_id}/commits",
        headers=_headers(),
        json={"action": "invoice.adjust", "resource_ref": f"ai_run:{run_id}"},
    )
    assert commit.status_code == 403
    assert commit.json()["detail"]["code"] == "AI_APPROVAL_REQUIRED"


def test_body_cannot_elevate_context(gateway: TestClient) -> None:
    response = gateway.post(
        "/v1/ai/runs",
        headers=_headers(),
        json={
            "goal": "elevate",
            "tenant_id": str(uuid4()),
            "platform_scope": True,
        },
    )
    assert response.status_code == 422
    locs = [tuple(err.get("loc", ())) for err in response.json()["detail"]]
    assert any("tenant_id" in loc for loc in locs)
