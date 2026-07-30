"""PHX-G45 multi-issuer JWKS allowlist + kid-miss refresh contracts."""

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
    verify_token,
)
from api.gateway.context import configure_jwt_settings

SUBJECT = uuid4()
TENANT = uuid4()
ISS_A = "https://idp-a.example/eaos"
ISS_B = "https://idp-b.example/eaos"
KID_A = "kid-a"
KID_B = "kid-b"
KID_ROTATED = "kid-rotated"


def _pem_and_jwk(kid: str) -> tuple[bytes, dict[str, str]]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    numbers = private_key.public_key().public_numbers()
    return private_pem, jwk_from_rsa_public_numbers(n=numbers.n, e=numbers.e, kid=kid)


@pytest.fixture()
def dual_issuers() -> dict[str, object]:
    pem_a, jwk_a = _pem_and_jwk(KID_A)
    pem_b, jwk_b = _pem_and_jwk(KID_B)
    settings = JwtSettings(
        secret="",
        issuer=None,
        audience="eaos-api",
        allow_dev_headers=True,
        require_jwt=False,
        issuers=(
            JwtIssuerBinding(issuer=ISS_A, jwks_json=json.dumps({"keys": [jwk_a]})),
            JwtIssuerBinding(issuer=ISS_B, jwks_json=json.dumps({"keys": [jwk_b]})),
        ),
    )
    clear_jwks_cache()
    configure_jwt_settings(settings)
    yield {"pem_a": pem_a, "pem_b": pem_b, "settings": settings}
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


def _token(private_pem: bytes, *, iss: str, kid: str, **extra: object) -> str:
    claims = {
        "sub": str(SUBJECT),
        "eaos_tenant_id": str(TENANT),
        "eaos_subject_type": "human",
        "iss": iss,
        "aud": "eaos-api",
        "exp": int(time.time()) + 3600,
        "jti": str(uuid4()),
    }
    claims.update(extra)
    return mint_rs256_token(claims, private_key_pem=private_pem, kid=kid)


def test_multi_issuer_accepts_allowlisted_iss(dual_issuers: dict[str, object]) -> None:
    client = TestClient(create_app())
    response = client.get(
        "/v1/context",
        headers={
            "Authorization": (
                f"Bearer {_token(dual_issuers['pem_a'], iss=ISS_A, kid=KID_A)}"  # type: ignore[arg-type]
            )
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["tenant_id"] == str(TENANT)

    response_b = client.get(
        "/v1/context",
        headers={
            "Authorization": (
                f"Bearer {_token(dual_issuers['pem_b'], iss=ISS_B, kid=KID_B)}"  # type: ignore[arg-type]
            )
        },
    )
    assert response_b.status_code == 200


def test_multi_issuer_rejects_unknown_iss(dual_issuers: dict[str, object]) -> None:
    client = TestClient(create_app())
    response = client.get(
        "/v1/context",
        headers={
            "Authorization": (
                f"Bearer {_token(dual_issuers['pem_a'], iss='https://evil.example', kid=KID_A)}"  # type: ignore[arg-type]
            )
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "GATEWAY_JWT_INVALID"


def test_multi_issuer_rejects_cross_issuer_key(dual_issuers: dict[str, object]) -> None:
    client = TestClient(create_app())
    # Token claims iss=A but signed with B's key / kid-b not in A's JWKS
    response = client.get(
        "/v1/context",
        headers={
            "Authorization": (
                f"Bearer {_token(dual_issuers['pem_b'], iss=ISS_A, kid=KID_B)}"  # type: ignore[arg-type]
            )
        },
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "GATEWAY_JWT_INVALID"


def test_jwks_url_kid_miss_refreshes_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    pem, jwk_new = _pem_and_jwk(KID_ROTATED)
    _, jwk_old = _pem_and_jwk("stale-kid")
    url = "https://jwks.example/keys.json"
    fetches: list[dict[str, object]] = []

    class _Resp:
        def __init__(self, payload: dict[str, object]) -> None:
            self._raw = json.dumps(payload).encode("utf-8")

        def read(self) -> bytes:
            return self._raw

        def __enter__(self) -> _Resp:
            return self

        def __exit__(self, *args: object) -> bool:
            return False

    def fake_urlopen(request_url: str, timeout: float = 5):  # type: ignore[no-untyped-def]
        assert request_url == url
        if not fetches:
            fetches.append({"keys": [jwk_old]})
            return _Resp(fetches[0])
        fetches.append({"keys": [jwk_new]})
        return _Resp(fetches[1])

    monkeypatch.setattr("api.gateway.auth_jwt.urllib.request.urlopen", fake_urlopen)
    clear_jwks_cache()
    settings = JwtSettings(
        secret="",
        issuer=None,
        audience="eaos-api",
        allow_dev_headers=True,
        require_jwt=False,
        issuers=(JwtIssuerBinding(issuer=ISS_A, jwks_url=url),),
    )
    # Prime cache with stale JWKS (no rotated kid)
    configure_jwt_settings(settings)
    token = _token(pem, iss=ISS_A, kid=KID_ROTATED)
    claims = verify_token(token, settings)
    assert claims["iss"] == ISS_A
    assert len(fetches) == 2
