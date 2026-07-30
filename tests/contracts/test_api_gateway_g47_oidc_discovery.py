"""PHX-G47 OIDC IdP Discovery contracts."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse
from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi import HTTPException
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings, mint_hs256_token as mint_id_token
from api.gateway.context import configure_jwt_settings
from api.gateway.oidc import (
    OidcSettings,
    clear_oidc_discovery_cache,
    clear_oidc_states,
    configure_oidc,
    resolve_oidc_endpoints,
)

SECRET = "eaos-oidc-discovery-secret"
TENANT = uuid4()
SUBJECT = uuid4()
ISSUER = "https://idp.example"
DISCOVERY_URL = "https://idp.example/.well-known/openid-configuration"


class _FakeTokenClient:
    def __init__(self, *, id_claims: dict) -> None:
        self._id_claims = id_claims
        self.calls = 0
        self.last_token_endpoint: str | None = None

    def exchange_code(self, **kwargs):  # type: ignore[no-untyped-def]
        self.calls += 1
        self.last_token_endpoint = kwargs.get("token_endpoint")
        token = mint_id_token(self._id_claims, secret="idp-secret")
        return {"id_token": token, "token_type": "Bearer", "expires_in": 3600}

    def refresh(self, **kwargs):  # type: ignore[no-untyped-def]
        raise NotImplementedError("refresh not used in G47 fixtures")


class _FakeDiscoveryClient:
    def __init__(self, document: dict, *, calls_limit: int | None = None) -> None:
        self.document = document
        self.calls = 0
        self.urls: list[str] = []
        self._calls_limit = calls_limit

    def fetch(self, url: str) -> dict:
        self.calls += 1
        self.urls.append(url)
        if self._calls_limit is not None and self.calls > self._calls_limit:
            raise AssertionError("discovery cache should prevent extra fetches")
        return self.document


def _base_settings(**overrides):  # type: ignore[no-untyped-def]
    values = {
        "issuer": ISSUER,
        "client_id": "eaos-client",
        "client_secret": "client-secret",
        "redirect_uri": "http://127.0.0.1:8000/v1/auth/oidc/callback",
        "authorization_endpoint": None,
        "token_endpoint": None,
        "scopes": "openid profile",
        "default_tenant_id": str(TENANT),
        "enabled": True,
        "discovery": True,
        "discovery_url": DISCOVERY_URL,
        "jwks_uri": None,
    }
    values.update(overrides)
    return OidcSettings(**values)


@pytest.fixture(autouse=True)
def _settings() -> None:
    clear_oidc_states()
    clear_oidc_discovery_cache()
    configure_jwt_settings(
        JwtSettings(
            secret=SECRET,
            issuer="https://eaos.example/issuer",
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    configure_oidc(
        _base_settings(),
        token_client=_FakeTokenClient(
            id_claims={
                "sub": str(SUBJECT),
                "eaos_tenant_id": str(TENANT),
            }
        ),
        discovery_client=_FakeDiscoveryClient(
            {
                "issuer": ISSUER,
                "authorization_endpoint": "https://idp.example/oauth2/v1/authorize",
                "token_endpoint": "https://idp.example/oauth2/v1/token",
                "jwks_uri": "https://idp.example/oauth2/v1/keys",
            }
        ),
    )
    yield
    clear_oidc_states()
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


def test_discovery_status_exposes_resolved_endpoints() -> None:
    client = TestClient(create_app())
    status = client.get("/v1/auth/oidc/status")
    assert status.status_code == 200
    data = status.json()["data"]
    assert data["enabled"] is True
    assert data["discovery"] is True
    assert data["discovery_url"] == DISCOVERY_URL
    assert data["authorization_endpoint"] == "https://idp.example/oauth2/v1/authorize"
    assert data["token_endpoint"] == "https://idp.example/oauth2/v1/token"
    assert data["jwks_uri"] == "https://idp.example/oauth2/v1/keys"


def test_discovery_login_uses_discovered_authorize() -> None:
    client = TestClient(create_app())
    login = client.get("/v1/auth/oidc/login", follow_redirects=False)
    assert login.status_code == 302
    location = login.headers["location"]
    assert location.startswith("https://idp.example/oauth2/v1/authorize?")
    query = parse_qs(urlparse(location).query)
    assert query["code_challenge_method"] == ["S256"]


def test_discovery_callback_uses_discovered_token_endpoint() -> None:
    client = TestClient(create_app())
    login = client.get("/v1/auth/oidc/login", follow_redirects=False)
    state = parse_qs(urlparse(login.headers["location"]).query)["state"][0]
    nonce = parse_qs(urlparse(login.headers["location"]).query)["nonce"][0]
    fake = _FakeTokenClient(
        id_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "nonce": nonce,
        }
    )
    configure_oidc(
        _base_settings(),
        token_client=fake,
        discovery_client=_FakeDiscoveryClient(
            {
                "issuer": ISSUER,
                "authorization_endpoint": "https://idp.example/oauth2/v1/authorize",
                "token_endpoint": "https://idp.example/oauth2/v1/token",
                "jwks_uri": "https://idp.example/oauth2/v1/keys",
            }
        ),
    )
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "auth-code", "state": state},
        headers={"Accept": "application/json"},
    )
    assert callback.status_code == 200
    assert fake.calls == 1
    assert fake.last_token_endpoint == "https://idp.example/oauth2/v1/token"


def test_discovery_issuer_mismatch_fail_closed() -> None:
    configure_oidc(
        _base_settings(),
        discovery_client=_FakeDiscoveryClient(
            {
                "issuer": "https://other-idp.example",
                "authorization_endpoint": "https://idp.example/oauth2/v1/authorize",
                "token_endpoint": "https://idp.example/oauth2/v1/token",
            }
        ),
    )
    client = TestClient(create_app())
    denied = client.get("/v1/auth/oidc/login", follow_redirects=False)
    assert denied.status_code == 503
    assert denied.json()["detail"]["code"] == "GATEWAY_OIDC_DISCOVERY_FAILED"


def test_explicit_endpoints_override_discovery() -> None:
    discovery = _FakeDiscoveryClient(
        {
            "issuer": ISSUER,
            "authorization_endpoint": "https://idp.example/oauth2/v1/authorize",
            "token_endpoint": "https://idp.example/oauth2/v1/token",
        }
    )
    settings = _base_settings(
        authorization_endpoint="https://idp.example/custom/authorize",
        token_endpoint="https://idp.example/custom/token",
    )
    configure_oidc(settings, discovery_client=discovery)
    resolved = resolve_oidc_endpoints(settings)
    assert resolved.authorization_endpoint == "https://idp.example/custom/authorize"
    assert resolved.token_endpoint == "https://idp.example/custom/token"
    assert discovery.calls == 1

    client = TestClient(create_app())
    login = client.get("/v1/auth/oidc/login", follow_redirects=False)
    assert login.status_code == 302
    assert login.headers["location"].startswith(
        "https://idp.example/custom/authorize?"
    )


def test_discovery_cache_reuses_document() -> None:
    discovery = _FakeDiscoveryClient(
        {
            "issuer": ISSUER,
            "authorization_endpoint": "https://idp.example/oauth2/v1/authorize",
            "token_endpoint": "https://idp.example/oauth2/v1/token",
        },
        calls_limit=1,
    )
    settings = _base_settings()
    configure_oidc(settings, discovery_client=discovery)
    clear_oidc_discovery_cache()
    resolve_oidc_endpoints(settings)
    resolve_oidc_endpoints(settings)
    assert discovery.calls == 1


def test_discovery_missing_endpoints_fail_closed() -> None:
    settings = _base_settings()
    configure_oidc(
        settings,
        discovery_client=_FakeDiscoveryClient(
            {
                "issuer": ISSUER,
                "authorization_endpoint": "https://idp.example/oauth2/v1/authorize",
            }
        ),
    )
    with pytest.raises(HTTPException) as exc:
        resolve_oidc_endpoints(settings)
    assert exc.value.status_code == 503
    assert exc.value.detail["code"] == "GATEWAY_OIDC_DISCOVERY_FAILED"
