"""PHX-G125 Organization Membership Transfer / End Thin Probe contracts."""

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


def test_terminal_exposes_organization_membership_transfer_end_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminOrganizationTransferMembership"' in html
    assert 'id="btnAdminOrganizationEndMembership"' in html
    assert "Organization membership transfer/end 薄探针（G125" in html
    assert "organizationMembershipUnit" in js
    assert "organizationMembershipEnd" in js
    assert "adminTransferOrganizationMembership" in js
    assert "adminEndOrganizationMembership" in js
    start = js.index("async function adminTransferOrganizationMembership")
    end = js.index("async function adminSuspendOrganizationEnterprise")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "/suspension" not in chunk
    assert "/status" not in chunk
    assert "adminCloseOrganizationEnterprise" not in chunk


def test_organization_membership_transfer_end_probe_api() -> None:
    service = OrganizationService(
        platform_governors={GOVERNOR},
        membership_eligibility=_AllowAllMembershipEligibility(),
    )
    created = service.create_tenant(_platform_ctx(), legal_name=f"G125-{uuid4()}")
    assert created.ok and created.data is not None
    tenant_id = created.data
    client = TestClient(create_app(organization_service=service))

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Transfer membership unit" in page.text
    assert "End membership" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminTransferOrganizationMembership" in script.text
    assert "adminEndOrganizationMembership" in script.text

    enterprise = client.post(
        "/v1/enterprises",
        headers=_headers(tenant_id),
        json={"legal_name": f"Ops-{uuid4()}"},
    )
    assert enterprise.status_code == 201
    enterprise_id = enterprise.json()["id"]

    unit_a = client.put(
        "/v1/organization-units",
        headers=_headers(tenant_id),
        json={
            "unit_type": "department",
            "name": f"Alpha-{uuid4()}",
            "enterprise_id": enterprise_id,
        },
    )
    assert unit_a.status_code == 200
    unit_a_id = unit_a.json()["id"]

    unit_b = client.put(
        "/v1/organization-units",
        headers=_headers(tenant_id),
        json={
            "unit_type": "department",
            "name": f"Beta-{uuid4()}",
            "enterprise_id": enterprise_id,
        },
    )
    assert unit_b.status_code == 200
    unit_b_id = unit_b.json()["id"]

    member_subject = uuid4()
    membership = client.post(
        "/v1/memberships",
        headers=_headers(tenant_id),
        json={
            "subject_id": str(member_subject),
            "enterprise_id": enterprise_id,
            "org_unit_id": unit_a_id,
            "membership_role_label": "member",
        },
    )
    assert membership.status_code == 201
    membership_id = membership.json()["id"]

    transferred = client.put(
        f"/v1/memberships/{membership_id}/unit",
        headers=_headers(tenant_id),
        json={"to_org_unit_id": unit_b_id, "expected_version": 1},
    )
    assert transferred.status_code == 200
    assert transferred.json()["ok"] is True

    after_transfer = client.get(
        "/v1/memberships",
        headers=_headers(tenant_id),
        params={"subject_id": str(member_subject)},
    ).json()[0]
    assert after_transfer["org_unit_id"] == unit_b_id
    assert after_transfer["version"] == 2

    ended = client.request(
        "DELETE",
        f"/v1/memberships/{membership_id}",
        headers=_headers(tenant_id),
        json={"reason": "exit", "expected_version": 2},
    )
    assert ended.status_code == 200
    assert ended.json()["ok"] is True
