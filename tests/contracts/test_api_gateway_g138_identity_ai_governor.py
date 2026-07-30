"""PHX-G138 Identity AI Employee / Platform Governor thin probe contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from kernel.identity.service import IdentityService

ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP = uuid4()
TENANT = str(uuid4())
CORR = str(uuid4())


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


def _platform_headers(subject_id: str | None = None) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": subject_id or str(BOOTSTRAP),
        "X-EAOS-Subject-Type": "service",
        "X-Correlation-Id": CORR,
    }


def _tenant_headers(subject_id: str | None = None) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": subject_id or str(BOOTSTRAP),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": TENANT,
        "X-Correlation-Id": CORR,
    }


def test_terminal_exposes_identity_ai_governor_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminIdentityGrantGovernor"' in html
    assert 'id="btnAdminIdentityRegisterAi"' in html
    assert 'id="btnAdminIdentityAssignAi"' in html
    assert 'id="btnAdminIdentityReassignAi"' in html
    assert 'id="identityAiSubjectId"' in html
    assert "Identity AI employee / platform governor 薄探针（G138" in html
    assert "adminGrantIdentityGovernor" in js
    assert "adminRegisterIdentityAi" in js
    assert "adminAssignIdentityAi" in js
    assert "adminReassignIdentityAi" in js
    start = js.index("async function adminGrantIdentityGovernor")
    end = js.index("async function adminGetOrganizationTenant")
    chunk = js[start:end]
    assert "platform_scope" not in chunk
    assert '"tenant_id"' not in chunk
    assert "to_tenant_id" in chunk  # allowed destination field on reassignment
    assert "identityPlatformGovernors" in chunk
    assert "identityAiEmployees" in chunk


def test_identity_ai_governor_probe_api() -> None:
    service = IdentityService(platform_governors={BOOTSTRAP})
    client = TestClient(create_app(identity_service=service))

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Register AI employee" in page.text
    assert "Grant platform identity governor" in page.text

    governor_subject = str(uuid4())
    granted = client.post(
        "/v1/identity/platform-governors",
        headers=_platform_headers(),
        json={"subject_id": governor_subject},
    )
    assert granted.status_code == 201
    assert "id" in granted.json()

    # Bootstrap loses authority once a persisted governor exists.
    denied = client.post(
        "/v1/identity/ai-employees",
        headers=_platform_headers(),
        json={
            "display_name": "Denied AI",
            "capabilities_profile": "default",
            "owner_policy": "platform",
        },
    )
    assert denied.status_code == 403

    registered = client.post(
        "/v1/identity/ai-employees",
        headers=_platform_headers(governor_subject),
        json={
            "display_name": "G138 Assistant",
            "capabilities_profile": "default",
            "owner_policy": "platform",
        },
    )
    assert registered.status_code == 201
    ai_id = registered.json()["id"]

    profile = client.get(
        f"/v1/identity/ai-employees/{ai_id}/profile",
        headers=_platform_headers(governor_subject),
    )
    assert profile.status_code == 200
    assert profile.json()["ai_subject_id"] == ai_id
    assert profile.json()["version"] == 1

    updated = client.patch(
        f"/v1/identity/ai-employees/{ai_id}/profile",
        headers=_platform_headers(governor_subject),
        json={
            "expected_version": 1,
            "capabilities_profile": "ops",
            "owner_policy": "platform",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["version"] == 2
    assert updated.json()["capabilities_profile_ref"] == "ops"

    assigned = client.post(
        f"/v1/identity/ai-employees/{ai_id}/assignments",
        headers=_tenant_headers(),
        json={"management_policy": "tenant_managed"},
    )
    assert assigned.status_code == 201

    archived = client.post(
        f"/v1/identity/ai-employees/{ai_id}/reassignments",
        headers=_platform_headers(governor_subject),
        json={"mode": "archive"},
    )
    assert archived.status_code == 201

    # Keep a second governor so revoke of the first is allowed after we add one.
    second = str(uuid4())
    assert (
        client.post(
            "/v1/identity/platform-governors",
            headers=_platform_headers(governor_subject),
            json={"subject_id": second},
        ).status_code
        == 201
    )
    revoked = client.post(
        f"/v1/identity/platform-governors/{second}/revocation",
        headers=_platform_headers(governor_subject),
        json={"reason": "g138 rotation"},
    )
    assert revoked.status_code == 204

    status = client.get("/v1/identity/status")
    surfaces = status.json()["data"]["supported_surfaces"]
    assert "platform_governor_grant" in surfaces
    assert "ai_employee_register" in surfaces
    assert "ai_employee_reassign" in surfaces
