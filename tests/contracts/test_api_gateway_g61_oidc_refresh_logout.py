"""PHX-G61 OIDC Refresh + RP-Logout contracts."""

from __future__ import annotations

from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import (
    JwtSettings,
    clear_jwks_cache,
    clear_runtime_denylist,
    mint_hs256_token,
    verify_token,
)
from api.gateway.context import configure_jwt_settings, current_jwt_settings
from api.gateway.oidc import (
    OidcSettings,
    clear_oidc_discovery_cache,
    clear_oidc_states,
    configure_oidc,
)

mint_id_token = mint_hs256_token

SECRET = "eaos-g61-secret"
SUBJECT = uuid4()
TENANT = uuid4()
OIDC_ISS = "https://idp-g61.example"
EAOS_ISS = "https://eaos.example/issuer"
END_SESSION = "https://idp-g61.example/logout"


class _FakeTokenClient:
    def __init__(self, *, id_claims: dict) -> None:
        self._id_claims = dict(id_claims)
        self.exchange_calls = 0
        self.refresh_calls = 0
        self.last_refresh_token: str | None = None

    def exchange_code(self, **kwargs):  # type: ignore[no-untyped-def]
        self.exchange_calls += 1
        token = mint_id_token(self._id_claims, secret="idp-secret")
        return {
            "id_token": token,
            "refresh_token": "refresh-1",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    def refresh(self, **kwargs):  # type: ignore[no-untyped-def]
        self.refresh_calls += 1
        self.last_refresh_token = kwargs.get("refresh_token")
        self._id_claims["nonce"] = "ignored-on-refresh"
        token = mint_id_token(self._id_claims, secret="idp-secret")
        return {
            "id_token": token,
            "refresh_token": "refresh-2",
            "token_type": "Bearer",
            "expires_in": 3600,
        }


def _oidc(**overrides):  # type: ignore[no-untyped-def]
    values = {
        "issuer": OIDC_ISS,
        "client_id": "eaos-client",
        "client_secret": "secret",
        "redirect_uri": "http://127.0.0.1:8000/v1/auth/oidc/callback",
        "authorization_endpoint": f"{OIDC_ISS}/authorize",
        "token_endpoint": f"{OIDC_ISS}/token",
        "scopes": "openid",
        "default_tenant_id": str(TENANT),
        "enabled": True,
        "discovery": False,
        "discovery_url": None,
        "jwks_uri": None,
        "jwks_wire": False,
        "discovery_registry_write": False,
        "refresh": True,
        "rp_logout": True,
        "end_session_endpoint": END_SESSION,
        "post_logout_redirect_uri": "http://127.0.0.1:8000/terminal/",
    }
    values.update(overrides)
    return OidcSettings(**values)


@pytest.fixture(autouse=True)
def _reset() -> None:
    clear_oidc_states()
    clear_oidc_discovery_cache()
    clear_runtime_denylist()
    clear_jwks_cache()
    configure_jwt_settings(
        JwtSettings(
            secret=SECRET,
            issuer=EAOS_ISS,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    client = _FakeTokenClient(
        id_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "nonce": "will-be-overwritten-by-state",
        }
    )
    configure_oidc(_oidc(), token_client=client)
    yield
    clear_oidc_states()
    clear_runtime_denylist()


def _login_json(client: TestClient) -> dict:
    from urllib.parse import parse_qs, urlparse

    login = client.get("/v1/auth/oidc/login", follow_redirects=False)
    assert login.status_code == 302
    query = parse_qs(urlparse(login.headers["location"]).query)
    state = query["state"][0]
    nonce = query["nonce"][0]
    fake = _FakeTokenClient(
        id_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "nonce": nonce,
            "eaos_subject_type": "human",
        }
    )
    configure_oidc(_oidc(), token_client=fake)
    response = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "auth-code", "state": state},
        headers={"Accept": "application/json"},
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_status_exposes_refresh_and_rp_logout_flags() -> None:
    client = TestClient(create_app())
    status = client.get("/v1/auth/oidc/status")
    assert status.status_code == 200
    body = status.json()["data"]
    assert body["refresh"] is True
    assert body["refresh_store"] == "process_memory"
    assert body["refresh_encrypt"] == "off"
    assert body["refresh_encrypt_key_count"] == 0
    assert body["refresh_encrypt_key_provider"] == "env"
    assert body["refresh_reencrypt_on_read"] is False
    assert body["tenant_idp_federation"] is False
    assert body["rp_logout"] is True
    assert body["end_session_endpoint"] == END_SESSION
    assert body["has_post_logout_redirect"] is True


def test_refresh_rotates_token_and_revokes_old_jti() -> None:
    client = TestClient(create_app())
    login = _login_json(client)
    assert login["refresh_available"] is True
    old = login["access_token"]
    old_claims = verify_token(old, current_jwt_settings())

    refreshed = client.post(
        "/v1/auth/oidc/refresh",
        headers={"Authorization": f"Bearer {old}"},
    )
    assert refreshed.status_code == 200
    data = refreshed.json()["data"]
    assert data["access_token"] != old
    assert data["refresh_available"] is True

    denied = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {old}"},
    )
    assert denied.status_code == 401
    assert denied.json()["detail"]["code"] == "GATEWAY_JWT_REVOKED"

    ok = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )
    assert ok.status_code == 200
    assert old_claims["jti"] != verify_token(
        data["access_token"], current_jwt_settings()
    )["jti"]


def test_logout_revokes_and_returns_end_session_url() -> None:
    client = TestClient(create_app())
    login = _login_json(client)
    token = login["access_token"]
    logout = client.post(
        "/v1/auth/oidc/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout.status_code == 200
    body = logout.json()["data"]
    assert body["revoked"] is True
    assert body["rp_logout"] is True
    assert body["end_session_url"].startswith(END_SESSION)
    assert "id_token_hint=" in body["end_session_url"]
    assert "post_logout_redirect_uri=" in body["end_session_url"]

    denied = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert denied.status_code == 401


def test_terminal_exposes_oidc_refresh_logout_controls() -> None:
    client = TestClient(create_app())
    html = client.get("/terminal/").text
    assert "OIDC Refresh" in html
    assert "OIDC Logout" in html
    assert "/v1/auth/oidc/refresh" in client.get("/terminal/app.js").text
    assert "/v1/auth/oidc/logout" in client.get("/terminal/app.js").text


def test_refresh_disabled_fail_closed() -> None:
    configure_oidc(_oidc(refresh=False), token_client=_FakeTokenClient(
        id_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "nonce": "x",
        }
    ))
    token = mint_hs256_token(
        {
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "eaos_subject_type": "human",
            "iss": EAOS_ISS,
            "aud": "eaos-api",
            "jti": "no-session",
        },
        secret=SECRET,
    )
    client = TestClient(create_app())
    response = client.post(
        "/v1/auth/oidc/refresh",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "GATEWAY_OIDC_REFRESH_DISABLED"
