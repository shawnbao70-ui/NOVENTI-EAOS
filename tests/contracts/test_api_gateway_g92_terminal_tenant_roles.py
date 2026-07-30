"""PHX-G92 Terminal Tenant Roles Catalog Read contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from api.gateway.role_catalog import reset_role_catalog
from kernel.permission.service import PermissionService

ROOT = Path(__file__).resolve().parents[2]
ADMIN = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id, tenant_id) -> bool:  # type: ignore[no-untyped-def]
        return True


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EAOS_ROLE_CATALOG", raising=False)
    reset_role_catalog()
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
    reset_role_catalog()


def _tenant_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(ADMIN),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }


def test_terminal_exposes_tenant_roles_catalog_control() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminTenantRoles"' in html
    assert "List tenant roles catalog" in html
    assert "租户角色目录只读（G92）" in html
    assert 'tenantRoles: "/v1/permission/roles"' in js
    assert "adminListTenantRolesCatalog" in js


def test_gateway_serves_tenant_roles_ui_and_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EAOS_ROLE_CATALOG", "viewer,operator")
    reset_role_catalog()
    service = PermissionService(
        grant_administrators={ADMIN},
        decision_auditors={ADMIN},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    client = TestClient(create_app(permission_service=service))
    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "List tenant roles catalog" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "tenantRoles" in script.text
    assert "adminListTenantRolesCatalog" in script.text

    listed = client.get("/v1/permission/roles", headers=_tenant_headers())
    assert listed.status_code == 200
    body = listed.json()
    names = {row["name"] for row in body["roles"]}
    assert "viewer" in names
    assert "operator" in names
