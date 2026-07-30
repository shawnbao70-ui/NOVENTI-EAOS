"""PHX-G333 Purchase Goods Receipt HTTP contracts."""

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
    GOODS_RECEIPT_RESOURCE,
    PURCHASE_ORDER_LINE_RESOURCE,
    PURCHASE_ORDER_RESOURCE,
    SUPPLIER_RESOURCE,
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
        correlation_id="corr-g333",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g333-http",
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
        (PURCHASE_ORDER_RESOURCE, {"create", "read", "archive"}),
        (PURCHASE_ORDER_LINE_RESOURCE, {"create", "read"}),
        (GOODS_RECEIPT_RESOURCE, {"create", "read"}),
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


def test_g333_http_goods_receipt_and_openapi() -> None:
    client = _client()
    supplier = client.post(
        "/v1/purchase/suppliers",
        headers=_headers(),
        json={"code": "SUP-G333", "display_name": "G333"},
    )
    assert supplier.status_code == 201
    supplier_id = supplier.json()["data"]["id"]

    order = client.post(
        "/v1/purchase/purchase-orders",
        headers=_headers(),
        json={
            "supplier_id": supplier_id,
            "code": "PO-G333",
            "currency": "USD",
            "idempotency_key": str(uuid4()),
        },
    )
    assert order.status_code == 201
    order_id = order.json()["data"]["id"]

    item_id = str(uuid4())
    line = client.post(
        f"/v1/purchase/purchase-orders/{order_id}/lines",
        headers=_headers(),
        json={
            "inventory_item_id": item_id,
            "quantity": "5.000",
            "unit_price": "1.25",
        },
    )
    assert line.status_code == 201
    assert line.json()["data"]["inventory_item_id"] == item_id

    rejected = client.post(
        f"/v1/purchase/purchase-orders/{order_id}/goods-receipt",
        headers=_headers(),
        json={
            "idempotency_key": str(uuid4()),
            "human_confirm": True,
            "quantity": "1",
        },
    )
    assert rejected.status_code == 422

    key = str(uuid4())
    receipt = client.post(
        f"/v1/purchase/purchase-orders/{order_id}/goods-receipt",
        headers=_headers(),
        json={"idempotency_key": key, "human_confirm": True},
    )
    assert receipt.status_code == 201
    assert receipt.json()["data"]["status"] == "received"
    assert INVENTORY_REPO.get_item_stock_balance(
        UUID(item_id)
    ).on_hand == __import__("decimal").Decimal("5.000")

    spec = client.get("/openapi.json").json()
    paths = spec["paths"]
    assert "/v1/purchase/purchase-orders/{purchase_order_id}/lines" in paths
    assert (
        "/v1/purchase/purchase-orders/{purchase_order_id}/goods-receipt"
        in paths
    )
    purchase_paths = " ".join(
        path for path in paths if path.startswith("/v1/purchase/")
    ).casefold()
    for forbidden in ("payment", "psp", "brain", "twin"):
        assert forbidden not in purchase_paths
    schema = spec["components"]["schemas"]["CreateGoodsReceiptRequest"]
    assert schema["additionalProperties"] is False
    assert "quantity" not in schema.get("properties", {})
    assert "stock_delta" not in schema.get("properties", {})
