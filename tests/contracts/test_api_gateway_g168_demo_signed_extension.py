"""PHX-G168 demo signed extension seed contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from api.gateway.demo import (
    DEMO_EXTENSION_KEY,
    DEMO_EXTENSION_VERSION,
    create_demo_app,
)

ROOT = Path(__file__).resolve().parents[2]


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


def test_g168_docs_and_terminal_autofill() -> None:
    assert (
        ROOT / "docs" / "decisions" / "ADR-0187-demo-signed-extension-seed.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G168_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G168_ARCHITECTURE_GATE.md").is_file()
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert "extension_id" in js
    assert "syncExtensionButtons" in js
    assert ("PHX-G28" in js or "OpenAPI inventory posture" in js)


def test_g168_bootstrap_includes_activated_extension_without_secrets() -> None:
    app = create_demo_app()
    client = TestClient(app)
    response = client.get("/v1/demo/bootstrap")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["available"] is True
    assert data["milestone"] in {"PHX-G168", "PHX-G172", "PHX-G182"}
    assert data["extension_id"] == str(app.state.demo_seeded_extension_id)
    assert data["extension_key"] == DEMO_EXTENSION_KEY
    assert data["extension_version"] == DEMO_EXTENSION_VERSION
    assert data["extensions_url"] == "/terminal/#extensions"
    blob = response.text.lower()
    assert "noventi-demo-extension-hmac" not in blob
    assert "access_token" not in data
    assert "password" not in data


def test_g168_seeded_extension_list_and_invoke() -> None:
    app = create_demo_app()
    client = TestClient(app)
    subject = str(app.state.demo_seeded_subject_id)
    tenant = str(app.state.demo_seeded_tenant_id)
    extension_id = str(app.state.demo_seeded_extension_id)
    headers = {
        "X-EAOS-Subject-Id": subject,
        "X-EAOS-Tenant-Id": tenant,
        "X-EAOS-Subject-Type": "human",
        "X-Correlation-Id": str(uuid4()),
    }
    listed = client.get("/v1/terminal/extensions", headers=headers)
    assert listed.status_code == 200
    items = listed.json()["data"]
    match = next(item for item in items if item["id"] == extension_id)
    assert match["extension_key"] == DEMO_EXTENSION_KEY
    assert match["status"] in {"active", "ACTIVE"}
    invoked = client.post(
        f"/v1/terminal/extensions/{extension_id}/actions",
        headers=headers,
        json={"action": "panel.render", "surface": "extensions"},
    )
    assert invoked.status_code == 200
    body = invoked.json()
    assert set(body.keys()) <= {"data", "audit_id"}
    data = body["data"]
    assert set(data.keys()) == {
        "extension_id",
        "action",
        "surface",
        "status",
        "executed",
    }
    assert data["extension_id"] == extension_id
    assert data["action"] == "panel.render"
    assert data["surface"] == "extensions"
    assert data["status"] == "accepted_sandboxed"
    assert data["executed"] is False

    empty = client.post(
        f"/v1/terminal/extensions/{extension_id}/actions",
        headers=headers,
        json={},
    )
    assert empty.status_code == 422


def test_g168_production_gateway_has_no_demo_bootstrap() -> None:
    client = TestClient(create_app())
    response = client.get("/v1/demo/bootstrap")
    assert response.status_code == 404


def test_g168_ledger_tip_manifest() -> None:
    ledger = (ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md").read_text(
        encoding="utf-8"
    )
    tip = (ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md").read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    assert "DAL-U041" in ledger
    assert "PHX-G168" in tip
    assert "PHX-G168" in manifest
