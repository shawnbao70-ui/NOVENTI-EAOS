"""PHX-G389 Brain confidence/bias honesty contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.foundation_status import BrainStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
BRAIN_OPENAPI = ROOT / "docs" / "api" / "brain.openapi.yaml"


def _client() -> TestClient:
    return TestClient(create_app())


def _load_openapi() -> dict[str, Any]:
    loaded = yaml.safe_load(BRAIN_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_g389_brain_status_confidence_bias_honesty() -> None:
    response = _client().get("/v1/brain/status")
    assert response.status_code == 200, response.text
    BrainStatusEnvelope.model_validate(response.json())
    data = response.json()["data"]
    assert data["writable"] is False
    assert data["execute_execution"] == "permission_gated"
    assert data["advisory_required"] is True
    assert data["confidence_field_required"] is True
    assert data["bias_notes_surface"] == "insight_payload"
    assert data["confidence_drives_execution"] is False
    assert data["commercial_auto_write"] is False


def test_g389_openapi_documents_confidence_bias_flags() -> None:
    spec = _load_openapi()
    props = spec["components"]["schemas"]["BrainStatusData"]["properties"]
    assert props["confidence_field_required"]["const"] is True
    assert props["bias_notes_surface"]["const"] == "insight_payload"
    assert props["confidence_drives_execution"]["const"] is False
    assert props["commercial_auto_write"]["const"] is False
