"""PHX-G91 Terminal Platform Roles Admin Thin Ops contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from api.gateway.role_catalog_store import (
    clear_role_catalog_store,
    configure_role_catalog_store,
)

ROOT = Path(__file__).resolve().parents[2]
GOVERNOR = uuid4()
CORR = str(uuid4())


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EAOS_ROLE_CATALOG_STORE", raising=False)
    configure_role_catalog_store(store="memory")
    clear_role_catalog_store()
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


def _platform_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(GOVERNOR),
        "X-EAOS-Subject-Type": "human",
        "X-Correlation-Id": CORR,
    }


def test_terminal_exposes_declared_roles_admin_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminRoleList"' in html
    assert 'id="btnAdminRoleUpsert"' in html
    assert 'id="btnAdminRoleDisable"' in html
    assert 'id="roleCatalogName"' in html
    assert 'id="roleCatalogId"' in html
    assert "/v1/platform/roles" in js
    assert "adminListDeclaredRoles" in js
    assert "adminUpsertDeclaredRole" in js
    assert "adminDisableDeclaredRole" in js
    assert "声明角色目录（G91）" in html


def test_gateway_serves_roles_admin_ui_and_platform_api() -> None:
    client = TestClient(create_app())
    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "List declared roles" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "platformRoles" in script.text

    created = client.post(
        "/v1/platform/roles",
        headers=_platform_headers(),
        json={"name": "operator"},
    )
    assert created.status_code == 201
    role_id = created.json()["data"]["id"]
    listed = client.get("/v1/platform/roles", headers=_platform_headers())
    assert listed.status_code == 200
    assert listed.json()["meta"]["count"] >= 1
    disabled = client.post(
        f"/v1/platform/roles/{role_id}/disable",
        headers=_platform_headers(),
        json={},
    )
    assert disabled.status_code == 200
    assert disabled.json()["data"]["status"] == "disabled"
