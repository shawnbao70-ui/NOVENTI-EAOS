"""PHX-G194 Terminal domain foundation status surface contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

from fastapi.testclient import TestClient

from api.gateway import app
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]

def test_g194_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0213-terminal-domain-foundation-status-surface.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G194_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G194_ARCHITECTURE_GATE.md").is_file()

def test_g194_terminal_ui_wired() -> None:
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    assert "function loadDomainFoundationStatus" in js
    assert "PHX-G194" in js
    assert 'terminalStatus: "/v1/terminal/status"' in js
    assert 'eventStatus: "/v1/events/status"' in js
    assert 'knowledgeStatus: "/v1/knowledge/status"' in js
    assert 'identityStatus: "/v1/identity/status"' in js
    assert 'organizationStatus: "/v1/organization/status"' in js
    assert 'marketplaceStatus: "/v1/marketplace/status"' in js
    assert '"/v1/permission/status"' in js
    assert "TERMINAL_PATHS.jwtStatus" in js
    assert "TERMINAL_PATHS.oidcStatus" in js
    assert "TERMINAL_PATHS.idpStatus" in js
    assert 'id="btnAdminDomainFoundationStatus"' in html
    assert 'id="domainFoundationStatus"' in html
    assert "loadDomainFoundationStatus({ quiet: true })" in js
    assert "execute_execution" in js
    assert "authorize_execution" in js
    assert "role_grant_auto_write" in js
    assert "jwt.require=" in js
    assert "oidc.login_product=" in js
    assert "idp.federation=" in js

def test_g194_status_endpoints_live() -> None:
    client = TestClient(app)
    for path in (
        "/v1/twin/status",
        "/v1/brain/status",
        "/v1/ai/status",
        "/v1/workflow/status",
        "/v1/packages/status",
        "/v1/terminal/status",
        "/v1/events/status",
        "/v1/knowledge/status",
        "/v1/identity/status",
        "/v1/organization/status",
        "/v1/marketplace/status",
        "/v1/permission/status",
        "/v1/auth/jwt/status",
        "/v1/auth/oidc/status",
        "/v1/auth/idp/status",
    ):
        data = client.get(path).json()["data"]
        if path.endswith("/oidc/status"):
            assert "enabled" in data
            assert "oidc_login_product" in data
        else:
            assert data.get("writable") is False

def test_g194_terminal_status_lists_extension_lifecycle_surfaces() -> None:
    client = TestClient(app)
    surfaces = client.get("/v1/terminal/status").json()["data"]["supported_surfaces"]
    for name in (
        "extension_list",
        "extension_register",
        "extension_activate",
        "extension_revoke",
        "extension_invoke",
    ):
        assert name in surfaces, name

def test_g194_ledger_tip_manifest_baseline() -> None:
    assert sdk_version == "0.2.5"
    assert_current_baseline()
    ledger = (ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md").read_text(
        encoding="utf-8"
    )
    tip = (ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md").read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    status = (ROOT / "docs" / "project" / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "DAL-U067" in ledger
    assert ("PHX-G194" in tip or "PHX-G2" in tip) and ("PHX-G194" in manifest or "PHX-G2" in manifest) and ("PHX-G2" in status)
