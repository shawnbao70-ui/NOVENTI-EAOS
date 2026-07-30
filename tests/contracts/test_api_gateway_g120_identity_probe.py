"""PHX-G120 Identity Status / Subject Thin Probe contracts."""

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


def test_terminal_exposes_identity_probe_controls() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminIdentityStatus"' in html
    assert 'id="btnAdminIdentityRegisterSubject"' in html
    assert 'id="btnAdminIdentityResolveSubject"' in html
    assert 'id="identitySubjectId"' in html
    assert 'id="identityDisplayName"' in html
    assert "Identity 状态/subject 薄探针（G120" in html
    assert 'identityStatus: "/v1/identity/status"' in js
    assert 'identitySubjects: "/v1/identity/subjects"' in js
    assert "adminRegisterIdentitySubject" in js
    assert "adminResolveIdentitySubject" in js
    start = js.index("async function adminRegisterIdentitySubject")
    end = js.index("async function adminBindIdentityCredential")
    chunk = js[start:end]
    assert "tenant_id" not in chunk
    assert "platform_scope" not in chunk
    assert "/credentials" not in chunk
    assert "/sessions" not in chunk


def test_identity_status_and_probe_api() -> None:
    client = TestClient(create_app(identity_service=IdentityService()))

    status = client.get("/v1/identity/status")
    assert status.status_code == 200
    data = status.json()["data"]
    assert data["writable"] is False
    assert "subject_register" in data["supported_surfaces"]
    assert "subject_resolve" in data["supported_surfaces"]
    assert "credential_bind" in data["supported_surfaces"]
    assert "session_create" in data["supported_surfaces"]

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Identity status" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "adminRegisterIdentitySubject" in script.text

    created = client.post(
        "/v1/identity/subjects",
        headers=_headers(),
        json={"subject_type": "human", "display_name": "G120-Ada"},
    )
    assert created.status_code == 201
    subject_id = created.json()["id"]

    resolved = client.get(
        f"/v1/identity/subjects/{subject_id}",
        headers=_headers(),
    )
    assert resolved.status_code == 200
    assert resolved.json()["display_name"] == "G120-Ada"
    assert resolved.json()["subject_type"] == "human"
