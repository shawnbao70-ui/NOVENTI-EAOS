"""PHX-G80 OIDC amr/acr Auth Context Gate contracts."""

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
from api.gateway.oidc_amr_acr import reset_oidc_amr_acr
from api.gateway.oidc_refresh_store import configure_oidc_refresh_store
from api.gateway.oidc_required_claims import configure_oidc_required_claims

SECRET = "eaos-g80-oidc-secret"
TENANT = uuid4()
SUBJECT = uuid4()


class _FakeTokenClient:
    def __init__(self, *, id_claims: dict, refresh_claims: dict | None = None) -> None:
        self._id_claims = id_claims
        self._refresh_claims = refresh_claims
        self.refresh_calls = 0

    def exchange_code(self, **kwargs):  # type: ignore[no-untyped-def]
        token = mint_id_token(self._id_claims, secret="idp-secret")
        return {
            "id_token": token,
            "refresh_token": "refresh-g80",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    def refresh(self, **kwargs):  # type: ignore[no-untyped-def]
        self.refresh_calls += 1
        claims = self._refresh_claims if self._refresh_claims is not None else self._id_claims
        token = mint_id_token(claims, secret="idp-secret")
        return {
            "id_token": token,
            "refresh_token": "refresh-g80-rotated",
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
        scopes="openid profile",
        default_tenant_id=str(TENANT),
        enabled=True,
        refresh=refresh,
    )


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EAOS_OIDC_REQUIRED_AMR", raising=False)
    monkeypatch.delenv("EAOS_OIDC_REQUIRED_ACR", raising=False)
    monkeypatch.delenv("EAOS_OIDC_REQUIRED_CLAIMS", raising=False)
    reset_oidc_amr_acr()
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
    reset_oidc_amr_acr()
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


def test_amr_acr_empty_config_is_noop() -> None:
    client = TestClient(create_app())
    status = client.get("/v1/auth/oidc/status").json()["data"]
    assert status["required_amr_enabled"] is False
    assert status["required_acr_enabled"] is False
    assert status["required_amr"] == []
    assert status["required_acr"] == []
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


def test_missing_amr_denies_callback_mint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_REQUIRED_AMR", "mfa,otp")
    reset_oidc_amr_acr()
    client = TestClient(create_app())
    state, nonce = _login_state(client)
    configure_oidc(
        _oidc_settings(),
        token_client=_FakeTokenClient(
            id_claims={
                "sub": str(SUBJECT),
                "eaos_tenant_id": str(TENANT),
                "nonce": nonce,
                "amr": ["pwd"],
            }
        ),
    )
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c2", "state": state},
        headers={"Accept": "application/json"},
    )
    assert callback.status_code == 401
    assert callback.json()["detail"]["code"] == "GATEWAY_OIDC_AMR_REQUIRED"


def test_missing_acr_denies_callback_mint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_REQUIRED_ACR", "urn:mace:incommon:iap:silver")
    reset_oidc_amr_acr()
    client = TestClient(create_app())
    state, nonce = _login_state(client)
    configure_oidc(
        _oidc_settings(),
        token_client=_FakeTokenClient(
            id_claims={
                "sub": str(SUBJECT),
                "eaos_tenant_id": str(TENANT),
                "nonce": nonce,
                "acr": "urn:mace:incommon:iap:bronze",
            }
        ),
    )
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c3", "state": state},
        headers={"Accept": "application/json"},
    )
    assert callback.status_code == 401
    assert callback.json()["detail"]["code"] == "GATEWAY_OIDC_ACR_REQUIRED"


def test_matching_amr_acr_allow_mint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_REQUIRED_AMR", "mfa,otp")
    monkeypatch.setenv("EAOS_OIDC_REQUIRED_ACR", "urn:mace:incommon:iap:silver")
    reset_oidc_amr_acr()
    client = TestClient(create_app())
    state, nonce = _login_state(client)
    configure_oidc(
        _oidc_settings(),
        token_client=_FakeTokenClient(
            id_claims={
                "sub": str(SUBJECT),
                "eaos_tenant_id": str(TENANT),
                "nonce": nonce,
                "amr": ["pwd", "otp"],
                "acr": "urn:mace:incommon:iap:silver",
            }
        ),
    )
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c4", "state": state},
        headers={"Accept": "application/json"},
    )
    assert callback.status_code == 200
    assert callback.json()["data"]["subject_id"] == str(SUBJECT)


def test_oidc_status_exposes_amr_acr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_REQUIRED_AMR", " mfa , otp ")
    monkeypatch.setenv("EAOS_OIDC_REQUIRED_ACR", " urn:example:loa2 ")
    reset_oidc_amr_acr()
    client = TestClient(create_app())
    body = client.get("/v1/auth/oidc/status").json()["data"]
    assert body["required_amr_enabled"] is True
    assert body["required_acr_enabled"] is True
    assert body["required_amr"] == ["mfa", "otp"]
    assert body["required_acr"] == ["urn:example:loa2"]


def test_refresh_remint_enforces_amr_acr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_REQUIRED_AMR", "mfa")
    reset_oidc_amr_acr()
    client = TestClient(create_app())
    state, nonce = _login_state(client)
    fake = _FakeTokenClient(
        id_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "nonce": nonce,
            "amr": ["mfa"],
        },
        refresh_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "amr": ["pwd"],
        },
    )
    configure_oidc(_oidc_settings(refresh=True), token_client=fake)
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c5", "state": state},
        headers={"Accept": "application/json"},
    )
    assert callback.status_code == 200
    token = callback.json()["data"]["access_token"]
    refreshed = client.post(
        "/v1/auth/oidc/refresh",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    assert refreshed.status_code == 401
    assert refreshed.json()["detail"]["code"] == "GATEWAY_OIDC_AMR_REQUIRED"
    assert fake.refresh_calls == 1
