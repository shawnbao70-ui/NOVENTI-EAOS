"""PHX-G525 CRM Return Authorization create/read UI contracts."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
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

ROOT = Path(__file__).resolve().parents[2]
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


def _context() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g525-grant",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g525-http",
    }


def _client(*, grant: bool = True, return_authorization: bool = True) -> TestClient:
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
            (SALES_ORDER_RESOURCE, {"create", "read", "confirm"}),
            (DELIVERY_ORDER_RESOURCE, {"create", "read", "release"}),
            (AR_INVOICE_RESOURCE, {"create", "read", "issue"}),
            (STOCK_RESOURCE, {"read", "adjust"}),
            (DELIVERY_SHIP_RESOURCE, {"read", "ship"}),
        ):
            assert permission.grant(
                _context(),
                principal_subject_id=SUBJECT,
                resource_type=resource,
                actions=actions,
                scope_level=ScopeLevel.TENANT,
            ).ok
        if return_authorization:
            assert permission.grant(
                _context(),
                principal_subject_id=SUBJECT,
                resource_type=RETURN_AUTHORIZATION_RESOURCE,
                actions={"create", "read"},
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
            permission_service=permission,
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


def _shipped_delivery_order(client: TestClient, suffix: str = "A") -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": f"C-G525-{suffix}", "display_name": f"G525 {suffix}"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": f"G525 Opp {suffix}"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={
            "opportunity_id": opportunity["id"],
            "title": f"G525 Req {suffix}",
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
                "unit_price": "30.00",
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
    detail = client.get(
        f"/v1/crm/delivery-orders/{delivery_order['id']}",
        headers=_headers(),
    )
    assert detail.status_code == 200
    return detail.json()["data"]


def test_g525_create_get_is_idempotent_and_do_scoped() -> None:
    client = _client()
    delivery_order = _shipped_delivery_order(client)
    create_key = str(uuid4())
    body = {
        "reason": "damaged in transit",
        "idempotency_key": create_key,
        "human_confirm": True,
    }
    first = client.post(
        f"/v1/crm/delivery-orders/{delivery_order['id']}/return-authorizations",
        headers=_headers(),
        json=body,
    )
    assert first.status_code == 201
    authorization = first.json()["data"]
    assert authorization["status"] == "draft"
    assert authorization["delivery_order_id"] == delivery_order["id"]
    assert authorization["reason"] == "damaged in transit"
    retry = client.post(
        f"/v1/crm/delivery-orders/{delivery_order['id']}/return-authorizations",
        headers=_headers(),
        json=body,
    )
    assert retry.status_code == 201
    assert retry.json()["data"]["id"] == authorization["id"]
    detail = client.get(
        f"/v1/crm/return-authorizations/{authorization['id']}",
        headers=_headers(),
    )
    assert detail.status_code == 200
    assert detail.json()["data"]["code"] == authorization["code"]


def test_g525_return_authorization_fails_closed_without_permission() -> None:
    no_ra = _client(return_authorization=False)
    delivery_order = _shipped_delivery_order(no_ra, "B")
    assert (
        no_ra.post(
            f"/v1/crm/delivery-orders/{delivery_order['id']}/return-authorizations",
            headers=_headers(),
            json={
                "reason": "no permission",
                "idempotency_key": str(uuid4()),
                "human_confirm": True,
            },
        ).status_code
        == 403
    )
    denied = _client(grant=False)
    assert (
        denied.get(
            f"/v1/crm/return-authorizations/{uuid4()}",
            headers=_headers(),
        ).status_code
        == 403
    )


def test_g525_terminal_exposes_ra_without_restock_credit_or_list() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    for control in (
        "btnCrmCreateReturnAuthorization",
        "crmCreateReturnAuthorizationForm",
        "crmCreateReturnAuthorizationReason",
        "crmCreateReturnAuthorizationConfirmed",
        "crmReturnAuthorizationDetail",
        "btnCrmRefreshReturnAuthorization",
    ):
        assert f'id="{control}"' in html
    assert "GET /v1/crm/return-authorizations?" not in app
    assert "crmReturnAuthorizations:" not in app
    assert "crm-g525-return-authorization-1" in html
    chunk = app[
        app.index("function openCrmCreateReturnAuthorizationEditor") :
        app.index("async function submitCrmArchive")
    ]
    assert "crmDeliveryOrderReturnAuthorization" in chunk
    assert "human_confirm: true" in chunk
    assert "/restock" not in chunk
    assert "/credit-notes" not in chunk
    assert "/void" not in chunk
    assert "tenant_id" not in chunk


def test_g525_closeout_preserves_successor_boundaries() -> None:
    roadmap = (ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md").read_text(
        encoding="utf-8"
    )
    acceptance = (
        ROOT / "docs" / "project" / "CRM_RETURN_AUTHORIZATION_UI_G525_ACCEPTANCE.md"
    ).read_text(encoding="utf-8")
    authorization = (
        ROOT
        / "docs"
        / "project"
        / "CRM_RETURN_AUTHORIZATION_G525_CODING_AUTHORIZATION_SUMMARY.md"
    ).read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    assert "FINAL STOP TRACK-G525" in roadmap
    assert "G526–G527 remain closed" in roadmap
    assert "FINAL STOP TRACK-G524" in roadmap
    assert "G525–G527 remain closed" in roadmap
    assert "PHX-G525 COMPLETE" in acceptance
    assert "69 passed" in acceptance
    assert "Further Coding / Runtime / Production: **None**" in acceptance
    assert "Backend/Database/Alembic/Runtime/Production: **None**" in authorization
    assert "id: PHX-G525" in manifest
