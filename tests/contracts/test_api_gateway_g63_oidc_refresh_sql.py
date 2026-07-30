"""PHX-G63 OIDC refresh binding SQL store contracts."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

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
from api.gateway.oidc_refresh_store import (
    configure_oidc_refresh_store,
    get_oidc_session,
    refresh_store_kind,
    refresh_store_label,
)
from kernel.infrastructure.persistence import create_session_factory, metadata

SECRET = "eaos-g63-secret"
SUBJECT = uuid4()
TENANT = uuid4()
OIDC_ISS = "https://idp-g63.example"
EAOS_ISS = "https://eaos.example/issuer"


class _FakeTokenClient:
    def __init__(self, *, id_claims: dict) -> None:
        self._id_claims = dict(id_claims)
        self.refresh_calls = 0

    def exchange_code(self, **kwargs):  # type: ignore[no-untyped-def]
        token = mint_hs256_token(self._id_claims, secret="idp-secret")
        return {
            "id_token": token,
            "refresh_token": "refresh-sql-1",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    def refresh(self, **kwargs):  # type: ignore[no-untyped-def]
        self.refresh_calls += 1
        token = mint_hs256_token(self._id_claims, secret="idp-secret")
        return {
            "id_token": token,
            "refresh_token": "refresh-sql-2",
            "token_type": "Bearer",
            "expires_in": 3600,
        }


def _engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.begin() as connection:
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS kernel")
        metadata.create_all(connection)
    return engine


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
        "rp_logout": False,
        "end_session_endpoint": None,
        "post_logout_redirect_uri": None,
    }
    values.update(overrides)
    return OidcSettings(**values)


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EAOS_OIDC_REFRESH_STORE", raising=False)
    monkeypatch.delenv("EAOS_DATABASE_URL", raising=False)
    configure_oidc_refresh_store(store="memory")
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
    configure_oidc(
        _oidc(),
        token_client=_FakeTokenClient(
            id_claims={
                "sub": str(SUBJECT),
                "eaos_tenant_id": str(TENANT),
                "nonce": "x",
            }
        ),
    )
    yield
    clear_oidc_states()
    configure_oidc_refresh_store(store="memory")
    clear_runtime_denylist()


def _login_json(client: TestClient) -> dict:
    login = client.get("/v1/auth/oidc/login", follow_redirects=False)
    assert login.status_code == 302
    query = parse_qs(urlparse(login.headers["location"]).query)
    state = query["state"][0]
    nonce = query["nonce"][0]
    configure_oidc(
        _oidc(),
        token_client=_FakeTokenClient(
            id_claims={
                "sub": str(SUBJECT),
                "eaos_tenant_id": str(TENANT),
                "nonce": nonce,
                "eaos_subject_type": "human",
            }
        ),
    )
    response = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "auth-code", "state": state},
        headers={"Accept": "application/json"},
    )
    assert response.status_code == 200
    return response.json()["data"]


def test_default_refresh_store_is_memory() -> None:
    assert refresh_store_kind() == "memory"
    assert refresh_store_label() == "process_memory"
    client = TestClient(create_app())
    status = client.get("/v1/auth/oidc/status")
    assert status.json()["data"]["refresh_store"] == "process_memory"


def test_sql_store_fail_closed_without_database_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_OIDC_REFRESH_STORE", "sql")
    configure_oidc_refresh_store(store=None)
    with pytest.raises(RuntimeError, match="EAOS_DATABASE_URL"):
        get_oidc_session("missing")


def test_sql_store_refresh_round_trip() -> None:
    factory = create_session_factory(_engine())
    configure_oidc_refresh_store(store="sql", session_factory=factory)
    assert refresh_store_label() == "sql"

    client = TestClient(create_app())
    login = _login_json(client)
    assert login["refresh_available"] is True
    old = login["access_token"]
    old_jti = verify_token(old, current_jwt_settings())["jti"]
    assert get_oidc_session(old_jti) is not None
    assert get_oidc_session(old_jti).refresh_token == "refresh-sql-1"

    refreshed = client.post(
        "/v1/auth/oidc/refresh",
        headers={"Authorization": f"Bearer {old}"},
    )
    assert refreshed.status_code == 200
    new_token = refreshed.json()["data"]["access_token"]
    assert get_oidc_session(old_jti) is None
    new_jti = verify_token(new_token, current_jwt_settings())["jti"]
    assert get_oidc_session(new_jti) is not None
    assert get_oidc_session(new_jti).refresh_token == "refresh-sql-2"

    status = client.get("/v1/auth/oidc/status")
    assert status.json()["data"]["refresh_store"] == "sql"
