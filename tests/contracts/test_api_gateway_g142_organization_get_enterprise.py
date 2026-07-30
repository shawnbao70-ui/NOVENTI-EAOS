"""PHX-G142 Organization Get Enterprise thin probe contracts."""

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


def test_terminal_exposes_organization_get_enterprise_control() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminOrganizationGetEnterprise"' in html
    assert "Organization get enterprise 薄探针（G142" in html
    assert "Organization Terminal 运维面齐" in html
    assert "adminGetOrganizationEnterprise" in js
    assert "organizationEnterprise" in js
    start = js.index("async function adminGetOrganizationEnterprise")
    end = js.index("async function adminUpsertOrganizationUnit")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk


def test_organization_get_enterprise_probe_api() -> None:
    service = OrganizationService(
        platform_governors={GOVERNOR},
        membership_eligibility=_AllowAllMembershipEligibility(),
    )
    created = service.create_tenant(_platform_ctx(), legal_name=f"G142-{uuid4()}")
    assert created.ok and created.data is not None
    tenant_id = created.data
    client = TestClient(create_app(organization_service=service))

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Get enterprise" in page.text

    enterprise = client.post(
        "/v1/enterprises",
        headers=_headers(tenant_id),
        json={"legal_name": f"G142-Ops-{uuid4()}"},
    )
    assert enterprise.status_code == 201
    enterprise_id = enterprise.json()["id"]

    fetched = client.get(
        f"/v1/enterprises/{enterprise_id}",
        headers=_headers(tenant_id),
    )
    assert fetched.status_code == 200
    assert fetched.json()["id"] == enterprise_id
    assert fetched.json()["status"] == "active"

    status = client.get("/v1/organization/status")
    assert "enterprise_get" in status.json()["data"]["supported_surfaces"]
