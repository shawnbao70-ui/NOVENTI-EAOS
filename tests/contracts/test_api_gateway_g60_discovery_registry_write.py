"""PHX-G60 OIDC Discovery → IdP registry writeback contracts."""

from __future__ import annotations

import time
from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
cryptography = pytest.importorskip("cryptography")
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import (
    JwtSettings,
    clear_jwks_cache,
    jwk_from_rsa_public_numbers,
    mint_rs256_token,
)
from api.gateway.context import configure_jwt_settings
from api.gateway.idp_registry import (
    clear_idp_registry,
    configure_idp_registry,
    list_idp_issuers,
)
from api.gateway.oidc import (
    OidcSettings,
    clear_oidc_discovery_cache,
    configure_oidc,
    maybe_write_discovery_to_registry,
)

GOVERNOR = uuid4()
SUBJECT = uuid4()
TENANT = uuid4()
CORR = str(uuid4())
OIDC_ISS = "https://writeback-idp.example"
JWKS_URL = "https://writeback-idp.example/oauth2/v1/keys"
KID = "wb-kid"


class _FakeDiscoveryClient:
    def __init__(self, document: dict) -> None:
        self.document = document
        self.calls = 0

    def fetch(self, url: str) -> dict:
        self.calls += 1
        return self.document


def _pem_and_jwk() -> tuple[bytes, dict[str, str]]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    numbers = private_key.public_key().public_numbers()
    return private_pem, jwk_from_rsa_public_numbers(n=numbers.n, e=numbers.e, kid=KID)


def _oidc_settings(**overrides):  # type: ignore[no-untyped-def]
    values = {
        "issuer": OIDC_ISS,
        "client_id": "eaos-client",
        "client_secret": "secret",
        "redirect_uri": "http://127.0.0.1:8000/v1/auth/oidc/callback",
        "authorization_endpoint": None,
        "token_endpoint": None,
        "scopes": "openid",
        "default_tenant_id": str(TENANT),
        "enabled": True,
        "discovery": True,
        "discovery_url": f"{OIDC_ISS}/.well-known/openid-configuration",
        "jwks_uri": None,
        "jwks_wire": False,
        "discovery_registry_write": True,
    }
    values.update(overrides)
    return OidcSettings(**values)


def _platform_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(GOVERNOR),
        "X-EAOS-Subject-Type": "human",
        "X-Correlation-Id": CORR,
    }


@pytest.fixture(autouse=True)
def _reset() -> None:
    configure_idp_registry(store="memory")
    clear_idp_registry()
    clear_jwks_cache()
    clear_oidc_discovery_cache()
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    configure_oidc(
        _oidc_settings(),
        discovery_client=_FakeDiscoveryClient(
            {
                "issuer": OIDC_ISS,
                "authorization_endpoint": f"{OIDC_ISS}/authorize",
                "token_endpoint": f"{OIDC_ISS}/token",
                "jwks_uri": JWKS_URL,
            }
        ),
    )
    yield
    clear_idp_registry()
    configure_idp_registry(store="memory")
    clear_jwks_cache()
    clear_oidc_discovery_cache()


def test_writeback_upserts_registry_and_status() -> None:
    result = maybe_write_discovery_to_registry()
    assert result["action"] == "created"
    assert result["issuer"] == OIDC_ISS
    assert result["jwks_url"] == JWKS_URL
    rows = list_idp_issuers(include_disabled=False)
    assert len(rows) == 1
    assert rows[0].jwks_url == JWKS_URL

    again = maybe_write_discovery_to_registry()
    assert again["action"] == "unchanged"

    client = TestClient(create_app())
    status = client.get("/v1/auth/idp/status")
    assert status.status_code == 200
    body = status.json()["data"]
    assert body["oidc"]["discovery_registry_write"] is True
    assert body["registry"]["discovery_write"]["action"] in {"unchanged", "created"}
    assert any(item["issuer"] == OIDC_ISS for item in body["registry"]["issuers"])


def test_env_issuer_still_wins_over_discovery_write() -> None:
    import json

    from api.gateway.auth_jwt import JwtIssuerBinding

    pem, jwk = _pem_and_jwk()
    maybe_write_discovery_to_registry()
    assert list_idp_issuers(include_disabled=False)[0].jwks_url == JWKS_URL

    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
            issuers=(
                JwtIssuerBinding(
                    issuer=OIDC_ISS,
                    jwks_json=json.dumps({"keys": [jwk]}),
                ),
            ),
        )
    )
    token = mint_rs256_token(
        {
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "eaos_subject_type": "human",
            "iss": OIDC_ISS,
            "aud": "eaos-api",
            "exp": int(time.time()) + 3600,
            "jti": str(uuid4()),
        },
        private_key_pem=pem,
        kid=KID,
    )
    client = TestClient(create_app())
    response = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["tenant_id"] == str(TENANT)


def test_platform_discovery_sync_endpoint() -> None:
    client = TestClient(create_app())
    denied = client.post("/v1/platform/idp/discovery/sync", json={})
    assert denied.status_code == 401

    synced = client.post(
        "/v1/platform/idp/discovery/sync",
        headers=_platform_headers(),
        json={},
    )
    assert synced.status_code == 200
    assert synced.json()["data"]["action"] in {"created", "unchanged", "updated"}
    assert synced.json()["data"]["issuer"] == OIDC_ISS


def test_writeback_disabled_is_noop() -> None:
    configure_oidc(
        _oidc_settings(discovery_registry_write=False),
        discovery_client=_FakeDiscoveryClient(
            {
                "issuer": OIDC_ISS,
                "authorization_endpoint": f"{OIDC_ISS}/authorize",
                "token_endpoint": f"{OIDC_ISS}/token",
                "jwks_uri": JWKS_URL,
            }
        ),
    )
    result = maybe_write_discovery_to_registry()
    assert result["action"] == "skipped"
    assert list_idp_issuers() == []


def test_writeback_fail_closed_without_discovery() -> None:
    configure_oidc(_oidc_settings(discovery=False, enabled=True, discovery_registry_write=True))
    with pytest.raises(Exception) as excinfo:
        maybe_write_discovery_to_registry(raise_on_error=True)
    assert "GATEWAY_OIDC_DISCOVERY_WRITE_FAILED" in str(excinfo.value)
