"""PHX-G23 Gateway Workflow HTTP surface contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.workflow.service import WorkflowService

ADMIN = uuid4()
INITIATOR = uuid4()
APPROVER = uuid4()
AI = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _headers(subject_id: UUID, **extra: str) -> dict[str, str]:
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
def gateway() -> tuple[TestClient, PermissionService, WorkflowService]:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    workflow = WorkflowService(
        permission,
        definition_administrators={ADMIN},
    )
    client = TestClient(
        create_app(permission_service=permission, workflow_service=workflow)
    )
    return client, permission, workflow


def _register_and_grant_start(
    client: TestClient,
    permission: PermissionService,
) -> str:
    created = client.post(
        "/v1/workflow/definitions",
        headers=_headers(ADMIN),
        json={
            "name": f"Flow-{uuid4()}",
            "definition_document_ref": "docs/workflows/g23",
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
    return definition_id


def test_workflow_requires_trusted_headers(gateway: tuple) -> None:
    client, _, _ = gateway
    response = client.get("/v1/workflow/tasks")
    assert response.status_code == 401


def test_create_definition_and_start_approval(gateway: tuple) -> None:
    client, permission, _ = gateway
    definition_id = _register_and_grant_start(client, permission)
    started = client.post(
        "/v1/workflow/instances",
        headers=_headers(INITIATOR),
        json={
            "definition_id": definition_id,
            "payload": {"action": "high-impact"},
            "approval_subject_id": str(APPROVER),
            "approval_principal_id": str(AI),
            "approval_action": "commit",
            "approval_resource_ref": "ledger:1",
        },
    )
    assert started.status_code == 201
    body = started.json()
    assert body["status"] == "pending_approval"
    assert body["task_id"] is not None

    instance = client.get(
        f"/v1/workflow/instances/{body['instance_id']}",
        headers=_headers(INITIATOR),
    )
    assert instance.status_code == 200
    assert instance.json()["status"] == "pending_approval"
    assert instance.json()["current_task_id"] == body["task_id"]


def test_approve_task_happy_path(gateway: tuple) -> None:
    client, permission, _ = gateway
    definition_id = _register_and_grant_start(client, permission)
    started = client.post(
        "/v1/workflow/instances",
        headers=_headers(INITIATOR),
        json={
            "definition_id": definition_id,
            "payload": {"action": "write"},
            "approval_subject_id": str(APPROVER),
            "approval_principal_id": str(AI),
            "approval_action": "commit",
            "approval_resource_ref": "ledger:2",
        },
    )
    instance_id = started.json()["instance_id"]
    task_id = started.json()["task_id"]
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=APPROVER,
        resource_type="workflow_task",
        resource_id=UUID(task_id),
        actions={"approve", "reject"},
    ).ok

    tasks = client.get("/v1/workflow/tasks", headers=_headers(APPROVER))
    assert tasks.status_code == 200
    assert any(item["id"] == task_id for item in tasks.json())

    approved = client.post(
        f"/v1/workflow/instances/{instance_id}/tasks/{task_id}/approval",
        headers=_headers(APPROVER),
        json={
            "comment": "ok",
            "expected_instance_version": 1,
            "expected_task_version": 1,
        },
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"


def test_reject_task(gateway: tuple) -> None:
    client, permission, _ = gateway
    definition_id = _register_and_grant_start(client, permission)
    started = client.post(
        "/v1/workflow/instances",
        headers=_headers(INITIATOR),
        json={
            "definition_id": definition_id,
            "payload": {},
            "approval_subject_id": str(APPROVER),
            "approval_principal_id": str(AI),
            "approval_action": "commit",
            "approval_resource_ref": "ledger:3",
        },
    )
    instance_id = started.json()["instance_id"]
    task_id = started.json()["task_id"]
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=APPROVER,
        resource_type="workflow_task",
        resource_id=UUID(task_id),
        actions={"approve", "reject"},
    ).ok
    rejected = client.post(
        f"/v1/workflow/instances/{instance_id}/tasks/{task_id}/rejection",
        headers=_headers(APPROVER),
        json={
            "reason": "no",
            "expected_instance_version": 1,
            "expected_task_version": 1,
        },
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rejected"


def test_start_without_permission_denied(gateway: tuple) -> None:
    client, _, _ = gateway
    created = client.post(
        "/v1/workflow/definitions",
        headers=_headers(ADMIN),
        json={
            "name": f"Locked-{uuid4()}",
            "definition_document_ref": "docs/workflows/locked",
            "version": "1.0",
        },
    )
    response = client.post(
        "/v1/workflow/instances",
        headers=_headers(INITIATOR),
        json={"definition_id": created.json()["id"], "payload": {}},
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "PERMISSION_DENIED"


def test_start_rejects_context_override(gateway: tuple) -> None:
    client, permission, _ = gateway
    definition_id = _register_and_grant_start(client, permission)
    response = client.post(
        "/v1/workflow/instances",
        headers=_headers(INITIATOR),
        json={
            "definition_id": definition_id,
            "payload": {},
            "tenant_id": str(uuid4()),
            "platform_scope": True,
        },
    )
    # Closed StartInstanceRequest rejects unknown fields before domain elevation check.
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any("tenant_id" in str(item.get("loc", ())) for item in detail)


def test_non_admin_cannot_register_definition(gateway: tuple) -> None:
    client, _, _ = gateway
    response = client.post(
        "/v1/workflow/definitions",
        headers=_headers(INITIATOR),
        json={
            "name": "Nope",
            "definition_document_ref": "docs/workflows/x",
            "version": "1.0",
        },
    )
    assert response.status_code == 403
