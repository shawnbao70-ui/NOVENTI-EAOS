"""PHX-G122 Organization Status / Tenant / Enterprise Thin Probe contracts."""

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


def test_terminal_exposes_organization_probe_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminOrganizationStatus"' in html
    assert 'id="btnAdminOrganizationGetTenant"' in html
    assert 'id="btnAdminOrganizationCreateEnterprise"' in html
    assert 'id="btnAdminOrganizationListEnterprises"' in html
    assert 'id="orgEnterpriseLegalName"' in html
    assert "Organization 状态/tenant/enterprise 薄探针（G122" in html
    assert 'organizationStatus: "/v1/organization/status"' in js
    assert "organizationTenant" in js
    assert 'organizationEnterprises: "/v1/enterprises"' in js
    assert "adminGetOrganizationTenant" in js
    assert "adminCreateOrganizationEnterprise" in js
    assert "adminListOrganizationEnterprises" in js
    start = js.index("async function adminGetOrganizationTenant")
    end = js.index("async function adminUpsertOrganizationUnit")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "/organization-units" not in chunk
    assert "/memberships" not in chunk


def test_organization_status_and_probe_api() -> None:
    service = OrganizationService(
        platform_governors={GOVERNOR},
        membership_eligibility=_AllowAllMembershipEligibility(),
    )
    created = service.create_tenant(_platform_ctx(), legal_name=f"G122-{uuid4()}")
    assert created.ok and created.data is not None
    tenant_id = created.data
    client = TestClient(create_app(organization_service=service))

    status = client.get("/v1/organization/status")
    assert status.status_code == 200
    data = status.json()["data"]
    assert data["writable"] is False
    assert "tenant_get" in data["supported_surfaces"]
    assert "enterprise_create" in data["supported_surfaces"]
    assert "enterprise_list" in data["supported_surfaces"]

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Organization status" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminCreateOrganizationEnterprise" in script.text

    tenant = client.get(f"/v1/tenants/{tenant_id}", headers=_headers(tenant_id))
    assert tenant.status_code == 200
    assert tenant.json()["id"] == str(tenant_id)
    assert tenant.json()["status"] == "active"

    enterprise = client.post(
        "/v1/enterprises",
        headers=_headers(tenant_id),
        json={"legal_name": f"G122-Ops-{uuid4()}"},
    )
    assert enterprise.status_code == 201
    enterprise_id = enterprise.json()["id"]

    listed = client.get("/v1/enterprises", headers=_headers(tenant_id))
    assert listed.status_code == 200
    ids = {item["id"] for item in listed.json()}
    assert enterprise_id in ids
