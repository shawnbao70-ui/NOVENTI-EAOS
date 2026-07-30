"""PHX-G165 Terminal declared Package Surface projection contracts."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings
from api.gateway.demo import DEMO_ADMIN, DEMO_OPERATOR, DEMO_TENANT, create_demo_app

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


def _headers(*, subject: UUID, tenant: UUID) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(tenant),
        "X-Correlation-Id": str(uuid4()),
    }


def test_terminal_exposes_declared_package_surface_projection() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'data-surface="product"' in html
    assert 'data-surface="ops"' in html
    assert "PHX-G165" in html
    assert "BOOK23" in html
    assert "SURFACE_DEFAULT_ACTIONS" in js
    assert "loadPackageSurfaces" in js
    assert "packageSurfaces" in js
    assert "packageActionResolve" in js
    product = ROOT / "packages" / "sample_product" / "manifest.json"
    assert product.is_file()
    payload = json.loads(product.read_text(encoding="utf-8"))
    assert payload["package_key"] == "noventi.sample.product"
    assert any(item["surface_key"] == "product.catalog" for item in payload["surfaces"])


def test_demo_gateway_seeds_declared_product_and_ops_surfaces() -> None:
    app = create_demo_app()
    client = TestClient(app)
    subject = app.state.demo_seeded_subject_id
    tenant = app.state.demo_seeded_tenant_id
    headers = _headers(subject=subject, tenant=tenant)

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert 'data-surface="product"' in page.text
    assert "PHX-G165" in page.text

    surfaces = client.get("/v1/packages/surfaces", headers=headers)
    assert surfaces.status_code == 200
    rows = surfaces.json()["data"]
    keys = {item["surface_key"] for item in rows}
    assert "product.catalog" in keys
    assert "ops.workbench" in keys

    product_action = client.post(
        "/v1/packages/actions/resolve",
        headers=headers,
        json={"action_key": "product.offer.review"},
    )
    assert product_action.status_code == 200
    body = product_action.json()
    assert body["package_key"] == "noventi.sample.product"
    assert body["action_key"] == "product.offer.review"
    assert body["source"] == "package_manifest"

    ops_action = client.post(
        "/v1/packages/actions/resolve",
        headers=headers,
        json={"action_key": "ops.brief.compose"},
    )
    assert ops_action.status_code == 200
    assert ops_action.json()["package_key"] == "noventi.sample.ops"

    # Legacy paste IDs remain usable for Operator grants.
    legacy = client.get(
        "/v1/packages/surfaces",
        headers=_headers(subject=DEMO_OPERATOR, tenant=DEMO_TENANT),
    )
    assert legacy.status_code == 200
    legacy_keys = {item["surface_key"] for item in legacy.json()["data"]}
    assert "product.catalog" in legacy_keys
    assert "ops.workbench" in legacy_keys
    assert DEMO_ADMIN  # keep import used / bootstrap actor present
