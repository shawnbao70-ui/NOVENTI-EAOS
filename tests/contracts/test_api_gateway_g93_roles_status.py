"""PHX-G93 Permission Roles Status Observability contracts."""

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
from api.gateway.role_catalog_store import (
    clear_role_catalog_store,
    configure_role_catalog_store,
)
from kernel.permission.role_grant_map import (
    configure_permission_role_grant_map,
    reset_permission_role_grant_map,
)
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
    for name in (
        "EAOS_ROLE_CATALOG",
        "EAOS_ROLE_CATALOG_STORE",
        "EAOS_PERMISSION_ROLE_GRANT_MAP",
    ):
        monkeypatch.delenv(name, raising=False)
    configure_role_catalog_store(store="memory")
    clear_role_catalog_store()
    reset_role_catalog()
    reset_permission_role_grant_map()
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
    clear_role_catalog_store()
    configure_role_catalog_store(store="memory")
    reset_role_catalog()
    reset_permission_role_grant_map()


def _tenant_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(ADMIN),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }


def _client() -> TestClient:
    service = PermissionService(
        grant_administrators={ADMIN},
        decision_auditors={ADMIN},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    return TestClient(create_app(permission_service=service))


def test_terminal_exposes_roles_status_control() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminRolesStatus"' in html
    assert "Roles status" in html
    assert "角色状态探针（G93）" in html
    assert 'rolesStatus: "/v1/permission/roles/status"' in js
    assert "adminRolesStatus" in js


def test_roles_status_empty_defaults() -> None:
    client = _client()
    response = client.get("/v1/permission/roles/status", headers=_tenant_headers())
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["catalog_store"] == "process_memory"
    assert data["catalog_enabled"] is False
    assert data["role_count"] == 0
    assert data["grant_map_enabled"] is False
    assert data["grant_map_role_count"] == 0
    assert data["source_counts"] == {
        "catalog": 0,
        "oidc_map": 0,
        "grant_map": 0,
    }


def test_roles_status_aggregates_and_requires_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EAOS_ROLE_CATALOG", "viewer,operator")
    reset_role_catalog()
    configure_permission_role_grant_map(
        {
            "operator": frozenset({("document", "read")}),
        }
    )
    client = _client()
    denied = client.get("/v1/permission/roles/status")
    assert denied.status_code == 401

    response = client.get("/v1/permission/roles/status", headers=_tenant_headers())
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["catalog_enabled"] is True
    assert data["role_count"] == 2
    assert data["grant_map_enabled"] is True
    assert data["grant_map_role_count"] == 1
    assert data["source_counts"]["catalog"] == 2
    assert data["source_counts"]["grant_map"] == 1
    assert "grants" not in data
    assert "EAOS_PERMISSION_ROLE_GRANT_MAP" not in response.text
    assert "resource_type" not in response.text

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Roles status" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "rolesStatus" in script.text
