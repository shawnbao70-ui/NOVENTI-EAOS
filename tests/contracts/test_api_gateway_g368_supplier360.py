"""PHX-G368 Supplier360 HTTP contracts."""

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
    AP_PAYMENT_RESOURCE,
    SUPPLIER_RESOURCE,
    PurchaseService,
)
from noventi.purchase.supplier360 import (
    SUPPLIER360_RESOURCE,
    AssembledSupplier360Repository,
    Supplier360Service,
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
        correlation_id="corr-g368",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g368-http",
    }


def _client(*, grant_360: bool = True) -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    for resource, actions in (
        (SUPPLIER_RESOURCE, {"create", "read"}),
        (AP_BILL_RESOURCE, {"create", "read", "post"}),
        (AP_PAYMENT_RESOURCE, {"create", "apply"}),
    ):
        assert permission.grant(
            _ctx(),
            principal_subject_id=SUBJECT,
            resource_type=resource,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok
    if grant_360:
        assert permission.grant(
            _ctx(),
            principal_subject_id=SUBJECT,
            resource_type=SUPPLIER360_RESOURCE,
            actions={"read"},
            scope_level=ScopeLevel.TENANT,
        ).ok
    purchase_repo = InMemoryPurchaseRepository(tenant_id=TENANT)
    return TestClient(
        create_app(
            purchase_service=PurchaseService(
                permission,
                repository=purchase_repo,
                audit_log=audit,
            ),
            supplier360_service=Supplier360Service(
                permission,
                repository=AssembledSupplier360Repository(purchase_repo),
                audit_log=audit,
            ),
        )
    )


def _seed_supplier_with_posted_bill_and_payment(client: TestClient) -> dict:
    supplier = client.post(
        "/v1/purchase/suppliers",
        headers=_headers(),
        json={
            "code": f"S360-{uuid4().hex[:8]}",
            "display_name": "Supplier360 API",
        },
    ).json()["data"]
    bill = client.post(
        "/v1/purchase/ap-bills",
        headers=_headers(),
        json={
            "supplier_id": supplier["id"],
            "code": f"BILL-{uuid4().hex[:8]}",
            "currency": "USD",
            "total_amount": "25.00",
            "idempotency_key": str(uuid4()),
        },
    ).json()["data"]
    assert (
        client.post(
            f"/v1/purchase/ap-bills/{bill['id']}/post",
            headers=_headers(),
            json={"human_confirm": True},
        ).status_code
        == 200
    )
    payment = client.post(
        "/v1/purchase/ap-payments",
        headers=_headers(),
        json={
            "supplier_id": supplier["id"],
            "amount": "5.00",
            "currency": "USD",
            "idempotency_key": str(uuid4()),
        },
    ).json()["data"]
    assert (
        client.post(
            f"/v1/purchase/ap-payments/{payment['id']}/apply",
            headers=_headers(),
            json={"ap_bill_id": bill["id"], "apply_key": str(uuid4())},
        ).status_code
        == 200
    )
    return {
        "supplier": supplier,
        "bill": bill,
        "payment": payment,
    }


def test_g368_supplier360_read_round_trip() -> None:
    client = _client()
    seeded = _seed_supplier_with_posted_bill_and_payment(client)
    supplier = seeded["supplier"]
    bill = seeded["bill"]
    payment = seeded["payment"]

    response = client.get(
        f"/v1/purchase/suppliers/{supplier['id']}/360", headers=_headers()
    )
    assert response.status_code == 200
    body = response.json()
    assert body["audit_id"]
    data = body["data"]
    assert data["supplier_id"] == supplier["id"]
    assert data["supplier_code"] == supplier["code"]
    assert data["display_name"] == supplier["display_name"]
    assert data["status"] == "active"
    assert data["balances"] == {"USD": "20.00"}
    assert len(data["bill_traces"]) == 1
    assert data["bill_traces"][0]["id"] == bill["id"]
    assert data["bill_traces"][0]["status"] == "partially_paid"
    assert data["bill_traces"][0]["total_amount"] == "25.00"
    assert len(data["payment_traces"]) == 1
    assert data["payment_traces"][0]["id"] == payment["id"]
    assert data["payment_traces"][0]["status"] == "applied"
    assert data["payment_traces"][0]["amount"] == "5.00"
    assert data["payment_traces"][0]["ap_bill_id"] == bill["id"]


def test_g368_default_deny_without_grant() -> None:
    client = _client(grant_360=False)
    supplier = client.post(
        "/v1/purchase/suppliers",
        headers=_headers(),
        json={"code": f"S360D-{uuid4().hex[:8]}", "display_name": "Deny"},
    ).json()["data"]
    response = client.get(
        f"/v1/purchase/suppliers/{supplier['id']}/360", headers=_headers()
    )
    assert response.status_code == 403


def test_g368_no_write_methods_on_360() -> None:
    client = _client()
    seeded = _seed_supplier_with_posted_bill_and_payment(client)
    path = f"/v1/purchase/suppliers/{seeded['supplier']['id']}/360"
    assert client.post(path, headers=_headers(), json={}).status_code == 405
    assert client.put(path, headers=_headers(), json={}).status_code == 405
    assert client.patch(path, headers=_headers(), json={}).status_code == 405
    assert client.delete(path, headers=_headers()).status_code == 405


def test_g368_openapi_forbids_brain_twin_writes() -> None:
    spec = _client().get("/openapi.json").json()
    path_key = "/v1/purchase/suppliers/{supplier_id}/360"
    assert path_key in spec["paths"]
    assert list(spec["paths"][path_key].keys()) == ["get"]
    paths = " ".join(
        path
        for path in spec["paths"]
        if path.startswith("/v1/purchase/suppliers") and path.endswith("/360")
    ).casefold()
    for forbidden in ("brain", "execute", "twin", "authorize"):
        assert forbidden not in paths
    schemas = spec["components"]["schemas"]
    assert schemas["Supplier360View"]["additionalProperties"] is False
    assert schemas["Supplier360Envelope"]["additionalProperties"] is False
