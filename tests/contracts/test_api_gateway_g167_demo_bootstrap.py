"""PHX-G167 demo bootstrap context contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from api.gateway.demo import create_demo_app

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


def test_g167_docs_and_terminal_probe() -> None:
    assert (ROOT / "docs" / "decisions" / "ADR-0186-demo-bootstrap-context.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G167_ACCEPTANCE.md").is_file()
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert "demoBootstrap" in js
    assert "loadDemoBootstrap" in js
    assert (
        "PHX-G167" in js
        or "PHX-G168" in js
        or "PHX-G172" in js
        or "PHX-G182" in js
    )


def test_g167_demo_bootstrap_returns_seed_without_secrets() -> None:
    app = create_demo_app()
    client = TestClient(app)
    response = client.get("/v1/demo/bootstrap")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["available"] is True
    assert data["milestone"] in {"PHX-G167", "PHX-G168", "PHX-G172", "PHX-G182"}
    assert data["subject_id"] == str(app.state.demo_seeded_subject_id)
    assert data["tenant_id"] == str(app.state.demo_seeded_tenant_id)
    assert "product.catalog" in data["declared_surface_keys"]
    assert "ops.workbench" in data["declared_surface_keys"]
    required = {
        "available",
        "milestone",
        "subject_id",
        "tenant_id",
        "subject_type",
        "declared_surface_keys",
        "product_url",
        "ops_url",
        "notes",
    }
    assert required <= set(data.keys())
    assert "access_token" not in data
    assert "refresh_token" not in data
    assert "password" not in data


def test_g167_production_gateway_has_no_demo_bootstrap() -> None:
    client = TestClient(create_app())
    response = client.get("/v1/demo/bootstrap")
    assert response.status_code == 404


def test_g167_ledger_tip_manifest() -> None:
    ledger = (ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md").read_text(
        encoding="utf-8"
    )
    tip = (ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md").read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    assert "DAL-U040" in ledger
    assert "PHX-G167" in tip
    assert "PHX-G167" in manifest
