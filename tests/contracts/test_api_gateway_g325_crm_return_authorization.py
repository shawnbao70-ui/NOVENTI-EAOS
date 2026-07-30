"""PHX-G325 CRM Return Authorization RET1 HTTP contracts."""

from __future__ import annotations

from dataclasses import replace
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.models import DeliveryOrderStatus
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import (
    AR_INVOICE_RESOURCE,
    CONVERSION_RESOURCE,
    CUSTOMER_RESOURCE,
    DELIVERY_ORDER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    QUOTE_LINE_RESOURCE,
    QUOTE_RESOURCE,
    REQUIREMENT_RESOURCE,
    RETURN_AUTHORIZATION_RESOURCE,
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
        correlation_id="corr-g325",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g325-http",
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
        AR_INVOICE_RESOURCE,
        RETURN_AUTHORIZATION_RESOURCE,
        STOCK_RESOURCE,
        DELIVERY_SHIP_RESOURCE,
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
                "void",
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
        crm_repo.save_delivery_order(
            replace(
                delivery_order,
                status=DeliveryOrderStatus.SHIPPED,
                version=delivery_order.version + 1,
            ),
            expected_version=expected_version,
        )

    return TestClient(
        create_app(
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


def _shipped_delivery_order(client: TestClient) -> str:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": f"RET1-{uuid4().hex[:8]}", "display_name": "RET1 API"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "RET1 Opp"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={"opportunity_id": opportunity["id"], "title": "RET1 Req"},
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
            json={
                "description": "RET1 line",
                "quantity": "1.000",
                "unit_price": "10.00",
            },
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
    sales_order = client.post(
        f"/v1/crm/conversions/{conversion['id']}/sales-order",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    assert (
        client.post(
            f"/v1/crm/sales-orders/{sales_order['id']}/confirm",
            headers=_headers(),
            json={"idempotency_key": str(uuid4()), "human_confirm": True},
        ).status_code
        == 200
    )
    delivery_order = client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/delivery-order",
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
    lines = client.get(
        f"/v1/crm/sales-orders/{sales_order['id']}/lines",
        headers=_headers(),
    ).json()["data"]
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
    shipped = client.post(
        f"/v1/inventory/delivery-orders/{delivery_order['id']}/ship",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert shipped.status_code == 200
    return delivery_order["id"]


def test_g325_http_return_authorization_create_get() -> None:
    client = _client()
    delivery_order_id = _shipped_delivery_order(client)
    key = str(uuid4())
    created = client.post(
        f"/v1/crm/delivery-orders/{delivery_order_id}/return-authorizations",
        headers=_headers(),
        json={
            "reason": "damaged in transit",
            "idempotency_key": key,
            "human_confirm": True,
        },
    )
    assert created.status_code == 201
    body = created.json()["data"]
    assert body["status"] == "draft"
    assert body["delivery_order_id"] == delivery_order_id
    assert body["reason"] == "damaged in transit"
    assert body["invoice_id"] is None
    authorization_id = body["id"]

    replay = client.post(
        f"/v1/crm/delivery-orders/{delivery_order_id}/return-authorizations",
        headers=_headers(),
        json={
            "reason": "damaged in transit",
            "idempotency_key": key,
            "human_confirm": True,
        },
    )
    assert replay.status_code == 201
    assert replay.json()["data"]["id"] == authorization_id

    got = client.get(
        f"/v1/crm/return-authorizations/{authorization_id}",
        headers=_headers(),
    )
    assert got.status_code == 200
    assert got.json()["data"]["code"] == body["code"]


def test_g325_rejects_context_override_on_create() -> None:
    client = _client()
    delivery_order_id = _shipped_delivery_order(client)
    response = client.post(
        f"/v1/crm/delivery-orders/{delivery_order_id}/return-authorizations",
        headers=_headers(),
        json={
            "reason": "override",
            "idempotency_key": str(uuid4()),
            "human_confirm": True,
            "tenant_id": str(uuid4()),
        },
    )
    assert response.status_code == 422


def test_g325_openapi_exposes_ret1_and_forbids_parked() -> None:
    spec = _client().get("/openapi.json").json()
    paths = spec["paths"]
    assert (
        "/v1/crm/delivery-orders/{delivery_order_id}/return-authorizations"
        in paths
    )
    assert "/v1/crm/return-authorizations/{return_authorization_id}" in paths

    crm_paths = " ".join(
        path for path in paths if path.startswith("/v1/crm/")
    ).casefold()
    for forbidden in (
        "putaway",
        "auto-credit",
        "psp-refund",
        "brain",
        "twin",
    ):
        assert forbidden not in crm_paths

    schema = spec["components"]["schemas"]["CreateReturnAuthorizationRequest"]
    assert schema["additionalProperties"] is False
    assert "ReturnAuthorizationView" in spec["components"]["schemas"]
