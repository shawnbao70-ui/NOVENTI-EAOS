"""PHX-G36 Complete Terminal UI contracts."""

from __future__ import annotations

from pathlib import Path

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app

ROOT = Path(__file__).resolve().parents[2]
UI_ROOT = ROOT / "smart_terminal" / "ui"
APP_JS = UI_ROOT / "app.js"
INDEX = UI_ROOT / "index.html"


def test_complete_ui_exposes_four_surfaces() -> None:
    html = INDEX.read_text(encoding="utf-8")
    for surface in ("operator", "approval", "admin", "ai"):
        assert f'data-surface="{surface}"' in html
        assert f'data-surface-panel="{surface}"' in html
    assert "Request Workflow approval" in html
    assert "Platform observability" in html
    assert "AI Collaboration" in html


def test_complete_ui_covers_approval_and_admin_paths() -> None:
    source = APP_JS.read_text(encoding="utf-8")
    assert "SURFACES" in source
    assert "/approvals" in source
    assert "/v1/health" in source
    assert "/v1/release" in source
    assert "/v1/adapters" in source
    assert "/v1/context" in source
    assert "requestApproval" in source or "btnRequestApproval" in source
    assert "presentApproval" in source or "btnPresentApproval" in source
    assert "FORBIDDEN_BODY_KEYS" in source
    assert "sanitizeBody" in source
    assert "claimed_tenant_id" not in source


def test_gateway_serves_complete_terminal_ui() -> None:
    client = TestClient(create_app())
    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "Approval" in page.text
    assert "Admin" in page.text
    assert "AI Collaboration" in page.text

    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "SURFACES" in script.text
    assert "/v1/terminal/previews/" in script.text
