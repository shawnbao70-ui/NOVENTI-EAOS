"""PHX-G86 OIDC Provider End-Session Catalog Gate contracts."""

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

SECRET = "eaos-g86-provider-end-session-secret"
TENANT = uuid4()
SUBJECT = uuid4()
JWT_SETTINGS = JwtSettings(
    secret=SECRET,
    issuer="https://eaos.example/issuer",
    audience="eaos-api",
    allow_dev_headers=True,
    require_jwt=False,
)


class _FakeTokenClient:
    def __init__(self, *, id_claims: dict) -> None:
        self._id_claims = dict(id_claims)

    def exchange_code(self, **kwargs):  # type: ignore[no-untyped-def]
        token = mint_id_token(self._id_claims, secret="idp-secret")
        return {
            "id_token": token,
            "refresh_token": "refresh-g86",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    def refresh(self, **kwargs):  # type: ignore[no-untyped-def]
        token = mint_id_token(self._id_claims, secret="idp-secret")
        return {
            "id_token": token,
            "refresh_token": "refresh-g86-rotated",
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
        refresh=True,
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


def test_parse_end_session_with_empty_middle_fields() -> None:
    mapping = parse_oidc_login_providers(
        "google|https://accounts.google.com|gid|gsecret|||"
        "https://accounts.google.com/logout"
    )
    assert mapping["google"].authorization_endpoint is None
    assert mapping["google"].token_endpoint is None
    assert (
        mapping["google"].end_session_endpoint
        == "https://accounts.google.com/logout"
    )


def test_providers_catalog_exposes_end_session() -> None:
    configure_oidc_login_providers(
        {
            "google": OidcLoginProvider(
                key="google",
                issuer="https://accounts.google.com",
                client_id="gid",
                client_secret="gsecret",
                end_session_endpoint="https://accounts.google.com/logout",
            )
        }
    )
    client = TestClient(create_app())
    catalog = client.get("/v1/auth/oidc/providers").json()["data"]["providers"]
    assert catalog == [
        {
            "key": "google",
            "issuer": "https://accounts.google.com",
            "has_end_session": True,
            "end_session_endpoint": "https://accounts.google.com/logout",
        }
    ]
    status = client.get("/v1/auth/oidc/status").json()["data"]["login_providers"]
    assert status[0]["has_end_session"] is True


def test_provider_logout_uses_provider_end_session() -> None:
    fake = _FakeTokenClient(
        id_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "nonce": "x",
        }
    )
    configure_oidc_login_providers(
        {
            "google": OidcLoginProvider(
                key="google",
                issuer="https://accounts.google.com",
                client_id="gid",
                client_secret="gsecret",
                authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
                token_endpoint="https://oauth2.googleapis.com/token",
                end_session_endpoint="https://accounts.google.com/logout",
            )
        }
    )
    configure_oidc(_oidc_settings(), token_client=fake)
    client = TestClient(create_app())
    login = client.get(
        "/v1/auth/oidc/login",
        params={"provider": "google"},
        follow_redirects=False,
    )
    query = parse_qs(urlparse(login.headers["location"]).query)
    fake._id_claims["nonce"] = query["nonce"][0]
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c-g86", "state": query["state"][0]},
        headers={"Accept": "application/json"},
    )
    token = callback.json()["data"]["access_token"]
    claims = verify_token(token, settings=JWT_SETTINGS)
    assert claims["eaos_oidc_login_provider"] == "google"

    logged_out = client.post(
        "/v1/auth/oidc/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logged_out.status_code == 200
    end_session = logged_out.json()["data"]["end_session_url"]
    assert end_session is not None
    assert end_session.startswith("https://accounts.google.com/logout?")
    assert "client_id=gid" in end_session
    assert "https://idp.example/logout" not in end_session


def test_provider_without_end_session_falls_back_to_primary() -> None:
    fake = _FakeTokenClient(
        id_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "nonce": "x",
        }
    )
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
    configure_oidc(_oidc_settings(), token_client=fake)
    client = TestClient(create_app())
    login = client.get(
        "/v1/auth/oidc/login",
        params={"provider": "google"},
        follow_redirects=False,
    )
    query = parse_qs(urlparse(login.headers["location"]).query)
    fake._id_claims["nonce"] = query["nonce"][0]
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c-g86b", "state": query["state"][0]},
        headers={"Accept": "application/json"},
    )
    token = callback.json()["data"]["access_token"]
    logged_out = client.post(
        "/v1/auth/oidc/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    end_session = logged_out.json()["data"]["end_session_url"]
    assert end_session is not None
    assert end_session.startswith("https://idp.example/logout?")
    assert "client_id=gid" in end_session
