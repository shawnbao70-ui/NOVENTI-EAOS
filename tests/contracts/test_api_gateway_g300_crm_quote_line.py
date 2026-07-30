"""PHX-G300 CRM Quote Line HTTP contracts."""

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
        correlation_id="corr-g300",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g300-http",
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
    ):
        assert permission.grant(
            _ctx(),
            principal_subject_id=SUBJECT,
            resource_type=resource,
            actions={"create", "read", "update", "archive"},
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


def _quote(client: TestClient) -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": "C7-API", "display_name": "C7 API Customer"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "C7 API Opportunity"},
    ).json()["data"]
    requirement = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={"opportunity_id": opportunity["id"], "title": "C7 API Requirement"},
    ).json()["data"]
    return client.post(
        "/v1/crm/quotes",
        headers=_headers(),
        json={"requirement_id": requirement["id"]},
    ).json()["data"]


def test_g300_quote_line_round_trip_and_server_amount() -> None:
    client = _client()
    quote = _quote(client)
    response = client.post(
        f"/v1/crm/quotes/{quote['id']}/lines",
        headers=_headers(),
        json={
            "description": "Manual line",
            "quantity": "2.500",
            "unit_price": "12.34",
        },
    )
    assert response.status_code == 201
    line = response.json()["data"]
    assert line["amount"] == "30.85"
    listed = client.get(
        f"/v1/crm/quotes/{quote['id']}/lines", headers=_headers()
    )
    assert listed.status_code == 200
    assert listed.json()["data"][0]["id"] == line["id"]


def test_g300_rejects_client_amount_and_tenant() -> None:
    client = _client()
    quote = _quote(client)
    response = client.post(
        f"/v1/crm/quotes/{quote['id']}/lines",
        headers=_headers(),
        json={
            "description": "Invalid",
            "quantity": "1",
            "unit_price": "2",
            "amount": "2",
            "tenant_id": str(uuid4()),
        },
    )
    assert response.status_code == 422


def test_g300_openapi_excludes_pricing_finance_inventory() -> None:
    spec = _client().get("/openapi.json").json()
    assert any("/lines" in path for path in spec["paths"])
    paths = " ".join(
        path
        for path in spec["paths"]
        if path.startswith("/v1/crm/quotes") and "/lines" in path
    ).casefold()
    for forbidden in (
        "pricing",
        "margin",
        "discount",
        "tax",
        "finance",
        "inventory",
    ):
        assert forbidden not in paths
    assert (
        spec["components"]["schemas"]["CreateQuoteLineRequest"][
            "additionalProperties"
        ]
        is False
    )
