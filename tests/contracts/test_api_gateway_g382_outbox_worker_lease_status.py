"""PHX-G382 Outbox worker/lease status honesty contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.event import EventStatusEnvelope
from kernel.event_bus.bus import DEFAULT_LEASE_SECONDS

ROOT = Path(__file__).resolve().parents[2]
EVENT_OPENAPI = ROOT / "docs" / "api" / "event.openapi.yaml"


def _client() -> TestClient:
    return TestClient(create_app())


def _load_openapi() -> dict[str, Any]:
    loaded = yaml.safe_load(EVENT_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_g382_event_status_worker_lease_honesty() -> None:
    response = _client().get("/v1/events/status")
    assert response.status_code == 200, response.text
    body = response.json()
    EventStatusEnvelope.model_validate(body)
    data = body["data"]
    assert data["writable"] is False
    assert data["background_worker_daemon"] is False
    assert data["dispatch_trigger"] == "http_post_dispatch"
    assert data["lease_claim_enabled"] is True
    assert data["default_lease_seconds"] == DEFAULT_LEASE_SECONDS == 30
    # G383 fields remain present on the same closed envelope.
    assert data["fail_closed_without_grant"] is True
    surfaces = data["supported_surfaces"]
    assert "dispatch_run" in surfaces
    assert "outbox_enqueue" in surfaces
    assert "outbox_list" not in surfaces


def test_g382_no_background_worker_invent_routes() -> None:
    paths = _client().get("/openapi.json").json()["paths"]
    assert "/v1/events/status" in paths
    for path in paths:
        if not path.startswith("/v1/events"):
            continue
        lowered = path.casefold()
        assert "worker/daemon" not in lowered
        assert "background-worker" not in lowered
        assert "/worker/start" not in lowered


def test_g382_event_openapi_documents_worker_lease_flags() -> None:
    spec = _load_openapi()
    assert str(spec["info"]["version"]).startswith("1.0.")
    path = spec["paths"]["/events/status"]["get"]
    assert path["operationId"] == "getEventStatus"
    schema = path["responses"]["200"]["content"]["application/json"]["schema"]
    assert schema["$ref"].endswith("EventStatusEnvelope")
    data = spec["components"]["schemas"]["EventStatusData"]
    props = data["properties"]
    assert props["background_worker_daemon"]["const"] is False
    assert props["dispatch_trigger"]["const"] == "http_post_dispatch"
    assert props["lease_claim_enabled"]["const"] is True
    assert props["default_lease_seconds"]["const"] == 30
