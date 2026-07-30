"""PHX-G66 tenant IdP federation binding contracts."""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

fastapi = pytest.importorskip("fastapi")

from api.gateway import create_app
from api.gateway.auth_jwt import (
    JwtSettings,
    clear_jwks_cache,
    clear_runtime_denylist,
    mint_hs256_token,
)
from api.gateway.context import configure_jwt_settings
from api.gateway.oidc import (
    OidcSettings,
    clear_oidc_discovery_cache,
    clear_oidc_states,
    configure_oidc,
)
from api.gateway.tenant_idp_federation import (
    clear_tenant_idp_federation,
    configure_tenant_idp_federation,
    tenant_idp_federation_enabled,
)

GOVERNOR = uuid4()
SUBJECT = uuid4()
TENANT = uuid4()
OTHER = uuid4()
CORR = str(uuid4())
SECRET = "eaos-g66-secret"
OIDC_ISS = "https://idp-g66.example"
EAOS_ISS = "https://eaos.example/issuer"


class _FakeTokenClient:
    def __init__(self, *, id_claims: dict) -> None:
        self._id_claims = dict(id_claims)

    def exchange_code(self, **kwargs):  # type: ignore[no-untyped-def]
        token = mint_hs256_token(self._id_claims, secret="idp-secret")
        return {
            "id_token": token,
            "refresh_token": "refresh-g66",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

    def refresh(self, **kwargs):  # type: ignore[no-untyped-def]
        token = mint_hs256_token(self._id_claims, secret="idp-secret")
        return {
            "id_token": token,
            "refresh_token": "refresh-g66-2",
            "token_type": "Bearer",
            "expires_in": 3600,
        }


def _platform_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(GOVERNOR),
        "X-EAOS-Subject-Type": "human",
        "X-Correlation-Id": CORR,
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
        "rp_logout": False,
        "end_session_endpoint": None,
        "post_logout_redirect_uri": None,
    }
    values.update(overrides)
    return OidcSettings(**values)


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EAOS_TENANT_IDP_FEDERATION", raising=False)
    monkeypatch.delenv("EAOS_TENANT_IDP_FEDERATION_STORE", raising=False)
    clear_tenant_idp_federation()
    configure_tenant_idp_federation(enforce=None, store="memory")
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
    clear_tenant_idp_federation()
    configure_tenant_idp_federation(enforce=None, store="memory")
    clear_runtime_denylist()


def test_federation_default_off_and_status() -> None:
    assert tenant_idp_federation_enabled() is False
    client = TestClient(create_app())
    oidc = client.get("/v1/auth/oidc/status").json()["data"]
    assert oidc["tenant_idp_federation"] is False
    idp = client.get("/v1/auth/idp/status").json()["data"]
    assert idp["federation"]["enabled"] is False
    assert idp["federation"]["store"] == "process_memory"
    assert idp["federation"]["planes"] == ["oidc", "jwt"]


def test_platform_bind_list_unbind() -> None:
    client = TestClient(create_app())
    denied = client.get(f"/v1/platform/idp/federation/tenants/{TENANT}/bindings")
    assert denied.status_code == 401

    created = client.post(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
        json={"issuer": OIDC_ISS + "/"},
    )
    assert created.status_code == 201
    data = created.json()["data"]
    assert data["issuer"] == OIDC_ISS
    assert data["bound_tenant_id"] == str(TENANT)
    assert data["status"] == "active"
    assert "tenant_id" not in data

    listed = client.get(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
    )
    assert listed.status_code == 200
    assert listed.json()["meta"]["count"] == 1

    conflict = client.post(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
        json={"issuer": OIDC_ISS},
    )
    assert conflict.status_code == 409

    body_override = client.post(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
        json={"issuer": "https://other.example", "tenant_id": str(OTHER)},
    )
    assert body_override.status_code == 422
    locs = [tuple(err.get("loc", ())) for err in body_override.json()["detail"]]
    assert any("tenant_id" in loc for loc in locs)

    unbound = client.post(
        f"/v1/platform/idp/federation/bindings/{data['id']}/unbind",
        headers=_platform_headers(),
        json={},
    )
    assert unbound.status_code == 200
    assert unbound.json()["data"]["status"] == "disabled"


def test_oidc_fail_closed_without_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_TENANT_IDP_FEDERATION", "1")
    configure_tenant_idp_federation(enforce=None)
    client = TestClient(create_app())
    login = client.get("/v1/auth/oidc/login", follow_redirects=False)
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
            }
        ),
    )
    denied = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "auth-code", "state": state},
        headers={"Accept": "application/json"},
    )
    assert denied.status_code == 403
    assert denied.json()["detail"]["code"] == "GATEWAY_TENANT_IDP_FEDERATION_DENIED"


def test_oidc_allows_when_bound(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EAOS_TENANT_IDP_FEDERATION", "1")
    configure_tenant_idp_federation(enforce=None)
    client = TestClient(create_app())
    bind = client.post(
        f"/v1/platform/idp/federation/tenants/{TENANT}/bindings",
        headers=_platform_headers(),
        json={"issuer": OIDC_ISS},
    )
    assert bind.status_code == 201

    login = client.get("/v1/auth/oidc/login", follow_redirects=False)
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
            }
        ),
    )
    ok = client.get(
        "/v1/auth/oidc/callback",
        params={"code": "auth-code", "state": state},
        headers={"Accept": "application/json"},
    )
    assert ok.status_code == 200
    assert ok.json()["data"]["tenant_id"] == str(TENANT)

    status = client.get("/v1/auth/oidc/status").json()["data"]
    assert status["tenant_idp_federation"] is True
