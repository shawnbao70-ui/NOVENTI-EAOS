"""PHX-G341 AP multi partial-payment HTTP contracts."""

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

SUBJECT, TENANT = uuid4(), uuid4()


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g341",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g341-http",
    }


def _client() -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    for resource, actions in (
        (SUPPLIER_RESOURCE, {"create"}),
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
    return TestClient(
        create_app(
            purchase_service=PurchaseService(
                permission,
                repository=InMemoryPurchaseRepository(tenant_id=TENANT),
                audit_log=audit,
            )
        )
    )


def _create_payment(client: TestClient, supplier_id: str, amount: str) -> str:
    response = client.post(
        "/v1/purchase/ap-payments",
        headers=_headers(),
        json={
            "supplier_id": supplier_id,
            "amount": amount,
            "currency": "USD",
            "idempotency_key": str(uuid4()),
        },
    )
    assert response.status_code == 201
    return response.json()["data"]["id"]


def _apply(client: TestClient, payment_id: str, bill_id: str) -> None:
    response = client.post(
        f"/v1/purchase/ap-payments/{payment_id}/apply",
        headers=_headers(),
        json={"ap_bill_id": bill_id, "apply_key": str(uuid4())},
    )
    assert response.status_code == 200


def test_g341_two_partial_payments_settle_bill_and_expose_balance() -> None:
    client = _client()
    supplier = client.post(
        "/v1/purchase/suppliers",
        headers=_headers(),
        json={"code": f"SUP-{uuid4().hex[:8]}", "display_name": "AP supplier"},
    ).json()["data"]
    bill = client.post(
        "/v1/purchase/ap-bills",
        headers=_headers(),
        json={
            "supplier_id": supplier["id"],
            "code": f"APB-{uuid4().hex[:8]}",
            "currency": "USD",
            "total_amount": "10.00",
            "idempotency_key": str(uuid4()),
        },
    ).json()["data"]
    assert client.post(
        f"/v1/purchase/ap-bills/{bill['id']}/post",
        headers=_headers(),
        json={"human_confirm": True},
    ).status_code == 200

    _apply(client, _create_payment(client, supplier["id"], "4.00"), bill["id"])
    partial = client.get(
        f"/v1/purchase/ap-bills/{bill['id']}", headers=_headers()
    ).json()["data"]
    assert partial["status"] == "partially_paid"
    assert partial["paid_amount"] == "4.00"
    assert partial["remaining_amount"] == "6.00"

    _apply(client, _create_payment(client, supplier["id"], "6.00"), bill["id"])
    settled = client.get(
        f"/v1/purchase/ap-bills/{bill['id']}", headers=_headers()
    ).json()["data"]
    assert settled["status"] == "paid"
    assert settled["paid_amount"] == "10.00"
    assert settled["remaining_amount"] == "0.00"

    over_apply = client.post(
        f"/v1/purchase/ap-payments/{_create_payment(client, supplier['id'], '1.00')}/apply",
        headers=_headers(),
        json={"ap_bill_id": bill["id"], "apply_key": str(uuid4())},
    )
    assert over_apply.status_code == 409
