"""PHX-G294 CRM C1 HTTP boundary contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import CONTACT_RESOURCE, CUSTOMER_RESOURCE, CRMService

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
        correlation_id="corr-g294-grant",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g294-http",
    }


def _client() -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    for resource_type in (CUSTOMER_RESOURCE, CONTACT_RESOURCE):
        assert permission.grant(
            _context(),
            principal_subject_id=SUBJECT,
            resource_type=resource_type,
            actions={"create", "read", "update", "archive"},
            scope_level=ScopeLevel.TENANT,
        ).ok
    crm = CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=TENANT),
        audit_log=audit,
    )
    return TestClient(create_app(crm_service=crm))


def test_g294_customer_contact_demo_round_trip() -> None:
    client = _client()
    customer_response = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": "C-294", "display_name": "C1 Demo"},
    )
    assert customer_response.status_code == 201
    customer = customer_response.json()["data"]
    assert customer["code"] == "C-294"
    assert "tenant_id" not in customer

    contact_response = client.post(
        f"/v1/crm/customers/{customer['id']}/contacts",
        headers=_headers(),
        json={
            "display_name": "Demo Contact",
            "email": "contact@example.test",
        },
    )
    assert contact_response.status_code == 201
    contact = contact_response.json()["data"]
    fetched = client.get(
        f"/v1/crm/customers/{customer['id']}/contacts/{contact['id']}",
        headers=_headers(),
    )
    assert fetched.status_code == 200
    assert fetched.json()["data"]["email"] == "contact@example.test"


def test_g294_rejects_context_override_and_unknown_fields() -> None:
    client = _client()
    response = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={
            "code": "C-OVERRIDE",
            "display_name": "Invalid",
            "tenant_id": str(uuid4()),
        },
    )
    assert response.status_code == 422


def test_g294_runtime_openapi_is_closed_and_has_no_gate_out_routes() -> None:
    spec = _client().get("/openapi.json").json()
    paths = spec["paths"]
    assert "/v1/crm/customers" in paths
    serialized_paths = " ".join(
        path for path in paths if path.startswith("/v1/crm/customers")
    ).casefold()
    for forbidden in (
        "opportunit",
        "quote",
        "finance",
        "follow-up",
        "customer360",
        "merge",
        "dedup",
    ):
        assert forbidden not in serialized_paths
    schemas = spec["components"]["schemas"]
    for name in (
        "CreateCustomerRequest",
        "UpdateCustomerRequest",
        "CreateContactRequest",
        "UpdateContactRequest",
    ):
        assert schemas[name]["additionalProperties"] is False
