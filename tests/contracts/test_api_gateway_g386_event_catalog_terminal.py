"""PHX-G386 Event catalog + Terminal read projection contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.commercial_event_catalog import commercial_event_catalog_projection
from api.gateway.schemas.event import EventCatalogEnvelope

ROOT = Path(__file__).resolve().parents[2]
EVENT_OPENAPI = ROOT / "docs" / "api" / "event.openapi.yaml"
TERMINAL_JS = ROOT / "smart_terminal" / "ui" / "app.js"
TERMINAL_HTML = ROOT / "smart_terminal" / "ui" / "index.html"

_EXPECTED_NAMES = {
    "crm.sales_order.confirmed",
    "inventory.delivery_order.shipped",
    "crm.quote.converted",
    "crm.delivery_order.released",
}


def _client() -> TestClient:
    return TestClient(create_app())


def _load_openapi() -> dict[str, Any]:
    loaded = yaml.safe_load(EVENT_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_g386_event_catalog_read_projection() -> None:
    response = _client().get("/v1/events/catalog")
    assert response.status_code == 200, response.text
    body = response.json()
    EventCatalogEnvelope.model_validate(body)
    data = body["data"]
    assert data["writable"] is False
    assert data["catalog_id"] == "EVT-COMMERCIAL-001"
    assert data["milestone"] == "PHX-G386"
    names = {item["event_name"] for item in data["events"]}
    assert names == _EXPECTED_NAMES
    assert data == commercial_event_catalog_projection()


def test_g386_status_surfaces_include_commercial_catalog() -> None:
    data = _client().get("/v1/events/status").json()["data"]
    assert "commercial_catalog" in data["supported_surfaces"]


def test_g386_no_catalog_write_invent_routes() -> None:
    paths = _client().get("/openapi.json").json()["paths"]
    assert "/v1/events/catalog" in paths
    assert list(paths["/v1/events/catalog"].keys()) == ["get"]
    for path in paths:
        if "catalog" in path.casefold() and path.startswith("/v1/events"):
            assert path == "/v1/events/catalog"


def test_g386_event_openapi_documents_catalog() -> None:
    spec = _load_openapi()
    assert str(spec["info"]["version"]).startswith("1.0.")
    path = spec["paths"]["/events/catalog"]["get"]
    assert path["operationId"] == "getEventCatalog"
    schema = path["responses"]["200"]["content"]["application/json"]["schema"]
    assert schema["$ref"].endswith("EventCatalogEnvelope")
    data = spec["components"]["schemas"]["EventCatalogData"]
    assert data["properties"]["writable"]["const"] is False
    assert data["properties"]["catalog_id"]["const"] == "EVT-COMMERCIAL-001"


def test_g386_terminal_read_projection_wired() -> None:
    js = TERMINAL_JS.read_text(encoding="utf-8")
    html = TERMINAL_HTML.read_text(encoding="utf-8")
    assert 'eventCatalog: "/v1/events/catalog"' in js
    assert "async function adminEventCatalog()" in js
    assert 'bind("btnAdminEventCatalog", adminEventCatalog)' in js
    assert 'id="btnAdminEventCatalog"' in html
