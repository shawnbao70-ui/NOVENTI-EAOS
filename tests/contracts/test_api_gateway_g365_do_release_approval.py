"""PHX-G365 DO.release Workflow approval HTTP contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.workflow.service import WorkflowService
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import (
    CONVERSION_RESOURCE,
    CUSTOMER_RESOURCE,
    DELIVERY_ORDER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    POLICY_RESOURCE,
    QUOTE_LINE_RESOURCE,
    QUOTE_RESOURCE,
    REQUIREMENT_RESOURCE,
    SALES_ORDER_RESOURCE,
    CRMService,
)

SUBJECT, TENANT = uuid4(), uuid4()


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g365",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g365-http",
    }


def _client() -> tuple[TestClient, PermissionService]:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    for resource in (
        CUSTOMER_RESOURCE,
        OPPORTUNITY_RESOURCE,
        REQUIREMENT_RESOURCE,
        QUOTE_RESOURCE,
        QUOTE_LINE_RESOURCE,
        CONVERSION_RESOURCE,
        SALES_ORDER_RESOURCE,
        DELIVERY_ORDER_RESOURCE,
        POLICY_RESOURCE,
    ):
        assert permission.grant(
            _ctx(),
            principal_subject_id=SUBJECT,
            resource_type=resource,
            actions={
                "create",
                "read",
                "update",
                "archive",
                "convert",
                "issue",
                "confirm",
                "release",
            },
            scope_level=ScopeLevel.TENANT,
        ).ok
    workflow = WorkflowService(permission, definition_administrators={SUBJECT})
    crm = CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=TENANT),
        audit_log=audit,
    )
    return (
        TestClient(
            create_app(
                permission_service=permission,
                workflow_service=workflow,
                crm_service=crm,
            )
        ),
        permission,
    )


def _draft_delivery_order(client: TestClient) -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": f"G365-{uuid4().hex[:8]}", "display_name": "G365 Customer"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "G365 Opportunity"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={"opportunity_id": opportunity["id"], "title": "G365 Requirement"},
    ).json()["data"]
    quote = client.post(
        "/v1/crm/quotes",
        headers=_headers(),
        json={"requirement_id": requirement["id"]},
    ).json()["data"]
    assert client.post(
        f"/v1/crm/quotes/{quote['id']}/lines",
        headers=_headers(),
        json={"description": "G365 line", "quantity": "1", "unit_price": "10"},
    ).status_code == 201
    assert client.post(
        f"/v1/crm/quotes/{quote['id']}/issue",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    ).status_code == 200
    conversion = client.post(
        f"/v1/crm/quotes/{quote['id']}/convert",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    sales_order = client.post(
        f"/v1/crm/conversions/{conversion['id']}/sales-order",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    assert client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/confirm",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    ).status_code == 200
    response = client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/delivery-order",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    )
    assert response.status_code == 201
    return response.json()["data"]


def _release(
    client: TestClient, delivery_order_id: str, *, approval_ref: str | None = None
):
    body = {"idempotency_key": str(uuid4()), "human_confirm": True}
    if approval_ref is not None:
        body["approval_ref"] = approval_ref
    return client.post(
        f"/v1/crm/delivery-orders/{delivery_order_id}/release",
        headers=_headers(),
        json=body,
    )


def _enable_policy(client: TestClient) -> None:
    response = client.put(
        "/v1/crm/policies/do-release-approval",
        headers=_headers(),
        json={"do_release_approval_required": True, "expected_version": 0},
    )
    assert response.status_code == 200
    assert response.json()["data"]["do_release_approval_required"] is True
    assert client.get(
        "/v1/crm/policies/do-release-approval", headers=_headers()
    ).json()["data"]["do_release_approval_required"] is True


def test_g365_policy_off_keeps_delivery_order_release_unchanged() -> None:
    client, _ = _client()
    delivery_order = _draft_delivery_order(client)

    released = _release(client, delivery_order["id"])

    assert released.status_code == 200
    assert released.json()["data"]["status"] == "released"


def test_g365_policy_on_denies_delivery_order_release_without_approval() -> None:
    client, _ = _client()
    _enable_policy(client)
    delivery_order = _draft_delivery_order(client)

    blocked = _release(client, delivery_order["id"])

    assert blocked.status_code == 403
    assert client.get(
        f"/v1/crm/delivery-orders/{delivery_order['id']}", headers=_headers()
    ).json()["data"]["status"] == "draft"


def test_g365_approved_workflow_unblocks_but_never_auto_releases() -> None:
    client, permission = _client()
    _enable_policy(client)
    delivery_order = _draft_delivery_order(client)
    definition = client.post(
        "/v1/workflow/definitions",
        headers=_headers(),
        json={
            "name": f"G365 DO Release {uuid4()}",
            "definition_document_ref": (
                "docs/decisions/ADR-0394-workflow-do-release-approval-boundary.md"
            ),
            "version": "1",
        },
    )
    assert definition.status_code == 201
    definition_id = UUID(definition.json()["id"])
    assert permission.grant(
        _ctx(),
        principal_subject_id=SUBJECT,
        resource_type="workflow_definition",
        resource_id=definition_id,
        actions={"start"},
    ).ok
    started = client.post(
        "/v1/workflow/instances",
        headers=_headers(),
        json={
            "definition_id": str(definition_id),
            "payload": {
                "delivery_order_id": delivery_order["id"],
                "action": "crm.delivery_order.release",
            },
            "approval_subject_id": str(SUBJECT),
            "approval_principal_id": str(SUBJECT),
            "approval_action": "crm.delivery_order.release",
            "approval_resource_ref": delivery_order["id"],
        },
    )
    assert started.status_code == 201
    instance_id, task_id = started.json()["instance_id"], started.json()["task_id"]
    assert permission.grant(
        _ctx(),
        principal_subject_id=SUBJECT,
        resource_type="workflow_task",
        resource_id=UUID(task_id),
        actions={"approve"},
    ).ok
    approved = client.post(
        f"/v1/workflow/instances/{instance_id}/tasks/{task_id}/approval",
        headers=_headers(),
        json={
            "comment": "G365 approved",
            "expected_instance_version": 1,
            "expected_task_version": 1,
        },
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    assert client.get(
        f"/v1/crm/delivery-orders/{delivery_order['id']}", headers=_headers()
    ).json()["data"]["status"] == "draft"

    released = _release(client, delivery_order["id"], approval_ref=instance_id)
    assert released.status_code == 200
    assert released.json()["data"]["status"] == "released"
