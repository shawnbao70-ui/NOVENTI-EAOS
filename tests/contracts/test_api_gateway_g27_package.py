"""PHX-G27 Gateway Package Platform HTTP surface contracts."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from eaos_platform.package.service import PackageService
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType

ADMIN = uuid4()
OPERATOR = uuid4()
TENANT = uuid4()
CORR = str(uuid4())
ROOT = Path(__file__).resolve().parents[2]
SAMPLE_MANIFEST = ROOT / "packages" / "sample_ops" / "manifest.json"


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _headers(subject_id: UUID = OPERATOR, **extra: str) -> dict[str, str]:
    base = {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }
    base.update(extra)
    return base


def _admin_ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=ADMIN,
        subject_type=SubjectType.HUMAN,
        tenant_id=TENANT,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


@pytest.fixture()
def gateway() -> tuple[TestClient, PermissionService]:
    permission = PermissionService(
        grant_administrators={ADMIN},
        principal_eligibility=_AllowAll(),
    )
    packages = PackageService(permission)
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
        create_app(permission_service=permission, package_service=packages)
    )
    return client, permission


def _sample_payload() -> dict:
    return json.loads(SAMPLE_MANIFEST.read_text(encoding="utf-8"))


def test_package_requires_trusted_headers(gateway: tuple) -> None:
    client, _ = gateway
    response = client.get("/v1/packages/surfaces")
    assert response.status_code == 401


def test_register_publish_install_surface_resolve_disable(gateway: tuple) -> None:
    client, _ = gateway
    payload = _sample_payload()
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

    surfaces = client.get("/v1/packages/surfaces", headers=_headers())
    assert surfaces.status_code == 200
    assert surfaces.json()["data"][0]["surface_key"] == "ops.workbench"

    resolved = client.post(
        "/v1/packages/actions/resolve",
        headers=_headers(),
        json={"action_key": "ops.brief.compose"},
    )
    assert resolved.status_code == 200
    body = resolved.json()
    assert body["package_key"] == payload["package_key"]
    assert body["installation_id"] == installation_id
    assert body["source"] == "package_manifest"

    disabled = client.post(
        f"/v1/packages/installations/{installation_id}/disable",
        headers=_headers(),
    )
    assert disabled.status_code == 200
    assert disabled.json()["data"] is True

    after = client.get("/v1/packages/surfaces", headers=_headers())
    assert after.json()["data"] == []

    denied = client.post(
        "/v1/packages/actions/resolve",
        headers=_headers(),
        json={"action_key": "ops.brief.compose"},
    )
    assert denied.status_code == 400
    assert denied.json()["detail"]["code"] == "PACKAGE_ACTION_UNDECLARED"


def test_ambiguous_action_resolve_is_conflict(gateway: tuple) -> None:
    client, _ = gateway
    for package_key in ("noventi.sample.ops.a", "noventi.sample.ops.b"):
        payload = _sample_payload()
        payload["package_key"] = package_key
        registered = client.post(
            "/v1/packages/manifests",
            headers=_headers(),
            json=payload,
        )
        assert registered.status_code == 201
        manifest_id = registered.json()["data"]
        assert client.post(
            f"/v1/packages/manifests/{manifest_id}/publish",
            headers=_headers(),
        ).status_code == 200
        assert client.post(
            "/v1/packages/installations",
            headers=_headers(),
            json={"manifest_id": manifest_id},
        ).status_code == 201

    ambiguous = client.post(
        "/v1/packages/actions/resolve",
        headers=_headers(),
        json={"action_key": "ops.brief.compose"},
    )
    assert ambiguous.status_code == 409
    detail = ambiguous.json()["detail"]
    assert detail["code"] == "PACKAGE_ACTION_AMBIGUOUS"
    assert "package_keys" in (detail.get("details") or {})


def test_kernel_fork_denied_via_http(gateway: tuple) -> None:
    client, _ = gateway
    response = client.post(
        "/v1/packages/manifests",
        headers=_headers(),
        json={
            "package_key": "kernel.identity.fork",
            "version": "1.0.0",
            "package_type": "business",
            "surfaces": [{"surface_key": "x", "title": "X"}],
            "actions": [
                {
                    "action_key": "x.run",
                    "resource_type": "pkg.x",
                    "permission_action": "run",
                }
            ],
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "PACKAGE_KERNEL_FORK_DENIED"


def test_body_cannot_elevate_context(gateway: tuple) -> None:
    client, _ = gateway
    response = client.post(
        "/v1/packages/manifests",
        headers=_headers(),
        json={
            "package_key": "noventi.demo",
            "version": "1.0.0",
            "package_type": "business",
            "tenant_id": str(uuid4()),
            "platform_scope": True,
        },
    )
    assert response.status_code == 422
    locs = [tuple(err.get("loc", ())) for err in response.json()["detail"]]
    assert any("tenant_id" in loc for loc in locs)
