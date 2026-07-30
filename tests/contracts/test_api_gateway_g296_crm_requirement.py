"""PHX-G296 CRM Requirement C3 HTTP boundary contracts."""

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
        correlation_id="corr-g296-grant",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g296-http",
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


def _opportunity(client: TestClient) -> dict:
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": "C3-API", "display_name": "C3 API Customer"},
    ).json()["data"]
    return client.post(
        "/v1/crm/opportunities",
        headers=_headers(),
        json={"customer_id": customer["id"], "title": "C3 API Opportunity"},
    ).json()["data"]


def test_g296_requirement_demo_round_trip() -> None:
    client = _client()
    opportunity = _opportunity(client)
    response = client.post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={
            "opportunity_id": opportunity["id"],
            "title": "C3 Demo Requirement",
            "description": "Minimal need",
        },
    )
    assert response.status_code == 201
    requirement = response.json()["data"]
    assert requirement["code"].startswith("REQ-")
    fetched = client.get(
        f"/v1/crm/requirements/{requirement['id']}", headers=_headers()
    )
    assert fetched.status_code == 200
    assert fetched.json()["data"]["opportunity_id"] == opportunity["id"]


def test_g296_client_cannot_assign_code_or_tenant() -> None:
    response = _client().post(
        "/v1/crm/requirements",
        headers=_headers(),
        json={
            "opportunity_id": str(uuid4()),
            "title": "Invalid",
            "code": "LEGACY-REQ",
            "tenant_id": str(uuid4()),
        },
    )
    assert response.status_code == 422


def test_g296_runtime_openapi_excludes_gate_out() -> None:
    spec = _client().get("/openapi.json").json()
    assert "/v1/crm/requirements" in spec["paths"]
    paths = " ".join(
        path
        for path in spec["paths"]
        if path.startswith("/v1/crm/requirements")
    ).casefold()
    for forbidden in (
        "analysis",
        "sample",
        "quote",
        "convert",
                "issue",
        "sales-order",
        "finance",
        "mining",
        "insight",
    ):
        assert forbidden not in paths
    assert (
        spec["components"]["schemas"]["CreateRequirementRequest"][
            "additionalProperties"
        ]
        is False
    )
