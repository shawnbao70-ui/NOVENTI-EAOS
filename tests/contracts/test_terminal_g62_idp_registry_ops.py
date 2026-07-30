"""PHX-G62 Platform IdP Registry Terminal Ops contracts."""

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

ROOT = Path(__file__).resolve().parents[2]
UI_ROOT = ROOT / "smart_terminal" / "ui"
INDEX = UI_ROOT / "index.html"
APP_JS = UI_ROOT / "app.js"

GOVERNOR = uuid4()
CORR = str(uuid4())


@pytest.fixture(autouse=True)
def _reset() -> None:
    configure_idp_registry(store="memory")
    clear_idp_registry()
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
    clear_idp_registry()


def _platform_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(GOVERNOR),
        "X-EAOS-Subject-Type": "human",
        "X-Correlation-Id": CORR,
    }


def test_admin_ui_exposes_idp_registry_ops_controls() -> None:
    html = INDEX.read_text(encoding="utf-8")
    js = APP_JS.read_text(encoding="utf-8")
    for needle in (
        'id="btnAdminIdpList"',
        'id="btnAdminIdpRegister"',
        'id="btnAdminIdpDisable"',
        'id="btnAdminIdpDiscoverySync"',
        'id="idpIssuer"',
        'id="idpJwksUrl"',
        'id="idpIssuerId"',
        "List IdP issuers",
        "Register IdP issuer",
    ):
        assert needle in html, needle
    assert "/v1/platform/idp/issuers" in js
    assert "/v1/platform/idp/discovery/sync" in js
    assert "platform: true" in js or "platform:true" in js.replace(" ", "")
    assert "tenant_id" in js  # still sanitized from bodies
    assert "FORBIDDEN_BODY_KEYS" in js


def test_gateway_serves_idp_registry_ops_assets() -> None:
    client = TestClient(create_app())
    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "List IdP issuers" in page.text
    assert "Register IdP issuer" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "idpIssuers" in script.text
    assert "adminRegisterIdpIssuer" in script.text


def test_platform_registry_round_trip_matches_ui_contract() -> None:
    """UI calls the same platform APIs; keep server contract green for Admin ops."""

    client = TestClient(create_app())
    created = client.post(
        "/v1/platform/idp/issuers",
        headers=_platform_headers(),
        json={
            "issuer": "https://g62-idp.example/eaos",
            "jwks_url": "https://g62-idp.example/jwks",
        },
    )
    assert created.status_code == 201
    issuer_id = created.json()["data"]["id"]
    assert created.json()["data"]["has_jwks_json"] is False

    listed = client.get("/v1/platform/idp/issuers", headers=_platform_headers())
    assert listed.status_code == 200
    assert listed.json()["meta"]["count"] >= 1

    disabled = client.post(
        f"/v1/platform/idp/issuers/{issuer_id}/disable",
        headers=_platform_headers(),
        json={},
    )
    assert disabled.status_code == 200
    assert disabled.json()["data"]["status"] == "disabled"

    # Body elevation still rejected
    elevated = client.post(
        "/v1/platform/idp/issuers",
        headers=_platform_headers(),
        json={
            "issuer": "https://evil.example",
            "jwks_url": "https://evil.example/jwks",
            "tenant_id": str(uuid4()),
        },
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
    assert "jwks_json" in js  # optional register input only
