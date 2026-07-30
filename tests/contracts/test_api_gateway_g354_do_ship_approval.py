"""PHX-G354 DO.ship Workflow approval HTTP contracts."""

from __future__ import annotations

from dataclasses import replace
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.workflow.service import WorkflowService
from noventi.crm.models import DeliveryOrderStatus
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
from noventi.inventory.repository import InMemoryInventoryRepository
from noventi.inventory.service import (
    DELIVERY_SHIP_RESOURCE,
    STOCK_RESOURCE,
    DeliveryOrderShipLineSnapshot,
    DeliveryOrderShipSnapshot,
    InventoryService,
)

SUBJECT, TENANT = uuid4(), uuid4()


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


class _CRMReader:
    def __init__(self, repo: InMemoryCRMRepository) -> None:
        self._repo = repo

    def do_ship_approval_required(self) -> bool:
        policy = self._repo.get_confirm_policy()
        return bool(policy is not None and policy.do_ship_approval_required)

    def get_delivery_order_ship_snapshot(
        self, delivery_order_id: UUID
    ) -> DeliveryOrderShipSnapshot | None:
        delivery_order = self._repo.get_delivery_order(delivery_order_id)
        if delivery_order is None:
            return None
        sales_order = self._repo.get_sales_order(delivery_order.sales_order_id)
        if sales_order is None:
            return None
        requirement = self._repo.get_requirement(sales_order.requirement_id)
        opportunity = (
            self._repo.get_opportunity(requirement.opportunity_id)
            if requirement is not None
            else None
        )
        customer = (
            self._repo.get_customer(opportunity.customer_id)
            if opportunity is not None
            else None
        )
        if customer is None:
            return None
        return DeliveryOrderShipSnapshot(
            id=delivery_order.id,
            tenant_id=delivery_order.tenant_id,
            status=delivery_order.status.value,
            version=delivery_order.version,
            sales_order_id=sales_order.id,
            sales_order_status=sales_order.status.value,
            sales_order_version=sales_order.version,
            customer_id=customer.id,
            commercial_hold=customer.commercial_hold,
            lines=tuple(
                DeliveryOrderShipLineSnapshot(id=line.id, quantity=line.quantity)
                for line in self._repo.list_sales_order_lines(sales_order.id)
            ),
        )


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g354",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g354-http",
    }


def _client() -> tuple[TestClient, PermissionService]:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    for resource in (
        CUSTOMER_RESOURCE, OPPORTUNITY_RESOURCE, REQUIREMENT_RESOURCE, QUOTE_RESOURCE,
        QUOTE_LINE_RESOURCE, CONVERSION_RESOURCE, SALES_ORDER_RESOURCE,
        DELIVERY_ORDER_RESOURCE, POLICY_RESOURCE, STOCK_RESOURCE, DELIVERY_SHIP_RESOURCE,
    ):
        assert permission.grant(
            _ctx(), principal_subject_id=SUBJECT, resource_type=resource,
            actions={"create", "read", "update", "convert", "issue", "confirm",
                     "release", "adjust", "ship"},
            scope_level=ScopeLevel.TENANT,
        ).ok
    repo = InMemoryCRMRepository(tenant_id=TENANT)

    def mark_shipped(delivery_order_id: UUID, expected_version: int, _shipped_at) -> None:
        delivery_order = repo.get_delivery_order(delivery_order_id)
        if delivery_order is None:
            raise ValueError("delivery order ship status conflict")
        repo.save_delivery_order(
            replace(delivery_order, status=DeliveryOrderStatus.SHIPPED,
                    version=delivery_order.version + 1),
            expected_version=expected_version,
        )

    reader = _CRMReader(repo)
    return TestClient(create_app(
        permission_service=permission,
        workflow_service=WorkflowService(permission, definition_administrators={SUBJECT}),
        crm_service=CRMService(permission, repository=repo, audit_log=audit),
        inventory_service=InventoryService(
            permission,
            repository=InMemoryInventoryRepository(
                tenant_id=TENANT, mark_delivery_order_shipped=mark_shipped
            ),
            audit_log=audit,
            delivery_order_reader=reader,
            do_ship_approval_policy_reader=reader,
        ),
    )), permission


def _released_and_stocked(client: TestClient) -> dict:
    customer = client.post("/v1/crm/customers", headers=_headers(), json={
        "code": f"G354-{uuid4().hex[:8]}", "display_name": "G354 Customer"
    }).json()["data"]
    opportunity = client.post("/v1/crm/opportunities", headers=_headers(), json={
        "customer_id": customer["id"], "title": "G354 Opportunity"
    }).json()["data"]
    requirement = client.post("/v1/crm/requirements", headers=_headers(), json={
        "opportunity_id": opportunity["id"], "title": "G354 Requirement"
    }).json()["data"]
    quote = client.post("/v1/crm/quotes", headers=_headers(), json={
        "requirement_id": requirement["id"]
    }).json()["data"]
    assert client.post(f"/v1/crm/quotes/{quote['id']}/lines", headers=_headers(), json={
        "description": "G354 line", "quantity": "1", "unit_price": "10"
    }).status_code == 201
    assert client.post(f"/v1/crm/quotes/{quote['id']}/issue", headers=_headers(), json={
        "idempotency_key": str(uuid4()), "human_confirm": True
    }).status_code == 200
    conversion = client.post(f"/v1/crm/quotes/{quote['id']}/convert", headers=_headers(),
                             json={"idempotency_key": str(uuid4())}).json()["data"]
    order = client.post(f"/v1/crm/conversions/{conversion['id']}/sales-order",
                        headers=_headers(), json={"idempotency_key": str(uuid4())}).json()["data"]
    order = client.post(f"/v1/crm/sales-orders/{order['id']}/confirm", headers=_headers(),
                        json={"idempotency_key": str(uuid4()), "human_confirm": True}).json()["data"]
    lines = client.get(f"/v1/crm/sales-orders/{order['id']}/lines", headers=_headers()).json()["data"]
    delivery_order = client.post(f"/v1/crm/sales-orders/{order['id']}/delivery-order",
                                 headers=_headers(), json={"idempotency_key": str(uuid4())}).json()["data"]
    assert client.post(f"/v1/crm/delivery-orders/{delivery_order['id']}/release",
                       headers=_headers(), json={"idempotency_key": str(uuid4()), "human_confirm": True}).status_code == 200
    for line in lines:
        assert client.post("/v1/inventory/stock/adjust", headers=_headers(), json={
            "sales_order_line_id": line["id"], "quantity_delta": line["quantity"],
            "idempotency_key": str(uuid4())
        }).status_code == 200
    return delivery_order


def _ship(client: TestClient, delivery_order_id: str, approval_ref: str | None = None):
    body = {"idempotency_key": str(uuid4()), "human_confirm": True}
    if approval_ref is not None:
        body["approval_ref"] = approval_ref
    return client.post(f"/v1/inventory/delivery-orders/{delivery_order_id}/ship",
                       headers=_headers(), json=body)


def test_g354_policy_off_keeps_do_ship_unchanged() -> None:
    client, _ = _client()
    delivery_order = _released_and_stocked(client)
    assert _ship(client, delivery_order["id"]).status_code == 200


def test_g354_policy_on_denies_do_ship_without_approval() -> None:
    client, _ = _client()
    assert client.put("/v1/crm/policies/do-ship-approval", headers=_headers(), json={
        "do_ship_approval_required": True, "expected_version": 0
    }).status_code == 200
    delivery_order = _released_and_stocked(client)
    assert _ship(client, delivery_order["id"]).status_code == 403
    assert client.get(f"/v1/crm/delivery-orders/{delivery_order['id']}",
                      headers=_headers()).json()["data"]["status"] == "released"


def test_g354_approved_workflow_unblocks_but_never_auto_ships() -> None:
    client, permission = _client()
    assert client.put("/v1/crm/policies/do-ship-approval", headers=_headers(), json={
        "do_ship_approval_required": True, "expected_version": 0
    }).status_code == 200
    delivery_order = _released_and_stocked(client)
    definition = client.post("/v1/workflow/definitions", headers=_headers(), json={
        "name": f"G354 DO Ship {uuid4()}",
        "definition_document_ref": "docs/decisions/ADR-0385-workflow-do-ship-approval-boundary.md",
        "version": "1",
    })
    assert definition.status_code == 201
    definition_id = UUID(definition.json()["id"])
    assert permission.grant(_ctx(), principal_subject_id=SUBJECT,
                            resource_type="workflow_definition", resource_id=definition_id,
                            actions={"start"}).ok
    started = client.post("/v1/workflow/instances", headers=_headers(), json={
        "definition_id": str(definition_id),
        "payload": {"delivery_order_id": delivery_order["id"], "action": "inventory.delivery_order.ship"},
        "approval_subject_id": str(SUBJECT), "approval_principal_id": str(SUBJECT),
        "approval_action": "inventory.delivery_order.ship",
        "approval_resource_ref": delivery_order["id"],
    })
    assert started.status_code == 201
    instance_id, task_id = started.json()["instance_id"], started.json()["task_id"]
    assert permission.grant(_ctx(), principal_subject_id=SUBJECT,
                            resource_type="workflow_task", resource_id=UUID(task_id),
                            actions={"approve"}).ok
    assert client.post(f"/v1/workflow/instances/{instance_id}/tasks/{task_id}/approval",
                       headers=_headers(), json={"comment": "G354 approved",
                       "expected_instance_version": 1, "expected_task_version": 1}).status_code == 200
    assert client.get(f"/v1/crm/delivery-orders/{delivery_order['id']}",
                      headers=_headers()).json()["data"]["status"] == "released"
    assert _ship(client, delivery_order["id"], instance_id).status_code == 200
