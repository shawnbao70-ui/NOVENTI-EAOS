"""PHX-G48 OIDC Discovery → JWT JWKS wire contracts."""

from __future__ import annotations

import json
import time
from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
cryptography = pytest.importorskip("cryptography")
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import (
    JwtIssuerBinding,
    JwtSettings,
    clear_jwks_cache,
    jwk_from_rsa_public_numbers,
    mint_hs256_token,
    mint_rs256_token,
)
from api.gateway.context import configure_jwt_settings
from api.gateway.oidc import (
    OidcSettings,
    clear_oidc_discovery_cache,
    configure_oidc,
    maybe_wire_discovery_jwks,
)

SUBJECT = uuid4()
TENANT = uuid4()
OIDC_ISS = "https://idp.example"
EAOS_ISS = "https://eaos.example/issuer"
JWKS_URL = "https://idp.example/oauth2/v1/keys"
KID = "wire-kid"
SECRET = "eaos-wire-hs256-secret"


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
        "jwks_wire": True,
    }
    values.update(overrides)
    return OidcSettings(**values)


@pytest.fixture(autouse=True)
def _reset() -> None:
    clear_jwks_cache()
    clear_oidc_discovery_cache()
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
    clear_jwks_cache()
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


def test_oidc_status_exposes_jwks_wire() -> None:
    client = TestClient(create_app())
    status = client.get("/v1/auth/oidc/status")
    assert status.status_code == 200
    data = status.json()["data"]
    assert data["jwks_wire"] is True
    assert data["jwks_uri"] == JWKS_URL


def test_wire_injects_discovery_jwks_binding() -> None:
    base = JwtSettings(
        secret=SECRET,
        issuer=EAOS_ISS,
        audience="eaos-api",
        allow_dev_headers=True,
        require_jwt=False,
    )
    wired = maybe_wire_discovery_jwks(base)
    assert len(wired.issuers) == 2
    assert wired.issuers[0] == JwtIssuerBinding(issuer=OIDC_ISS, jwks_url=JWKS_URL)
    assert wired.issuers[1] == JwtIssuerBinding(issuer=EAOS_ISS)


def test_wire_accepts_idp_rs256_bearer(monkeypatch: pytest.MonkeyPatch) -> None:
    pem, jwk = _pem_and_jwk()

    class _Resp:
        def read(self) -> bytes:
            return json.dumps({"keys": [jwk]}).encode("utf-8")

        def __enter__(self) -> _Resp:
            return self

        def __exit__(self, *args: object) -> bool:
            return False

    monkeypatch.setattr(
        "api.gateway.auth_jwt.urllib.request.urlopen",
        lambda *args, **kwargs: _Resp(),
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


def test_wire_preserves_eaos_hs256_bearer() -> None:
    token = mint_hs256_token(
        {
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "eaos_subject_type": "human",
            "iss": EAOS_ISS,
            "aud": "eaos-api",
            "exp": int(time.time()) + 3600,
            "jti": str(uuid4()),
        },
        secret=SECRET,
    )
    client = TestClient(create_app())
    response = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


def test_explicit_jwks_wins_over_wire() -> None:
    pem, jwk = _pem_and_jwk()
    explicit = JwtSettings(
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
    wired = maybe_wire_discovery_jwks(explicit)
    assert wired is explicit
    assert wired.issuers[0].jwks_json is not None
    assert wired.issuers[0].jwks_url is None


def test_wire_off_is_noop() -> None:
    configure_oidc(_oidc_settings(jwks_wire=False))
    base = JwtSettings(
        secret=SECRET,
        issuer=EAOS_ISS,
        audience="eaos-api",
        allow_dev_headers=True,
        require_jwt=False,
    )
    assert maybe_wire_discovery_jwks(base) is base


def test_wire_requires_discovery() -> None:
    configure_oidc(_oidc_settings(discovery=False, jwks_wire=True, enabled=True))
    with pytest.raises(HTTPException) as exc:
        maybe_wire_discovery_jwks(
            JwtSettings(
                secret=SECRET,
                issuer=EAOS_ISS,
                audience="eaos-api",
                allow_dev_headers=True,
                require_jwt=False,
            )
        )
    assert exc.value.status_code == 503
    assert exc.value.detail["code"] == "GATEWAY_OIDC_JWKS_WIRE_FAILED"


def test_wire_missing_jwks_uri_fail_closed() -> None:
    configure_oidc(
        _oidc_settings(),
        discovery_client=_FakeDiscoveryClient(
            {
                "issuer": OIDC_ISS,
                "authorization_endpoint": f"{OIDC_ISS}/authorize",
                "token_endpoint": f"{OIDC_ISS}/token",
            }
        ),
    )
    clear_oidc_discovery_cache()
    with pytest.raises(HTTPException) as exc:
        maybe_wire_discovery_jwks(
            JwtSettings(
                secret="",
                issuer=None,
                audience="eaos-api",
                allow_dev_headers=True,
                require_jwt=False,
            )
        )
    assert exc.value.detail["code"] == "GATEWAY_OIDC_JWKS_WIRE_FAILED"
