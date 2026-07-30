"""PHX-G85 OIDC Per-Provider Refresh Gate contracts."""

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
    reset_oidc_login_providers,
)
from api.gateway.oidc_refresh_store import configure_oidc_refresh_store

SECRET = "eaos-g85-provider-refresh-secret"
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
        self._id_claims = dict(id_claims)
        self.last_refresh: dict | None = None
        self.refresh_calls = 0

    def exchange_code(self, **kwargs):  # type: ignore[no-untyped-def]
        token = mint_id_token(self._id_claims, secret="idp-secret")
        return {
            "id_token": token,
            "refresh_token": "refresh-g85",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    def refresh(self, **kwargs):  # type: ignore[no-untyped-def]
        self.refresh_calls += 1
        self.last_refresh = dict(kwargs)
        self._id_claims["nonce"] = "ignored-on-refresh"
        token = mint_id_token(self._id_claims, secret="idp-secret")
        return {
            "id_token": token,
            "refresh_token": "refresh-g85-rotated",
            "token_type": "Bearer",
            "expires_in": 3600,
        }


def _oidc_settings(*, refresh: bool = True) -> OidcSettings:
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
        refresh=refresh,
        rp_logout=True,
        end_session_endpoint="https://idp.example/logout",
        post_logout_redirect_uri="http://127.0.0.1:8000/terminal/",
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


def _provider_login(client: TestClient, fake: _FakeTokenClient) -> str:
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
    configure_oidc(_oidc_settings(refresh=True), token_client=fake)
    login = client.get(
        "/v1/auth/oidc/login",
        params={"provider": "google"},
        follow_redirects=False,
    )
    assert login.status_code == 302
    query = parse_qs(urlparse(login.headers["location"]).query)
    state = query["state"][0]
    nonce = query["nonce"][0]
    fake._id_claims["nonce"] = nonce
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c-g85", "state": state},
        headers={"Accept": "application/json"},
    )
    assert callback.status_code == 200
    body = callback.json()["data"]
    assert body["refresh_available"] is True
    return body["access_token"]


def test_provider_login_mints_provider_claim() -> None:
    fake = _FakeTokenClient(
        id_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "nonce": "x",
        }
    )
    client = TestClient(create_app())
    token = _provider_login(client, fake)
    claims = _claims(token)
    assert claims["eaos_oidc_login_provider"] == "google"
    assert claims["eaos_oidc_issuer"] == "https://accounts.google.com"


def test_provider_refresh_uses_overlay_token_endpoint() -> None:
    fake = _FakeTokenClient(
        id_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "nonce": "x",
        }
    )
    client = TestClient(create_app())
    token = _provider_login(client, fake)
    refreshed = client.post(
        "/v1/auth/oidc/refresh",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert refreshed.status_code == 200
    assert fake.refresh_calls == 1
    assert fake.last_refresh is not None
    assert fake.last_refresh["token_endpoint"] == "https://oauth2.googleapis.com/token"
    assert fake.last_refresh["client_id"] == "gid"
    new_claims = _claims(refreshed.json()["data"]["access_token"])
    assert new_claims["eaos_oidc_login_provider"] == "google"
    assert new_claims["eaos_oidc_issuer"] == "https://accounts.google.com"


def test_primary_login_refresh_unchanged() -> None:
    fake = _FakeTokenClient(
        id_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "nonce": "x",
        }
    )
    configure_oidc(_oidc_settings(refresh=True), token_client=fake)
    client = TestClient(create_app())
    login = client.get("/v1/auth/oidc/login", follow_redirects=False)
    query = parse_qs(urlparse(login.headers["location"]).query)
    fake._id_claims["nonce"] = query["nonce"][0]
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c-primary", "state": query["state"][0]},
        headers={"Accept": "application/json"},
    )
    token = callback.json()["data"]["access_token"]
    assert "eaos_oidc_login_provider" not in _claims(token)
    refreshed = client.post(
        "/v1/auth/oidc/refresh",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert refreshed.status_code == 200
    assert fake.last_refresh is not None
    assert fake.last_refresh["token_endpoint"] == "https://idp.example/token"
    assert fake.last_refresh["client_id"] == "eaos-client"


def test_refresh_fails_if_provider_removed() -> None:
    fake = _FakeTokenClient(
        id_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "nonce": "x",
        }
    )
    client = TestClient(create_app())
    token = _provider_login(client, fake)
    reset_oidc_login_providers()
    configure_oidc_login_providers({})
    denied = client.post(
        "/v1/auth/oidc/refresh",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert denied.status_code == 400
    assert denied.json()["detail"]["code"] == "GATEWAY_OIDC_UNKNOWN_PROVIDER"


def test_provider_logout_uses_overlay_client_id() -> None:
    fake = _FakeTokenClient(
        id_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "nonce": "x",
        }
    )
    client = TestClient(create_app())
    token = _provider_login(client, fake)
    logged_out = client.post(
        "/v1/auth/oidc/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logged_out.status_code == 200
    data = logged_out.json()["data"]
    assert data["rp_logout"] is True
    assert "client_id=gid" in (data["end_session_url"] or "")
