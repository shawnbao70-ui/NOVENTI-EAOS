"""PHX-G121 Identity Credential / Session Thin Probe contracts."""

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


def test_terminal_exposes_identity_credential_session_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminIdentityBindCredential"' in html
    assert 'id="btnAdminIdentityCreateSession"' in html
    assert 'id="btnAdminIdentityValidateSession"' in html
    assert 'id="identityCredentialId"' in html
    assert 'id="identitySecretHandle"' in html
    assert 'id="identitySessionId"' in html
    assert "Identity credential/session 薄探针（G121" in html
    assert "Identity Terminal 运维面齐" in html
    assert "identityCredentials" in js
    assert "identitySessions" in js
    assert "identitySessionValidation" in js
    assert "adminBindIdentityCredential" in js
    assert "adminCreateIdentitySession" in js
    assert "adminValidateIdentitySession" in js
    start = js.index("async function adminBindIdentityCredential")
    end = js.index("async function adminGrantIdentityGovernor")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "subjectId" in chunk
    assert "secret_handle" in chunk


def test_identity_credential_session_probe_api() -> None:
    client = TestClient(create_app(identity_service=IdentityService()))

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Bind identity credential" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminBindIdentityCredential" in script.text
    assert "adminCreateIdentitySession" in script.text

    registered = client.post(
        "/v1/identity/subjects",
        headers=_headers(),
        json={"subject_type": "human", "display_name": "G121-User"},
    )
    assert registered.status_code == 201
    subject_id = registered.json()["id"]

    bound = client.post(
        "/v1/identity/credentials",
        headers=_headers(),
        json={
            "subject_id": subject_id,
            "credential_kind": "password_hash",
            "secret_handle": "vault:ref/g121",
        },
    )
    assert bound.status_code == 201
    credential_id = bound.json()["id"]

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
