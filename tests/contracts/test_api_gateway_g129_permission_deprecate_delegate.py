"""PHX-G129 Permission Deprecate / Delegate Thin Probe contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from kernel.permission.service import PermissionService

ROOT = Path(__file__).resolve().parents[2]
ADMIN = uuid4()
TENANT = uuid4()
CORR = str(uuid4())


class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


@pytest.fixture(autouse=True)
def _reset() -> None:
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


def _headers(subject_id: UUID = ADMIN) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject_id),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(TENANT),
        "X-Correlation-Id": CORR,
    }


def test_terminal_exposes_permission_deprecate_delegate_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminPermissionDeprecatePolicy"' in html
    assert 'id="btnAdminPermissionDelegateGrant"' in html
    assert 'id="permDelegateePrincipalId"' in html
    assert "Permission deprecate/delegate 薄探针（G129" in html
    assert "permissionPolicyDeprecation" in js
    assert "permissionGrantDelegations" in js
    assert "adminDeprecatePermissionPolicy" in js
    assert "adminDelegatePermissionGrant" in js
    start = js.index("async function adminDeprecatePermissionPolicy")
    end = js.index("async function adminEventDeliveryStats")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "ROLE_GRANT_MAP" not in chunk
    assert "role_grant_map" not in chunk
    assert "/revocation" not in chunk
    assert "/activation" not in chunk


def test_permission_deprecate_delegate_probe_api() -> None:
    service = PermissionService(
        grant_administrators={ADMIN},
        decision_auditors={ADMIN},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    client = TestClient(create_app(permission_service=service))

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Deprecate permission policy" in page.text
    assert "Delegate permission grant" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminDeprecatePermissionPolicy" in script.text
    assert "adminDelegatePermissionGrant" in script.text

    parent_principal = uuid4()
    child_principal = uuid4()
    granted = client.post(
        "/v1/permission/grants",
        headers=_headers(),
        json={
            "principal_id": str(parent_principal),
            "resource_type": "document",
            "scope_level": "tenant",
            "actions": ["read", "write"],
            "delegable": True,
            "delegation_depth": 1,
        },
    )
    assert granted.status_code == 201
    grant_id = granted.json()["id"]

    delegated = client.post(
        f"/v1/permission/grants/{grant_id}/delegations",
        headers=_headers(subject_id=parent_principal),
        json={
            "delegatee_principal_id": str(child_principal),
            "scope_level": "tenant",
            "actions": ["read"],
            "expected_version": 1,
        },
    )
    assert delegated.status_code == 201
    assert "id" in delegated.json()

    child_allowed = client.post(
        "/v1/permission/evaluations",
        headers=_headers(subject_id=child_principal),
        json={"action": "read", "resource_type": "document"},
    )
    assert child_allowed.status_code == 200
    assert child_allowed.json()["effect"] == "allow"

    created = client.post(
        "/v1/permission/policies",
        headers=_headers(),
        json={
            "name": f"deny-read-{uuid4().hex[:8]}",
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
        json={"expected_version": 1},
    )
    assert activated.status_code == 200

    denied = client.post(
        "/v1/permission/evaluations",
        headers=_headers(subject_id=child_principal),
        json={"action": "read", "resource_type": "document"},
    )
    assert denied.json()["effect"] == "deny"

    deprecated = client.post(
        f"/v1/permission/policies/{policy_id}/deprecation",
        headers=_headers(),
        json={"reason": "retire", "expected_version": 2},
    )
    assert deprecated.status_code == 200
    assert deprecated.json()["ok"] is True

    restored = client.post(
        "/v1/permission/evaluations",
        headers=_headers(subject_id=child_principal),
        json={"action": "read", "resource_type": "document"},
    )
    assert restored.json()["effect"] == "allow"
