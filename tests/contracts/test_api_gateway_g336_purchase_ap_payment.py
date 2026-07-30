"""PHX-G336 Purchase AP payment HTTP contracts."""

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
        correlation_id="corr-g336",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g336-http",
    }


def _client(*, grant: bool = True) -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    if grant:
        for resource, actions in (
            (SUPPLIER_RESOURCE, {"create"}),
            (AP_BILL_RESOURCE, {"create", "read", "post"}),
            (AP_PAYMENT_RESOURCE, {"create", "read", "apply"}),
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


def _supplier_and_bill(client: TestClient, amount: str = "10.00") -> tuple[str, str]:
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
            "total_amount": amount,
            "idempotency_key": str(uuid4()),
        },
    ).json()["data"]
    return supplier["id"], bill["id"]


def test_g336_denies_without_grant() -> None:
    response = _client(grant=False).post(
        "/v1/purchase/ap-payments",
        headers=_headers(),
        json={
            "supplier_id": str(uuid4()),
            "amount": "1.00",
            "currency": "USD",
            "idempotency_key": str(uuid4()),
        },
    )
    assert response.status_code == 403


def test_g336_post_create_apply_paid_and_idempotent() -> None:
    client = _client()
    supplier_id, bill_id = _supplier_and_bill(client)
    posted = client.post(
        f"/v1/purchase/ap-bills/{bill_id}/post",
        headers=_headers(),
        json={"human_confirm": True},
    )
    assert posted.status_code == 200
    assert posted.json()["data"]["status"] == "posted"
    payment = client.post(
        "/v1/purchase/ap-payments",
        headers=_headers(),
        json={
            "supplier_id": supplier_id,
            "amount": "10.00",
            "currency": "USD",
            "idempotency_key": str(uuid4()),
        },
    )
    assert payment.status_code == 201
    payment_id = payment.json()["data"]["id"]
    assert client.get(
        f"/v1/purchase/ap-bills/{bill_id}", headers=_headers()
    ).json()["data"]["status"] == "posted"
    apply_key = str(uuid4())
    applied = client.post(
        f"/v1/purchase/ap-payments/{payment_id}/apply",
        headers=_headers(),
        json={"ap_bill_id": bill_id, "apply_key": apply_key},
    )
    assert applied.status_code == 200
    assert applied.json()["data"]["status"] == "applied"
    assert client.post(
        f"/v1/purchase/ap-payments/{payment_id}/apply",
        headers=_headers(),
        json={"ap_bill_id": bill_id, "apply_key": apply_key},
    ).status_code == 200
    assert client.get(
        f"/v1/purchase/ap-bills/{bill_id}", headers=_headers()
    ).json()["data"]["status"] == "paid"


def test_g336_partial_payment_and_draft_bill_rejected() -> None:
    client = _client()
    supplier_id, draft_bill_id = _supplier_and_bill(client)
    draft_payment = client.post(
        "/v1/purchase/ap-payments",
        headers=_headers(),
        json={
            "supplier_id": supplier_id,
            "amount": "1.00",
            "currency": "USD",
            "idempotency_key": str(uuid4()),
        },
    ).json()["data"]
    assert client.post(
        f"/v1/purchase/ap-payments/{draft_payment['id']}/apply",
        headers=_headers(),
        json={"ap_bill_id": draft_bill_id, "apply_key": str(uuid4())},
    ).status_code == 409
    supplier_id, bill_id = _supplier_and_bill(client)
    assert client.post(
        f"/v1/purchase/ap-bills/{bill_id}/post",
        headers=_headers(),
        json={"human_confirm": True},
    ).status_code == 200
    payment = client.post(
        "/v1/purchase/ap-payments",
        headers=_headers(),
        json={
            "supplier_id": supplier_id,
            "amount": "4.00",
            "currency": "USD",
            "idempotency_key": str(uuid4()),
        },
    ).json()["data"]
    assert client.post(
        f"/v1/purchase/ap-payments/{payment['id']}/apply",
        headers=_headers(),
        json={"ap_bill_id": bill_id, "apply_key": str(uuid4())},
    ).status_code == 200
    assert client.get(
        f"/v1/purchase/ap-bills/{bill_id}", headers=_headers()
    ).json()["data"]["status"] == "partially_paid"
