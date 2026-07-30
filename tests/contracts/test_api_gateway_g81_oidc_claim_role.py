"""PHX-G81 OIDC Claim→Role JWT Mint Gate contracts."""

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
from api.gateway.oidc_amr_acr import reset_oidc_amr_acr
from api.gateway.oidc_claim_role import reset_oidc_claim_role
from api.gateway.oidc_refresh_store import configure_oidc_refresh_store
from api.gateway.oidc_required_claims import configure_oidc_required_claims

SECRET = "eaos-g81-oidc-secret"
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
    def __init__(self, *, id_claims: dict, refresh_claims: dict | None = None) -> None:
        self._id_claims = id_claims
        self._refresh_claims = refresh_claims
        self.refresh_calls = 0

    def exchange_code(self, **kwargs):  # type: ignore[no-untyped-def]
        token = mint_id_token(self._id_claims, secret="idp-secret")
        return {
            "id_token": token,
            "refresh_token": "refresh-g81",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    def refresh(self, **kwargs):  # type: ignore[no-untyped-def]
        self.refresh_calls += 1
        claims = self._refresh_claims if self._refresh_claims is not None else self._id_claims
        token = mint_id_token(claims, secret="idp-secret")
        return {
            "id_token": token,
            "refresh_token": "refresh-g81-rotated",
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
    for name in (
        "EAOS_OIDC_ROLE_CLAIM",
        "EAOS_OIDC_ROLE_MAP",
        "EAOS_OIDC_REQUIRE_MAPPED_ROLE",
        "EAOS_OIDC_REQUIRED_CLAIMS",
        "EAOS_OIDC_REQUIRED_AMR",
        "EAOS_OIDC_REQUIRED_ACR",
    ):
        monkeypatch.delenv(name, raising=False)
    reset_oidc_claim_role()
    reset_oidc_amr_acr()
    configure_oidc_required_claims()
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
    reset_oidc_claim_role()
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


def test_claim_role_empty_config_is_noop() -> None:
    client = TestClient(create_app())
    status = client.get("/v1/auth/oidc/status").json()["data"]
    assert status["role_claim_enabled"] is False
    assert status["role_claim"] is None
    assert status["role_map_size"] == 0
    assert status["require_mapped_role"] is False
    state, nonce = _login_state(client)
    configure_oidc(
        _oidc_settings(),
        token_client=_FakeTokenClient(
            id_claims={
                "sub": str(SUBJECT),
                "eaos_tenant_id": str(TENANT),
                "nonce": nonce,
                "groups": ["Engineering"],
            }
        ),
    )
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c1", "state": state},
        headers={"Accept": "application/json"},
    )
    assert callback.status_code == 200
    claims = _claims(callback.json()["data"]["access_token"])
    assert "eaos_roles" not in claims


def test_status_exposes_role_claim_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_ROLE_CLAIM", "groups")
    monkeypatch.setenv("EAOS_OIDC_ROLE_MAP", "Engineering=operator,Admins=admin")
    monkeypatch.setenv("EAOS_OIDC_REQUIRE_MAPPED_ROLE", "1")
    reset_oidc_claim_role()
    client = TestClient(create_app())
    body = client.get("/v1/auth/oidc/status").json()["data"]
    assert body["role_claim"] == "groups"
    assert body["role_claim_enabled"] is True
    assert body["role_map_size"] == 2
    assert body["require_mapped_role"] is True


def test_mapped_groups_mint_eaos_roles_on_callback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EAOS_OIDC_ROLE_CLAIM", "groups")
    monkeypatch.setenv("EAOS_OIDC_ROLE_MAP", "Engineering=operator,Admins=admin")
    reset_oidc_claim_role()
    client = TestClient(create_app())
    state, nonce = _login_state(client)
    configure_oidc(
        _oidc_settings(),
        token_client=_FakeTokenClient(
            id_claims={
                "sub": str(SUBJECT),
                "eaos_tenant_id": str(TENANT),
                "nonce": nonce,
                "groups": ["Engineering", "Other", "Admins"],
            }
        ),
    )
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c2", "state": state},
        headers={"Accept": "application/json"},
    )
    assert callback.status_code == 200
    claims = _claims(callback.json()["data"]["access_token"])
    assert claims["eaos_roles"] == ["admin", "operator"]


def test_unmapped_values_omit_roles(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_ROLE_CLAIM", "groups")
    monkeypatch.setenv("EAOS_OIDC_ROLE_MAP", "Engineering=operator")
    reset_oidc_claim_role()
    client = TestClient(create_app())
    state, nonce = _login_state(client)
    configure_oidc(
        _oidc_settings(),
        token_client=_FakeTokenClient(
            id_claims={
                "sub": str(SUBJECT),
                "eaos_tenant_id": str(TENANT),
                "nonce": nonce,
                "groups": ["Contractors"],
            }
        ),
    )
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c3", "state": state},
        headers={"Accept": "application/json"},
    )
    assert callback.status_code == 200
    claims = _claims(callback.json()["data"]["access_token"])
    assert "eaos_roles" not in claims


def test_require_mapped_role_denies_callback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_ROLE_CLAIM", "groups")
    monkeypatch.setenv("EAOS_OIDC_ROLE_MAP", "Engineering=operator")
    monkeypatch.setenv("EAOS_OIDC_REQUIRE_MAPPED_ROLE", "1")
    reset_oidc_claim_role()
    client = TestClient(create_app())
    state, nonce = _login_state(client)
    configure_oidc(
        _oidc_settings(),
        token_client=_FakeTokenClient(
            id_claims={
                "sub": str(SUBJECT),
                "eaos_tenant_id": str(TENANT),
                "nonce": nonce,
                "groups": ["Contractors"],
            }
        ),
    )
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c4", "state": state},
        headers={"Accept": "application/json"},
    )
    assert callback.status_code == 401
    assert callback.json()["detail"]["code"] == "GATEWAY_OIDC_ROLE_REQUIRED"


def test_refresh_remap_applies_claim_role(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_ROLE_CLAIM", "groups")
    monkeypatch.setenv("EAOS_OIDC_ROLE_MAP", "Engineering=operator")
    reset_oidc_claim_role()
    client = TestClient(create_app())
    state, nonce = _login_state(client)
    fake = _FakeTokenClient(
        id_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "nonce": nonce,
            "groups": ["Engineering"],
        },
        refresh_claims={
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "groups": ["Engineering"],
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
    assert refreshed.status_code == 200
    claims = _claims(refreshed.json()["data"]["access_token"])
    assert claims["eaos_roles"] == ["operator"]
    assert fake.refresh_calls == 1


def test_g79_g80_still_compose_before_role_map(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_REQUIRED_CLAIMS", "email")
    monkeypatch.setenv("EAOS_OIDC_REQUIRED_AMR", "mfa")
    monkeypatch.setenv("EAOS_OIDC_ROLE_CLAIM", "groups")
    monkeypatch.setenv("EAOS_OIDC_ROLE_MAP", "Engineering=operator")
    configure_oidc_required_claims()
    reset_oidc_amr_acr()
    reset_oidc_claim_role()
    client = TestClient(create_app())
    state, nonce = _login_state(client)
    configure_oidc(
        _oidc_settings(),
        token_client=_FakeTokenClient(
            id_claims={
                "sub": str(SUBJECT),
                "eaos_tenant_id": str(TENANT),
                "nonce": nonce,
                "groups": ["Engineering"],
                # missing email + amr
            }
        ),
    )
    callback = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "c6", "state": state},
        headers={"Accept": "application/json"},
    )
    assert callback.status_code == 401
    assert callback.json()["detail"]["code"] == "GATEWAY_OIDC_REQUIRED_CLAIM_MISSING"
