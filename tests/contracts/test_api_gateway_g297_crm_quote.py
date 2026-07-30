"""PHX-G297 CRM Quote C4 HTTP boundary contracts."""

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
    QUOTE_RESOURCE,
    REQUIREMENT_RESOURCE,
    CRMService,
)

SUBJECT = uuid4()
TENANT = uuid4()


class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _context() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g297-grant",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g297-http",
    }


def _client() -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    for resource_type in (
        CUSTOMER_RESOURCE,
        OPPORTUNITY_RESOURCE,
        REQUIREMENT_RESOURCE,
        QUOTE_RESOURCE,
    ):
        assert permission.grant(
            _context(),
            principal_subject_id=SUBJECT,
            resource_type=resource_type,
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


def _requirement(client: TestClient) -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": "C4-API", "display_name": "C4 API Customer"},
    ).json()["data"]
    opportunity = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "C4 API Opportunity"},
    ).json()["data"]
    return client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={"opportunity_id": opportunity["id"], "title": "C4 API Requirement"},
    ).json()["data"]


def test_g297_quote_demo_round_trip() -> None:
    client = _client()
    requirement = _requirement(client)
    response = client.post(
        "/v1/crm/quotes",
        headers=_headers(),
        json={
            "requirement_id": requirement["id"],
            "currency": "eur",
            "notes": "Draft only",
        },
    )
    assert response.status_code == 201
    quote = response.json()["data"]
    assert quote["code"].startswith("QTE-")
    assert quote["currency"] == "EUR"
    fetched = client.get(f"/v1/crm/quotes/{quote['id']}", headers=_headers())
    assert fetched.status_code == 200
    assert fetched.json()["data"]["requirement_id"] == requirement["id"]


def test_g297_client_cannot_assign_code_or_tenant() -> None:
    response = _client().post(
        "/v1/crm/quotes",
        headers=_headers(),
        json={
            "requirement_id": str(uuid4()),
            "code": "LEGACY-QT",
            "tenant_id": str(uuid4()),
        },
    )
    assert response.status_code == 422


def test_g297_runtime_openapi_excludes_gate_out() -> None:
    spec = _client().get("/openapi.json").json()
    assert "/v1/crm/quotes" in spec["paths"]
    paths = " ".join(
        path
        for path in spec["paths"]
        if path.startswith("/v1/crm/quotes")
        and not path.endswith("/convert")
        and "/lines" not in path
    ).casefold()
    for forbidden in (
        "line",
        "price",
        "approve",
        "issue",
        "convert",
        "sales-order",
        "finance",
        "payment",
        "psp",
    ):
        assert forbidden not in paths
    assert (
        spec["components"]["schemas"]["CreateQuoteRequest"]["additionalProperties"]
        is False
    )
