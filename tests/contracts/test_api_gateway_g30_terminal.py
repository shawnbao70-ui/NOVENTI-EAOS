"""PHX-G30 Gateway Smart Terminal HTTP surface contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.workflow.service import WorkflowService
from smart_terminal.service import SmartTerminalService

ADMIN = uuid4()
OPERATOR = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _headers(subject_id: UUID = OPERATOR, **extra: str) -> dict[str, str]:
    base = {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
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
    terminal = SmartTerminalService(permission, workflow)
    admin = _admin_ctx()
    for resource_type, actions in (
        ("terminal_session", {"open", "read", "close"}),
        ("terminal_intent", {"compose", "read"}),
        ("terminal_preview", {"build", "read"}),
        ("terminal_approval", {"present", "request"}),
        ("terminal_commit", {"execute"}),
        # Preview binds Package metadata when declared; undeclared probes need resolve.
        ("package_action", {"resolve"}),
    ):
        assert permission.grant(
            admin,
            principal_subject_id=OPERATOR,
            resource_type=resource_type,
            actions=actions,
        ).ok
    return TestClient(
        create_app(
            permission_service=permission,
            workflow_service=workflow,
            terminal_service=terminal,
        )
    )


def test_terminal_requires_trusted_headers(gateway: TestClient) -> None:
    response = gateway.post("/v1/terminal/sessions", json={})
    assert response.status_code == 401


def test_claimed_mismatch_denied(gateway: TestClient) -> None:
    response = gateway.post(
        "/v1/terminal/sessions",
        headers=_headers(),
        json={"claimed_tenant_id": str(uuid4())},
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "TERMINAL_CONTEXT_ELEVATION_DENIED"


def test_session_intent_preview_commit_low_impact(gateway: TestClient) -> None:
    opened = gateway.post(
        "/v1/terminal/sessions",
        headers=_headers(),
        json={"device_trust": "trusted"},
    )
    assert opened.status_code == 201
    session_id = opened.json()["data"]

    session = gateway.get(
        f"/v1/terminal/sessions/{session_id}",
        headers=_headers(),
    )
    assert session.status_code == 200
    assert session.json()["status"] == "open"
    assert session.json()["tenant_id"] == str(TENANT)

    intent = gateway.post(
        "/v1/terminal/intents",
        headers=_headers(),
        json={
            "terminal_session_id": session_id,
            "text": "Prepare monthly report",
        },
    )
    assert intent.status_code == 201
    intent_id = intent.json()["data"]

    preview = gateway.post(
        "/v1/terminal/previews",
        headers=_headers(),
        json={
            "intent_id": intent_id,
            "action": "report.generate",
            "resource_ref": "report:monthly",
            "plan_version": "v1",
            "scope": "tenant",
            "impact_summary": "Generate read-only monthly report",
            "high_impact": False,
        },
    )
    assert preview.status_code == 201
    preview_id = preview.json()["data"]

    fetched = gateway.get(
        f"/v1/terminal/previews/{preview_id}",
        headers=_headers(),
    )
    assert fetched.status_code == 200
    assert fetched.json()["status"] == "active"

    committed = gateway.post(
        f"/v1/terminal/previews/{preview_id}/commits",
        headers=_headers(),
    )
    assert committed.status_code == 200
    assert committed.json()["verified_against"] == "permission"
    assert committed.json()["approved"] is False

    closed = gateway.post(
        f"/v1/terminal/sessions/{session_id}",
        headers=_headers(),
    )
    assert closed.status_code == 200
    assert closed.json()["data"] is True


def test_high_impact_commit_requires_approval(gateway: TestClient) -> None:
    opened = gateway.post("/v1/terminal/sessions", headers=_headers(), json={})
    session_id = opened.json()["data"]
    intent = gateway.post(
        "/v1/terminal/intents",
        headers=_headers(),
        json={"terminal_session_id": session_id, "text": "Adjust ledger"},
    )
    preview = gateway.post(
        "/v1/terminal/previews",
        headers=_headers(),
        json={
            "intent_id": intent.json()["data"],
            "action": "ledger.adjust",
            "resource_ref": "ledger:42",
            "plan_version": "v1",
            "scope": "tenant",
            "impact_summary": "Adjust ledger balance by 100",
            "high_impact": True,
        },
    )
    preview_id = preview.json()["data"]
    blocked = gateway.post(
        f"/v1/terminal/previews/{preview_id}/commits",
        headers=_headers(),
    )
    assert blocked.status_code == 403
    assert blocked.json()["detail"]["code"] == "TERMINAL_APPROVAL_INVALID"


def test_body_cannot_elevate_with_tenant_id(gateway: TestClient) -> None:
    response = gateway.post(
        "/v1/terminal/sessions",
        headers=_headers(),
        json={"tenant_id": str(uuid4()), "platform_scope": True},
    )
    # Closed OpenSessionRequest rejects unknown fields before domain elevation check.
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any("tenant_id" in str(item.get("loc", ())) for item in detail)


def test_intent_body_cannot_elevate_context(gateway: TestClient) -> None:
    opened = gateway.post("/v1/terminal/sessions", headers=_headers(), json={})
    session_id = opened.json()["data"]
    response = gateway.post(
        "/v1/terminal/intents",
        headers=_headers(),
        json={
            "terminal_session_id": session_id,
            "text": "elevate",
            "tenant_id": str(uuid4()),
            "platform_scope": True,
        },
    )
    assert response.status_code == 422
    locs = [tuple(err.get("loc", ())) for err in response.json()["detail"]]
    assert any("tenant_id" in loc for loc in locs)


def test_preview_body_cannot_elevate_context(gateway: TestClient) -> None:
    opened = gateway.post("/v1/terminal/sessions", headers=_headers(), json={})
    session_id = opened.json()["data"]
    intent = gateway.post(
        "/v1/terminal/intents",
        headers=_headers(),
        json={"terminal_session_id": session_id, "text": "elevate preview"},
    )
    response = gateway.post(
        "/v1/terminal/previews",
        headers=_headers(),
        json={
            "intent_id": intent.json()["data"],
            "action": "report.generate",
            "resource_ref": "report:x",
            "plan_version": "v1",
            "scope": "tenant",
            "impact_summary": "probe",
            "high_impact": False,
            "tenant_id": str(uuid4()),
        },
    )
    assert response.status_code == 422
    locs = [tuple(err.get("loc", ())) for err in response.json()["detail"]]
    assert any("tenant_id" in loc for loc in locs)
