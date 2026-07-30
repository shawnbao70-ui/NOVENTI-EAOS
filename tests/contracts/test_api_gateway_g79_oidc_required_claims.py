"""PHX-G79 OIDC Required Claims Gate contracts."""

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
from api.gateway.oidc_required_claims import configure_oidc_required_claims
from api.gateway.oidc_refresh_store import configure_oidc_refresh_store

SECRET = "eaos-g79-oidc-secret"
TENANT = uuid4()
SUBJECT = uuid4()


class _FakeTokenClient:
    def __init__(self, *, id_claims: dict, refresh_claims: dict | None = None) -> None:
        self._id_claims = id_claims
        self._refresh_claims = refresh_claims
        self.exchange_calls = 0
        self.refresh_calls = 0

    def exchange_code(self, **kwargs):  # type: ignore[no-untyped-def]
        self.exchange_calls += 1
        token = mint_id_token(self._id_claims, secret="idp-secret")
        return {
            "id_token": token,
            "refresh_token": "refresh-g79",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    def refresh(self, **kwargs):  # type: ignore[no-untyped-def]
        self.refresh_calls += 1
        claims = self._refresh_claims if self._refresh_claims is not None else self._id_claims
        token = mint_id_token(claims, secret="idp-secret")
        return {
            "id_token": token,
            "refresh_token": "refresh-g79-rotated",
            "token_type": "Bearer",
            "expires_in": 3600,
        }


def _oidc_settings(*, refresh: bool = False) -> OidcSettings:
    return OidcSettings(
        issuer="https://idp.example",
        client_id="eaos-client",
        client_secret="client-secret",
        redirect_uri="http://127.0.0.1:8000/v1/auth/oidc/callback",
        authorization_endpoint="https://idp.example/authorize",
        token_endpoint="https://idp.example/token",
        scopes="openid profile email",
        default_tenant_id=str(TENANT),
        enabled=True,
        refresh=refresh,
    )


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EAOS_OIDC_REQUIRED_CLAIMS", raising=False)
    configure_oidc_required_claims()
    clear_oidc_states()
    configure_oidc_refresh_store(store="memory")
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
    configure_oidc_required_claims()
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


def _login_state(client: TestClient) -> tuple[str, str]:
    login = client.get("/v1/auth/oidc/login", follow_redirects=False)
    assert login.status_code == 302
    query = parse_qs(urlparse(login.headers["location"]).query)
    return query["state"][0], query["nonce"][0]


def test_required_claims_empty_config_is_noop() -> None:
    client = TestClient(create_app())
    status = client.get("/v1/auth/oidc/status").json()["data"]
    assert status["required_claims_enabled"] is False
    assert status["required_claims"] == []
    state, nonce = _login_state(client)
    configure_oidc(
        _oidc_settings(),
        token_client=_FakeTokenClient(
            id_claims={
                "sub": str(SUBJECT),
                "eaos_tenant_id": str(TENANT),
                "nonce": nonce,
            }
        ),
    )
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c1", "state": state},
        headers={"Accept": "application/json"},
    )
    assert callback.status_code == 200


def test_missing_required_claim_denies_callback_mint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EAOS_OIDC_REQUIRED_CLAIMS", "email,email_verified")
    configure_oidc_required_claims()
    client = TestClient(create_app())
    state, nonce = _login_state(client)
    configure_oidc(
        _oidc_settings(),
        token_client=_FakeTokenClient(
            id_claims={
                "sub": str(SUBJECT),
                "eaos_tenant_id": str(TENANT),
                "nonce": nonce,
                "email": "user@example.com",
                # email_verified missing
            }
        ),
    )
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c2", "state": state},
        headers={"Accept": "application/json"},
    )
    assert callback.status_code == 401
    detail = callback.json()["detail"]
    assert detail["code"] == "GATEWAY_OIDC_REQUIRED_CLAIM_MISSING"
    assert "email_verified" in detail["details"]["claims"]


def test_present_required_claims_allow_mint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_REQUIRED_CLAIMS", "email,email_verified")
    configure_oidc_required_claims()
    client = TestClient(create_app())
    state, nonce = _login_state(client)
    configure_oidc(
        _oidc_settings(),
        token_client=_FakeTokenClient(
            id_claims={
                "sub": str(SUBJECT),
                "eaos_tenant_id": str(TENANT),
                "nonce": nonce,
                "email": "user@example.com",
                "email_verified": False,
            }
        ),
    )
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c3", "state": state},
        headers={"Accept": "application/json"},
    )
    assert callback.status_code == 200
    assert callback.json()["data"]["subject_id"] == str(SUBJECT)


def test_oidc_status_exposes_required_claims(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_REQUIRED_CLAIMS", " email , email_verified ")
    configure_oidc_required_claims()
    client = TestClient(create_app())
    body = client.get("/v1/auth/oidc/status").json()["data"]
    assert body["required_claims_enabled"] is True
    assert body["required_claims"] == ["email", "email_verified"]


def test_refresh_remint_enforces_required_claims(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EAOS_OIDC_REQUIRED_CLAIMS", "email")
    configure_oidc_required_claims()
    client = TestClient(create_app())
    state, nonce = _login_state(client)
    fake = _FakeTokenClient(
        id_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "nonce": nonce,
            "email": "user@example.com",
        },
        refresh_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            # email missing on refresh id_token
        },
    )
    configure_oidc(_oidc_settings(refresh=True), token_client=fake)
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c4", "state": state},
        headers={"Accept": "application/json"},
    )
    assert callback.status_code == 200
    token = callback.json()["data"]["access_token"]
    refreshed = client.post(
        "/v1/auth/oidc/refresh",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    assert refreshed.status_code == 401
    assert refreshed.json()["detail"]["code"] == "GATEWAY_OIDC_REQUIRED_CLAIM_MISSING"
    assert fake.refresh_calls == 1
