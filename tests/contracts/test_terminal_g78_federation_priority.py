"""PHX-G78 Federation Priority Terminal Ops contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings, clear_jwks_cache
from api.gateway.context import configure_jwt_settings
from api.gateway.tenant_idp_federation import (
    clear_tenant_idp_federation,
    configure_tenant_idp_federation,
)

ROOT = Path(__file__).resolve().parents[2]
UI_ROOT = ROOT / "smart_terminal" / "ui"
INDEX = UI_ROOT / "index.html"
APP_JS = UI_ROOT / "app.js"

GOVERNOR = uuid4()
TENANT = uuid4()
CORR = str(uuid4())
ISS = "https://g78-fed-priority.example/eaos"


@pytest.fixture(autouse=True)
def _reset() -> None:
    configure_tenant_idp_federation(store="memory")
    clear_tenant_idp_federation()
    clear_jwks_cache()
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience=None,
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    yield
    clear_tenant_idp_federation()
    configure_tenant_idp_federation(store="memory")


def _platform_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(GOVERNOR),
        "X-EAOS-Subject-Type": "human",
        "X-Correlation-Id": CORR,
    }


def test_admin_ui_exposes_federation_priority_controls() -> None:
    html = INDEX.read_text(encoding="utf-8")
    js = APP_JS.read_text(encoding="utf-8")
    assert 'id="btnAdminFedPriority"' in html
    assert 'id="fedPriority"' in html
    assert "Set federation priority" in html
    assert "/priority" in js
    assert "adminSetFederationPriority" in js
    assert "fedPriority" in js
    assert "platform: true" in js or "platform:true" in js.replace(" ", "")


def test_admin_set_federation_priority_uses_platform_context() -> None:
    client = TestClient(create_app())
    created = client.post(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
        json={"issuer": ISS},
    )
    assert created.status_code == 201
    binding_id = created.json()["data"]["id"]
    updated = client.post(
        f"/v1/platform/idp/federation/bindings/{binding_id}/priority",
        headers=_platform_headers(),
        json={"priority": 7},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["priority"] == 7
    page = client.get("/terminal/")
    assert "Set federation priority" in page.text
    script = client.get("/terminal/app.js")
    assert "adminSetFederationPriority" in script.text
