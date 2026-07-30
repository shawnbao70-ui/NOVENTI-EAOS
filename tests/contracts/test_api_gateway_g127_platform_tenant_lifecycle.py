"""PHX-G127 Platform Tenant Lifecycle Thin Probe contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from kernel.organization.service import OrganizationService

ROOT = Path(__file__).resolve().parents[2]
GOVERNOR = uuid4()
CORR = str(uuid4())


@pytest.fixture(autouse=True)
def _reset() -> None:
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    yield


def _platform_headers(subject_id=GOVERNOR) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-Correlation-Id": CORR,
    }


def _tenant_headers(tenant_id, subject_id=GOVERNOR) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(tenant_id),
        "X-Correlation-Id": CORR,
    }


def test_terminal_exposes_platform_tenant_lifecycle_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminPlatformCreateTenant"' in html
    assert 'id="btnAdminPlatformSuspendTenant"' in html
    assert 'id="btnAdminPlatformReactivateTenant"' in html
    assert 'id="platformTenantLegalName"' in html
    assert "Platform tenant lifecycle 薄探针（G127" in html
    assert "platformTenants" in js
    assert "platformTenantSuspension" in js
    assert "adminCreatePlatformTenant" in js
    assert "adminSuspendPlatformTenant" in js
    assert "adminReactivatePlatformTenant" in js
    start = js.index("async function adminCreatePlatformTenant")
    end = js.index("async function adminListDeclaredRoles")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "/enterprises" not in chunk
    assert "platform: true" in chunk
    assert "platform: false" not in chunk


def test_platform_tenant_lifecycle_probe_api() -> None:
    service = OrganizationService(platform_governors={GOVERNOR})
    client = TestClient(create_app(organization_service=service))

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Create platform tenant" in page.text
    assert "Suspend platform tenant" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminCreatePlatformTenant" in script.text
    assert "adminSuspendPlatformTenant" in script.text
    assert "adminReactivatePlatformTenant" in script.text

    created = client.post(
        "/v1/platform/tenants",
        headers=_platform_headers(),
        json={"legal_name": f"G127-{uuid4()}"},
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
    ).json()
    assert after_suspend["status"] == "suspended"
    assert after_suspend["version"] == 2

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
    ).json()
    assert after_reactivate["status"] == "active"
