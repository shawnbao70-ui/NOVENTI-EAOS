"""PHX-G520 CRM Sales Order Confirm UI contracts."""

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
        correlation_id="corr-g520-grant",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g520-http",
    }


def _client(*, grant: bool = True, confirm: bool = True) -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    if grant:
        so_actions = {"create", "read"}
        if confirm:
            so_actions.add("confirm")
        for resource, actions in (
            (CUSTOMER_RESOURCE, {"create", "read", "update", "archive"}),
            (OPPORTUNITY_RESOURCE, {"create", "read", "update", "archive"}),
            (REQUIREMENT_RESOURCE, {"create", "read", "update", "archive"}),
            (QUOTE_RESOURCE, {"create", "read", "update", "archive", "issue"}),
            (QUOTE_LINE_RESOURCE, {"create", "read", "update", "archive"}),
            (CONVERSION_RESOURCE, {"create", "read", "convert"}),
            (SALES_ORDER_RESOURCE, so_actions),
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
        json={"code": f"C-G520-{suffix}", "display_name": f"G520 {suffix}"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": f"G520 Opp {suffix}"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={
            "opportunity_id": opportunity["id"],
            "title": f"G520 Req {suffix}",
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
                "quantity": "2.000",
                "unit_price": "12.50",
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


def test_g520_confirm_is_idempotent_and_materializes_lines() -> None:
    client = _client()
    order = _sales_order(client, "A")
    assert order["status"] == "created"
    assert (
        client.get(
            f"/v1/crm/sales-orders/{order['id']}/lines", headers=_headers()
        ).json()["data"]
        == []
    )
    key = str(uuid4())
    first = client.post(
        f"/v1/crm/sales-orders/{order['id']}/confirm",
        headers=_headers(),
        json={"idempotency_key": key, "human_confirm": True},
    )
    assert first.status_code == 200
    confirmed = first.json()["data"]
    assert confirmed["status"] == "confirmed"
    assert confirmed["id"] == order["id"]
    lines = client.get(
        f"/v1/crm/sales-orders/{order['id']}/lines", headers=_headers()
    ).json()["data"]
    assert len(lines) == 1
    assert lines[0]["amount"] == "25.00"
    retry = client.post(
        f"/v1/crm/sales-orders/{order['id']}/confirm",
        headers=_headers(),
        json={"idempotency_key": key, "human_confirm": True},
    )
    assert retry.status_code == 200
    assert retry.json()["data"]["id"] == order["id"]
    assert retry.json()["data"]["status"] == "confirmed"


def test_g520_confirm_requires_human_confirm_and_fails_closed() -> None:
    no_confirm = _client(confirm=False)
    order = _sales_order(no_confirm, "B")
    assert (
        no_confirm.post(
            f"/v1/crm/sales-orders/{order['id']}/confirm",
            headers=_headers(),
            json={"idempotency_key": str(uuid4()), "human_confirm": True},
        ).status_code
        == 403
    )
    denied = _client(grant=False)
    assert (
        denied.post(
            f"/v1/crm/sales-orders/{uuid4()}/confirm",
            headers=_headers(),
            json={"idempotency_key": str(uuid4()), "human_confirm": True},
        ).status_code
        == 403
    )
    granted = _client()
    order2 = _sales_order(granted, "C")
    assert (
        granted.post(
            f"/v1/crm/sales-orders/{order2['id']}/confirm",
            headers=_headers(),
            json={"idempotency_key": str(uuid4()), "human_confirm": False},
        ).status_code
        == 422
    )


def test_g520_terminal_exposes_confirm_without_delivery_or_invoice() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    for control in (
        "btnCrmConfirmSalesOrder",
        "crmConfirmSoForm",
        "crmConfirmSoConfirmed",
        "crmConfirmSoApprovalRef",
        "btnCrmSubmitConfirmSo",
        "crmSalesOrderWriteControls",
    ):
        assert f'id="{control}"' in html
    chunk = app[
        app.index("async function submitCrmConfirmSalesOrder") :
        app.index("async function submitCrmCreateDeliveryOrder")
    ]
    assert "human_confirm: true" in chunk
    assert "crmSalesOrderConfirm" in chunk
    assert "crmSalesOrderDeliveryOrder" not in chunk
    assert "ar-invoice" not in chunk
    assert "tenant_id" not in chunk
    assert "openCrmConfirmSalesOrderEditor" in app
    assert "submitCrmConfirmSalesOrder" in app


def test_g520_closeout_preserves_successor_boundaries() -> None:
    roadmap = (ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    acceptance = (
        ROOT / "docs" / "project" / "CRM_SALES_ORDER_CONFIRM_UI_G520_ACCEPTANCE.md"
    ).read_text(encoding="utf-8")
    authorization = (
        ROOT
        / "docs"
        / "project"
        / "CRM_SALES_ORDER_CONFIRM_G520_CODING_AUTHORIZATION_SUMMARY.md"
    ).read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    assert "FINAL STOP TRACK-G520" in roadmap
    assert "G521–G527 remain closed" in roadmap
    assert "PHX-G520 COMPLETE" in acceptance
    assert "49 passed" in acceptance
    assert "Further Coding / Runtime / Production: **None**" in acceptance
    assert "Backend/Database/Alembic/Runtime/Production: **None**" in authorization
    assert "id: PHX-G520" in manifest
