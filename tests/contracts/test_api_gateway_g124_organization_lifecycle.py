"""PHX-G124 Organization Lifecycle Thin Probe contracts."""

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


def test_terminal_exposes_organization_lifecycle_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminOrganizationSetUnitStatus"' in html
    assert 'id="btnAdminOrganizationSuspendMembership"' in html
    assert 'id="btnAdminOrganizationReactivateMembership"' in html
    assert 'id="orgUnitStatus"' in html
    assert 'id="orgLifecycleReason"' in html
    assert "Organization lifecycle 薄探针（G124" in html
    assert "organizationUnitStatus" in js
    assert "organizationMembershipSuspension" in js
    assert "adminSetOrganizationUnitStatus" in js
    assert "adminSuspendOrganizationMembership" in js
    assert "adminReactivateOrganizationMembership" in js
    start = js.index("async function adminSetOrganizationUnitStatus")
    end = js.index("async function adminTransferOrganizationMembership")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "/unit" not in chunk
    assert "adminEndOrganizationMembership" not in chunk


def test_organization_lifecycle_probe_api() -> None:
    service = OrganizationService(
        platform_governors={GOVERNOR},
        membership_eligibility=_AllowAllMembershipEligibility(),
    )
    created = service.create_tenant(_platform_ctx(), legal_name=f"G124-{uuid4()}")
    assert created.ok and created.data is not None
    tenant_id = created.data
    client = TestClient(create_app(organization_service=service))

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Set organization unit status" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminSetOrganizationUnitStatus" in script.text
    assert "adminSuspendOrganizationMembership" in script.text

    unit = client.put(
        "/v1/organization-units",
        headers=_headers(tenant_id),
        json={"unit_type": "department", "name": f"Ops-{uuid4()}"},
    )
    assert unit.status_code == 200
    unit_id = unit.json()["id"]

    tree = client.get("/v1/organization-units/tree", headers=_headers(tenant_id))
    assert tree.status_code == 200
    version = next(item["version"] for item in tree.json() if item["id"] == unit_id)

    inactivated = client.put(
        f"/v1/organization-units/{unit_id}/status",
        headers=_headers(tenant_id),
        json={
            "status": "inactive",
            "reason": "empty",
            "expected_version": version,
        },
    )
    assert inactivated.status_code == 200
    assert inactivated.json()["ok"] is True

    member_subject = uuid4()
    membership = client.post(
        "/v1/memberships",
        headers=_headers(tenant_id),
        json={
            "subject_id": str(member_subject),
            "membership_role_label": "member",
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
    assert listed.json()[0]["version"] == 1

    suspended = client.post(
        f"/v1/memberships/{membership_id}/suspension",
        headers=_headers(tenant_id),
        json={"reason": "leave", "expected_version": 1},
    )
    assert suspended.status_code == 200
    assert suspended.json()["ok"] is True

    reactivated = client.request(
        "DELETE",
        f"/v1/memberships/{membership_id}/suspension",
        headers=_headers(tenant_id),
        json={"reason": "return", "expected_version": 2},
    )
    assert reactivated.status_code == 200
    assert reactivated.json()["ok"] is True
