"""PHX-G295 CRM Opportunity C2 HTTP boundary contracts."""

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
        correlation_id="corr-g295-grant",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g295-http",
    }


def _client() -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    for resource_type, actions in (
        (CUSTOMER_RESOURCE, {"create", "read"}),
        (OPPORTUNITY_RESOURCE, {"create", "read", "update", "archive"}),
    ):
        assert permission.grant(
            _context(),
            principal_subject_id=SUBJECT,
            resource_type=resource_type,
            actions=actions,
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


def test_g295_opportunity_demo_round_trip() -> None:
    client = _client()
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": "C2-API", "display_name": "C2 API Customer"},
    ).json()["data"]
    created_response = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={
            "customer_id": customer["id"],
            "title": "C2 Demo Opportunity",
        },
    )
    assert created_response.status_code == 201
    opportunity = created_response.json()["data"]
    assert opportunity["code"].startswith("OPP-")
    fetched = client.get(
        f"/v1/crm/opportunities/{opportunity['id']}",
        headers=_headers(),
    )
    assert fetched.status_code == 200
    assert fetched.json()["data"]["customer_id"] == customer["id"]


def test_g295_client_cannot_assign_code_or_tenant() -> None:
    client = _client()
    response = client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={
            "customer_id": str(uuid4()),
            "title": "Invalid",
            "code": "LEGACY-001",
            "tenant_id": str(uuid4()),
        },
    )
    assert response.status_code == 422


def test_g295_runtime_openapi_excludes_gate_out() -> None:
    spec = _client().get("/openapi.json").json()
    assert "/v1/crm/opportunities" in spec["paths"]
    paths = " ".join(
        path for path in spec["paths"] if path.startswith("/v1/crm/opportunities")
    ).casefold()
    for forbidden in (
        "requirement",
        "quote",
        "convert",
                "issue",
        "finance",
        "follow-up",
        "customer360",
        "mining",
        "insight",
    ):
        assert forbidden not in paths
    assert (
        spec["components"]["schemas"]["CreateOpportunityRequest"][
            "additionalProperties"
        ]
        is False
    )
