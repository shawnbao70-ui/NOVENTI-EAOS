"""PHX-G306 CRM Quote Issue HTTP contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import (
    CONVERSION_RESOURCE,
    CUSTOMER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    QUOTE_LINE_RESOURCE,
    QUOTE_RESOURCE,
    REQUIREMENT_RESOURCE,
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
        correlation_id="corr-g306",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g306-http",
    }


def _client() -> TestClient:
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
            },
            scope_level=ScopeLevel.TENANT,
        ).ok
    return TestClient(
        create_app(
            crm_service=CRMService(
                permission,
                repository=InMemoryCRMRepository(tenant_id=TENANT),
                audit_log=audit,
            )
        )
    )


def _quote_with_line(client: TestClient) -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": f"C13-{uuid4().hex[:8]}", "display_name": "C13 API Customer"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "C13 API Opportunity"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={"opportunity_id": opportunity["id"], "title": "C13 API Requirement"},
    ).json()["data"]
    quote = client.post(
        "/v1/crm/quotes",
        headers=_headers(),
        json={"requirement_id": requirement["id"]},
    ).json()["data"]
    assert client.post(
        f"/v1/crm/quotes/{quote['id']}/lines",
        headers=_headers(),
        json={"description": "C13 line", "quantity": "2", "unit_price": "10"},
    ).status_code == 201
    return quote


def test_g306_issue_round_trip() -> None:
    client = _client()
    quote = _quote_with_line(client)
    response = client.post(
        f"/v1/crm/quotes/{quote['id']}/issue",
        headers=_headers(),
        json={"idempotency_key": str(uuid4()), "human_confirm": True},
    )
    assert response.status_code == 200
    issued = response.json()["data"]
    assert issued["status"] == "issued"
    assert issued["issued_at"] is not None
    convert = client.post(
        f"/v1/crm/quotes/{quote['id']}/convert",
        headers=_headers(),
        json={"idempotency_key": str(uuid4())},
    )
    assert convert.status_code == 201


def test_g306_rejects_context_override() -> None:
    client = _client()
    quote = _quote_with_line(client)
    response = client.post(
        f"/v1/crm/quotes/{quote['id']}/issue",
        headers=_headers(),
        json={
            "idempotency_key": str(uuid4()),
            "human_confirm": True,
            "tenant_id": str(uuid4()),
        },
    )
    assert response.status_code == 422


def test_g306_openapi_excludes_send_approval_finance_surfaces() -> None:
    spec = _client().get("/openapi.json").json()
    assert "/v1/crm/quotes/{quote_id}/issue" in spec["paths"]
    paths = " ".join(
        path
        for path in spec["paths"]
        if path.endswith("/issue") or path.startswith("/v1/crm/quotes")
    ).casefold()
    for forbidden in (
        "email",
        "pdf",
        "approval-center",
        "workflow",
        "psp",
        "ship",
        "invoice-issue",
    ):
        assert forbidden not in paths
    assert (
        spec["components"]["schemas"]["IssueQuoteRequest"]["additionalProperties"]
        is False
    )
