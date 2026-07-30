"""PHX-G201 Terminal role catalog status surface contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

from fastapi.testclient import TestClient

from api.gateway import app
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]

def test_g201_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0220-terminal-role-catalog-status-surface.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G201_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G201_ARCHITECTURE_GATE.md").is_file()

def test_g201_terminal_ui_wired() -> None:
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    assert "function loadRoleCatalogStatus" in js
    assert ("PHX-G28" in js or "OpenAPI inventory posture" in js)
    assert 'rolesStatus: "/v1/permission/roles/status"' in js
    assert "source_counts" in js
    assert 'id="btnAdminRoleCatalogStatus"' in html
    assert 'id="roleCatalogAdminStatus"' in html
    assert 'id="btnRoleCatalogStatusRefresh"' in html
    assert 'id="roleCatalogStatusPosture"' in html
    assert "loadRoleCatalogStatus({ quiet: true })" in js
    assert 'api("GET", TERMINAL_PATHS.rolesStatus' in js
    assert "auth: true" in js
    assert "Cap" in js and "grant" in js.casefold()

def test_g201_roles_status_endpoint_live() -> None:
    from uuid import uuid4

    headers = {
        "X-EAOS-Subject-Id": str(uuid4()),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(uuid4()),
        "X-Correlation-ID": "g201-roles-status",
    }
    data = (
        TestClient(app)
        .get("/v1/permission/roles/status", headers=headers)
        .json()["data"]
    )
    assert "source_counts" in data
    assert set(data["source_counts"]) >= {"catalog", "oidc_map", "grant_map"}
    assert "role_grant_product" in data
    product = data["role_grant_product"]
    assert product.get("cap_is_grant") is False or "cap_is_grant" not in product
    assert product.get("auto_grant_from_role_enabled") is False

def test_g201_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U074" in ledger
    assert (
        ("PHX-G201" in tip or "PHX-G2" in tip)
        and ("PHX-G201" in manifest or "PHX-G2" in manifest)
        and ("PHX-G201" in status or "PHX-G2" in status)
    )
