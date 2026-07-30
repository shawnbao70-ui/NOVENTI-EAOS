"""PHX-G55 multi-IdP read-only status UI contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtIssuerBinding, JwtSettings
from api.gateway.context import configure_jwt_settings
from api.gateway.oidc import OidcSettings, clear_oidc_discovery_cache, configure_oidc

ROOT = Path(__file__).resolve().parents[2]
UI_ROOT = ROOT / "smart_terminal" / "ui"
APP_JS = UI_ROOT / "app.js"
INDEX = UI_ROOT / "index.html"
SECRET = "eaos-idp-status-secret"
ISS_A = "https://idp-a.example/eaos"
ISS_B = "https://idp-b.example/eaos"


@pytest.fixture(autouse=True)
def _reset() -> None:
    clear_oidc_discovery_cache()
    configure_jwt_settings(
        JwtSettings(
            secret=SECRET,
            issuer="https://eaos.example/issuer",
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
            issuers=(
                JwtIssuerBinding(issuer=ISS_A, jwks_url="https://idp-a.example/jwks"),
                JwtIssuerBinding(
                    issuer=ISS_B,
                    jwks_json='{"keys":[{"kty":"RSA","kid":"x","n":"ab","e":"AQAB"}]}',
                ),
            ),
        )
    )
    configure_oidc(
        OidcSettings(
            issuer="https://idp.example",
            client_id="eaos-client",
            client_secret="must-not-leak",
            redirect_uri="http://127.0.0.1:8000/v1/auth/oidc/callback",
            authorization_endpoint="https://idp.example/authorize",
            token_endpoint="https://idp.example/token",
            scopes="openid",
            default_tenant_id=str(uuid4()),
            enabled=True,
            discovery=False,
            jwks_wire=False,
        )
    )
    yield
    clear_oidc_discovery_cache()
    configure_oidc(
        OidcSettings(
            issuer=None,
            client_id=None,
            client_secret=None,
            redirect_uri=None,
            authorization_endpoint=None,
            token_endpoint=None,
            scopes="openid",
            default_tenant_id=None,
            enabled=False,
        )
    )
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience=None,
            allow_dev_headers=True,
            require_jwt=False,
        )
    )


def test_idp_status_aggregates_redacted_view() -> None:
    client = TestClient(create_app())
    response = client.get("/v1/auth/idp/status")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["writable"] is False
    assert data["config_source"] == "environment+registry"
    assert data["registry"]["writable"] is True
    assert data["registry"]["store"] == "process_memory"
    assert data["oidc"]["enabled"] is True
    assert data["oidc"]["issuer"] == "https://idp.example"
    assert data["jwt"]["multi_issuer"] is True
    assert data["jwt"]["has_secret"] is True
    assert data["jwt"]["issuers"] == [
        {
            "issuer": ISS_A,
            "jwks_url": "https://idp-a.example/jwks",
            "has_jwks_json": False,
        },
        {
            "issuer": ISS_B,
            "jwks_url": None,
            "has_jwks_json": True,
        },
    ]
    raw = response.text
    assert "must-not-leak" not in raw
    assert SECRET not in raw
    assert '"kty"' not in raw
    assert "AQAB" not in raw


def test_admin_ui_exposes_idp_probe() -> None:
    html = INDEX.read_text(encoding="utf-8")
    js = APP_JS.read_text(encoding="utf-8")
    assert 'id="btnAdminIdp"' in html
    assert "IdP / JWT status" in html
    assert "/v1/auth/idp/status" in js
    assert "btnAdminIdp" in js


def test_gateway_serves_admin_idp_probe_assets() -> None:
    client = TestClient(create_app())
    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "IdP / JWT status" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "idpStatus" in script.text
