"""PHX-G123 Organization Unit / Membership Thin Probe contracts."""

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


def test_terminal_exposes_organization_unit_membership_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminOrganizationUpsertUnit"' in html
    assert 'id="btnAdminOrganizationUnitTree"' in html
    assert 'id="btnAdminOrganizationAddMembership"' in html
    assert 'id="btnAdminOrganizationListMemberships"' in html
    assert 'id="orgUnitName"' in html
    assert 'id="orgMembershipSubjectId"' in html
    assert "Organization unit/membership 薄探针（G123" in html
    assert "Organization Terminal 运维面齐" in html
    assert 'organizationUnits: "/v1/organization-units"' in js
    assert 'organizationUnitTree: "/v1/organization-units/tree"' in js
    assert 'organizationMemberships: "/v1/memberships"' in js
    assert "adminUpsertOrganizationUnit" in js
    assert "adminGetOrganizationUnitTree" in js
    assert "adminAddOrganizationMembership" in js
    assert "adminListOrganizationMemberships" in js
    start = js.index("async function adminUpsertOrganizationUnit")
    end = js.index("async function adminSetOrganizationUnitStatus")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "/status" not in chunk
    assert "/suspension" not in chunk


def test_organization_unit_membership_probe_api() -> None:
    service = OrganizationService(
        platform_governors={GOVERNOR},
        membership_eligibility=_AllowAllMembershipEligibility(),
    )
    created = service.create_tenant(_platform_ctx(), legal_name=f"G123-{uuid4()}")
    assert created.ok and created.data is not None
    tenant_id = created.data
    client = TestClient(create_app(organization_service=service))

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Upsert organization unit" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminUpsertOrganizationUnit" in script.text
    assert "adminAddOrganizationMembership" in script.text

    unit = client.put(
        "/v1/organization-units",
        headers=_headers(tenant_id),
        json={"unit_type": "department", "name": "Finance"},
    )
    assert unit.status_code == 200
    unit_id = unit.json()["id"]

    tree = client.get("/v1/organization-units/tree", headers=_headers(tenant_id))
    assert tree.status_code == 200
    assert any(item["id"] == unit_id for item in tree.json())

    member_subject = uuid4()
    membership = client.post(
        "/v1/memberships",
        headers=_headers(tenant_id),
        json={
            "subject_id": str(member_subject),
            "membership_role_label": "member",
            "org_unit_id": unit_id,
        },
    )
    assert membership.status_code == 201
    membership_id = membership.json()["id"]

    listed = client.get(
        "/v1/memberships",
        headers=_headers(tenant_id),
        params={"subject_id": str(member_subject)},
    )
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["id"] == membership_id
    assert listed.json()[0]["subject_id"] == str(member_subject)
