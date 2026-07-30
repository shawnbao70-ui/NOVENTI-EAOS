"""Foundation harden — Ops health/release/adapters/context closed response_models."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.ops import (
    AdaptersEnvelope,
    ContextEchoEnvelope,
    ContextEnvelope,
    HealthEnvelope,
    ReleaseEnvelope,
)

ROOT = Path(__file__).resolve().parents[2]


def _route(path: str, method: str):
    app = create_app()
    for route in app.routes:
        if getattr(route, "path", None) == path and method in getattr(
            route, "methods", set()
        ):
            return route
    raise AssertionError(f"missing route {method} {path}")


def test_ops_routes_use_closed_response_models() -> None:
    assert _route("/v1/health", "GET").response_model is HealthEnvelope
    assert _route("/v1/release", "GET").response_model is ReleaseEnvelope
    assert _route("/v1/adapters", "GET").response_model is AdaptersEnvelope
    assert _route("/v1/context", "GET").response_model is ContextEnvelope
    assert _route("/v1/context/echo", "POST").response_model is ContextEchoEnvelope


def test_health_includes_gateway_store() -> None:
    body = TestClient(create_app()).get("/v1/health").json()
    assert body["data"]["status"] == "ok"
    assert body["data"]["gateway_store"] == "memory"


def test_ops_openapi_health_payload_documents_gateway_store() -> None:
    doc = yaml.safe_load(
        (ROOT / "docs" / "api" / "ops.openapi.yaml").read_text(encoding="utf-8")
    )
    props = doc["components"]["schemas"]["HealthPayload"]["properties"]
    assert "gateway_store" in props
    assert "gateway_store" in doc["components"]["schemas"]["HealthPayload"]["required"]


def test_adapters_closed_envelope_includes_sample_pack() -> None:
    body = TestClient(create_app()).get("/v1/adapters").json()
    assert body["meta"]["sample_knowledge_pack_product"]["milestone"] == "PHX-G293"
    assert body["meta"]["openapi_inventory_product"]["milestone"] == "PHX-G288"


def test_context_echo_closed_envelope() -> None:
    client = TestClient(create_app())
    headers = {
        "X-EAOS-Subject-Id": str(uuid4()),
        "X-EAOS-Subject-Type": "human",
        "X-EAOS-Tenant-Id": str(uuid4()),
        "X-Correlation-Id": str(uuid4()),
    }
    response = client.post("/v1/context/echo", headers=headers, json={"probe": True})
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert "context" in data and "echo" in data
    assert data["echo"]["probe"] is True
