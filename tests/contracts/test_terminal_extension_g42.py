"""PHX-G42 Terminal Extension iframe + CSP contracts."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from kernel.shared.errors import ErrorCode, KernelError
from smart_terminal.extension_runtime import (
    DEMO_PANEL_PATH,
    EXTENSION_PANEL_CSP,
    IFRAME_SANDBOX_TOKENS,
    validate_bridge_message,
)

UI_ROOT = Path(__file__).resolve().parents[2] / "smart_terminal" / "ui"


def test_bridge_allowlists_invoke_and_rejects_elevation() -> None:
    action, surface = validate_bridge_message(
        {
            "type": "eaos.extension.invoke",
            "action": "panel.render",
            "surface": "extensions",
        }
    )
    assert action == "panel.render"
    assert surface == "extensions"

    with pytest.raises(KernelError) as elevated:
        validate_bridge_message(
            {
                "type": "eaos.extension.invoke",
                "action": "panel.render",
                "surface": "extensions",
                "tenant_id": str(uuid4()),
            }
        )
    assert elevated.value.code == ErrorCode.TERMINAL_EXTENSION_SANDBOX_DENIED

    with pytest.raises(KernelError) as unknown:
        validate_bridge_message(
            {
                "type": "eaos.extension.shell.mutate",
                "action": "hide_approval",
                "surface": "extensions",
            }
        )
    assert unknown.value.code == ErrorCode.TERMINAL_EXTENSION_SANDBOX_DENIED


def test_demo_panel_assets_and_sandbox_policy() -> None:
    panel = UI_ROOT / "extensions" / "demo-panel.html"
    script = UI_ROOT / "extensions" / "demo-panel.js"
    shell = UI_ROOT / "index.html"
    assert panel.is_file()
    assert script.is_file()
    html = shell.read_text(encoding="utf-8")
    assert 'sandbox="allow-scripts"' in html
    assert "allow-same-origin" not in html
    assert IFRAME_SANDBOX_TOKENS == frozenset({"allow-scripts"})
    assert DEMO_PANEL_PATH == "/terminal/extensions/demo-panel.html"
    assert "connect-src 'none'" in EXTENSION_PANEL_CSP


def test_gateway_serves_demo_panel_with_csp() -> None:
    client = TestClient(create_app())
    response = client.get(DEMO_PANEL_PATH)
    assert response.status_code == 200
    assert "Demo Panel" in response.text
    assert response.headers.get("content-security-policy") == EXTENSION_PANEL_CSP
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "SAMEORIGIN"

    parent = client.get("/terminal/")
    assert parent.status_code == 200
    assert parent.headers.get("content-security-policy") != EXTENSION_PANEL_CSP
