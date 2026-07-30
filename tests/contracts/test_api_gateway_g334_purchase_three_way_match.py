"""PHX-G334 Purchase Three-Way Match HTTP contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.inventory.receipt_adapter import InventoryPurchaseReceiptAdapter
from noventi.inventory.repository import InMemoryInventoryRepository
from noventi.purchase.repository import InMemoryPurchaseRepository
from noventi.purchase.service import (
    AP_BILL_LINE_RESOURCE,
    AP_BILL_RESOURCE,
    GOODS_RECEIPT_RESOURCE,
    PURCHASE_ORDER_LINE_RESOURCE,
    PURCHASE_ORDER_RESOURCE,
    SUPPLIER_RESOURCE,
    THREE_WAY_MATCH_RESOURCE,
    PurchaseService,
)

SUBJECT, TENANT = uuid4(), uuid4()
PURCHASE_REPO = InMemoryPurchaseRepository(tenant_id=TENANT)
INVENTORY_REPO = InMemoryInventoryRepository(tenant_id=TENANT)


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g334",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g334-http",
    }


def _client() -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    for resource, actions in (
        (SUPPLIER_RESOURCE, {"create", "read", "archive"}),
        (AP_BILL_RESOURCE, {"create", "read"}),
        (AP_BILL_LINE_RESOURCE, {"create", "read", "archive"}),
        (PURCHASE_ORDER_RESOURCE, {"create", "read", "archive"}),
        (PURCHASE_ORDER_LINE_RESOURCE, {"create", "read"}),
        (GOODS_RECEIPT_RESOURCE, {"create", "read"}),
        (THREE_WAY_MATCH_RESOURCE, {"create", "read"}),
    ):
        assert permission.grant(
            _ctx(),
            principal_subject_id=SUBJECT,
            resource_type=resource,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok
    return TestClient(
        create_app(
            purchase_service=PurchaseService(
                permission,
                repository=PURCHASE_REPO,
                audit_log=audit,
                inventory_receipt_port=InventoryPurchaseReceiptAdapter(
                    INVENTORY_REPO
                ),
            )
        )
    )


def test_g334_http_three_way_match_and_openapi() -> None:
    client = _client()
    supplier = client.post(
        "/v1/purchase/suppliers",
        headers=_headers(),
        json={"code": "SUP-G334", "display_name": "G334"},
    )
    assert supplier.status_code == 201
    supplier_id = supplier.json()["data"]["id"]

    order = client.post(
        "/v1/purchase/purchase-orders",
        headers=_headers(),
        json={
            "supplier_id": supplier_id,
            "code": "PO-G334",
            "currency": "USD",
            "idempotency_key": str(uuid4()),
        },
    )
    assert order.status_code == 201
    order_id = order.json()["data"]["id"]

    assert (
        client.post(
            f"/v1/purchase/purchase-orders/{order_id}/lines",
            headers=_headers(),
            json={
                "inventory_item_id": str(uuid4()),
                "quantity": "2.000",
                "unit_price": "5.00",
            },
        ).status_code
        == 201
    )

    receipt = client.post(
        f"/v1/purchase/purchase-orders/{order_id}/goods-receipt",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert receipt.status_code == 201
    receipt_id = receipt.json()["data"]["id"]

    bill = client.post(
        "/v1/purchase/ap-bills",
        headers=_headers(),
        json={
            "supplier_id": supplier_id,
            "code": "APB-G334",
            "currency": "USD",
            "total_amount": "10.00",
            "idempotency_key": str(uuid4()),
        },
    )
    assert bill.status_code == 201
    bill_id = bill.json()["data"]["id"]
    assert (
        client.post(
            f"/v1/purchase/ap-bills/{bill_id}/lines",
            headers=_headers(),
            json={
                "description": "line",
                "quantity": "2.000",
                "unit_price": "5.00",
            },
        ).status_code
        == 201
    )

    matched = client.post(
        "/v1/purchase/three-way-matches",
        headers=_headers(),
        json={
            "purchase_order_id": order_id,
            "goods_receipt_id": receipt_id,
            "ap_bill_id": bill_id,
            "idempotency_key": str(uuid4()),
        },
    )
    assert matched.status_code == 201
    assert matched.json()["data"]["status"] == "matched"

    spec = client.get("/openapi.json").json()
    assert "/v1/purchase/three-way-matches" in spec["paths"]
    purchase_paths = " ".join(
        path for path in spec["paths"] if path.startswith("/v1/purchase/")
    ).casefold()
    for forbidden in ("psp", "brain", "twin"):
        assert forbidden not in purchase_paths
    schema = spec["components"]["schemas"]["CreateThreeWayMatchRequest"]
    assert schema["additionalProperties"] is False
