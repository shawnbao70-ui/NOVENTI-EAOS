"""PHX-G21 Gateway Organization HTTP surface contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.organization.service import OrganizationService
from kernel.shared.context import ExecutionContext, SubjectType


class _AllowAllMembershipEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


ACTOR = uuid4()
GOVERNOR = uuid4()
CORR = str(uuid4())


def _platform_ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=GOVERNOR,
        subject_type=SubjectType.HUMAN,
        tenant_id=None,
        platform_scope=True,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def _headers(tenant_id: UUID, **extra: str) -> dict[str, str]:
    base = {
        "X-EAOS-Subject-Id": str(ACTOR),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(tenant_id),
        "X-Correlation-Id": CORR,
    }
    base.update(extra)
    return base


@pytest.fixture()
def org_setup() -> tuple[TestClient, UUID, OrganizationService]:
    service = OrganizationService(
        platform_governors={GOVERNOR},
        membership_eligibility=_AllowAllMembershipEligibility(),
    )
    created = service.create_tenant(_platform_ctx(), legal_name=f"G21-{uuid4()}")
    assert created.ok and created.data is not None
    client = TestClient(create_app(organization_service=service))
    return client, created.data, service


def test_organization_requires_trusted_headers(org_setup: tuple) -> None:
    client, tenant_id, _ = org_setup
    missing = client.get(f"/v1/tenants/{tenant_id}")
    assert missing.status_code == 401


def test_get_tenant_happy_path(org_setup: tuple) -> None:
    client, tenant_id, _ = org_setup
    response = client.get(f"/v1/tenants/{tenant_id}", headers=_headers(tenant_id))
    assert response.status_code == 200
    assert response.json()["id"] == str(tenant_id)
    assert response.json()["status"] == "active"


def test_get_tenant_cross_tenant_denied(org_setup: tuple) -> None:
    client, tenant_id, _ = org_setup
    response = client.get(
        f"/v1/tenants/{tenant_id}",
        headers=_headers(uuid4()),
    )
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "ORG_TENANT_NOT_FOUND"


def test_create_rejects_context_override(org_setup: tuple) -> None:
    client, tenant_id, _ = org_setup
    response = client.post(
        "/v1/enterprises",
        headers=_headers(tenant_id),
        json={
            "legal_name": "Override Co",
            "tenant_id": str(uuid4()),
            "platform_scope": True,
        },
    )
    # Closed CreateEnterpriseRequest rejects unknown fields before domain elevation check.
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any("tenant_id" in str(item.get("loc", ())) for item in detail)


def test_create_and_list_enterprises(org_setup: tuple) -> None:
    client, tenant_id, _ = org_setup
    created = client.post(
        "/v1/enterprises",
        headers=_headers(tenant_id),
        json={"legal_name": "Secondary Ops"},
    )
    assert created.status_code == 201
    enterprise_id = created.json()["id"]
    listed = client.get("/v1/enterprises", headers=_headers(tenant_id))
    assert listed.status_code == 200
    ids = {item["id"] for item in listed.json()}
    assert enterprise_id in ids
    assert any(item["is_primary"] for item in listed.json())


def test_duplicate_enterprise_conflict(org_setup: tuple) -> None:
    client, tenant_id, _ = org_setup
    name = f"Dup-{uuid4()}"
    assert client.post(
        "/v1/enterprises",
        headers=_headers(tenant_id),
        json={"legal_name": name},
    ).status_code == 201
    again = client.post(
        "/v1/enterprises",
        headers=_headers(tenant_id),
        json={"legal_name": name},
    )
    assert again.status_code == 409
    assert again.json()["detail"]["code"] == "ORG_ENTERPRISE_DUPLICATE_NAME"


def test_upsert_unit(org_setup: tuple) -> None:
    client, tenant_id, _ = org_setup
    response = client.put(
        "/v1/organization-units",
        headers=_headers(tenant_id),
        json={"unit_type": "department", "name": "Finance"},
    )
    assert response.status_code == 200
    assert "id" in response.json()


def test_add_and_list_memberships(org_setup: tuple) -> None:
    client, tenant_id, _ = org_setup
    subject_id = uuid4()
    created = client.post(
        "/v1/memberships",
        headers=_headers(tenant_id),
        json={"subject_id": str(subject_id), "membership_role_label": "member"},
    )
    assert created.status_code == 201
    listed = client.get(
        "/v1/memberships",
        headers=_headers(tenant_id),
        params={"subject_id": str(subject_id)},
    )
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["subject_id"] == str(subject_id)


def test_add_membership_ineligible() -> None:
    service = OrganizationService(platform_governors={GOVERNOR})
    created = service.create_tenant(_platform_ctx(), legal_name=f"Deny-{uuid4()}")
    assert created.data is not None
    client = TestClient(create_app(organization_service=service))
    response = client.post(
        "/v1/memberships",
        headers=_headers(created.data),
        json={"subject_id": str(uuid4())},
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "ORG_SUBJECT_INELIGIBLE"
