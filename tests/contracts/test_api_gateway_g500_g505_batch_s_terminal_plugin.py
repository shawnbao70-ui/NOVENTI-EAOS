"""PHX-G500–G505 Batch S Terminal/Plugin residual contracts."""

from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.terminal import TerminalStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
OPENAPI = ROOT / "docs" / "api" / "terminal.openapi.yaml"
TERMINAL = ROOT / "smart_terminal" / "ui" / "app.js"


def test_g500_g504_terminal_plugin_residual() -> None:
    response = TestClient(create_app()).get("/v1/terminal/status")
    TerminalStatusEnvelope.model_validate(response.json())
    data = response.json()["data"]
    assert data["extension_signature_bypass"] is False
    assert data["sandbox_escape"] is False
    assert data["admin_strip_consistent"] is True
    assert data["extension_host_path"] == "allowlisted_only"
    assert data["openapi_inventory_synced"] is True
    assert data["holds_business_truth"] is False


def test_g500_g504_terminal_openapi_parity() -> None:
    spec = yaml.safe_load(OPENAPI.read_text(encoding="utf-8"))
    props = spec["components"]["schemas"]["TerminalStatusData"]["properties"]
    assert props["extension_signature_bypass"]["const"] is False
    assert props["sandbox_escape"]["const"] is False
    assert props["admin_strip_consistent"]["const"] is True
    assert props["extension_host_path"]["const"] == "allowlisted_only"
    assert props["openapi_inventory_synced"]["const"] is True


def test_g502_terminal_admin_strip_residual() -> None:
    js = TERMINAL.read_text(encoding="utf-8")
    assert "sig_bypass=" in js
    assert "sandbox_escape=" in js
    assert "host_path=" in js
