"""PHX-G69 Tenant IdP Federation Terminal Ops contracts."""

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
ISS = "https://g69-fed-idp.example/eaos"


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


def test_admin_ui_exposes_federation_ops_controls() -> None:
    html = INDEX.read_text(encoding="utf-8")
    js = APP_JS.read_text(encoding="utf-8")
    for needle in (
        'id="btnAdminFedList"',
        'id="btnAdminFedBind"',
        'id="btnAdminFedUnbind"',
        'id="fedTenantId"',
        'id="fedIssuer"',
        'id="fedBindingId"',
        "List federation bindings",
        "Bind federation issuer",
        "Unbind federation",
    ):
        assert needle in html, needle
    assert "/v1/platform/idp/federation/tenants/" in js
    assert "/unbind" in js
    assert "platform: true" in js or "platform:true" in js.replace(" ", "")
    assert "FORBIDDEN_BODY_KEYS" in js
    assert "adminBindFederationIssuer" in js
    assert "fedBindings" in js


def test_gateway_serves_federation_ops_assets() -> None:
    client = TestClient(create_app())
    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "List federation bindings" in page.text
    assert "Bind federation issuer" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "fedBindings" in script.text
    assert "adminListFederationBindings" in script.text


def test_platform_federation_round_trip_matches_ui_contract() -> None:
    client = TestClient(create_app())
    created = client.post(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
        json={"issuer": ISS},
    )
    assert created.status_code == 201
    binding_id = created.json()["data"]["id"]
    assert created.json()["data"]["bound_tenant_id"] == str(TENANT)
    assert "tenant_id" not in created.json()["data"]

    listed = client.get(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
    )
    assert listed.status_code == 200
    assert listed.json()["meta"]["count"] == 1

    unbound = client.post(
        f"/v1/platform/idp/federation/bindings/{binding_id}/unbind",
        headers=_platform_headers(),
        json={},
    )
    assert unbound.status_code == 200
    assert unbound.json()["data"]["status"] == "disabled"

    elevated = client.post(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
        json={"issuer": "https://evil.example", "tenant_id": str(uuid4())},
    )
    assert elevated.status_code == 422
    locs = [tuple(err.get("loc", ())) for err in elevated.json()["detail"]]
    assert any("tenant_id" in loc for loc in locs)


def test_admin_ui_does_not_embed_secret_fields() -> None:
    html = INDEX.read_text(encoding="utf-8")
    js = APP_JS.read_text(encoding="utf-8")
    assert "EAOS_JWT_SECRET" not in html
    assert "EAOS_JWT_SECRET" not in js
    assert "client_secret" not in js.casefold()
    assert "fedTenantId" in js
