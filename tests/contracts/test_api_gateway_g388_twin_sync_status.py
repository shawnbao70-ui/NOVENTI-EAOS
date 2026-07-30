"""PHX-G388 Twin sync thin status honesty contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.foundation_status import TwinStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
BRAIN_OPENAPI = ROOT / "docs" / "api" / "brain.openapi.yaml"


def _client() -> TestClient:
    return TestClient(create_app())


def _load_openapi() -> dict[str, Any]:
    loaded = yaml.safe_load(BRAIN_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_g388_twin_status_sync_honesty() -> None:
    response = _client().get("/v1/twin/status")
    assert response.status_code == 200, response.text
    TwinStatusEnvelope.model_validate(response.json())
    data = response.json()["data"]
    assert data["writable"] is False
    assert data["authorize_execution"] == "permission_gated"
    assert data["continuous_sync_daemon"] is False
    assert data["sync_mode"] == "snapshot_upsert"
    assert data["commercial_auto_write"] is False


def test_g388_no_sync_daemon_invent_routes() -> None:
    paths = _client().get("/openapi.json").json()["paths"]
    for path in paths:
        if not path.startswith("/v1/twin"):
            continue
        lowered = path.casefold()
        assert "sync/daemon" not in lowered
        assert "/sync/start" not in lowered
        assert "continuous-sync" not in lowered


def test_g388_openapi_documents_sync_flags() -> None:
    spec = _load_openapi()
    props = spec["components"]["schemas"]["TwinStatusData"]["properties"]
    assert props["continuous_sync_daemon"]["const"] is False
    assert props["sync_mode"]["const"] == "snapshot_upsert"
    assert props["commercial_auto_write"]["const"] is False
