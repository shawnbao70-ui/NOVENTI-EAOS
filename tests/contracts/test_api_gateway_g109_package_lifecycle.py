"""PHX-G109 Package Publish / Install / Disable / Resolve Thin Probe contracts."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from eaos_platform.package.service import PackageService
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType

ROOT = Path(__file__).resolve().parents[2]
SAMPLE_MANIFEST = ROOT / "packages" / "sample_ops" / "manifest.json"
ADMIN = uuid4()
OPERATOR = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


class _AllowAll:
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


def _headers(subject_id: UUID = OPERATOR) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }


def _admin_ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=CORR,
        request_time=ExecutionContext.utc_now(),
    )


def test_terminal_exposes_package_lifecycle_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminPackagePublishManifest"' in html
    assert 'id="btnAdminPackageInstall"' in html
    assert 'id="btnAdminPackageDisableInstallation"' in html
    assert 'id="btnAdminPackageResolveAction"' in html
    assert 'id="packageInstallationId"' in html
    assert 'id="packageActionKey"' in html
    assert "Package publish/install/disable/resolve" in html
    assert "Package Terminal 运维面齐" in html
    assert "packageManifestPublish" in js
    assert "packageInstallations" in js
    assert "packageInstallationDisable" in js
    assert "packageActionResolve" in js
    assert "adminPublishPackageManifest" in js
    assert "adminInstallPackage" in js
    assert "adminDisablePackageInstallation" in js
    assert "adminResolvePackageAction" in js
    start = js.index("async function adminPublishPackageManifest")
    end = js.index("async function adminUpsertKnowledgeEntity")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk


def test_gateway_serves_package_lifecycle_ui_and_api() -> None:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    for resource_type, actions in (
        ("package_manifest", {"register", "publish", "read"}),
        ("package_installation", {"install", "disable", "read"}),
        ("package_surface", {"read"}),
        ("package_action", {"resolve"}),
        ("pkg.ops.brief", {"compose", "publish"}),
    ):
        assert permission.grant(
            _admin_ctx(),
            principal_subject_id=OPERATOR,
            resource_type=resource_type,
            actions=actions,
        ).ok
    client = TestClient(
        create_app(
            permission_service=permission,
            package_service=PackageService(permission),
        )
    )

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Publish package manifest" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminPublishPackageManifest" in script.text

    payload = json.loads(SAMPLE_MANIFEST.read_text(encoding="utf-8"))
    registered = client.post(
        "/v1/packages/manifests",
        headers=_headers(),
        json=payload,
    )
    assert registered.status_code == 201
    manifest_id = registered.json()["data"]

    published = client.post(
        f"/v1/packages/manifests/{manifest_id}/publish",
        headers=_headers(),
    )
    assert published.status_code == 200
    assert published.json()["data"] is True

    installed = client.post(
        "/v1/packages/installations",
        headers=_headers(),
        json={"manifest_id": manifest_id},
    )
    assert installed.status_code == 201
    installation_id = installed.json()["data"]

    resolved = client.post(
        "/v1/packages/actions/resolve",
        headers=_headers(),
        json={"action_key": "ops.brief.compose"},
    )
    assert resolved.status_code == 200
    assert resolved.json()["installation_id"] == installation_id

    disabled = client.post(
        f"/v1/packages/installations/{installation_id}/disable",
        headers=_headers(),
    )
    assert disabled.status_code == 200
    assert disabled.json()["data"] is True
