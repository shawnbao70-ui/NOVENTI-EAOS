"""PHX-G396 Extension host signature posture deepen contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.terminal import TerminalStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
TERMINAL_OPENAPI = ROOT / "docs" / "api" / "terminal.openapi.yaml"


def _load_openapi() -> dict[str, Any]:
    loaded = yaml.safe_load(TERMINAL_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_g396_terminal_status_signature_posture() -> None:
    response = TestClient(create_app()).get("/v1/terminal/status")
    assert response.status_code == 200, response.text
    TerminalStatusEnvelope.model_validate(response.json())
    data = response.json()["data"]
    assert data["extension_signature_required_on_activate"] is True
    assert data["unsigned_extension_activate"] == "fail_closed"
    assert "hmac-sha256" in data["extension_signature_algs"]
    assert "ed25519" in data["extension_signature_algs"]
    assert data["holds_business_truth"] is False


def test_g396_openapi_documents_signature_flags() -> None:
    props = _load_openapi()["components"]["schemas"]["TerminalStatusData"]["properties"]
    assert props["extension_signature_required_on_activate"]["const"] is True
    assert props["unsigned_extension_activate"]["const"] == "fail_closed"
