"""PHX-G329 Purchase AP Bill Line HTTP contracts."""

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
    AP_BILL_LINE_RESOURCE,
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
        correlation_id="corr-g329",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g329-http",
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
    assert permission.grant(
        _ctx(),
        principal_subject_id=SUBJECT,
        resource_type=AP_BILL_LINE_RESOURCE,
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


def _create_bill(client: TestClient) -> str:
    supplier = client.post(
        "/v1/purchase/suppliers",
        headers=_headers(),
        json={"code": f"SUP-{uuid4().hex[:8]}", "display_name": "Line HTTP"},
    )
    assert supplier.status_code == 201
    bill = client.post(
        "/v1/purchase/ap-bills",
        headers=_headers(),
        json={
            "supplier_id": supplier.json()["data"]["id"],
            "code": f"APB-{uuid4().hex[:8]}",
            "currency": "USD",
            "total_amount": "0.00",
            "idempotency_key": str(uuid4()),
        },
    )
    assert bill.status_code == 201
    return bill.json()["data"]["id"]


def test_g329_http_ap_bill_line_lifecycle() -> None:
    client = _client()
    bill_id = _create_bill(client)

    created = client.post(
        f"/v1/purchase/ap-bills/{bill_id}/lines",
        headers=_headers(),
        json={
            "description": "Widget",
            "quantity": "2",
            "unit_price": "5.00",
        },
    )
    assert created.status_code == 201
    line = created.json()["data"]
    assert line["amount"] == "10.00"
    assert line["status"] == "active"
    line_id = line["id"]

    listed = client.get(
        f"/v1/purchase/ap-bills/{bill_id}/lines", headers=_headers()
    )
    assert listed.status_code == 200
    assert len(listed.json()["data"]) == 1

    got = client.get(
        f"/v1/purchase/ap-bills/{bill_id}/lines/{line_id}",
        headers=_headers(),
    )
    assert got.status_code == 200
    assert got.json()["data"]["description"] == "Widget"

    bill = client.get(f"/v1/purchase/ap-bills/{bill_id}", headers=_headers())
    assert bill.status_code == 200
    assert bill.json()["data"]["total_amount"] == "10.00"

    archived = client.post(
        f"/v1/purchase/ap-bills/{bill_id}/lines/{line_id}/archive",
        headers=_headers(),
        json={"reason": "remove", "expected_version": 1},
    )
    assert archived.status_code == 200
    assert archived.json()["data"]["status"] == "archived"

    bill = client.get(f"/v1/purchase/ap-bills/{bill_id}", headers=_headers())
    assert bill.status_code == 200
    assert bill.json()["data"]["total_amount"] == "0.00"


def test_g329_rejects_context_override_on_line_create() -> None:
    client = _client()
    bill_id = _create_bill(client)
    response = client.post(
        f"/v1/purchase/ap-bills/{bill_id}/lines",
        headers=_headers(),
        json={
            "description": "Override",
            "quantity": "1",
            "unit_price": "1.00",
            "tenant_id": str(uuid4()),
        },
    )
    assert response.status_code == 422


def test_g329_openapi_exposes_ap2_and_forbids_parked() -> None:
    spec = _client().get("/openapi.json").json()
    paths = spec["paths"]
    assert "/v1/purchase/ap-bills/{bill_id}/lines" in paths
    assert "/v1/purchase/ap-bills/{bill_id}/lines/{line_id}" in paths
    assert (
        "/v1/purchase/ap-bills/{bill_id}/lines/{line_id}/archive" in paths
    )

    purchase_paths = " ".join(
        path for path in paths if path.startswith("/v1/purchase/")
    ).casefold()
    for forbidden in (
        "issue",
        "payment",
        "psp",
        "brain",
        "twin",
    ):
        assert forbidden not in purchase_paths

    schema = spec["components"]["schemas"]["CreateApBillLineRequest"]
    assert schema["additionalProperties"] is False
    assert "ApBillLineView" in spec["components"]["schemas"]
