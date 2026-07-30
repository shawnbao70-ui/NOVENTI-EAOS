"""PHX-G96 JWT Denylist Status Observability contracts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.auth_jwt import (
    JwtSettings,
    clear_denylist_cache,
    clear_runtime_denylist,
    revoke_runtime_jti,
)
from api.gateway.context import configure_jwt_settings

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _reset(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "EAOS_JWT_DENYLIST_JSON",
        "EAOS_JWT_DENYLIST_URL",
        "EAOS_JWT_SECRET",
    ):
        monkeypatch.delenv(name, raising=False)
    clear_denylist_cache()
    clear_runtime_denylist()
    configure_jwt_settings(
        JwtSettings(
            secret="test-secret",
            issuer="https://issuer.example/eaos",
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    yield
    clear_denylist_cache()
    clear_runtime_denylist()
    # Restore permissive Gateway defaults so later contract modules are not polluted.
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )


def test_terminal_exposes_jwt_status_control() -> None:
    html = (ROOT / "smart_terminal" / "ui" / "index.html").read_text(encoding="utf-8")
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert 'id="btnAdminJwtStatus"' in html
    assert "JWT status" in html
    assert "JWT/denylist 状态探针（G96）" in html
    assert 'jwtStatus: "/v1/auth/jwt/status"' in js


def test_jwt_status_defaults_and_runtime_count() -> None:
    client = TestClient(create_app())
    response = client.get("/v1/auth/jwt/status")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["writable"] is False
    assert data["require_jwt"] is False
    assert data["has_secret"] is True
    assert data["denylist"]["enabled"] is False
    assert data["denylist"]["configured_entry_count"] is None
    assert data["denylist"]["runtime_revoked_count"] == 0

    revoke_runtime_jti("revoked-jti-1", iss="https://issuer.example/eaos")
    again = client.get("/v1/auth/jwt/status")
    assert again.json()["data"]["denylist"]["runtime_revoked_count"] == 1
    assert "revoked-jti-1" not in again.text


def test_jwt_status_configured_denylist_count_and_ui(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    document = json.dumps([{"jti": "blocked-1"}, {"jti": "blocked-2"}])
    configure_jwt_settings(
        JwtSettings(
            secret="test-secret",
            issuer="https://issuer.example/eaos",
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=True,
            denylist_json=document,
        )
    )
    client = TestClient(create_app())
    response = client.get("/v1/auth/jwt/status")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["require_jwt"] is True
    assert data["denylist"]["enabled"] is True
    assert data["denylist"]["has_json"] is True
    assert data["denylist"]["configured_entry_count"] == 2
    assert "blocked-1" not in response.text
    assert document not in response.text

    page = client.get("/terminal/")
    assert page.status_code == 200
    assert "JWT status" in page.text
    script = client.get("/terminal/app.js")
    assert script.status_code == 200
    assert "jwtStatus" in script.text
