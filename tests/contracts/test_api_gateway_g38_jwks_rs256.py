"""PHX-G38 JWKS / RS256 trusted context contracts."""

from __future__ import annotations

import json
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

SUBJECT = uuid4()
TENANT = uuid4()
CORR = str(uuid4())
KID = "eaos-test-key-1"


@pytest.fixture()
def rsa_material() -> tuple[bytes, str]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    numbers = private_key.public_key().public_numbers()
    other_numbers = (
        rsa.generate_private_key(public_exponent=65537, key_size=2048)
        .public_key()
        .public_numbers()
    )
    jwks = {
        "keys": [
            jwk_from_rsa_public_numbers(n=numbers.n, e=numbers.e, kid=KID),
            jwk_from_rsa_public_numbers(
                n=other_numbers.n,
                e=other_numbers.e,
                kid="other-key",
            ),
        ]
    }
    return private_pem, json.dumps(jwks)


@pytest.fixture(autouse=True)
def _reset_jwt(rsa_material: tuple[bytes, str]):
    _, jwks_json = rsa_material
    clear_jwks_cache()
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer="https://issuer.example/eaos",
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
            jwks_json=jwks_json,
        )
    )
    yield
    clear_jwks_cache()
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience=None,
            allow_dev_headers=True,
            require_jwt=False,
        )
    )


def _token(private_pem: bytes, *, kid: str = KID, **extra: object) -> str:
    claims = {
        "sub": str(SUBJECT),
        "eaos_tenant_id": str(TENANT),
        "eaos_subject_type": "human",
        "iss": "https://issuer.example/eaos",
        "aud": "eaos-api",
        "exp": int(time.time()) + 3600,
        "jti": CORR,
    }
    claims.update(extra)
    return mint_rs256_token(claims, private_key_pem=private_pem, kid=kid)


def test_rs256_bearer_derives_tenant_context(rsa_material: tuple[bytes, str]) -> None:
    private_pem, _ = rsa_material
    client = TestClient(create_app())
    response = client.get(
        "/v1/context",
        headers={
            "Authorization": f"Bearer {_token(private_pem)}",
            "X-Correlation-Id": "from-header",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["subject_id"] == str(SUBJECT)
    assert data["tenant_id"] == str(TENANT)
    assert data["correlation_id"] == "from-header"


def test_rs256_wrong_kid_rejected(rsa_material: tuple[bytes, str]) -> None:
    private_pem, _ = rsa_material
    client = TestClient(create_app())
    response = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {_token(private_pem, kid='missing-kid')}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "GATEWAY_JWT_INVALID"


def test_rs256_forged_signature_rejected(rsa_material: tuple[bytes, str]) -> None:
    private_pem, _ = rsa_material
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    other_pem = other.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    client = TestClient(create_app())
    response = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {_token(other_pem)}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "GATEWAY_JWT_INVALID"
