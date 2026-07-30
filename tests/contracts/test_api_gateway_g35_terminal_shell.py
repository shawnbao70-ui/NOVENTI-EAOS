"""PHX-G35 Smart Terminal Operator Shell contracts."""

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


def test_operator_shell_assets_exist() -> None:
    assert INDEX.is_file()
    assert APP_JS.is_file()
    assert (UI_ROOT / "styles.css").is_file()
    html = INDEX.read_text(encoding="utf-8")
    assert "NOVENTI" in html
    assert "Smart Terminal" in html
    assert 'src="/terminal/app.js' in html
    assert 'href="/terminal/styles.css' in html


def test_shell_forbids_context_elevation_in_body_builder() -> None:
    source = APP_JS.read_text(encoding="utf-8")
    for key in ("tenant_id", "subject_id", "platform_scope", "session_id"):
        assert f'"{key}"' in source
    assert "FORBIDDEN_BODY_KEYS" in source
    assert "sanitizeBody" in source
    assert "delete clean[key]" in source
    # Must not treat claimed elevation helpers as shell defaults in open session.
    assert 'device_trust: "trusted"' in source
    assert "claimed_tenant_id" not in source
    assert "claimed_subject_id" not in source


def test_shell_targets_terminal_gateway_paths() -> None:
    source = APP_JS.read_text(encoding="utf-8")
    assert "/v1/terminal/sessions" in source
    assert "/v1/terminal/intents" in source
    assert "/v1/terminal/previews" in source
    assert "/commits" in source
    assert "X-EAOS-Tenant-Id" in source
    assert "X-EAOS-Subject-Id" in source
    assert "X-Correlation-Id" in source


def test_shell_build_preview_uses_server_high_impact() -> None:
    """Operator step routing must follow GET preview.high_impact, not checkbox alone."""

    source = APP_JS.read_text(encoding="utf-8")
    assert "async function buildPreview()" in source
    assert "preview.high_impact" in source
    assert 'setStep(highImpact ? "approval" : "commit")' in source
    # Ops brief handoff must resolve Package action before Operator (fail-closed).
    assert "async function composeOpsBriefAndHandoff()" in source
    assert "packageActionResolve" in source
    assert 'action_key: actionKey' in source or 'action_key: "ops.brief.compose"' in source


def test_shell_fixture_handoffs_resolve_fail_closed() -> None:
    source = APP_JS.read_text(encoding="utf-8")
    assert "Product fixture resolve denied — handoff blocked (fail-closed)" in source
    assert "Ops fixture resolve denied — handoff blocked (fail-closed)" in source
    assert "Sample flow resolve denied — handoff blocked (fail-closed)" in source
    assert "Order flow resolve denied — handoff blocked (fail-closed)" in source
    assert (
        "Declared product surface resolve denied — handoff blocked (fail-closed)"
        in source
    )
    assert (
        "Declared ops surface resolve denied — handoff blocked (fail-closed)" in source
    )
    assert "Ops brief resolve denied — handoff blocked (fail-closed)" in source


def test_gateway_serves_operator_shell() -> None:
    client = TestClient(create_app())
    response = client.get("/terminal/")
    assert response.status_code == 200
    assert "NOVENTI" in response.text
    assert "Smart Terminal" in response.text

    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "sanitizeBody" in script.text

    styles = client.get("/terminal/styles.css")
    assert styles.status_code == 200
    assert "--accent" in styles.text
