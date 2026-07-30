"""PHX-G95 Terminal Effective Permissions Thin Probe contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from kernel.permission.service import PermissionService

ROOT = Path(__file__).resolve().parents[2]
ADMIN = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id, tenant_id) -> bool:  # type: ignore[no-untyped-def]
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


def _tenant_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(ADMIN),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }


def test_terminal_exposes_effective_permissions_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminEffectivePerms"' in html
    assert 'id="effectivePrincipalId"' in html
    assert "List effective permissions" in html
    assert "effective-permissions 只读探针（G95）" in html
    assert "effectivePermissions" in js
    assert "adminListEffectivePermissions" in js
    assert "/v1/permission/principals/" in js
    assert "effective-permissions" in js
    start = js.index("async function adminListEffectivePermissions")
    end = js.index("async function adminCreatePermissionPolicy")
    chunk = js[start:end]
    assert "principal_id" not in chunk
    assert "tenant_id" not in chunk
    assert "adminCreatePermissionGrant" not in chunk


def test_gateway_serves_effective_permissions_ui_and_api() -> None:
    service = PermissionService(
        grant_administrators={ADMIN},
        decision_auditors={ADMIN},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    client = TestClient(create_app(permission_service=service))
    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "List effective permissions" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminListEffectivePermissions" in script.text

    listed = client.get(
        f"/v1/permission/principals/{ADMIN}/effective-permissions",
        headers=_tenant_headers(),
    )
    assert listed.status_code == 200
    assert isinstance(listed.json(), list)
