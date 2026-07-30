"""PHX-G367 Ship POD / evidence HTTP contracts."""

from __future__ import annotations

from dataclasses import replace
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.models import DeliveryOrderStatus, SalesOrderStatus
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
    SHIP_POD_POLICY_RESOURCE,
    STOCK_RESOURCE,
    DeliveryOrderShipLineSnapshot,
    DeliveryOrderShipSnapshot,
    InventoryService,
)

SUBJECT, TENANT = uuid4(), uuid4()


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


class _CRMShipReader:
    def __init__(self, crm_repo: InMemoryCRMRepository) -> None:
        self._crm = crm_repo

    def get_delivery_order_ship_snapshot(
        self, delivery_order_id: UUID
    ) -> DeliveryOrderShipSnapshot | None:
        delivery_order = self._crm.get_delivery_order(delivery_order_id)
        if delivery_order is None:
            return None
        sales_order = self._crm.get_sales_order(delivery_order.sales_order_id)
        if sales_order is None:
            return None
        requirement = self._crm.get_requirement(sales_order.requirement_id)
        if requirement is None:
            return None
        opportunity = self._crm.get_opportunity(requirement.opportunity_id)
        if opportunity is None:
            return None
        customer = self._crm.get_customer(opportunity.customer_id)
        if customer is None:
            return None
        lines = self._crm.list_sales_order_lines(sales_order.id)
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
                for line in lines
            ),
        )


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g367",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g367-http",
    }


def _client() -> TestClient:
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
        STOCK_RESOURCE,
        DELIVERY_SHIP_RESOURCE,
        SHIP_POD_POLICY_RESOURCE,
    ):
        assert permission.grant(
            _ctx(),
            principal_subject_id=SUBJECT,
            resource_type=resource,
            actions={
                "create",
                "read",
                "update",
                "convert",
                "issue",
                "confirm",
                "release",
                "adjust",
                "ship",
            },
            scope_level=ScopeLevel.TENANT,
        ).ok
    crm_repo = InMemoryCRMRepository(tenant_id=TENANT)

    def _mark_shipped(
        delivery_order_id: UUID, expected_version: int, _shipped_at
    ) -> None:
        delivery_order = crm_repo.get_delivery_order(delivery_order_id)
        if delivery_order is None or delivery_order.version != expected_version:
            raise ValueError("delivery order ship status conflict")
        sales_order = crm_repo.get_sales_order(delivery_order.sales_order_id)
        if sales_order is None:
            raise ValueError("sales order not found")
        quantity = sum(
            (
                line.quantity
                for line in crm_repo.list_sales_order_lines(sales_order.id)
            ),
            start=0,
        )
        crm_repo.save_delivery_order(
            replace(
                delivery_order,
                status=DeliveryOrderStatus.SHIPPED,
                version=delivery_order.version + 1,
            ),
            expected_version=expected_version,
        )
        crm_repo.save_sales_order(
            replace(
                sales_order,
                status=SalesOrderStatus.SHIPPED,
                shipped_quantity=sales_order.shipped_quantity + quantity,
                version=sales_order.version + 1,
            ),
            expected_version=sales_order.version,
        )

    return TestClient(
        create_app(
            permission_service=permission,
            crm_service=CRMService(
                permission, repository=crm_repo, audit_log=audit
            ),
            inventory_service=InventoryService(
                permission,
                repository=InMemoryInventoryRepository(
                    tenant_id=TENANT,
                    mark_delivery_order_shipped=_mark_shipped,
                ),
                audit_log=audit,
                delivery_order_reader=_CRMShipReader(crm_repo),
            ),
        )
    )


def _released_and_stocked(client: TestClient) -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": f"G367-{uuid4().hex[:8]}", "display_name": "G367 Customer"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "G367 Opportunity"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={"opportunity_id": opportunity["id"], "title": "G367 Requirement"},
    ).json()["data"]
    quote = client.post(
        "/v1/crm/quotes",
        headers=_headers(),
        json={"requirement_id": requirement["id"]},
    ).json()["data"]
    assert (
        client.post(
            f"/v1/crm/quotes/{quote['id']}/lines",
            headers=_headers(),
            json={"description": "G367 line", "quantity": "1", "unit_price": "10"},
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"/v1/crm/quotes/{quote['id']}/issue",
            headers=_headers(),
            json={"idempotency_key": str(uuid4()), "human_confirm": True},
        ).status_code
        == 200
    )
    conversion = client.post(
        f"/v1/crm/quotes/{quote['id']}/convert",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    order = client.post(
        f"/v1/crm/conversions/{conversion['id']}/sales-order",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    order = client.post(
        f"/v1/crm/sales-orders/{order['id']}/confirm",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    ).json()["data"]
    lines = client.get(
        f"/v1/crm/sales-orders/{order['id']}/lines", headers=_headers()
    ).json()["data"]
    delivery_order = client.post(
        f"/v1/crm/sales-orders/{order['id']}/delivery-order",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    assert (
        client.post(
            f"/v1/crm/delivery-orders/{delivery_order['id']}/release",
            headers=_headers(),
            json={"idempotency_key": str(uuid4()), "human_confirm": True},
        ).status_code
        == 200
    )
    for line in lines:
        assert (
            client.post(
                "/v1/inventory/stock/adjust",
                headers=_headers(),
                json={
                    "sales_order_line_id": line["id"],
                    "quantity_delta": line["quantity"],
                    "idempotency_key": str(uuid4()),
                },
            ).status_code
            == 200
        )
    return delivery_order


def _ship(
    client: TestClient,
    delivery_order_id: str,
    *,
    pod_ref: str | None = None,
):
    body: dict = {"idempotency_key": str(uuid4()), "human_confirm": True}
    if pod_ref is not None:
        body["pod_ref"] = pod_ref
    return client.post(
        f"/v1/inventory/delivery-orders/{delivery_order_id}/ship",
        headers=_headers(),
        json=body,
    )


def test_g367_default_policy_allows_ship_without_pod() -> None:
    client = _client()
    default = client.get("/v1/inventory/policies/ship-pod", headers=_headers())
    assert default.status_code == 200
    assert default.json()["data"]["ship_pod_required"] is False
    assert default.json()["data"]["version"] == 0

    delivery_order = _released_and_stocked(client)
    shipped = _ship(client, delivery_order["id"])
    assert shipped.status_code == 200
    assert shipped.json()["data"]["pod_ref"] is None
    assert shipped.json()["data"]["pod_captured_at"] is None


def test_g367_required_policy_rejects_without_pod_accepts_with_pod() -> None:
    client = _client()
    updated = client.put(
        "/v1/inventory/policies/ship-pod",
        headers=_headers(),
        json={"ship_pod_required": True, "expected_version": 0},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["ship_pod_required"] is True
    assert updated.json()["data"]["version"] == 1

    delivery_order = _released_and_stocked(client)
    denied = _ship(client, delivery_order["id"])
    assert denied.status_code == 400
    assert "pod" in denied.json()["detail"]["message"].casefold()

    assert (
        client.get(
            f"/v1/crm/delivery-orders/{delivery_order['id']}",
            headers=_headers(),
        ).json()["data"]["status"]
        == "released"
    )

    shipped = _ship(client, delivery_order["id"], pod_ref="POD-G367-001")
    assert shipped.status_code == 200
    assert shipped.json()["data"]["pod_ref"] == "POD-G367-001"
    assert shipped.json()["data"]["pod_captured_at"] is not None

    fetched = client.get(
        f"/v1/inventory/delivery-orders/{delivery_order['id']}/ship",
        headers=_headers(),
    )
    assert fetched.status_code == 200
    assert fetched.json()["data"]["pod_ref"] == "POD-G367-001"
    assert fetched.json()["data"]["pod_captured_at"] is not None


def test_g367_openapi_closed_for_ship_pod() -> None:
    client = _client()
    assert (
        client.put(
            "/v1/inventory/policies/ship-pod",
            headers=_headers(),
            json={
                "ship_pod_required": True,
                "expected_version": 0,
                "tenant_id": str(uuid4()),
            },
        ).status_code
        == 422
    )
    spec = client.get("/openapi.json").json()
    assert "/v1/inventory/policies/ship-pod" in spec["paths"]
    schema = spec["components"]["schemas"]["ShipDeliveryOrderRequest"]
    assert "pod_ref" in schema["properties"]
    assert schema["additionalProperties"] is False
    posting = spec["components"]["schemas"]["DeliveryShipPostingView"]
    assert "pod_ref" in posting["properties"]
    assert "pod_captured_at" in posting["properties"]
