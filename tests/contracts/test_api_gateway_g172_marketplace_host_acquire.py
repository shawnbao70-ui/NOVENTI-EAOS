"""PHX-G172 Marketplace listing → Extension Host acquire contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path
from uuid import uuid4

import pytest
import yaml

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from api.gateway.demo import DEMO_EXTENSION_KEY, create_demo_app
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
MARKETPLACE = ROOT / "docs" / "api" / "marketplace.openapi.yaml"

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

def test_g172_docs_and_ui() -> None:
    assert (
        ROOT / "docs" / "decisions" / "ADR-0191-marketplace-listing-host-acquire.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G172_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G172_ARCHITECTURE_GATE.md").is_file()
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    assert "marketplaceListingHostAcquire" in js
    assert "adminAcquireListingToHost" in js
    assert "PHX-G172" in js
    assert 'id="btnAdminListingAcquireHost"' in html
    assert "eval(" not in js

def test_g172_openapi_host_acquire_path() -> None:
    spec = yaml.safe_load(MARKETPLACE.read_text(encoding="utf-8"))
    assert str(spec["info"]["version"]).startswith("1.2.")
    assert "/marketplace/listings/{listingId}/host-acquire" in spec["paths"]
    assert "HostAcquireResult" in spec["components"]["schemas"]

def test_g172_demo_host_acquire_and_idempotent() -> None:
    app = create_demo_app()
    client = TestClient(app)
    bootstrap = client.get("/v1/demo/bootstrap").json()["data"]
    assert bootstrap["milestone"] in {"PHX-G172", "PHX-G182"}
    listing_id = bootstrap["listing_id"]
    assert listing_id == str(app.state.demo_seeded_listing_id)
    headers = {
        "X-EAOS-Subject-Id": bootstrap["subject_id"],
        "X-EAOS-Tenant-Id": bootstrap["tenant_id"],
        "X-EAOS-Subject-Type": "human",
        "X-Correlation-Id": str(uuid4()),
    }
    first = client.post(
        f"/v1/marketplace/listings/{listing_id}/host-acquire",
        headers=headers,
    )
    assert first.status_code == 201
    body = first.json()["data"]
    assert body["package_key"] == DEMO_EXTENSION_KEY
    assert body["extension_id"]
    assert body["extension_status"] == "active"
    assert "no Marketplace arbitrary script" in " ".join(body.get("notes") or [])

    second = client.post(
        f"/v1/marketplace/listings/{listing_id}/host-acquire",
        headers=headers,
    )
    assert second.status_code == 201
    again = second.json()["data"]
    assert again["already_acquired"] is True
    assert again["extension_id"] == body["extension_id"]

def test_g172_non_allowlist_rejected() -> None:
    app = create_demo_app()
    client = TestClient(app)
    bootstrap = client.get("/v1/demo/bootstrap").json()["data"]
    headers = {
        "X-EAOS-Subject-Id": bootstrap["subject_id"],
        "X-EAOS-Tenant-Id": bootstrap["tenant_id"],
        "X-EAOS-Subject-Type": "human",
        "X-Correlation-Id": str(uuid4()),
    }
    created = client.post(
        "/v1/marketplace/listings",
        headers=headers,
        json={
            "package_key": "vendor.untrusted.panel",
            "package_version": "9.9.9",
            "required_permissions": ["terminal_extension:invoke"],
            "declared_events": [],
            "data_scope": "tenant.demo",
        },
    )
    assert created.status_code == 201
    listing_id = created.json()["data"]
    assert (
        client.post(
            f"/v1/marketplace/listings/{listing_id}/signature",
            headers=headers,
            json={"signature_ref": "sig:demo:untrusted"},
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/v1/marketplace/listings/{listing_id}/submit",
            headers=headers,
            json={},
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/v1/marketplace/listings/{listing_id}/review",
            headers=headers,
            json={"approve": True, "notes": "no"},
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/v1/marketplace/listings/{listing_id}/publish",
            headers=headers,
            json={},
        ).status_code
        == 200
    )
    denied = client.post(
        f"/v1/marketplace/listings/{listing_id}/host-acquire",
        headers=headers,
    )
    assert denied.status_code == 400
    detail = denied.json()["detail"]
    assert "allowlist" in detail["message"].casefold()

def test_g172_production_has_route_but_no_demo_bootstrap() -> None:
    client = TestClient(create_app())
    assert client.get("/v1/demo/bootstrap").status_code == 404
    # Route is mounted; without seed/grants it fails closed on auth/context.
    response = client.post(
        f"/v1/marketplace/listings/{uuid4()}/host-acquire",
        headers={"X-Correlation-Id": str(uuid4())},
    )
    assert response.status_code in {400, 401, 403, 404}

def test_g172_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U045" in ledger
    assert "PHX-G172" in tip
    assert "PHX-G172" in manifest
    assert "PHX-G172" in status or "PHX-G18" in status
