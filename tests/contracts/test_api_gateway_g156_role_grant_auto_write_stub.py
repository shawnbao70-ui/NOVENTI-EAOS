"""PHX-G156 Role→grant auto-write stub deepen contracts."""

from __future__ import annotations

from tests.contracts._baseline import EXPECTED_PACKAGE, assert_current_baseline

from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.role_grant_auto_write import (
    GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED,
    ROLE_GRANT_AUTO_WRITE_STUB_ROUTES,
)
from api.gateway.role_grant_product import role_grant_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0175-role-grant-auto-write-stub-deepen.md"
GATE = ROOT / "docs" / "project" / "PHX-G156_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G156_ACCEPTANCE.md"
PERMISSION_OPENAPI = ROOT / "docs" / "api" / "permission.openapi.yaml"
APP = ROOT / "api" / "gateway" / "app.py"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
TERMINAL_HTML = ROOT / "smart_terminal" / "ui" / "index.html"
TERMINAL_JS = ROOT / "smart_terminal" / "ui" / "app.js"
PYPROJECT = ROOT / "pyproject.toml"

def _permission_spec() -> dict[str, Any]:
    loaded = yaml.safe_load(PERMISSION_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded

def test_g156_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "PHX-G156" in adr
    assert "GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED" in adr
    assert "explicit PO" in adr.casefold() or "explicit po" in adr.casefold() or "PO" in adr
    acceptance = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Brain" in acceptance and "Twin" in acceptance
    assert "Cap" in acceptance or "cap" in acceptance.casefold()

def test_g156_posture_lists_stub_routes() -> None:
    posture = role_grant_product_posture()
    # G156 delivered stub; G161 may advance milestone while default remains OFF.
    assert posture["milestone"].startswith("PHX-G")
    assert posture["auto_grant_from_role_enabled"] is False
    assert posture["auto_write_routes"] == list(ROLE_GRANT_AUTO_WRITE_STUB_ROUTES)
    assert posture["auto_write_stub_observability"] is True
    reasons = " ".join(posture["fail_closed_reasons"]).casefold()
    assert "cap" in reasons or "stub" in reasons or "default" in reasons or "po" in reasons

def test_g156_stub_route_returns_503() -> None:
    assert "permission_role_grants_router" in APP.read_text(encoding="utf-8")
    client = TestClient(create_app())
    response = client.post("/v1/permission/role-grants")
    assert response.status_code == 503
    detail = response.json().get("detail") or {}
    assert detail.get("code") == GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED
    assert detail.get("auto_write_step") == "role_grants"
    assert detail.get("grant_minted") is False
    assert detail.get("cap_is_grant") is False
    assert detail.get("title_is_permission") is False
    assert detail.get("next_action") == "none"

def test_g156_openapi_1_1_2_documents_stub() -> None:
    spec = _permission_spec()
    # G156 = 1.1.2；G161 bump = 1.1.3（still documents disabled/stub codes）
    assert str(spec["info"]["version"]).startswith("1.1.")
    assert "/permission/role-grants" in spec["paths"]
    schemas = spec["components"]["schemas"]
    assert "RoleGrantAutoWriteStubDetail" in schemas
    assert schemas["RoleGrantAutoWriteStubDetail"]["properties"]["grant_minted"].get("const") is False
    body = PERMISSION_OPENAPI.read_text(encoding="utf-8")
    assert "GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED" in body

def test_g156_package_dal_terminal() -> None:
    assert sdk_version == "0.2.5"
    assert f'version = "{EXPECTED_PACKAGE}"' in PYPROJECT.read_text(encoding="utf-8")
    assert_current_baseline()
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-U028" in ledger
    assert "PHX-G156" in ledger
    html = TERMINAL_HTML.read_text(encoding="utf-8")
    js = TERMINAL_JS.read_text(encoding="utf-8")
    assert "stub" in html.casefold() or "503" in html or "auto-write" in html.casefold()
    assert "stub" in js.casefold() or "auto_write_routes" in js or "503" in js
