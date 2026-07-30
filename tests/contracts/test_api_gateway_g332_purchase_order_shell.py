"""PHX-G332 Purchase Order shell HTTP contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.purchase.repository import InMemoryPurchaseRepository
from noventi.purchase.service import (
    PURCHASE_ORDER_RESOURCE,
    SUPPLIER_RESOURCE,
    PurchaseService,
)

SUBJECT, TENANT = uuid4(), uuid4()
REPO = InMemoryPurchaseRepository(tenant_id=TENANT)


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g332",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g332-http",
    }


def _client() -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    assert permission.grant(
        _ctx(),
        principal_subject_id=SUBJECT,
        resource_type=SUPPLIER_RESOURCE,
        actions={"create", "read", "update", "archive"},
        scope_level=ScopeLevel.TENANT,
    ).ok
    assert permission.grant(
        _ctx(),
        principal_subject_id=SUBJECT,
        resource_type=PURCHASE_ORDER_RESOURCE,
        actions={"create", "read", "archive"},
        scope_level=ScopeLevel.TENANT,
    ).ok
    return TestClient(
        create_app(
            purchase_service=PurchaseService(
                permission,
                repository=REPO,
                audit_log=audit,
            )
        )
    )


def test_g332_http_purchase_order_shell() -> None:
    client = _client()
    supplier = client.post(
        "/v1/purchase/suppliers",
        headers=_headers(),
        json={"code": "SUP-G332", "display_name": "G332 Supplier"},
    )
    assert supplier.status_code == 201
    supplier_id = supplier.json()["data"]["id"]

    key = str(uuid4())
    created = client.post(
        "/v1/purchase/purchase-orders",
        headers=_headers(),
        json={
            "supplier_id": supplier_id,
            "code": "PO-HTTP-1",
            "currency": "USD",
            "idempotency_key": key,
            "notes": "shell",
        },
    )
    assert created.status_code == 201
    body = created.json()["data"]
    assert body["status"] == "draft"
    assert body["notes"] == "shell"
    order_id = body["id"]

    replay = client.post(
        "/v1/purchase/purchase-orders",
        headers=_headers(),
        json={
            "supplier_id": supplier_id,
            "code": "PO-HTTP-1",
            "currency": "USD",
            "idempotency_key": key,
            "notes": "shell",
        },
    )
    assert replay.status_code == 201
    assert replay.json()["data"]["id"] == order_id

    got = client.get(
        f"/v1/purchase/purchase-orders/{order_id}", headers=_headers()
    )
    assert got.status_code == 200
    assert got.json()["data"]["code"] == "PO-HTTP-1"

    archived = client.post(
        f"/v1/purchase/purchase-orders/{order_id}/archive",
        headers=_headers(),
        json={"reason": "cancelled", "expected_version": 1},
    )
    assert archived.status_code == 200
    assert archived.json()["data"]["status"] == "archived"


def test_g332_rejects_context_override_on_create() -> None:
    client = _client()
    response = client.post(
        "/v1/purchase/purchase-orders",
        headers=_headers(),
        json={
            "supplier_id": str(uuid4()),
            "code": "PO-OVERRIDE",
            "currency": "USD",
            "idempotency_key": str(uuid4()),
            "tenant_id": str(uuid4()),
        },
    )
    assert response.status_code == 422


def test_g332_openapi_exposes_po_and_forbids_parked() -> None:
    spec = _client().get("/openapi.json").json()
    paths = spec["paths"]
    assert "/v1/purchase/purchase-orders" in paths
    assert "/v1/purchase/purchase-orders/{purchase_order_id}" in paths
    assert "/v1/purchase/purchase-orders/{purchase_order_id}/archive" in paths

    purchase_paths = " ".join(
        path for path in paths if path.startswith("/v1/purchase/")
    ).casefold()
    for forbidden in (
        "payment",
        "psp",
        "brain",
        "twin",
    ):
        assert forbidden not in purchase_paths

    schema = spec["components"]["schemas"]["CreatePurchaseOrderRequest"]
    assert schema["additionalProperties"] is False
    assert "PurchaseOrderView" in spec["components"]["schemas"]
