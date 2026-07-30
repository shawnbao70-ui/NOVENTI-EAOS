"""PHX-G128 Permission Policy / Grant Manual Write Thin Probe contracts."""

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


def test_terminal_exposes_permission_policy_grant_write_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminPermissionCreatePolicy"' in html
    assert 'id="btnAdminPermissionActivatePolicy"' in html
    assert 'id="btnAdminPermissionCreateGrant"' in html
    assert 'id="btnAdminPermissionRevokeGrant"' in html
    assert 'id="permPolicyName"' in html
    assert "Permission policy/grant 手工写入薄探针（G128" in html
    assert "≠ Role→grant" in html
    assert "permissionPolicies" in js
    assert "permissionPolicyActivation" in js
    assert "permissionGrants" in js
    assert "permissionGrantRevocation" in js
    assert "adminCreatePermissionPolicy" in js
    assert "adminActivatePermissionPolicy" in js
    assert "adminCreatePermissionGrant" in js
    assert "adminRevokePermissionGrant" in js
    start = js.index("async function adminCreatePermissionPolicy")
    end = js.index("async function adminDeprecatePermissionPolicy")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "ROLE_GRANT_MAP" not in chunk
    assert "role_grant_map" not in chunk
    assert "/delegations" not in chunk
    assert "/deprecation" not in chunk
    assert "adminDelegatePermissionGrant" not in chunk


def test_permission_policy_grant_write_probe_api() -> None:
    service = PermissionService(
        grant_administrators={ADMIN},
        decision_auditors={ADMIN},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    client = TestClient(create_app(permission_service=service))

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Create permission policy" in page.text
    assert "Create permission grant" in page.text
    assert "≠ Role→grant" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminCreatePermissionPolicy" in script.text
    assert "adminCreatePermissionGrant" in script.text
    assert "adminRevokePermissionGrant" in script.text

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
    assert activated.json()["ok"] is True

    denied_by_policy = client.post(
        "/v1/permission/evaluations",
        headers=_headers(subject_id=principal),
        json={"action": "read", "resource_type": "document"},
    )
    assert denied_by_policy.json()["effect"] == "deny"

    revoked = client.post(
        f"/v1/permission/grants/{grant_id}/revocation",
        headers=_headers(),
        json={"reason": "cleanup", "expected_version": 1},
    )
    assert revoked.status_code == 200
    assert revoked.json()["ok"] is True
