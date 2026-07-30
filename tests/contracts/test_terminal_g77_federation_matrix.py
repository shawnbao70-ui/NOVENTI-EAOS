"""PHX-G77 Federation Matrix Terminal Ops contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings, clear_jwks_cache
from api.gateway.context import configure_jwt_settings
from api.gateway.idp_registry import clear_idp_registry, configure_idp_registry
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
ISS = "https://g77-fed-matrix.example/eaos"


@pytest.fixture(autouse=True)
def _reset() -> None:
    configure_idp_registry(store="memory")
    clear_idp_registry()
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
    clear_idp_registry()
    configure_tenant_idp_federation(store="memory")
    configure_idp_registry(store="memory")


def _platform_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(GOVERNOR),
        "X-EAOS-Subject-Type": "human",
        "X-Correlation-Id": CORR,
    }


def test_admin_ui_exposes_federation_matrix_controls() -> None:
    html = INDEX.read_text(encoding="utf-8")
    js = APP_JS.read_text(encoding="utf-8")
    assert 'id="btnAdminFedMatrix"' in html
    assert "Federation matrix" in html
    assert "/v1/platform/idp/federation/matrix" in js
    assert "adminFederationMatrix" in js
    assert "fedMatrix" in js
    assert "platform: true" in js or "platform:true" in js.replace(" ", "")
    assert "FORBIDDEN_BODY_KEYS" in js


def test_gateway_serves_federation_matrix_assets() -> None:
    client = TestClient(create_app())
    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Federation matrix" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "fedMatrix" in script.text
    assert "adminFederationMatrix" in script.text


def test_platform_federation_matrix_round_trip_matches_ui_contract() -> None:
    client = TestClient(create_app())
    created = client.post(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
        json={"issuer": ISS},
    )
    assert created.status_code == 201

    matrix = client.get(
        "/v1/platform/idp/federation/matrix",
        headers=_platform_headers(),
    )
    assert matrix.status_code == 200
    cells = matrix.json()["data"]["cells"]
    assert any(
        c["bound_tenant_id"] == str(TENANT) and c["issuer"] == ISS and c["state"] == "active"
        for c in cells
    )


def test_admin_ui_does_not_embed_secret_fields() -> None:
    html = INDEX.read_text(encoding="utf-8")
    js = APP_JS.read_text(encoding="utf-8")
    assert "EAOS_JWT_SECRET" not in html
    assert "EAOS_JWT_SECRET" not in js
    assert "client_secret" not in js.casefold()
