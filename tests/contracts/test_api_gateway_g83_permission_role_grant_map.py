"""PHX-G83 Gateway Permission role grant map contracts."""

from __future__ import annotations

import time
from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings, mint_hs256_token
from api.gateway.context import configure_jwt_settings
from kernel.permission.role_grant_map import (
    configure_permission_role_grant_map,
    reset_permission_role_grant_map,
)
from kernel.permission.service import PermissionService

SECRET = "eaos-g83-role-grant-secret"
TENANT = uuid4()
SUBJECT = uuid4()
ADMIN = uuid4()
CORR = "corr-g83"
JWT_SETTINGS = JwtSettings(
    secret=SECRET,
    issuer="https://issuer.example/eaos",
    audience="eaos-api",
    allow_dev_headers=True,
    require_jwt=False,
)


class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


@pytest.fixture(autouse=True)
def _reset() -> None:
    reset_permission_role_grant_map()
    configure_jwt_settings(JWT_SETTINGS)
    yield
    reset_permission_role_grant_map()
    configure_jwt_settings(JWT_SETTINGS)


def _token(*, roles: list[str] | None = None) -> str:
    claims: dict[str, object] = {
        "sub": str(SUBJECT),
        "eaos_tenant_id": str(TENANT),
        "eaos_subject_type": "human",
        "iss": "https://issuer.example/eaos",
        "aud": "eaos-api",
        "exp": int(time.time()) + 3600,
    }
    if roles is not None:
        claims["eaos_roles"] = roles
    return mint_hs256_token(claims, secret=SECRET)


def _client() -> TestClient:
    service = PermissionService(
        grant_administrators={ADMIN},
        decision_auditors={ADMIN, SUBJECT},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    return TestClient(create_app(permission_service=service))


def test_bearer_roles_allow_via_map() -> None:
    configure_permission_role_grant_map(
        {"operator": frozenset({("document", "read")})}
    )
    client = _client()
    response = client.post(
        "/v1/permission/evaluations",
        headers={
            "Authorization": f"Bearer {_token(roles=['operator'])}",
            "X-Correlation-Id": CORR,
        },
        json={"action": "read", "resource_type": "document"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["effect"] == "allow"
    assert body["reason_code"] == "MATCHED_CONTEXT_ROLE"

    explained = client.get(
        f"/v1/permission/decisions/{body['decision_id']}/explanation",
        headers={
            "Authorization": f"Bearer {_token(roles=['operator'])}",
            "X-Correlation-Id": CORR,
        },
    )
    assert explained.status_code == 200
    assert explained.json()["matched_roles"] == ["operator"]


def test_dev_headers_roles_empty_cannot_allow_via_map() -> None:
    configure_permission_role_grant_map(
        {"operator": frozenset({("document", "read")})}
    )
    client = _client()
    response = client.post(
        "/v1/permission/evaluations",
        headers={
            "X-EAOS-Subject-Id": str(SUBJECT),
            "X-EAOS-Subject-Type": "human",
            "X-EAOS-Tenant-Id": str(TENANT),
            "X-Correlation-Id": CORR,
        },
        json={"action": "read", "resource_type": "document"},
    )
    assert response.status_code == 200
    assert response.json()["effect"] == "deny"


def test_evaluate_rejects_roles_body_override() -> None:
    configure_permission_role_grant_map(
        {"operator": frozenset({("document", "read")})}
    )
    client = _client()
    response = client.post(
        "/v1/permission/evaluations",
        headers={
            "Authorization": f"Bearer {_token(roles=[])}",
            "X-Correlation-Id": CORR,
        },
        json={
            "action": "read",
            "resource_type": "document",
            "roles": ["operator"],
        },
    )
    assert response.status_code == 422
    locs = [tuple(err.get("loc", ())) for err in response.json()["detail"]]
    assert any("roles" in loc for loc in locs)
