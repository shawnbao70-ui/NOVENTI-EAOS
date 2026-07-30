"""PHX-G82 JWT eaos_roles → ExecutionContext Roles Gate contracts."""

from __future__ import annotations

import time
from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings, mint_hs256_token
from api.gateway.context import configure_jwt_settings

SECRET = "eaos-g82-context-roles-secret"
TENANT = uuid4()
SUBJECT = uuid4()
CORR = "corr-g82"
JWT_SETTINGS = JwtSettings(
    secret=SECRET,
    issuer="https://issuer.example/eaos",
    audience="eaos-api",
    allow_dev_headers=True,
    require_jwt=False,
)


@pytest.fixture(autouse=True)
def _jwt() -> None:
    configure_jwt_settings(JWT_SETTINGS)
    yield
    configure_jwt_settings(JWT_SETTINGS)


def _token(**extra: object) -> str:
    claims: dict[str, object] = {
        "sub": str(SUBJECT),
        "eaos_tenant_id": str(TENANT),
        "eaos_subject_type": "human",
        "iss": "https://issuer.example/eaos",
        "aud": "eaos-api",
        "exp": int(time.time()) + 3600,
    }
    claims.update(extra)
    return mint_hs256_token(claims, secret=SECRET)


def test_bearer_eaos_roles_populate_context() -> None:
    client = TestClient(create_app())
    response = client.get(
        "/v1/context",
        headers={
            "Authorization": f"Bearer {_token(eaos_roles=['operator', 'viewer', 'operator'])}",
            "X-Correlation-Id": CORR,
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["roles"] == ["operator", "viewer"]
    assert data["tenant_id"] == str(TENANT)


def test_missing_eaos_roles_yields_empty_roles() -> None:
    client = TestClient(create_app())
    response = client.get(
        "/v1/context",
        headers={
            "Authorization": f"Bearer {_token()}",
            "X-Correlation-Id": CORR,
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["roles"] == []


def test_invalid_eaos_roles_type_rejected() -> None:
    client = TestClient(create_app())
    response = client.get(
        "/v1/context",
        headers={
            "Authorization": f"Bearer {_token(eaos_roles='operator')}",
            "X-Correlation-Id": CORR,
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "CTX_INVALID"


def test_invalid_eaos_roles_element_rejected() -> None:
    client = TestClient(create_app())
    response = client.get(
        "/v1/context",
        headers={
            "Authorization": f"Bearer {_token(eaos_roles=['ok', 1])}",
            "X-Correlation-Id": CORR,
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "CTX_INVALID"


def test_dev_headers_context_roles_empty() -> None:
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
    assert response.json()["data"]["roles"] == []


def test_echo_rejects_roles_body_override() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/v1/context/echo",
        headers={
            "Authorization": f"Bearer {_token(eaos_roles=['viewer'])}",
            "X-Correlation-Id": CORR,
            "Content-Type": "application/json",
        },
        json={"roles": ["admin"], "ping": True},
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "TERMINAL_CONTEXT_ELEVATION_DENIED"
    assert "roles" in detail["details"]["fields"]
