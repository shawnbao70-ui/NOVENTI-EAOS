"""PHX-G87 OIDC Authorize ACR/Prompt Step-Up Gate contracts."""

from __future__ import annotations

from uuid import uuid4
from urllib.parse import parse_qs, urlparse

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from api.gateway.oidc import OidcSettings, clear_oidc_states, configure_oidc
from api.gateway.oidc_authorize_stepup import reset_oidc_authorize_stepup
from api.gateway.oidc_refresh_store import configure_oidc_refresh_store

SECRET = "eaos-g87-authorize-stepup-secret"
TENANT = uuid4()
JWT_SETTINGS = JwtSettings(
    secret=SECRET,
    issuer="https://eaos.example/issuer",
    audience="eaos-api",
    allow_dev_headers=True,
    require_jwt=False,
)


def _oidc_settings() -> OidcSettings:
    return OidcSettings(
        issuer="https://idp.example",
        client_id="eaos-client",
        client_secret="client-secret",
        redirect_uri="http://127.0.0.1:8000/v1/auth/oidc/callback",
        authorization_endpoint="https://idp.example/authorize",
        token_endpoint="https://idp.example/token",
        scopes="openid profile",
        default_tenant_id=str(TENANT),
        enabled=True,
    )


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "EAOS_OIDC_AUTHORIZE_ACR_VALUES",
        "EAOS_OIDC_AUTHORIZE_PROMPT",
    ):
        monkeypatch.delenv(name, raising=False)
    reset_oidc_authorize_stepup()
    clear_oidc_states()
    configure_oidc_refresh_store(store="memory")
    configure_jwt_settings(JWT_SETTINGS)
    configure_oidc(_oidc_settings())
    yield
    reset_oidc_authorize_stepup()
    clear_oidc_states()
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


def test_stepup_empty_config_is_noop() -> None:
    client = TestClient(create_app())
    status = client.get("/v1/auth/oidc/status").json()["data"]
    assert status["authorize_stepup_enabled"] is False
    assert status["authorize_acr_values"] is None
    assert status["authorize_prompt"] is None
    login = client.get("/v1/auth/oidc/login", follow_redirects=False)
    assert login.status_code == 302
    query = parse_qs(urlparse(login.headers["location"]).query)
    assert "acr_values" not in query
    assert "prompt" not in query


def test_status_exposes_stepup_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "EAOS_OIDC_AUTHORIZE_ACR_VALUES",
        "urn:mace:incommon:iap:silver",
    )
    monkeypatch.setenv("EAOS_OIDC_AUTHORIZE_PROMPT", "login")
    reset_oidc_authorize_stepup()
    client = TestClient(create_app())
    body = client.get("/v1/auth/oidc/status").json()["data"]
    assert body["authorize_stepup_enabled"] is True
    assert body["authorize_acr_values"] == "urn:mace:incommon:iap:silver"
    assert body["authorize_prompt"] == "login"


def test_login_adds_acr_values_and_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "EAOS_OIDC_AUTHORIZE_ACR_VALUES",
        "urn:mace:incommon:iap:silver",
    )
    monkeypatch.setenv("EAOS_OIDC_AUTHORIZE_PROMPT", "login")
    reset_oidc_authorize_stepup()
    client = TestClient(create_app())
    login = client.get("/v1/auth/oidc/login", follow_redirects=False)
    assert login.status_code == 302
    query = parse_qs(urlparse(login.headers["location"]).query)
    assert query["acr_values"] == ["urn:mace:incommon:iap:silver"]
    assert query["prompt"] == ["login"]
    assert query["client_id"] == ["eaos-client"]
    assert "code_challenge" in query


def test_prompt_only_stepup(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_AUTHORIZE_PROMPT", "consent")
    reset_oidc_authorize_stepup()
    client = TestClient(create_app())
    login = client.get("/v1/auth/oidc/login", follow_redirects=False)
    query = parse_qs(urlparse(login.headers["location"]).query)
    assert query["prompt"] == ["consent"]
    assert "acr_values" not in query
