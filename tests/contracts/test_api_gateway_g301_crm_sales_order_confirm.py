"""PHX-G301 CRM Sales Order Confirmation HTTP contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import (
    CONVERSION_RESOURCE,
    CUSTOMER_RESOURCE,
    OPPORTUNITY_RESOURCE,
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
        correlation_id="corr-g301",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g301-http",
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
            },
            scope_level=ScopeLevel.TENANT,
        ).ok
    return TestClient(
        create_app(
            crm_service=CRMService(
                permission,
                repository=InMemoryCRMRepository(tenant_id=TENANT),
                audit_log=audit,
            )
        )
    )


def _sales_order(client: TestClient) -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": f"C8-{uuid4().hex[:8]}", "display_name": "C8 API Customer"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "C8 API Opportunity"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={"opportunity_id": opportunity["id"], "title": "C8 API Requirement"},
    ).json()["data"]
    quote = client.post(
        "/v1/crm/quotes",
        headers=_headers(),
        json={"requirement_id": requirement["id"]},
    ).json()["data"]
    line_response = client.post(
        f"/v1/crm/quotes/{quote['id']}/lines",
        headers=_headers(),
        json={
            "description": "C8 API line",
            "quantity": "2",
            "unit_price": "15.25",
        },
    )
    assert line_response.status_code == 201
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
    return client.post(
        f"/v1/crm/conversions/{conversion['id']}/sales-order",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]


def test_g301_confirm_round_trip_and_line_snapshot() -> None:
    client = _client()
    sales_order = _sales_order(client)
    response = client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/confirm",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert response.status_code == 200
    confirmed = response.json()["data"]
    assert confirmed["status"] == "confirmed"
    assert confirmed["total_amount"] == "30.50"
    lines = client.get(
        f"/v1/crm/sales-orders/{sales_order['id']}/lines",
        headers=_headers(),
    )
    assert lines.status_code == 200
    assert lines.json()["data"][0]["amount"] == "30.50"


def test_g301_requires_literal_human_confirmation() -> None:
    client = _client()
    sales_order = _sales_order(client)
    response = client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/confirm",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": False},
    )
    assert response.status_code == 422


def test_g301_openapi_excludes_finance_inventory_fulfillment() -> None:
    spec = _client().get("/openapi.json").json()
    assert any(path.endswith("/confirm") for path in spec["paths"])
    paths = " ".join(
        path
        for path in spec["paths"]
        if path.startswith("/v1/crm/sales-orders")
        and (path.endswith("/confirm") or path.endswith("/lines"))
    ).casefold()
    for forbidden in (
        "finance",
        "receivable",
        "payment",
        "psp",
        "inventory",
        "shipment",
        "delivery",
        "fulfillment",
    ):
        assert forbidden not in paths
    assert (
        spec["components"]["schemas"]["ConfirmSalesOrderRequest"][
            "additionalProperties"
        ]
        is False
    )
