"""PHX-G43 Terminal Extension Worker runtime contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.shared.errors import ErrorCode, KernelError
from smart_terminal.extension_runtime import (
    ALLOWED_BRIDGE_CHANNELS,
    DEMO_WORKER_PATH,
    EXTENSION_PANEL_CSP,
    validate_bridge_message,
)

UI_ROOT = Path(__file__).resolve().parents[2] / "smart_terminal" / "ui"


def test_worker_bridge_channel_allowlist() -> None:
    action, surface = validate_bridge_message(
        {
            "type": "eaos.extension.invoke",
            "action": "panel.render",
            "surface": "extensions",
            "channel": "worker",
        }
    )
    assert action == "panel.render"
    assert surface == "extensions"
    assert ALLOWED_BRIDGE_CHANNELS == frozenset({"iframe", "worker"})

    with pytest.raises(KernelError) as denied:
        validate_bridge_message(
            {
                "type": "eaos.extension.invoke",
                "action": "panel.render",
                "surface": "extensions",
                "channel": "service-worker",
            }
        )
    assert denied.value.code == ErrorCode.TERMINAL_EXTENSION_SANDBOX_DENIED

    with pytest.raises(KernelError) as elevated:
        validate_bridge_message(
            {
                "type": "eaos.extension.invoke",
                "action": "panel.render",
                "surface": "extensions",
                "channel": "worker",
                "platform_scope": True,
            }
        )
    assert elevated.value.code == ErrorCode.TERMINAL_EXTENSION_SANDBOX_DENIED


def test_demo_worker_asset_exists() -> None:
    worker = UI_ROOT / "extensions" / "demo-worker.js"
    shell = UI_ROOT / "index.html"
    assert worker.is_file()
    text = worker.read_text(encoding="utf-8")
    assert "eaos.extension.invoke" in text
    assert "channel: \"worker\"" in text or "channel: 'worker'" in text
    assert "btnExtWorker" in shell.read_text(encoding="utf-8")
    assert DEMO_WORKER_PATH == "/terminal/extensions/demo-worker.js"


def test_gateway_serves_demo_worker_with_csp() -> None:
    client = TestClient(create_app())
    response = client.get(DEMO_WORKER_PATH)
    assert response.status_code == 200
    assert "eaos.extension.invoke" in response.text
    assert response.headers.get("content-security-policy") == EXTENSION_PANEL_CSP
    assert response.headers.get("x-content-type-options") == "nosniff"
