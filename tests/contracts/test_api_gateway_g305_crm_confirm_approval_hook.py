"""PHX-G305 CRM confirm approval hook HTTP contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.approval import AllowConfirmApprovalGate, DenyConfirmApprovalGate
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import (
    CONVERSION_RESOURCE,
    CUSTOMER_RESOURCE,
    DELIVERY_ORDER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    POLICY_RESOURCE,
    QUOTE_LINE_RESOURCE,
    QUOTE_RESOURCE,
    REQUIREMENT_RESOURCE,
    SALES_ORDER_RESOURCE,
    CRMService,
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
        correlation_id="corr-g305",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g305-http",
    }


def _client(*, gate=None) -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_Eligibility(),
    )
    for resource in (
        CUSTOMER_RESOURCE,
        OPPORTUNITY_RESOURCE,
        REQUIREMENT_RESOURCE,
        QUOTE_RESOURCE,
        QUOTE_LINE_RESOURCE,
        CONVERSION_RESOURCE,
        SALES_ORDER_RESOURCE,
        DELIVERY_ORDER_RESOURCE,
        POLICY_RESOURCE,
    ):
        assert permission.grant(
            _ctx(),
            principal_subject_id=SUBJECT,
            resource_type=resource,
            actions={
                "create",
                "read",
                "update",
                "archive",
                "convert",
                "issue",
                "confirm",
            },
            scope_level=ScopeLevel.TENANT,
        ).ok
    return TestClient(
        create_app(
            crm_service=CRMService(
                permission,
                repository=InMemoryCRMRepository(tenant_id=TENANT),
                audit_log=audit,
                confirm_approval_gate=gate,
            )
        )
    )


def _sales_order(client: TestClient) -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": f"C12-{uuid4().hex[:8]}", "display_name": "C12 API Customer"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "C12 API Opportunity"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={"opportunity_id": opportunity["id"], "title": "C12 API Requirement"},
    ).json()["data"]
    quote = client.post(
        "/v1/crm/quotes",
        headers=_headers(),
        json={"requirement_id": requirement["id"]},
    ).json()["data"]
    assert client.post(
        f"/v1/crm/quotes/{quote['id']}/lines",
        headers=_headers(),
        json={"description": "C12 line", "quantity": "2", "unit_price": "10"},
    ).status_code == 201
    assert client.post(
        f"/v1/crm/quotes/{quote['id']}/issue",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    ).status_code == 200
    conversion = client.post(
        f"/v1/crm/quotes/{quote['id']}/convert",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]
    return client.post(
        f"/v1/crm/conversions/{conversion['id']}/sales-order",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    ).json()["data"]


def test_g305_policy_round_trip() -> None:
    client = _client(gate=AllowConfirmApprovalGate())
    fetched = client.get("/v1/crm/policies/confirm-approval", headers=_headers())
    assert fetched.status_code == 200
    assert fetched.json()["data"]["confirm_approval_required"] is False
    assert fetched.json()["data"]["version"] == 0
    updated = client.put(
        "/v1/crm/policies/confirm-approval",
        headers=_headers(),
        json={"confirm_approval_required": True, "expected_version": 0},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["confirm_approval_required"] is True
    assert updated.json()["data"]["version"] == 1


def test_g305_rejects_context_override() -> None:
    client = _client()
    response = client.put(
        "/v1/crm/policies/confirm-approval",
        headers=_headers(),
        json={
            "confirm_approval_required": True,
            "expected_version": 0,
            "tenant_id": str(uuid4()),
        },
    )
    assert response.status_code == 422


def test_g305_confirm_blocked_and_allowed_via_http() -> None:
    client = _client(gate=DenyConfirmApprovalGate())
    sales_order = _sales_order(client)
    assert client.put(
        "/v1/crm/policies/confirm-approval",
        headers=_headers(),
        json={"confirm_approval_required": True, "expected_version": 0},
    ).status_code == 200
    blocked = client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/confirm",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert blocked.status_code == 409
    assert "approval" in blocked.json()["detail"]["message"].casefold()

    allow_client = _client(gate=AllowConfirmApprovalGate())
    sales_order = _sales_order(allow_client)
    assert allow_client.put(
        "/v1/crm/policies/confirm-approval",
        headers=_headers(),
        json={"confirm_approval_required": True, "expected_version": 0},
    ).status_code == 200
    confirmed = allow_client.post(
        f"/v1/crm/sales-orders/{sales_order['id']}/confirm",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert confirmed.status_code == 200
    assert confirmed.json()["data"]["status"] == "confirmed"


def test_g305_openapi_excludes_approval_center_and_finance_surfaces() -> None:
    spec = _client().get("/openapi.json").json()
    assert "/v1/crm/policies/confirm-approval" in spec["paths"]
    paths = " ".join(
        path
        for path in spec["paths"]
        if path.startswith("/v1/crm/policies")
        or "confirm-approval" in path
    ).casefold()
    for forbidden in (
        "approval-center",
        "workflow-definition",
        "invoice-issue",
        "psp",
        "ledger",
        "credit-limit",
    ):
        assert forbidden not in paths
    assert (
        spec["components"]["schemas"]["SetConfirmApprovalPolicyRequest"][
            "additionalProperties"
        ]
        is False
    )
