"""PHX-G137 Identity Credential Validate/Revoke & Session Revoke contracts."""

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
ACTOR = str(uuid4())
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


def _headers(subject_id: str = ACTOR) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": subject_id,
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": TENANT,
        "X-Correlation-Id": CORR,
    }


def test_terminal_exposes_identity_credential_session_revoke_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminIdentityValidateCredential"' in html
    assert 'id="btnAdminIdentityRevokeCredential"' in html
    assert 'id="btnAdminIdentityRevokeSession"' in html
    assert 'id="identityRevokeReason"' in html
    assert "Identity credential validate/revoke 与 session revoke 薄探针（G137" in html
    assert "adminValidateIdentityCredential" in js
    assert "adminRevokeIdentityCredential" in js
    assert "adminRevokeIdentitySession" in js
    assert "identityCredentialValidation" in js
    assert "identityCredentialRevocation" in js
    assert "identitySessionRevocation" in js
    start = js.index("async function adminValidateIdentityCredential")
    end = js.index("async function adminGrantIdentityGovernor")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "/v1/identity/ai-employees" not in chunk
    assert "/v1/identity/platform-governors" not in chunk


def test_identity_credential_session_revoke_probe_api() -> None:
    client = TestClient(create_app(identity_service=IdentityService()))

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Validate identity credential" in page.text
    assert "Revoke identity session" in page.text

    registered = client.post(
        "/v1/identity/subjects",
        headers=_headers(),
        json={"subject_type": "human", "display_name": "G137-User"},
    )
    assert registered.status_code == 201
    subject_id = registered.json()["id"]
    subject_headers = _headers(subject_id=subject_id)

    bound = client.post(
        "/v1/identity/credentials",
        headers=_headers(),
        json={
            "subject_id": subject_id,
            "credential_kind": "password_hash",
            "secret_handle": "vault:ref/g137",
        },
    )
    assert bound.status_code == 201
    credential_id = bound.json()["id"]

    validated = client.get(
        f"/v1/identity/credentials/{credential_id}/validation",
        headers=subject_headers,
    )
    assert validated.status_code == 200
    body = validated.json()
    assert body["valid"] is True
    assert body["status"] == "active"
    assert body["credential_id"] == credential_id
    assert "secret_handle" not in body

    session = client.post(
        "/v1/identity/sessions",
        headers=subject_headers,
        json={"credential_id": credential_id, "ttl_minutes": 30},
    )
    assert session.status_code == 201
    session_id = session.json()["session_id"]

    revoked_session = client.post(
        f"/v1/identity/sessions/{session_id}/revocation",
        headers=subject_headers,
        json={"reason": "g137 session revoke"},
    )
    assert revoked_session.status_code == 204

    after_revoke = client.get(
        f"/v1/identity/sessions/{session_id}/validation",
        headers=subject_headers,
    )
    assert after_revoke.status_code in {400, 403, 404, 409, 422}

    revoked_cred = client.post(
        f"/v1/identity/credentials/{credential_id}/revocation",
        headers=subject_headers,
        json={"reason": "g137 credential revoke"},
    )
    assert revoked_cred.status_code == 204

    status = client.get("/v1/identity/status")
    assert status.status_code == 200
    surfaces = status.json()["data"]["supported_surfaces"]
    assert "credential_validate" in surfaces
    assert "credential_revoke" in surfaces
    assert "session_revoke" in surfaces
