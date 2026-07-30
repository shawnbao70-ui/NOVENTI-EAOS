"""PHX-G324 Purchase Supplier + AP Bill draft HTTP contracts."""

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
    AP_BILL_RESOURCE,
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
        correlation_id="corr-g324",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g324-http",
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
        resource_type=AP_BILL_RESOURCE,
        actions={"create", "read"},
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


def test_g324_http_supplier_and_ap_bill_draft() -> None:
    client = _client()
    created = client.post(
        "/v1/purchase/suppliers",
        headers=_headers(),
        json={"code": "SUP-HTTP", "display_name": "Gateway Supplier"},
    )
    assert created.status_code == 201
    supplier = created.json()["data"]
    assert supplier["status"] == "active"
    supplier_id = supplier["id"]

    updated = client.patch(
        f"/v1/purchase/suppliers/{supplier_id}",
        headers=_headers(),
        json={"display_name": "Gateway Supplier Ltd", "expected_version": 1},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["display_name"] == "Gateway Supplier Ltd"
    assert updated.json()["data"]["version"] == 2

    key = str(uuid4())
    bill = client.post(
        "/v1/purchase/ap-bills",
        headers=_headers(),
        json={
            "supplier_id": supplier_id,
            "code": "APB-HTTP-1",
            "currency": "USD",
            "total_amount": "25.50",
            "idempotency_key": key,
        },
    )
    assert bill.status_code == 201
    body = bill.json()["data"]
    assert body["status"] == "draft"
    assert body["total_amount"] == "25.50"
    bill_id = body["id"]

    replay = client.post(
        "/v1/purchase/ap-bills",
        headers=_headers(),
        json={
            "supplier_id": supplier_id,
            "code": "APB-HTTP-1",
            "currency": "USD",
            "total_amount": "25.50",
            "idempotency_key": key,
        },
    )
    assert replay.status_code == 201
    assert replay.json()["data"]["id"] == bill_id

    got = client.get(f"/v1/purchase/ap-bills/{bill_id}", headers=_headers())
    assert got.status_code == 200
    assert got.json()["data"]["code"] == "APB-HTTP-1"

    archived = client.post(
        f"/v1/purchase/suppliers/{supplier_id}/archive",
        headers=_headers(),
        json={"reason": "retired", "expected_version": 2},
    )
    assert archived.status_code == 200
    assert archived.json()["data"]["status"] == "archived"


def test_g324_rejects_context_override_on_create() -> None:
    client = _client()
    response = client.post(
        "/v1/purchase/suppliers",
        headers=_headers(),
        json={
            "code": "SUP-OVERRIDE",
            "display_name": "Override",
            "tenant_id": str(uuid4()),
        },
    )
    assert response.status_code == 422


def test_g324_openapi_exposes_ap1_and_forbids_parked() -> None:
    spec = _client().get("/openapi.json").json()
    paths = spec["paths"]
    assert "/v1/purchase/suppliers" in paths
    assert "/v1/purchase/suppliers/{supplier_id}" in paths
    assert "/v1/purchase/suppliers/{supplier_id}/archive" in paths
    assert "/v1/purchase/ap-bills" in paths
    assert "/v1/purchase/ap-bills/{bill_id}" in paths

    purchase_paths = " ".join(
        path for path in paths if path.startswith("/v1/purchase/")
    ).casefold()
    for forbidden in (
        "bill-line",
        "payment",
        "psp",
        "brain",
        "twin",
    ):
        assert forbidden not in purchase_paths

    schema = spec["components"]["schemas"]["CreateApBillRequest"]
    assert schema["additionalProperties"] is False
    assert "SupplierView" in spec["components"]["schemas"]
    assert "ApBillView" in spec["components"]["schemas"]
