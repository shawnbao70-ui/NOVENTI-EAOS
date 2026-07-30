"""PHX-G22 Gateway Permission HTTP surface contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.permission.service import PermissionService

ADMIN = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _headers(subject_id: UUID = ADMIN, **extra: str) -> dict[str, str]:
    base = {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }
    base.update(extra)
    return base


@pytest.fixture()
def client() -> TestClient:
    service = PermissionService(
        grant_administrators={ADMIN},
        decision_auditors={ADMIN},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    return TestClient(create_app(permission_service=service))


def test_permission_requires_trusted_headers(client: TestClient) -> None:
    response = client.post(
        "/v1/permission/evaluations",
        json={"action": "read", "resource_type": "document"},
    )
    assert response.status_code == 401


def test_evaluate_default_deny(client: TestClient) -> None:
    response = client.post(
        "/v1/permission/evaluations",
        headers=_headers(),
        json={"action": "read", "resource_type": "document"},
    )
    assert response.status_code == 200
    assert response.json()["effect"] == "deny"
    assert "decision_id" in response.json()


def test_grant_evaluate_explain_and_effective(client: TestClient) -> None:
    principal = uuid4()
    granted = client.post(
        "/v1/permission/grants",
        headers=_headers(),
        json={
            "principal_id": str(principal),
            "resource_type": "document",
            "scope_level": "tenant",
            "actions": ["read"],
        },
    )
    assert granted.status_code == 201
    grant_id = granted.json()["id"]

    allowed = client.post(
        "/v1/permission/evaluations",
        headers=_headers(subject_id=principal),
        json={"action": "read", "resource_type": "document"},
    )
    assert allowed.status_code == 200
    assert allowed.json()["effect"] == "allow"
    decision_id = allowed.json()["decision_id"]

    explained = client.get(
        f"/v1/permission/decisions/{decision_id}/explanation",
        headers=_headers(subject_id=principal),
    )
    assert explained.status_code == 200
    assert explained.json()["effect"] == "allow"
    assert grant_id in explained.json()["matched_grant_ids"]

    effective = client.get(
        f"/v1/permission/principals/{principal}/effective-permissions",
        headers=_headers(subject_id=principal),
    )
    assert effective.status_code == 200
    assert any(item["grant_id"] == grant_id for item in effective.json())


def test_revoke_restores_deny(client: TestClient) -> None:
    principal = uuid4()
    granted = client.post(
        "/v1/permission/grants",
        headers=_headers(),
        json={
            "principal_id": str(principal),
            "resource_type": "record",
            "scope_level": "tenant",
            "actions": ["read"],
        },
    )
    grant_id = granted.json()["id"]
    revoked = client.post(
        f"/v1/permission/grants/{grant_id}/revocation",
        headers=_headers(),
        json={"reason": "cleanup", "expected_version": 1},
    )
    assert revoked.status_code == 200
    assert revoked.json()["ok"] is True
    denied = client.post(
        "/v1/permission/evaluations",
        headers=_headers(subject_id=principal),
        json={"action": "read", "resource_type": "record"},
    )
    assert denied.json()["effect"] == "deny"


def test_create_and_activate_policy_deny(client: TestClient) -> None:
    principal = uuid4()
    assert client.post(
        "/v1/permission/grants",
        headers=_headers(),
        json={
            "principal_id": str(principal),
            "resource_type": "document",
            "scope_level": "tenant",
            "actions": ["read"],
        },
    ).status_code == 201
    created = client.post(
        "/v1/permission/policies",
        headers=_headers(),
        json={
            "name": "deny-read",
            "rules": [
                {
                    "effect": "deny",
                    "actions": ["read"],
                    "resource_type": "document",
                    "scope_level": "tenant",
                }
            ],
        },
    )
    assert created.status_code == 201
    policy_id = created.json()["id"]
    activated = client.post(
        f"/v1/permission/policies/{policy_id}/activation",
        headers=_headers(),
        json={"reason": "go-live", "expected_version": 1},
    )
    assert activated.status_code == 200
    decision = client.post(
        "/v1/permission/evaluations",
        headers=_headers(subject_id=principal),
        json={"action": "read", "resource_type": "document"},
    )
    assert decision.json()["effect"] == "deny"


def test_grant_rejects_context_override(client: TestClient) -> None:
    response = client.post(
        "/v1/permission/grants",
        headers=_headers(),
        json={
            "principal_id": str(uuid4()),
            "resource_type": "document",
            "scope_level": "tenant",
            "actions": ["read"],
            "tenant_id": str(uuid4()),
            "platform_scope": True,
        },
    )
    # Closed GrantRequest rejects unknown fields before domain elevation check.
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any("tenant_id" in str(item.get("loc", ())) for item in detail)


def test_non_admin_cannot_grant(client: TestClient) -> None:
    response = client.post(
        "/v1/permission/grants",
        headers=_headers(subject_id=uuid4()),
        json={
            "principal_id": str(uuid4()),
            "resource_type": "document",
            "scope_level": "tenant",
            "actions": ["read"],
        },
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "PERMISSION_DENIED"


def test_effective_permissions_hidden_from_others(client: TestClient) -> None:
    principal = uuid4()
    assert client.post(
        "/v1/permission/grants",
        headers=_headers(),
        json={
            "principal_id": str(principal),
            "resource_type": "document",
            "scope_level": "tenant",
            "actions": ["read"],
        },
    ).status_code == 201
    stranger = client.get(
        f"/v1/permission/principals/{principal}/effective-permissions",
        headers=_headers(subject_id=uuid4()),
    )
    assert stranger.status_code == 403
