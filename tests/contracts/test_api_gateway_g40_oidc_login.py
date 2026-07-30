"""PHX-G40 OIDC Authorization Code login contracts."""

from __future__ import annotations

from uuid import uuid4
from urllib.parse import parse_qs, urlparse

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings, mint_hs256_token as mint_id_token
from api.gateway.context import configure_jwt_settings
from api.gateway.oidc import OidcSettings, clear_oidc_states, configure_oidc

SECRET = "eaos-oidc-test-secret"
TENANT = uuid4()
SUBJECT = uuid4()


class _FakeTokenClient:
    def __init__(self, *, id_claims: dict) -> None:
        self._id_claims = id_claims
        self.calls = 0

    def exchange_code(self, **kwargs):  # type: ignore[no-untyped-def]
        self.calls += 1
        token = mint_id_token(self._id_claims, secret="idp-secret")
        return {"id_token": token, "token_type": "Bearer", "expires_in": 3600}

    def refresh(self, **kwargs):  # type: ignore[no-untyped-def]
        raise NotImplementedError("refresh not used in G40 fixtures")


@pytest.fixture(autouse=True)
def _settings() -> None:
    clear_oidc_states()
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
        OidcSettings(
            issuer="https://idp.example",
            client_id="eaos-client",
            client_secret="client-secret",
            redirect_uri="http://127.0.0.1:8000/v1/auth/oidc/callback",
            authorization_endpoint="https://idp.example/authorize",
            token_endpoint="https://idp.example/token",
            scopes="openid profile",
            default_tenant_id=str(TENANT),
            enabled=True,
        ),
        token_client=_FakeTokenClient(
            id_claims={
                "sub": str(SUBJECT),
                "eaos_tenant_id": str(TENANT),
                "nonce": "will-be-overwritten-by-state",
            }
        ),
    )
    yield
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
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience=None,
            allow_dev_headers=True,
            require_jwt=False,
        )
    )


def test_oidc_status_and_unconfigured() -> None:
    client = TestClient(create_app())
    status = client.get("/v1/auth/oidc/status")
    assert status.status_code == 200
    assert status.json()["data"]["enabled"] is True

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
    denied = client.get("/v1/auth/oidc/login", follow_redirects=False)
    assert denied.status_code == 503
    assert denied.json()["detail"]["code"] == "GATEWAY_OIDC_UNCONFIGURED"


def test_oidc_login_callback_mints_eaos_jwt() -> None:
    # Align fake id_token nonce with login state by patching exchange after login
    client = TestClient(create_app())
    login = client.get("/v1/auth/oidc/login", follow_redirects=False)
    assert login.status_code == 302
    location = login.headers["location"]
    parsed = urlparse(location)
    query = parse_qs(parsed.query)
    assert query["code_challenge_method"] == ["S256"]
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
    configure_oidc(
        OidcSettings(
            issuer="https://idp.example",
            client_id="eaos-client",
            client_secret="client-secret",
            redirect_uri="http://127.0.0.1:8000/v1/auth/oidc/callback",
            authorization_endpoint="https://idp.example/authorize",
            token_endpoint="https://idp.example/token",
            scopes="openid profile",
            default_tenant_id=str(TENANT),
            enabled=True,
        ),
        token_client=fake,
    )

    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "auth-code", "state": state},
        headers={"Accept": "application/json"},
    )
    assert callback.status_code == 200
    data = callback.json()["data"]
    assert data["token_type"] == "Bearer"
    assert data["subject_id"] == str(SUBJECT)
    assert data["tenant_id"] == str(TENANT)
    assert fake.calls == 1

    context = client.get(
        "/v1/context",
        headers={
            "Authorization": f"Bearer {data['access_token']}",
            "X-Correlation-Id": "oidc-corr",
        },
    )
    assert context.status_code == 200
    assert context.json()["data"]["tenant_id"] == str(TENANT)


def test_oidc_invalid_state_rejected() -> None:
    client = TestClient(create_app())
    response = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "x", "state": "missing"},
        headers={"Accept": "application/json"},
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "GATEWAY_OIDC_INVALID_STATE"
