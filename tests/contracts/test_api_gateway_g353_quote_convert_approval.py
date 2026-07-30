"""PHX-G353 Quote.convert Workflow approval HTTP contracts."""

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
        correlation_id="corr-g353",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g353-http",
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
            actions={"create", "read", "update", "archive", "convert", "issue"},
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


def _issued_quote(client: TestClient) -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": f"G353-{uuid4().hex[:8]}", "display_name": "G353 Customer"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "G353 Opportunity"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={"opportunity_id": opportunity["id"], "title": "G353 Requirement"},
    ).json()["data"]
    quote = client.post(
        "/v1/crm/quotes",
        headers=_headers(),
        json={"requirement_id": requirement["id"]},
    ).json()["data"]
    assert client.post(
        f"/v1/crm/quotes/{quote['id']}/lines",
        headers=_headers(),
        json={"description": "G353 line", "quantity": "1", "unit_price": "10"},
    ).status_code == 201
    issued = client.post(
        f"/v1/crm/quotes/{quote['id']}/issue",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert issued.status_code == 200
    return quote


def _enable_policy(client: TestClient) -> None:
    response = client.put(
        "/v1/crm/policies/quote-convert-approval",
        headers=_headers(),
        json={"quote_convert_approval_required": True, "expected_version": 0},
    )
    assert response.status_code == 200
    assert response.json()["data"]["quote_convert_approval_required"] is True


def _convert(
    client: TestClient, quote_id: str, *, approval_ref: str | None = None
):
    body = {"idempotency_key": str(uuid4())}
    if approval_ref is not None:
        body["approval_ref"] = approval_ref
    return client.post(
        f"/v1/crm/quotes/{quote_id}/convert",
        headers=_headers(),
        json=body,
    )


def test_g353_policy_off_keeps_quote_convert_unchanged() -> None:
    client, _ = _client()
    quote = _issued_quote(client)

    converted = _convert(client, quote["id"])

    assert converted.status_code == 201
    assert converted.json()["data"]["quote_id"] == quote["id"]


def test_g353_policy_on_denies_quote_convert_without_approval() -> None:
    client, _ = _client()
    _enable_policy(client)
    quote = _issued_quote(client)

    blocked = _convert(client, quote["id"])

    assert blocked.status_code == 403
    assert client.get(f"/v1/crm/quotes/{quote['id']}", headers=_headers()).json()[
        "data"
    ]["status"] == "issued"


def test_g353_approved_workflow_unblocks_but_never_auto_converts() -> None:
    client, permission = _client()
    _enable_policy(client)
    quote = _issued_quote(client)

    definition = client.post(
        "/v1/workflow/definitions",
        headers=_headers(),
        json={
            "name": f"G353 Quote Convert {uuid4()}",
            "definition_document_ref": (
                "docs/decisions/ADR-0384-workflow-quote-convert-approval-boundary.md"
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
            "payload": {"quote_id": quote["id"], "action": "crm.quote.convert"},
            "approval_subject_id": str(SUBJECT),
            "approval_principal_id": str(SUBJECT),
            "approval_action": "crm.quote.convert",
            "approval_resource_ref": quote["id"],
        },
    )
    assert started.status_code == 201
    instance_id, task_id = started.json()["instance_id"], started.json()["task_id"]
    assert task_id
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
            "comment": "G353 approved",
            "expected_instance_version": 1,
            "expected_task_version": 1,
        },
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    assert client.get(f"/v1/crm/quotes/{quote['id']}", headers=_headers()).json()[
        "data"
    ]["status"] == "issued"

    converted = _convert(client, quote["id"], approval_ref=instance_id)
    assert converted.status_code == 201
    assert converted.json()["data"]["quote_id"] == quote["id"]
