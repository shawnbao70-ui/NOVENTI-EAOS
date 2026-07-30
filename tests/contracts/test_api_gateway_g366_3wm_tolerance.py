"""PHX-G366 Purchase three-way match tolerance HTTP contracts."""

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
    THREE_WAY_MATCH_TOLERANCE_POLICY_RESOURCE,
    PurchaseService,
)

class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _client() -> tuple[TestClient, UUID, UUID]:
    subject, tenant = uuid4(), uuid4()
    purchase_repo = InMemoryPurchaseRepository(tenant_id=tenant)
    inventory_repo = InMemoryInventoryRepository(tenant_id=tenant)

    def ctx() -> ExecutionContext:
        return ExecutionContext(
            subject_id=subject,
            subject_type=SubjectType.HUMAN,
            tenant_id=tenant,
            correlation_id="corr-g366",
            request_time=ExecutionContext.utc_now(),
        )

    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={subject},
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
        (THREE_WAY_MATCH_TOLERANCE_POLICY_RESOURCE, {"read", "update"}),
    ):
        assert permission.grant(
            ctx(),
            principal_subject_id=subject,
            resource_type=resource,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok
    client = TestClient(
        create_app(
            purchase_service=PurchaseService(
                permission,
                repository=purchase_repo,
                audit_log=audit,
                inventory_receipt_port=InventoryPurchaseReceiptAdapter(
                    inventory_repo
                ),
            )
        )
    )
    return client, subject, tenant


def _headers(subject: UUID, tenant: UUID) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(tenant),
        "X-Correlation-Id": "corr-g366-http",
    }


def _seed_po_receipt_bill(
    client: TestClient,
    subject: UUID,
    tenant: UUID,
    *,
    suffix: str,
    po_qty: str,
    po_unit_price: str,
    bill_total: str,
    bill_qty: str,
    bill_unit_price: str,
) -> tuple[str, str, str]:
    headers = _headers(subject, tenant)
    supplier = client.post(
        "/v1/purchase/suppliers",
        headers=headers,
        json={"code": f"SUP-{suffix}", "display_name": f"G366 {suffix}"},
    )
    assert supplier.status_code == 201
    supplier_id = supplier.json()["data"]["id"]

    order = client.post(
        "/v1/purchase/purchase-orders",
        headers=headers,
        json={
            "supplier_id": supplier_id,
            "code": f"PO-{suffix}",
            "currency": "USD",
            "idempotency_key": str(uuid4()),
        },
    )
    assert order.status_code == 201
    order_id = order.json()["data"]["id"]
    assert (
        client.post(
            f"/v1/purchase/purchase-orders/{order_id}/lines",
            headers=headers,
            json={
                "inventory_item_id": str(uuid4()),
                "quantity": po_qty,
                "unit_price": po_unit_price,
            },
        ).status_code
        == 201
    )

    receipt = client.post(
        f"/v1/purchase/purchase-orders/{order_id}/goods-receipt",
        headers=headers,
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert receipt.status_code == 201
    receipt_id = receipt.json()["data"]["id"]

    bill = client.post(
        "/v1/purchase/ap-bills",
        headers=headers,
        json={
            "supplier_id": supplier_id,
            "code": f"APB-{suffix}",
            "currency": "USD",
            "total_amount": bill_total,
            "idempotency_key": str(uuid4()),
        },
    )
    assert bill.status_code == 201
    bill_id = bill.json()["data"]["id"]
    assert (
        client.post(
            f"/v1/purchase/ap-bills/{bill_id}/lines",
            headers=headers,
            json={
                "description": "line",
                "quantity": bill_qty,
                "unit_price": bill_unit_price,
            },
        ).status_code
        == 201
    )
    return order_id, receipt_id, bill_id


def test_g366_default_zero_tolerance_requires_exact_match() -> None:
    client, subject, tenant = _client()
    headers = _headers(subject, tenant)
    default = client.get(
        "/v1/purchase/policies/three-way-match-tolerance", headers=headers
    )
    assert default.status_code == 200
    assert default.json()["data"]["amount_tolerance_abs"] == "0.00"
    assert default.json()["data"]["amount_tolerance_pct"] in ("0", "0.0000")
    assert default.json()["data"]["version"] == 0

    order_id, receipt_id, bill_id = _seed_po_receipt_bill(
        client,
        subject,
        tenant,
        suffix="EXACT",
        po_qty="2.000",
        po_unit_price="5.00",
        bill_total="10.01",
        bill_qty="1.000",
        bill_unit_price="10.01",
    )
    mismatched = client.post(
        "/v1/purchase/three-way-matches",
        headers=headers,
        json={
            "purchase_order_id": order_id,
            "goods_receipt_id": receipt_id,
            "ap_bill_id": bill_id,
            "idempotency_key": str(uuid4()),
        },
    )
    assert mismatched.status_code == 409
    assert "mismatch" in mismatched.json()["detail"]["message"].casefold()


def test_g366_within_abs_tolerance_matches_outside_mismatches() -> None:
    client, subject, tenant = _client()
    headers = _headers(subject, tenant)
    updated = client.put(
        "/v1/purchase/policies/three-way-match-tolerance",
        headers=headers,
        json={
            "amount_tolerance_abs": "0.05",
            "amount_tolerance_pct": "0",
            "expected_version": 0,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["amount_tolerance_abs"] == "0.05"
    assert updated.json()["data"]["version"] == 1

    within_order, within_receipt, within_bill = _seed_po_receipt_bill(
        client,
        subject,
        tenant,
        suffix="WITHIN",
        po_qty="2.000",
        po_unit_price="5.00",
        bill_total="10.03",
        bill_qty="1.000",
        bill_unit_price="10.03",
    )
    matched = client.post(
        "/v1/purchase/three-way-matches",
        headers=headers,
        json={
            "purchase_order_id": within_order,
            "goods_receipt_id": within_receipt,
            "ap_bill_id": within_bill,
            "idempotency_key": str(uuid4()),
        },
    )
    assert matched.status_code == 201
    assert matched.json()["data"]["status"] == "matched"

    outside_order, outside_receipt, outside_bill = _seed_po_receipt_bill(
        client,
        subject,
        tenant,
        suffix="OUTSIDE",
        po_qty="2.000",
        po_unit_price="5.00",
        bill_total="10.06",
        bill_qty="1.000",
        bill_unit_price="10.06",
    )
    mismatched = client.post(
        "/v1/purchase/three-way-matches",
        headers=headers,
        json={
            "purchase_order_id": outside_order,
            "goods_receipt_id": outside_receipt,
            "ap_bill_id": outside_bill,
            "idempotency_key": str(uuid4()),
        },
    )
    assert mismatched.status_code == 409
    assert "mismatch" in mismatched.json()["detail"]["message"].casefold()


def test_g366_pct_tolerance_and_openapi_closed() -> None:
    client, subject, tenant = _client()
    headers = _headers(subject, tenant)
    updated = client.put(
        "/v1/purchase/policies/three-way-match-tolerance",
        headers=headers,
        json={
            "amount_tolerance_abs": "0",
            "amount_tolerance_pct": "1.0000",
            "expected_version": 0,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["amount_tolerance_pct"] == "1.0000"

    order_id, receipt_id, bill_id = _seed_po_receipt_bill(
        client,
        subject,
        tenant,
        suffix="PCT",
        po_qty="1.000",
        po_unit_price="100.00",
        bill_total="100.50",
        bill_qty="1.000",
        bill_unit_price="100.50",
    )
    matched = client.post(
        "/v1/purchase/three-way-matches",
        headers=headers,
        json={
            "purchase_order_id": order_id,
            "goods_receipt_id": receipt_id,
            "ap_bill_id": bill_id,
            "idempotency_key": str(uuid4()),
        },
    )
    assert matched.status_code == 201
    assert matched.json()["data"]["status"] == "matched"

    assert (
        client.put(
            "/v1/purchase/policies/three-way-match-tolerance",
            headers=headers,
            json={
                "amount_tolerance_abs": "0",
                "amount_tolerance_pct": "0",
                "expected_version": updated.json()["data"]["version"],
                "tenant_id": str(uuid4()),
            },
        ).status_code
        == 422
    )

    spec = client.get("/openapi.json").json()
    assert "/v1/purchase/policies/three-way-match-tolerance" in spec["paths"]
    schema = spec["components"]["schemas"][
        "SetThreeWayMatchTolerancePolicyRequest"
    ]
    assert schema["additionalProperties"] is False
