"""PHX-G304 CRM Commercial Hold gate HTTP contracts."""

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
    DELIVERY_ORDER_RESOURCE,
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
        correlation_id="corr-g304",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g304-http",
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


def _created_sales_order(client: TestClient) -> tuple[dict, dict]:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": f"C11-{uuid4().hex[:8]}", "display_name": "C11 API Customer"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "C11 API Opportunity"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={"opportunity_id": opportunity["id"], "title": "C11 API Requirement"},
    ).json()["data"]
    quote = client.post(
        "/v1/crm/quotes",
        headers=_headers(),
        json={"requirement_id": requirement["id"]},
    ).json()["data"]
    assert client.post(
        f"/v1/crm/quotes/{quote['id']}/lines",
        headers=_headers(),
        json={"description": "C11 line", "quantity": "2", "unit_price": "10"},
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
    return customer, sales_order


def test_g304_commercial_hold_round_trip() -> None:
    client = _client()
    customer, _ = _created_sales_order(client)
    assert customer["commercial_hold"] is False
    response = client.post(
        f"/v1/crm/customers/{customer['id']}/commercial-hold",
        headers=_headers(),
        json={"commercial_hold": True, "expected_version": customer["version"]},
    )
    assert response.status_code == 200
    held = response.json()["data"]
    assert held["commercial_hold"] is True
    assert held["version"] == customer["version"] + 1


def test_g304_rejects_context_override() -> None:
    client = _client()
    customer, _ = _created_sales_order(client)
    response = client.post(
        f"/v1/crm/customers/{customer['id']}/commercial-hold",
        headers=_headers(),
        json={
            "commercial_hold": True,
            "expected_version": customer["version"],
            "tenant_id": str(uuid4()),
        },
    )
    assert response.status_code == 422


def test_g304_hold_blocks_confirm_and_delivery_order_http() -> None:
    client = _client()
    customer, sales_order = _created_sales_order(client)
    held = client.post(
        f"/v1/crm/customers/{customer['id']}/commercial-hold",
        headers=_headers(),
        json={"commercial_hold": True, "expected_version": customer["version"]},
    ).json()["data"]
    blocked_confirm = client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/confirm",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert blocked_confirm.status_code == 409
    assert "commercial hold" in blocked_confirm.json()["detail"]["message"].casefold()
    cleared = client.post(
        f"/v1/crm/customers/{held['id']}/commercial-hold",
        headers=_headers(),
        json={"commercial_hold": False, "expected_version": held["version"]},
    ).json()["data"]
    confirmed = client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/confirm",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert confirmed.status_code == 200
    held_again = client.post(
        f"/v1/crm/customers/{cleared['id']}/commercial-hold",
        headers=_headers(),
        json={
            "commercial_hold": True,
            "expected_version": cleared["version"],
        },
    )
    assert held_again.status_code == 200
    blocked_do = client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/delivery-order",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    )
    assert blocked_do.status_code == 409
    assert "commercial hold" in blocked_do.json()["detail"]["message"].casefold()


def test_g304_openapi_excludes_credit_override_finance_surfaces() -> None:
    spec = _client().get("/openapi.json").json()
    hold_path = "/v1/crm/customers/{customer_id}/commercial-hold"
    assert hold_path in spec["paths"]
    paths = " ".join(
        path
        for path in spec["paths"]
        if "commercial-hold" in path or path.startswith("/v1/crm/customers")
    ).casefold()
    for forbidden in (
        "credit-limit",
        "aging",
        "override",
        "psp",
        "ledger",
        "workflow",
        "approval",
    ):
        assert forbidden not in paths
    assert (
        spec["components"]["schemas"]["SetCommercialHoldRequest"][
            "additionalProperties"
        ]
        is False
    )
