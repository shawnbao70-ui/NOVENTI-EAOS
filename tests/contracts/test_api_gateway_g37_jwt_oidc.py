"""PHX-G37 JWT/OIDC trusted context contracts."""

from __future__ import annotations

import time
from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings, mint_hs256_token
from api.gateway.context import configure_jwt_settings

SECRET = "eaos-test-jwt-secret"
SUBJECT = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


@pytest.fixture(autouse=True)
def _jwt_settings() -> None:
    configure_jwt_settings(
        JwtSettings(
            secret=SECRET,
            issuer="https://issuer.example/eaos",
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    yield
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience=None,
            allow_dev_headers=True,
            require_jwt=False,
        )
    )


def _token(**extra: object) -> str:
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
    return mint_hs256_token(claims, secret=SECRET)


def test_dev_headers_still_work_when_jwt_optional() -> None:
    client = TestClient(create_app())
    response = client.get(
        "/v1/context",
        headers={
            "X-EAOS-Subject-Id": str(SUBJECT),
            "X-EAOS-Subject-Type": "human",
            "X-EAOS-Tenant-Id": str(TENANT),
            "X-Correlation-Id": CORR,
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["tenant_id"] == str(TENANT)


def test_bearer_jwt_derives_tenant_context() -> None:
    client = TestClient(create_app())
    response = client.get(
        "/v1/context",
        headers={
            "Authorization": f"Bearer {_token()}",
            "X-Correlation-Id": "from-header",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["subject_id"] == str(SUBJECT)
    assert data["tenant_id"] == str(TENANT)
    assert data["platform_scope"] is False
    assert data["correlation_id"] == "from-header"


def test_forged_signature_rejected() -> None:
    client = TestClient(create_app())
    bad = mint_hs256_token(
        {
            "sub": str(SUBJECT),
            "eaos_tenant_id": str(TENANT),
            "iss": "https://issuer.example/eaos",
            "aud": "eaos-api",
            "exp": int(time.time()) + 3600,
        },
        secret="wrong-secret",
    )
    response = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {bad}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "GATEWAY_JWT_INVALID"


def test_platform_scope_claim_denied_on_tenant_plane() -> None:
    client = TestClient(create_app())
    response = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {_token(eaos_platform_scope=True)}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "CTX_PLATFORM_ELEVATION_DENIED"


def test_require_jwt_blocks_header_only() -> None:
    configure_jwt_settings(
        JwtSettings(
            secret=SECRET,
            issuer="https://issuer.example/eaos",
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=True,
        )
    )
    client = TestClient(create_app())
    denied = client.get(
        "/v1/context",
        headers={
            "X-EAOS-Subject-Id": str(SUBJECT),
            "X-EAOS-Tenant-Id": str(TENANT),
            "X-Correlation-Id": CORR,
        },
    )
    assert denied.status_code == 401
    assert denied.json()["detail"]["code"] == "GATEWAY_JWT_REQUIRED"

    ok = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {_token()}"},
    )
    assert ok.status_code == 200


def test_disallow_dev_headers_blocks_header_only_tenant_and_platform() -> None:
    """Production posture: EAOS_ALLOW_DEV_CONTEXT_HEADERS=0 → header-only 401."""

    configure_jwt_settings(
        JwtSettings(
            secret=SECRET,
            issuer="https://issuer.example/eaos",
            audience="eaos-api",
            allow_dev_headers=False,
            require_jwt=False,
        )
    )
    client = TestClient(create_app())
    tenant_denied = client.get(
        "/v1/context",
        headers={
            "X-EAOS-Subject-Id": str(SUBJECT),
            "X-EAOS-Subject-Type": "human",
            "X-EAOS-Tenant-Id": str(TENANT),
            "X-Correlation-Id": CORR,
        },
    )
    assert tenant_denied.status_code == 401
    assert tenant_denied.json()["detail"]["code"] == "GATEWAY_AUTH_REQUIRED"

    platform_denied = client.get(
        "/v1/platform/roles",
        headers={
            "X-EAOS-Subject-Id": str(SUBJECT),
            "X-EAOS-Subject-Type": "human",
            "X-Correlation-Id": CORR,
        },
    )
    assert platform_denied.status_code == 401
    assert platform_denied.json()["detail"]["code"] == "GATEWAY_AUTH_REQUIRED"

    ok = client.get(
        "/v1/context",
        headers={"Authorization": f"Bearer {_token()}"},
    )
    assert ok.status_code == 200
