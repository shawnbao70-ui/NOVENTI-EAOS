"""Sample + Order Terminal demo surface contracts (knowledge-aligned handoff)."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID, uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

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


def _headers(*, subject: UUID, tenant: UUID) -> dict[str, str]:
    return {
        "X-EAOS-Subject-Id": str(subject),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(tenant),
        "X-Correlation-Id": str(uuid4()),
    }


def test_manifests_declare_sample_and_order_surfaces() -> None:
    product = json.loads(
        (ROOT / "packages" / "sample_product" / "manifest.json").read_text(encoding="utf-8")
    )
    ops = json.loads(
        (ROOT / "packages" / "sample_ops" / "manifest.json").read_text(encoding="utf-8")
    )
    product_keys = {item["surface_key"] for item in product["surfaces"]}
    ops_keys = {item["surface_key"] for item in ops["surfaces"]}
    assert "product.sample" in product_keys
    assert "ops.order" in ops_keys
    product_actions = {item["action_key"] for item in product["actions"]}
    ops_actions = {item["action_key"] for item in ops["actions"]}
    assert "sample.intake.compose" in product_actions
    assert "sample.quote.handoff" in product_actions
    assert "order.convert.compose" in ops_actions
    assert "order.approve.compose" in ops_actions
    assert "order.do.create" in ops_actions


def test_terminal_ui_exposes_sample_and_order_demo_queues() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="sampleFlowQueue"' in html
    assert 'id="orderFlowQueue"' in html
    assert "样品流程（演示）" in html
    assert "订单流程（演示）" in html
    assert "DEMO_SAMPLE_FLOW" in js
    assert "DEMO_ORDER_FLOW" in js
    assert "handoffSelectedSampleFlow" in js
    assert "handoffSelectedOrderFlow" in js
    assert '"product.sample": "sample.intake.compose"' in js
    assert '"ops.order": "order.convert.compose"' in js
    assert "demo_fixture_after_resolve_deny" not in js
    assert "handoff blocked (fail-closed)" in js


def test_demo_gateway_resolves_sample_and_order_actions() -> None:
    app = create_demo_app()
    client = TestClient(app)
    headers = _headers(
        subject=app.state.demo_seeded_subject_id,
        tenant=app.state.demo_seeded_tenant_id,
    )

    surfaces = client.get("/v1/packages/surfaces", headers=headers)
    assert surfaces.status_code == 200
    keys = {item["surface_key"] for item in surfaces.json()["data"]}
    assert "product.sample" in keys
    assert "ops.order" in keys

    sample = client.post(
        "/v1/packages/actions/resolve",
        headers=headers,
        json={"action_key": "sample.intake.compose"},
    )
    assert sample.status_code == 200
    assert sample.json()["package_key"] == "noventi.sample.product"
    assert sample.json()["high_impact"] is False

    approve = client.post(
        "/v1/packages/actions/resolve",
        headers=headers,
        json={"action_key": "order.approve.compose"},
    )
    assert approve.status_code == 200
    assert approve.json()["package_key"] == "noventi.sample.ops"
    assert approve.json()["high_impact"] is True

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "样品流程（演示）" in page.text
    assert "订单流程（演示）" in page.text
