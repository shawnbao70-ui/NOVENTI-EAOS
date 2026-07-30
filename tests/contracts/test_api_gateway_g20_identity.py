"""PHX-G20 Gateway Identity HTTP surface contracts."""

from __future__ import annotations

from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.identity.service import IdentityService

ACTOR = str(uuid4())
TENANT = str(uuid4())
CORR = str(uuid4())


def _headers(subject_id: str = ACTOR, **extra: str) -> dict[str, str]:
    base = {
        "X-EAOS-Subject-Id": subject_id,
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": TENANT,
        "X-Correlation-Id": CORR,
    }
    base.update(extra)
    return base


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app(identity_service=IdentityService()))


def test_identity_requires_trusted_headers(client: TestClient) -> None:
    missing = client.post(
        "/v1/identity/subjects",
        json={"subject_type": "human", "display_name": "A"},
    )
    assert missing.status_code == 401


def test_register_and_resolve_subject(client: TestClient) -> None:
    created = client.post(
        "/v1/identity/subjects",
        headers=_headers(),
        json={"subject_type": "human", "display_name": "Ada"},
    )
    assert created.status_code == 201
    body = created.json()
    assert body["id"] == body["data"]
    subject_id = body["id"]
    resolved = client.get(
        f"/v1/identity/subjects/{subject_id}",
        headers=_headers(),
    )
    assert resolved.status_code == 200
    assert resolved.json()["display_name"] == "Ada"
    assert resolved.json()["subject_type"] == "human"


def test_register_rejects_context_override(client: TestClient) -> None:
    response = client.post(
        "/v1/identity/subjects",
        headers=_headers(),
        json={
            "subject_type": "human",
            "display_name": "X",
            "tenant_id": str(uuid4()),
            "platform_scope": True,
        },
    )
    # Closed RegisterSubjectRequest rejects unknown fields before domain elevation check.
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any("tenant_id" in str(item.get("loc", ())) for item in detail)


def test_resolve_missing_subject(client: TestClient) -> None:
    response = client.get(
        f"/v1/identity/subjects/{uuid4()}",
        headers=_headers(),
    )
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "IDENTITY_NOT_FOUND"


def test_register_rejects_ai_employee_type(client: TestClient) -> None:
    response = client.post(
        "/v1/identity/subjects",
        headers=_headers(),
        json={"subject_type": "ai_employee", "display_name": "Bot"},
    )
    # Closed subject_type enum excludes ai_employee (register via /ai-employees).
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert any("subject_type" in str(item.get("loc", ())) for item in detail)


def test_credential_session_validation_happy_path(client: TestClient) -> None:
    registered = client.post(
        "/v1/identity/subjects",
        headers=_headers(),
        json={"subject_type": "human", "display_name": "Session User"},
    )
    assert registered.status_code == 201
    subject_id = registered.json()["id"]

    bound = client.post(
        "/v1/identity/credentials",
        headers=_headers(),
        json={
            "subject_id": subject_id,
            "credential_kind": "password_hash",
            "secret_handle": "vault:ref/g20",
        },
    )
    assert bound.status_code == 201
    credential_id = bound.json()["id"]

    # create/validate require ctx.subject_id == credential/session subject
    subject_headers = _headers(subject_id=subject_id)
    session = client.post(
        "/v1/identity/sessions",
        headers=subject_headers,
        json={"credential_id": credential_id, "ttl_minutes": 30},
    )
    assert session.status_code == 201
    session_id = session.json()["session_id"]
    assert "expires_at" in session.json()

    validated = client.get(
        f"/v1/identity/sessions/{session_id}/validation",
        headers=subject_headers,
    )
    assert validated.status_code == 200
    assert validated.json()["valid"] is True
    assert validated.json()["status"] == "active"


def test_validate_session_wrong_subject_denied(client: TestClient) -> None:
    registered = client.post(
        "/v1/identity/subjects",
        headers=_headers(),
        json={"subject_type": "human", "display_name": "Owner"},
    )
    subject_id = registered.json()["id"]
    bound = client.post(
        "/v1/identity/credentials",
        headers=_headers(),
        json={
            "subject_id": subject_id,
            "credential_kind": "password_hash",
            "secret_handle": "vault:ref/deny",
        },
    )
    credential_id = bound.json()["id"]
    session = client.post(
        "/v1/identity/sessions",
        headers=_headers(subject_id=subject_id),
        json={"credential_id": credential_id},
    )
    session_id = session.json()["session_id"]

    other = client.get(
        f"/v1/identity/sessions/{session_id}/validation",
        headers=_headers(subject_id=str(uuid4())),
    )
    assert other.status_code == 404
    assert other.json()["detail"]["code"] == "IDENTITY_SESSION_NOT_FOUND"


def test_bind_allows_resource_subject_id(client: TestClient) -> None:
    registered = client.post(
        "/v1/identity/subjects",
        headers=_headers(),
        json={"subject_type": "service", "display_name": "Svc"},
    )
    subject_id = registered.json()["id"]
    bound = client.post(
        "/v1/identity/credentials",
        headers=_headers(),
        json={
            "subject_id": subject_id,
            "credential_kind": "api_key",
            "secret_handle": "vault:ok",
        },
    )
    assert bound.status_code == 201
