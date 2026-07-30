"""PHX-G32 Gateway Organization route completion contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.organization.service import OrganizationService
from kernel.shared.context import ExecutionContext, SubjectType


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


ACTOR = uuid4()
GOVERNOR = uuid4()
SUBJECT = uuid4()
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
def gateway() -> tuple[TestClient, UUID]:
    service = OrganizationService(
        platform_governors={GOVERNOR},
        membership_eligibility=_AllowAll(),
    )
    created = service.create_tenant(_platform_ctx(), legal_name=f"G32-{uuid4()}")
    assert created.ok and created.data is not None
    client = TestClient(create_app(organization_service=service))
    return client, created.data


def test_enterprise_lifecycle(gateway: tuple) -> None:
    client, tenant_id = gateway
    created = client.post(
        "/v1/enterprises",
        headers=_headers(tenant_id),
        json={"legal_name": f"Secondary-{uuid4()}"},
    )
    assert created.status_code == 201
    enterprise_id = created.json()["id"]

    got = client.get(
        f"/v1/enterprises/{enterprise_id}",
        headers=_headers(tenant_id),
    )
    assert got.status_code == 200
    assert got.json()["status"] == "active"
    version = got.json()["version"]

    suspended = client.post(
        f"/v1/enterprises/{enterprise_id}/suspension",
        headers=_headers(tenant_id),
        json={"reason": "hold", "expected_version": version},
    )
    assert suspended.status_code == 200
    assert suspended.json()["ok"] is True

    after_suspend = client.get(
        f"/v1/enterprises/{enterprise_id}",
        headers=_headers(tenant_id),
    ).json()
    assert after_suspend["status"] == "suspended"

    reactivated = client.request(
        "DELETE",
        f"/v1/enterprises/{enterprise_id}/suspension",
        headers=_headers(tenant_id),
        json={"reason": "resume", "expected_version": after_suspend["version"]},
    )
    assert reactivated.status_code == 200

    after_reactivate = client.get(
        f"/v1/enterprises/{enterprise_id}",
        headers=_headers(tenant_id),
    ).json()
    assert after_reactivate["status"] == "active"

    closed = client.request(
        "DELETE",
        f"/v1/enterprises/{enterprise_id}",
        headers=_headers(tenant_id),
        json={"reason": "wind-down", "expected_version": after_reactivate["version"]},
    )
    assert closed.status_code == 200
    assert closed.json()["ok"] is True


def test_unit_tree_status_and_membership_lifecycle(gateway: tuple) -> None:
    client, tenant_id = gateway
    enterprise = client.post(
        "/v1/enterprises",
        headers=_headers(tenant_id),
        json={"legal_name": f"Ops-{uuid4()}"},
    ).json()["id"]

    unit_a = client.put(
        "/v1/organization-units",
        headers=_headers(tenant_id),
        json={
            "unit_type": "department",
            "name": "Alpha",
            "enterprise_id": enterprise,
        },
    )
    assert unit_a.status_code == 200
    unit_a_id = unit_a.json()["id"]

    unit_b = client.put(
        "/v1/organization-units",
        headers=_headers(tenant_id),
        json={
            "unit_type": "department",
            "name": "Beta",
            "enterprise_id": enterprise,
        },
    ).json()["id"]

    tree = client.get(
        "/v1/organization-units/tree",
        headers=_headers(tenant_id),
    )
    assert tree.status_code == 200
    assert {item["id"] for item in tree.json()} >= {unit_a_id, unit_b}

    membership = client.post(
        "/v1/memberships",
        headers=_headers(tenant_id),
        json={
            "subject_id": str(SUBJECT),
            "enterprise_id": enterprise,
            "org_unit_id": unit_a_id,
            "membership_role_label": "member",
        },
    )
    assert membership.status_code == 201
    membership_id = membership.json()["id"]

    listed = client.get(
        "/v1/memberships",
        headers=_headers(tenant_id),
        params={"subject_id": str(SUBJECT)},
    )
    assert listed.status_code == 200
    assert listed.json()[0]["version"] == 1

    suspended = client.post(
        f"/v1/memberships/{membership_id}/suspension",
        headers=_headers(tenant_id),
        json={"reason": "leave", "expected_version": 1},
    )
    assert suspended.status_code == 200

    reactivated = client.request(
        "DELETE",
        f"/v1/memberships/{membership_id}/suspension",
        headers=_headers(tenant_id),
        json={"reason": "return", "expected_version": 2},
    )
    assert reactivated.status_code == 200

    transferred = client.put(
        f"/v1/memberships/{membership_id}/unit",
        headers=_headers(tenant_id),
        json={"to_org_unit_id": unit_b, "expected_version": 3},
    )
    assert transferred.status_code == 200

    after_transfer = client.get(
        "/v1/memberships",
        headers=_headers(tenant_id),
        params={"subject_id": str(SUBJECT)},
    ).json()[0]
    assert after_transfer["org_unit_id"] == unit_b
    assert after_transfer["version"] == 4

    ended = client.request(
        "DELETE",
        f"/v1/memberships/{membership_id}",
        headers=_headers(tenant_id),
        json={"reason": "exit", "expected_version": 4},
    )
    assert ended.status_code == 200

    # Units with no active memberships can be inactivated.
    tree_versions = {
        item["id"]: item["version"]
        for item in client.get(
            "/v1/organization-units/tree",
            headers=_headers(tenant_id),
        ).json()
    }
    inactivated = client.put(
        f"/v1/organization-units/{unit_a_id}/status",
        headers=_headers(tenant_id),
        json={
            "status": "inactive",
            "reason": "empty",
            "expected_version": tree_versions[unit_a_id],
        },
    )
    assert inactivated.status_code == 200
    assert inactivated.json()["ok"] is True


def test_body_cannot_elevate_on_extension_routes(gateway: tuple) -> None:
    client, tenant_id = gateway
    enterprise = client.post(
        "/v1/enterprises",
        headers=_headers(tenant_id),
        json={"legal_name": f"Elev-{uuid4()}"},
    ).json()["id"]
    response = client.post(
        f"/v1/enterprises/{enterprise}/suspension",
        headers=_headers(tenant_id),
        json={
            "reason": "x",
            "expected_version": 1,
            "tenant_id": str(uuid4()),
            "platform_scope": True,
        },
    )
    # Closed VersionedReasonRequest rejects unknown fields before domain elevation check.
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any("tenant_id" in str(item.get("loc", ())) for item in detail)
