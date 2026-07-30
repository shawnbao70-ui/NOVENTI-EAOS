"""PHX-G31 Gateway domain route completion contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from eaos_platform.knowledge.service import KnowledgeService
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.workflow.service import WorkflowService

ADMIN = uuid4()
OPERATOR = uuid4()
PEER = uuid4()
APPROVER = uuid4()
ESCALATEE = uuid4()
AI = uuid4()
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
def gateway() -> tuple[TestClient, PermissionService]:
    permission = PermissionService(
        grant_administrators={ADMIN},
        decision_auditors={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    workflow = WorkflowService(permission, definition_administrators={ADMIN})
    knowledge = KnowledgeService(permission)
    for resource_type, actions in (
        ("knowledge_entity", {"upsert", "read", "archive", "share"}),
        ("knowledge_link", {"create", "read"}),
        ("knowledge_graph", {"query", "search"}),
        ("knowledge_provenance", {"read"}),
    ):
        assert permission.grant(
            _admin_ctx(),
            principal_subject_id=OPERATOR,
            resource_type=resource_type,
            actions=actions,
            resource_id=TENANT if resource_type == "knowledge_graph" else None,
        ).ok
    client = TestClient(
        create_app(
            permission_service=permission,
            workflow_service=workflow,
            knowledge_service=knowledge,
        )
    )
    return client, permission


def test_workflow_deprecate_signal_cancel_compensate(gateway: tuple) -> None:
    client, permission = gateway
    created = client.post(
        "/v1/workflow/definitions",
        headers=_headers(ADMIN),
        json={
            "name": f"G31-{uuid4()}",
            "definition_document_ref": "docs/workflows/g31",
            "version": "1.0",
        },
    )
    assert created.status_code == 201
    definition_id = created.json()["id"]

    deprecated = client.post(
        f"/v1/workflow/definitions/{definition_id}/deprecation",
        headers=_headers(ADMIN),
        json={"reason": "retire", "expected_version": 1},
    )
    assert deprecated.status_code == 200
    assert deprecated.json()["ok"] is True

    active = client.post(
        "/v1/workflow/definitions",
        headers=_headers(ADMIN),
        json={
            "name": f"G31-run-{uuid4()}",
            "definition_document_ref": "docs/workflows/g31-run",
            "version": "1.0",
        },
    )
    run_def = active.json()["id"]
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=OPERATOR,
        resource_type="workflow_definition",
        resource_id=UUID(run_def),
        actions={"start"},
    ).ok
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=OPERATOR,
        resource_type="workflow_instance",
        actions={"read", "signal", "cancel", "compensate"},
        scope_level=ScopeLevel.TENANT,
    ).ok

    started = client.post(
        "/v1/workflow/instances",
        headers=_headers(OPERATOR),
        json={"definition_id": run_def, "payload": {"k": 1}},
    )
    assert started.status_code == 201
    instance_id = started.json()["instance_id"]
    assert started.json()["status"] == "running"

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

    compensated = client.post(
        f"/v1/workflow/instances/{instance_id}/compensation",
        headers=_headers(OPERATOR),
        json={"reason": "rollback", "expected_version": 2},
    )
    assert compensated.status_code == 200
    assert compensated.json()["status"] == "compensating"

    started2 = client.post(
        "/v1/workflow/instances",
        headers=_headers(OPERATOR),
        json={"definition_id": run_def, "payload": {"k": 2}},
    )
    instance2 = started2.json()["instance_id"]
    cancelled = client.post(
        f"/v1/workflow/instances/{instance2}/cancellation",
        headers=_headers(OPERATOR),
        json={"reason": "abort", "expected_version": 1},
    )
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"


def test_workflow_escalate_task(gateway: tuple) -> None:
    client, permission = gateway
    created = client.post(
        "/v1/workflow/definitions",
        headers=_headers(ADMIN),
        json={
            "name": f"G31-esc-{uuid4()}",
            "definition_document_ref": "docs/workflows/g31-esc",
            "version": "1.0",
        },
    )
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
        actions={"read"},
        scope_level=ScopeLevel.TENANT,
    ).ok
    started = client.post(
        "/v1/workflow/instances",
        headers=_headers(OPERATOR),
        json={
            "definition_id": definition_id,
            "payload": {},
            "approval_subject_id": str(APPROVER),
            "approval_principal_id": str(AI),
            "approval_action": "commit",
            "approval_resource_ref": "ledger:g31",
        },
    )
    assert started.status_code == 201
    instance_id = started.json()["instance_id"]
    task_id = started.json()["task_id"]
    assert permission.grant(
        _admin_ctx(),
        principal_subject_id=APPROVER,
        resource_type="workflow_task",
        resource_id=UUID(task_id),
        actions={"approve", "reject", "escalate"},
    ).ok
    escalated = client.post(
        f"/v1/workflow/instances/{instance_id}/tasks/{task_id}/escalation",
        headers=_headers(APPROVER),
        json={
            "to_subject_id": str(ESCALATEE),
            "reason": "out of office",
            "expected_instance_version": 1,
            "expected_task_version": 1,
        },
    )
    assert escalated.status_code == 200
    assert escalated.json()["status"] == "pending_approval"


def test_knowledge_archive_and_share(gateway: tuple) -> None:
    client, _ = gateway
    created = client.post(
        "/v1/knowledge/entities",
        headers=_headers(),
        json={
            "entity_type": "Capability",
            "name": "Shared Cap",
            "layer": "canonical",
            "source_ref": "docs/g31.md",
            "reason": "seed",
        },
    )
    assert created.status_code == 200
    entity_id = created.json()["id"]
    version = client.get(
        f"/v1/knowledge/entities/{entity_id}",
        headers=_headers(),
    ).json()["version"]

    shared = client.post(
        f"/v1/knowledge/entities/{entity_id}/share",
        headers=_headers(),
        json={
            "share_with_subject_id": str(PEER),
            "source_ref": "docs/g31.md",
            "reason": "collaborate",
            "expected_version": version,
        },
    )
    assert shared.status_code == 200
    assert shared.json()["ok"] is True

    after_share = client.get(
        f"/v1/knowledge/entities/{entity_id}",
        headers=_headers(),
    ).json()
    assert str(PEER) in after_share["shared_with_subject_ids"]

    archived = client.post(
        f"/v1/knowledge/entities/{entity_id}/archive",
        headers=_headers(),
        json={
            "source_ref": "docs/g31.md",
            "reason": "retire",
            "expected_version": after_share["version"],
        },
    )
    assert archived.status_code == 200
    assert archived.json()["ok"] is True
    denied = client.get(
        f"/v1/knowledge/entities/{entity_id}",
        headers=_headers(),
    )
    assert denied.status_code == 409
    assert denied.json()["detail"]["code"] == "KNOWLEDGE_ARCHIVED"
    listed = client.get(
        "/v1/knowledge/entities",
        headers=_headers(),
        params={"includeArchived": "true"},
    )
    assert listed.status_code == 200
    assert any(
        item["id"] == entity_id and item["status"] == "archived"
        for item in listed.json()["data"]
    )


def test_permission_deprecate_and_delegate(gateway: tuple) -> None:
    client, _ = gateway
    created = client.post(
        "/v1/permission/policies",
        headers=_headers(ADMIN),
        json={
            "name": f"g31-{uuid4()}",
            "rules": [
                {
                    "effect": "allow",
                    "actions": ["read"],
                    "resource_type": "memo",
                    "scope_level": "tenant",
                }
            ],
        },
    )
    assert created.status_code == 201
    policy_id = created.json()["id"]
    assert client.post(
        f"/v1/permission/policies/{policy_id}/activation",
        headers=_headers(ADMIN),
        json={"reason": "live", "expected_version": 1},
    ).status_code == 200
    deprecated = client.post(
        f"/v1/permission/policies/{policy_id}/deprecation",
        headers=_headers(ADMIN),
        json={"reason": "supersede", "expected_version": 2},
    )
    assert deprecated.status_code == 200
    assert deprecated.json()["ok"] is True

    parent = client.post(
        "/v1/permission/grants",
        headers=_headers(ADMIN),
        json={
            "principal_id": str(OPERATOR),
            "resource_type": "memo",
            "scope_level": "tenant",
            "actions": ["read", "write"],
            "delegable": True,
            "delegation_depth": 2,
        },
    )
    assert parent.status_code == 201
    grant_id = parent.json()["id"]
    delegated = client.post(
        f"/v1/permission/grants/{grant_id}/delegations",
        headers=_headers(OPERATOR),
        json={
            "delegatee_principal_id": str(PEER),
            "scope_level": "tenant",
            "actions": ["read"],
            "expected_version": 1,
        },
    )
    assert delegated.status_code == 201
    assert "id" in delegated.json()

    allowed = client.post(
        "/v1/permission/evaluations",
        headers=_headers(PEER),
        json={"action": "read", "resource_type": "memo"},
    )
    assert allowed.status_code == 200
    assert allowed.json()["effect"] == "allow"
