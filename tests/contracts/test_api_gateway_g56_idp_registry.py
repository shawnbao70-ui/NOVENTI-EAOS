"""PHX-G56 multi-IdP write registry contracts."""

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
    JwtIssuerBinding,
    JwtSettings,
    clear_jwks_cache,
    jwk_from_rsa_public_numbers,
    mint_rs256_token,
)
from api.gateway.context import configure_jwt_settings
from api.gateway.idp_registry import clear_idp_registry, configure_idp_registry

GOVERNOR = uuid4()
SUBJECT = uuid4()
TENANT = uuid4()
CORR = str(uuid4())
REG_ISS = "https://registry-idp.example/eaos"
ENV_ISS = "https://env-idp.example/eaos"
KID = "reg-kid"


def _platform_headers() -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(GOVERNOR),
        "X-EAOS-Subject-Type": "human",
        "X-Correlation-Id": CORR,
    }


def _pem_and_jwk() -> tuple[bytes, dict[str, str]]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    numbers = private_key.public_key().public_numbers()
    return private_pem, jwk_from_rsa_public_numbers(n=numbers.n, e=numbers.e, kid=KID)


@pytest.fixture(autouse=True)
def _reset() -> None:
    configure_idp_registry(store="memory")
    clear_idp_registry()
    clear_jwks_cache()
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    yield
    clear_idp_registry()
    configure_idp_registry(store="memory")
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


def test_platform_registry_create_list_disable() -> None:
    client = TestClient(create_app())
    denied = client.get("/v1/platform/idp/issuers")
    assert denied.status_code == 401

    created = client.post(
        "/v1/platform/idp/issuers",
        headers=_platform_headers(),
        json={
            "issuer": REG_ISS,
            "jwks_url": "https://registry-idp.example/jwks",
        },
    )
    assert created.status_code == 201
    data = created.json()["data"]
    assert data["issuer"] == REG_ISS
    assert data["status"] == "active"
    assert data["has_jwks_json"] is False
    issuer_id = data["id"]

    listed = client.get("/v1/platform/idp/issuers", headers=_platform_headers())
    assert listed.status_code == 200
    assert listed.json()["meta"]["count"] == 1

    status = client.get("/v1/auth/idp/status")
    assert status.status_code == 200
    body = status.json()["data"]
    assert body["registry"]["writable"] is True
    assert body["registry"]["store"] == "process_memory"
    assert any(item["issuer"] == REG_ISS for item in body["registry"]["issuers"])
    dumped = json.dumps(body["registry"])
    assert '"jwks_json"' not in dumped
    assert "keys" not in dumped

    disabled = client.post(
        f"/v1/platform/idp/issuers/{issuer_id}/disable",
        headers=_platform_headers(),
        json={},
    )
    assert disabled.status_code == 200
    assert disabled.json()["data"]["status"] == "disabled"


def test_registry_issuer_accepted_for_bearer_jwt() -> None:
    pem, jwk = _pem_and_jwk()
    client = TestClient(create_app())
    created = client.post(
        "/v1/platform/idp/issuers",
        headers=_platform_headers(),
        json={"issuer": REG_ISS, "jwks_json": {"keys": [jwk]}},
    )
    assert created.status_code == 201

    token = mint_rs256_token(
        {
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "eaos_subject_type": "human",
            "iss": REG_ISS,
            "aud": "eaos-api",
            "exp": int(time.time()) + 3600,
            "jti": str(uuid4()),
        },
        private_key_pem=pem,
        kid=KID,
    )
    response = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["tenant_id"] == str(TENANT)


def test_env_issuer_wins_over_registry_duplicate() -> None:
    pem, jwk = _pem_and_jwk()
    client = TestClient(create_app())
    # Registry first with empty keys; env binding configured after must win at verify time
    created = client.post(
        "/v1/platform/idp/issuers",
        headers=_platform_headers(),
        json={"issuer": ENV_ISS, "jwks_json": {"keys": []}},
    )
    assert created.status_code == 201
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
            issuers=(
                JwtIssuerBinding(
                    issuer=ENV_ISS,
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
            "iss": ENV_ISS,
            "aud": "eaos-api",
            "exp": int(time.time()) + 3600,
            "jti": str(uuid4()),
        },
        private_key_pem=pem,
        kid=KID,
    )
    response = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


def test_create_requires_jwks_material() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/v1/platform/idp/issuers",
        headers=_platform_headers(),
        json={"issuer": REG_ISS},
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "GATEWAY_IDP_INVALID"
