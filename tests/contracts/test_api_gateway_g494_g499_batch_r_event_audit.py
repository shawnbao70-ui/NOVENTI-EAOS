"""PHX-G494–G499 Batch R Event/Outbox/Audit residual contracts."""

from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.event import EventStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
OPENAPI = ROOT / "docs" / "api" / "event.openapi.yaml"
TERMINAL = ROOT / "smart_terminal" / "ui" / "app.js"


def test_g494_g497_event_audit_residual() -> None:
    response = TestClient(create_app()).get("/v1/events/status")
    EventStatusEnvelope.model_validate(response.json())
    data = response.json()["data"]
    assert data["outbox_delivery_mode"] == "on_demand"
    assert data["audit_read_surface"] is True
    assert data["commercial_emit_catalog_only"] is True
    assert data["replay_stats_read_only"] is True
    assert data["multi_region_failover"] is False
    assert data["fail_closed_without_grant"] is True


def test_g494_g497_event_openapi_parity() -> None:
    spec = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
    props = spec["components"]["schemas"]["EventStatusData"]["properties"]
    assert props["outbox_delivery_mode"]["const"] == "on_demand"
    assert props["audit_read_surface"]["const"] is True
    assert props["commercial_emit_catalog_only"]["const"] is True
    assert props["replay_stats_read_only"]["const"] is True
    assert props["multi_region_failover"]["const"] is False


def test_g498_terminal_event_residual_strip() -> None:
    js = TERMINAL.read_text(encoding="utf-8")
    assert "delivery=" in js
    assert "audit_read=" in js
    assert "multi_region=" in js
