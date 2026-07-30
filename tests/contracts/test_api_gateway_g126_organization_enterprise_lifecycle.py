"""PHX-G126 Organization Enterprise Lifecycle Thin Probe contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from kernel.organization.service import OrganizationService
from kernel.shared.context import ExecutionContext, SubjectType

ROOT = Path(__file__).resolve().parents[2]
ACTOR = uuid4()
GOVERNOR = uuid4()
CORR = str(uuid4())


class _AllowAllMembershipEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


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


def _platform_ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=GOVERNOR,
        subject_type=SubjectType.HUMAN,
        tenant_id=None,
        platform_scope=True,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def _headers(tenant_id: UUID) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(ACTOR),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(tenant_id),
        "X-Correlation-Id": CORR,
    }


def test_terminal_exposes_organization_enterprise_lifecycle_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminOrganizationSuspendEnterprise"' in html
    assert 'id="btnAdminOrganizationReactivateEnterprise"' in html
    assert 'id="btnAdminOrganizationCloseEnterprise"' in html
    assert "Organization enterprise lifecycle 薄探针（G126" in html
    assert "organizationEnterpriseSuspension" in js
    assert "organizationEnterpriseEnd" in js
    assert "adminSuspendOrganizationEnterprise" in js
    assert "adminReactivateOrganizationEnterprise" in js
    assert "adminCloseOrganizationEnterprise" in js
    start = js.index("async function adminSuspendOrganizationEnterprise")
    end = js.index("async function adminCreatePlatformTenant")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "/memberships" not in chunk
    assert "/unit" not in chunk
    assert "adminCreatePlatformTenant" not in chunk
    assert "/platform/tenants" not in chunk


def test_organization_enterprise_lifecycle_probe_api() -> None:
    service = OrganizationService(
        platform_governors={GOVERNOR},
        membership_eligibility=_AllowAllMembershipEligibility(),
    )
    created = service.create_tenant(_platform_ctx(), legal_name=f"G126-{uuid4()}")
    assert created.ok and created.data is not None
    tenant_id = created.data
    client = TestClient(create_app(organization_service=service))

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Suspend enterprise" in page.text
    assert "Close enterprise" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminSuspendOrganizationEnterprise" in script.text
    assert "adminCloseOrganizationEnterprise" in script.text

    enterprise = client.post(
        "/v1/enterprises",
        headers=_headers(tenant_id),
        json={"legal_name": f"G126-Ops-{uuid4()}"},
    )
    assert enterprise.status_code == 201
    enterprise_id = enterprise.json()["id"]

    got = client.get(
        f"/v1/enterprises/{enterprise_id}",
        headers=_headers(tenant_id),
    )
    assert got.status_code == 200
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
    assert reactivated.json()["ok"] is True

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
