"""PHX-G108 Package Status / Manifest / Surfaces Thin Probe contracts."""

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


def test_terminal_exposes_package_probe_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminPackageStatus"' in html
    assert 'id="btnAdminPackageRegisterManifest"' in html
    assert 'id="btnAdminPackageGetManifest"' in html
    assert 'id="btnAdminPackageListSurfaces"' in html
    assert 'id="packageManifestId"' in html
    assert 'id="packageManifestJson"' in html
    assert "Package 状态/manifest/surfaces 薄探针（G108" in html
    assert 'packageStatus: "/v1/packages/status"' in js
    assert 'packageManifests: "/v1/packages/manifests"' in js
    assert "adminRegisterPackageManifest" in js
    assert "adminGetPackageManifest" in js
    assert "adminListPackageSurfaces" in js
    start = js.index("async function adminRegisterPackageManifest")
    end = js.index("async function adminPublishPackageManifest")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "/publish" not in chunk
    assert "/installations" not in chunk
    assert "/actions/resolve" not in chunk


def test_package_status_and_probe_api() -> None:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    for resource_type, actions in (
        ("package_manifest", {"register", "read"}),
        ("package_surface", {"read"}),
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

    status = client.get("/v1/packages/status")
    assert status.status_code == 200
    data = status.json()["data"]
    assert data["writable"] is False
    assert "manifest_register" in data["supported_surfaces"]
    assert "surface_list" in data["supported_surfaces"]

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Package status" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminRegisterPackageManifest" in script.text

    payload = json.loads(SAMPLE_MANIFEST.read_text(encoding="utf-8"))
    registered = client.post(
        "/v1/packages/manifests",
        headers=_headers(),
        json=payload,
    )
    assert registered.status_code == 201
    manifest_id = registered.json()["data"]

    fetched = client.get(
        f"/v1/packages/manifests/{manifest_id}",
        headers=_headers(),
    )
    assert fetched.status_code == 200
    assert fetched.json()["package_key"] == payload["package_key"]
    assert fetched.json()["status"] == "draft"

    surfaces = client.get("/v1/packages/surfaces", headers=_headers())
    assert surfaces.status_code == 200
    assert "data" in surfaces.json()
