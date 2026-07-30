"""PHX-G84 OIDC Multi-Provider Login Gate contracts."""

from __future__ import annotations

from uuid import uuid4
from urllib.parse import parse_qs, urlparse

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings, mint_hs256_token as mint_id_token, verify_token
from api.gateway.context import configure_jwt_settings
from api.gateway.oidc import OidcSettings, clear_oidc_states, configure_oidc
from api.gateway.oidc_login_providers import (
    OidcLoginProvider,
    configure_oidc_login_providers,
    parse_oidc_login_providers,
    reset_oidc_login_providers,
)
from api.gateway.oidc_refresh_store import configure_oidc_refresh_store

SECRET = "eaos-g84-oidc-providers-secret"
TENANT = uuid4()
SUBJECT = uuid4()
JWT_SETTINGS = JwtSettings(
    secret=SECRET,
    issuer="https://eaos.example/issuer",
    audience="eaos-api",
    allow_dev_headers=True,
    require_jwt=False,
)


def _claims(access_token: str) -> dict:
    return verify_token(access_token, settings=JWT_SETTINGS)


class _FakeTokenClient:
    def __init__(self, *, id_claims: dict) -> None:
        self._id_claims = id_claims
        self.last_exchange: dict | None = None

    def exchange_code(self, **kwargs):  # type: ignore[no-untyped-def]
        self.last_exchange = dict(kwargs)
        token = mint_id_token(self._id_claims, secret="idp-secret")
        return {
            "id_token": token,
            "refresh_token": "refresh-g84",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    def refresh(self, **kwargs):  # type: ignore[no-untyped-def]
        token = mint_id_token(self._id_claims, secret="idp-secret")
        return {
            "id_token": token,
            "refresh_token": "refresh-g84-rotated",
            "token_type": "Bearer",
            "expires_in": 3600,
        }


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
    monkeypatch.delenv("EAOS_OIDC_LOGIN_PROVIDERS", raising=False)
    reset_oidc_login_providers()
    clear_oidc_states()
    configure_oidc_refresh_store(store="memory")
    configure_jwt_settings(JWT_SETTINGS)
    configure_oidc(
        _oidc_settings(),
        token_client=_FakeTokenClient(
            id_claims={
                "sub": str(SUBJECT),
                "eaos_tenant_id": str(TENANT),
                "nonce": "placeholder",
            }
        ),
    )
    yield
    reset_oidc_login_providers()
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


def test_parse_login_providers() -> None:
    mapping = parse_oidc_login_providers(
        "google|https://accounts.google.com|gid|gsecret,"
        "corp|https://idp.corp|cid|csecret|https://idp.corp/a|https://idp.corp/t|"
        "https://idp.corp/logout"
    )
    assert mapping["google"].issuer == "https://accounts.google.com"
    assert mapping["google"].client_id == "gid"
    assert mapping["google"].end_session_endpoint is None
    assert mapping["corp"].authorization_endpoint == "https://idp.corp/a"
    assert mapping["corp"].token_endpoint == "https://idp.corp/t"
    assert mapping["corp"].end_session_endpoint == "https://idp.corp/logout"


def test_empty_providers_is_noop() -> None:
    client = TestClient(create_app())
    status = client.get("/v1/auth/oidc/status").json()["data"]
    assert status["login_providers_enabled"] is False
    assert status["login_providers"] == []
    catalog = client.get("/v1/auth/oidc/providers").json()["data"]
    assert catalog["providers"] == []
    login = client.get("/v1/auth/oidc/login", follow_redirects=False)
    assert login.status_code == 302
    assert login.headers["location"].startswith("https://idp.example/authorize?")


def test_unknown_provider_rejected() -> None:
    configure_oidc_login_providers(
        {
            "google": OidcLoginProvider(
                key="google",
                issuer="https://accounts.google.com",
                client_id="gid",
                client_secret="gsecret",
            )
        }
    )
    client = TestClient(create_app())
    response = client.get(
        "/v1/auth/oidc/login",
        params={"provider": "missing"},
        follow_redirects=False,
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "GATEWAY_OIDC_UNKNOWN_PROVIDER"


def test_provider_login_and_callback_uses_overlay() -> None:
    configure_oidc_login_providers(
        {
            "google": OidcLoginProvider(
                key="google",
                issuer="https://accounts.google.com",
                client_id="gid",
                client_secret="gsecret",
                authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
                token_endpoint="https://oauth2.googleapis.com/token",
            )
        }
    )
    fake = _FakeTokenClient(
        id_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "nonce": "will-replace",
        }
    )
    configure_oidc(_oidc_settings(), token_client=fake)
    client = TestClient(create_app())

    status = client.get("/v1/auth/oidc/status").json()["data"]
    assert status["login_providers_enabled"] is True
    assert status["login_providers"] == [
        {
            "key": "google",
            "issuer": "https://accounts.google.com",
            "has_end_session": False,
            "end_session_endpoint": None,
        }
    ]

    login = client.get(
        "/v1/auth/oidc/login",
        params={"provider": "google"},
        follow_redirects=False,
    )
    assert login.status_code == 302
    location = urlparse(login.headers["location"])
    assert location.scheme == "https"
    assert location.netloc == "accounts.google.com"
    query = parse_qs(location.query)
    assert query["client_id"] == ["gid"]
    state = query["state"][0]
    nonce = query["nonce"][0]

    fake._id_claims["nonce"] = nonce
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c-google", "state": state},
        headers={"Accept": "application/json"},
    )
    assert callback.status_code == 200
    assert fake.last_exchange is not None
    assert fake.last_exchange["token_endpoint"] == "https://oauth2.googleapis.com/token"
    assert fake.last_exchange["client_id"] == "gid"
    assert (
        fake.last_exchange["redirect_uri"]
        == "http://127.0.0.1:8000/v1/auth/oidc/callback"
    )
    claims = _claims(callback.json()["data"]["access_token"])
    assert claims["eaos_oidc_issuer"] == "https://accounts.google.com"


def test_terminal_ui_mentions_provider_links() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    html = (root / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (root / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="oidcProviderLinks"' in html
    assert "/v1/auth/oidc/providers" in js
    assert "loadOidcProviderLinks" in js
