"""PHX-G25 Gateway platform tenant lifecycle contracts."""

from __future__ import annotations

from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.context import derive_platform_context, derive_tenant_context
from kernel.organization.service import OrganizationService

GOVERNOR = uuid4()
CORR = str(uuid4())


def _platform_headers(subject_id=GOVERNOR, **extra: str) -> dict[str, str]:
    base = {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-Correlation-Id": CORR,
    }
    base.update(extra)
    return base


def _tenant_headers(tenant_id, subject_id=GOVERNOR) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(tenant_id),
        "X-Correlation-Id": CORR,
    }


@pytest.fixture()
def client() -> TestClient:
    service = OrganizationService(platform_governors={GOVERNOR})
    return TestClient(create_app(organization_service=service))


def test_platform_create_requires_subject(client: TestClient) -> None:
    response = client.post(
        "/v1/platform/tenants",
        json={"legal_name": "No Subject"},
    )
    assert response.status_code == 401


def test_create_suspend_reactivate_tenant(client: TestClient) -> None:
    created = client.post(
        "/v1/platform/tenants",
        headers=_platform_headers(),
        json={"legal_name": f"Platform-{uuid4()}"},
    )
    assert created.status_code == 201
    tenant_id = created.json()["id"]

    viewed = client.get(
        f"/v1/tenants/{tenant_id}",
        headers=_tenant_headers(tenant_id),
    )
    assert viewed.status_code == 200
    assert viewed.json()["status"] == "active"
    assert viewed.json()["version"] == 1

    suspended = client.post(
        f"/v1/platform/tenants/{tenant_id}/suspension",
        headers=_platform_headers(),
        json={"reason": "hold", "expected_version": 1},
    )
    assert suspended.status_code == 200
    assert suspended.json()["ok"] is True

    after_suspend = client.get(
        f"/v1/tenants/{tenant_id}",
        headers=_tenant_headers(tenant_id),
    )
    assert after_suspend.json()["status"] == "suspended"
    assert after_suspend.json()["version"] == 2

    reactivated = client.request(
        "DELETE",
        f"/v1/platform/tenants/{tenant_id}/suspension",
        headers=_platform_headers(),
        json={"reason": "resume", "expected_version": 2},
    )
    assert reactivated.status_code == 200
    assert reactivated.json()["ok"] is True

    after_reactivate = client.get(
        f"/v1/tenants/{tenant_id}",
        headers=_tenant_headers(tenant_id),
    )
    assert after_reactivate.json()["status"] == "active"


def test_non_governor_cannot_create_tenant(client: TestClient) -> None:
    response = client.post(
        "/v1/platform/tenants",
        headers=_platform_headers(subject_id=uuid4()),
        json={"legal_name": f"Denied-{uuid4()}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "PERMISSION_DENIED"


def test_tenant_plane_cannot_create_platform_tenant(client: TestClient) -> None:
    # Tenant-plane path does not exist for create; posting to enterprises is not create_tenant.
    # Ensure /platform/tenants with only tenant headers still uses platform derivation
    # (tenant header ignored) — missing correlation already covered; here ensure
    # tenant-scoped POST /enterprises is not a substitute for create_tenant.
    response = client.post(
        "/v1/enterprises",
        headers=_tenant_headers(uuid4()),
        json={"legal_name": "Not A Tenant"},
    )
    # No tenant seeded → ORG_TENANT_NOT_FOUND style failure, not tenant creation.
    assert response.status_code in {400, 403, 404}


def test_create_rejects_body_context_override(client: TestClient) -> None:
    response = client.post(
        "/v1/platform/tenants",
        headers=_platform_headers(),
        json={
            "legal_name": f"Override-{uuid4()}",
            "tenant_id": str(uuid4()),
            "platform_scope": False,
        },
    )
    # Closed CreateTenantRequest rejects unknown fields before domain elevation check.
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any("tenant_id" in str(item.get("loc", ())) for item in detail)


def test_derive_platform_context_sets_platform_scope() -> None:
    ctx = derive_platform_context(
        x_eaos_subject_id=str(GOVERNOR),
        x_eaos_subject_type="human",
        x_correlation_id=CORR,
    )
    assert ctx.platform_scope is True
    assert ctx.tenant_id is None

    tenant_ctx = derive_tenant_context(
        x_eaos_subject_id=str(GOVERNOR),
        x_eaos_subject_type="human",
        x_eaos_tenant_id=str(uuid4()),
        x_correlation_id=CORR,
    )
    assert tenant_ctx.platform_scope is False
    assert tenant_ctx.tenant_id is not None
