"""PHX-G519 CRM Sales Order list-query and read-only UI contracts."""

from __future__ import annotations

from pathlib import Path
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

ROOT = Path(__file__).resolve().parents[2]
SUBJECT, TENANT = uuid4(), uuid4()


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _context() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g519-grant",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g519-http",
    }


def _client(*, grant: bool = True) -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    if grant:
        for resource, actions in (
            (CUSTOMER_RESOURCE, {"create", "read", "update", "archive"}),
            (OPPORTUNITY_RESOURCE, {"create", "read", "update", "archive"}),
            (REQUIREMENT_RESOURCE, {"create", "read", "update", "archive"}),
            (QUOTE_RESOURCE, {"create", "read", "update", "archive", "issue"}),
            (QUOTE_LINE_RESOURCE, {"create", "read", "update", "archive"}),
            (CONVERSION_RESOURCE, {"create", "read", "convert"}),
            (SALES_ORDER_RESOURCE, {"create", "read"}),
        ):
            assert permission.grant(
                _context(),
                principal_subject_id=SUBJECT,
                resource_type=resource,
                actions=actions,
                scope_level=ScopeLevel.TENANT,
            ).ok
    crm = CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=TENANT),
        audit_log=audit,
    )
    return TestClient(create_app(crm_service=crm, permission_service=permission))


def _sales_order(client: TestClient, suffix: str) -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": f"C-G519-{suffix}", "display_name": f"G519 {suffix}"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": f"G519 Opp {suffix}"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={
            "opportunity_id": opportunity["id"],
            "title": f"G519 Req {suffix}",
            "description": None,
        },
    ).json()["data"]
    quote = client.post(
        "/v1/crm/quotes",
        headers=_headers(),
        json={
            "requirement_id": requirement["id"],
            "currency": "USD",
            "notes": None,
        },
    ).json()["data"]
    assert (
        client.post(
            f"/v1/crm/quotes/{quote['id']}/lines",
            headers=_headers(),
            json={
                "description": f"Line {suffix}",
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
    )
    assert sales_order.status_code == 201
    return sales_order.json()["data"]


def test_g519_sales_order_list_is_bounded_minimal_and_paginated() -> None:
    client = _client()
    first = _sales_order(client, "A")
    second = _sales_order(client, "B")
    page = client.get(
        "/v1/crm/sales-orders", headers=_headers(), params={"limit": 1}
    ).json()["data"]
    assert page["next_cursor"]
    assert set(page["items"][0]) == {
        "id",
        "conversion_id",
        "quote_id",
        "requirement_id",
        "code",
        "currency",
        "status",
        "total_amount",
        "created_at",
        "version",
    }
    assert "functional_currency" not in page["items"][0]
    assert "fx_rate" not in page["items"][0]
    next_page = client.get(
        "/v1/crm/sales-orders",
        headers=_headers(),
        params={"limit": 1, "cursor": page["next_cursor"]},
    ).json()["data"]
    assert {page["items"][0]["id"], next_page["items"][0]["id"]} == {
        first["id"],
        second["id"],
    }


def test_g519_list_fails_closed_and_validates_pagination() -> None:
    assert (
        _client(grant=False)
        .get("/v1/crm/sales-orders", headers=_headers())
        .status_code
        == 403
    )
    client = _client()
    assert (
        client.get("/v1/crm/sales-orders?limit=101", headers=_headers()).status_code
        == 422
    )
    assert (
        client.get(
            "/v1/crm/sales-orders",
            headers=_headers(),
            params={"cursor": "invalid"},
        ).status_code
        == 400
    )


def test_g519_created_order_lines_empty_until_confirm_and_confirm_stays_closed() -> None:
    client = _client()
    order = _sales_order(client, "L")
    assert order["status"] == "created"
    lines = client.get(
        f"/v1/crm/sales-orders/{order['id']}/lines", headers=_headers()
    ).json()["data"]
    assert lines == []
    assert (
        client.post(
            f"/v1/crm/sales-orders/{order['id']}/confirm",
            headers=_headers(),
            json={"idempotency_key": str(uuid4()), "human_confirm": True},
        ).status_code
        == 403
    )


def test_g519_terminal_exposes_read_only_sales_order_surface() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    for control in (
        "btnCrmRefreshSalesOrders",
        "crmSalesOrderList",
        "crmSalesOrderDetail",
        "crmSalesOrderLineList",
        "crmSalesOrderLineDetail",
    ):
        assert f'id="{control}"' in html
    # Confirm controls may exist for later slices; G519 read path must stay closed.
    chunk = app[
        app.index("function renderCrmSalesOrders") :
        app.index("function closeCrmEditors")
    ]
    assert "crmSalesOrderConfirm" not in chunk
    assert "delivery-order" not in chunk
    assert "ar-invoice" not in chunk
    assert "tenant_id" not in chunk


def test_g519_closeout_preserves_successor_boundaries() -> None:
    roadmap = (ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    acceptance = (
        ROOT / "docs" / "project" / "CRM_SALES_ORDER_UI_G519_ACCEPTANCE.md"
    ).read_text(encoding="utf-8")
    hold = (
        ROOT / "docs" / "project" / "CRM_SALES_ORDER_UI_G519_HOLD.md"
    ).read_text(encoding="utf-8")
    authorization = (
        ROOT
        / "docs"
        / "project"
        / "CRM_SALES_ORDER_G519_CODING_AUTHORIZATION_SUMMARY.md"
    ).read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    assert "FINAL STOP TRACK-G519" in roadmap
    assert "G520–G525 remain closed" in roadmap
    assert "PHX-G519 COMPLETE" in acceptance
    assert "45 passed" in acceptance
    assert "Further Coding / Runtime / Production: **None**" in acceptance
    assert "Queue: **RESOLVED**" in hold
    assert "Database/Alembic/Runtime/Production: **None**" in authorization
    assert "id: PHX-G519" in manifest
