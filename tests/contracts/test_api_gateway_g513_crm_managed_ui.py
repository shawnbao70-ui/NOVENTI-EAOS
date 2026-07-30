"""PHX-G513 CRM Customer and Contact managed Terminal UI contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import CONTACT_RESOURCE, CUSTOMER_RESOURCE, CRMService

ROOT = Path(__file__).resolve().parents[2]
SUBJECT = uuid4()
TENANT = uuid4()


class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _context() -> ExecutionContext:
    return ExecutionContext(
        subject_id=SUBJECT,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id="corr-g513-grant",
        request_time=ExecutionContext.utc_now(),
    )


def _headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(SUBJECT),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": "corr-g513-http",
    }


def _client(*, grant: bool = True) -> TestClient:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={SUBJECT},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    if grant:
        for resource_type in (CUSTOMER_RESOURCE, CONTACT_RESOURCE):
            assert permission.grant(
                _context(),
                principal_subject_id=SUBJECT,
                resource_type=resource_type,
                actions={"create", "read", "update", "archive"},
                scope_level=ScopeLevel.TENANT,
            ).ok
    crm = CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=TENANT),
        audit_log=audit,
    )
    return TestClient(create_app(crm_service=crm, permission_service=permission))


def test_g513_effective_permissions_drive_fail_closed_write_visibility() -> None:
    allowed = _client().get(
        f"/v1/permission/principals/{SUBJECT}/effective-permissions",
        headers=_headers(),
    )
    assert allowed.status_code == 200
    grants = allowed.json()
    assert {item["resource_type"] for item in grants} == {
        CUSTOMER_RESOURCE,
        CONTACT_RESOURCE,
    }
    assert all(item["effect"] == "allow" for item in grants)
    assert all({"create", "read", "update", "archive"} <= set(item["actions"]) for item in grants)

    denied = _client(grant=False).get(
        f"/v1/permission/principals/{SUBJECT}/effective-permissions",
        headers=_headers(),
    )
    assert denied.status_code == 200
    assert denied.json() == []


def test_g513_customer_writes_use_versions_and_never_overwrite_conflicts() -> None:
    client = _client()
    created = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": "C-G513", "display_name": "Initial"},
    )
    assert created.status_code == 201
    customer = created.json()["data"]

    updated = client.patch(
        f"/v1/crm/customers/{customer['id']}",
        headers=_headers(),
        json={
            "display_name": "Current",
            "owner_subject_id": None,
            "expected_version": customer["version"],
        },
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["version"] == customer["version"] + 1

    stale = client.patch(
        f"/v1/crm/customers/{customer['id']}",
        headers=_headers(),
        json={
            "display_name": "Stale overwrite",
            "owner_subject_id": None,
            "expected_version": customer["version"],
        },
    )
    assert stale.status_code == 409
    detail = client.get(
        f"/v1/crm/customers/{customer['id']}",
        headers=_headers(),
    )
    assert detail.json()["data"]["display_name"] == "Current"


def test_g513_contact_writes_and_archive_are_governed() -> None:
    client = _client()
    customer = client.post(
        "/v1/crm/customers",
        headers=_headers(),
        json={"code": "C-G513-CONTACT", "display_name": "Contact Parent"},
    ).json()["data"]
    created = client.post(
        f"/v1/crm/customers/{customer['id']}/contacts",
        headers=_headers(),
        json={
            "display_name": "Managed Contact",
            "title": None,
            "email": None,
            "phone": None,
        },
    )
    assert created.status_code == 201
    contact = created.json()["data"]

    updated = client.patch(
        f"/v1/crm/customers/{customer['id']}/contacts/{contact['id']}",
        headers=_headers(),
        json={
            "display_name": "Managed Contact",
            "title": "Buyer",
            "email": "buyer@example.test",
            "phone": None,
            "expected_version": contact["version"],
        },
    )
    assert updated.status_code == 200
    current = updated.json()["data"]

    archived = client.post(
        f"/v1/crm/customers/{customer['id']}/contacts/{contact['id']}/archive",
        headers=_headers(),
        json={"reason": "Duplicate contact", "expected_version": current["version"]},
    )
    assert archived.status_code == 200
    assert archived.json()["data"]["status"] == "archived"


def test_g513_terminal_exposes_only_authorized_managed_actions() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    app = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")

    for control in (
        "btnCrmNewCustomer",
        "btnCrmEditCustomer",
        "btnCrmArchiveCustomer",
        "btnCrmNewContact",
        "btnCrmEditContact",
        "btnCrmArchiveContact",
        "crmArchiveConfirmed",
    ):
        assert f'id="{control}"' in html
    assert "effectivePermissions" in app
    assert "loadCrmPermissions" in app
    assert "crmCan(" in app
    assert "expected_version" in app
    assert "Version conflict" in app
    assert "No automatic retry was attempted" in app
    assert "tenant_id" not in app[app.index("async function submitCrmCustomer") : app.index("async function loadDemoBootstrap")]
    assert "btnCrmImport" not in html
    assert "btnCrmMerge" not in html


def test_g513_governance_authorizes_frontend_only() -> None:
    authorization = (
        ROOT
        / "docs"
        / "project"
        / "CRM_CUSTOMER_CONTACT_MANAGED_UI_CODING_AUTHORIZATION_SUMMARY.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT
        / "docs"
        / "project"
        / "CRM_CUSTOMER_CONTACT_MANAGED_UI_ACCEPTANCE.md"
    ).read_text(encoding="utf-8")
    acceptance = (
        ROOT / "docs" / "project" / "CRM_CUSTOMER_CONTACT_UI_G513_ACCEPTANCE.md"
    ).read_text(encoding="utf-8")
    roadmap = (
        ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"
    ).read_text(encoding="utf-8")
    manifest = (
        ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"
    ).read_text(encoding="utf-8")

    assert "PHX-G513" in authorization
    assert "Coding Authorization: **Approved**" in authorization
    assert "Backend/Database/Alembic authorization: **None**" in authorization
    assert "Coding Authorization: None" in gate
    assert "12 passed" in acceptance
    assert "Production Authorization: **None**" in acceptance
    assert "TRACK-G513 COMPLETE" in roadmap
    assert "FINAL STOP TRACK-G513" in roadmap
    assert "PHX-G513" in manifest
    assert "crm_customer_contact_managed_terminal_ui" in manifest
