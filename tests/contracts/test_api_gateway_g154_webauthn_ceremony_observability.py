"""PHX-G154 WebAuthn ceremony stub observability contracts."""

from __future__ import annotations

from tests.contracts._baseline import EXPECTED_PACKAGE, assert_current_baseline

from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from api.gateway.webauthn_ceremony import GATEWAY_WEBAUTHN_REGISTRATION_DISABLED
from api.gateway.webauthn_product import webauthn_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0173-webauthn-ceremony-stub-observability.md"
GATE = ROOT / "docs" / "project" / "PHX-G154_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G154_ACCEPTANCE.md"
AUTH_OPENAPI = ROOT / "docs" / "api" / "auth.openapi.yaml"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
TERMINAL_HTML = ROOT / "smart_terminal" / "ui" / "index.html"
TERMINAL_JS = ROOT / "smart_terminal" / "ui" / "app.js"
PYPROJECT = ROOT / "pyproject.toml"

def _auth_spec() -> dict[str, Any]:
    loaded = yaml.safe_load(AUTH_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded

def test_g154_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "PHX-G154" in adr
    assert "ceremony_step" in adr
    assert "GATEWAY_WEBAUTHN_REGISTRATION_DISABLED" in adr
    acceptance = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Brain" in acceptance and "Twin" in acceptance

def test_g154_posture_and_inventory_fence() -> None:
    posture = webauthn_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["webauthn_registration_enabled"] is False
    assert posture["ceremony_stub_observability"] is True
    reasons = " ".join(posture["fail_closed_reasons"]).casefold()
    assert "observability" in reasons or "g154" in reasons or "enabled" in reasons or "mint" in reasons
    inventory = openapi_inventory_product_posture()
    fences = " ".join(inventory["known_defer_fences"]).casefold()
    # G154 fenced live mint；G160 opens mint and fences attestation crypto instead
    assert "webauthn_attestation" in fences or "webauthn_live_credential_mint" in fences
    assert "webauthn_registration_ceremony" not in fences

def test_g154_stub_detail_includes_step_fields() -> None:
    client = TestClient(create_app())
    options = client.post("/v1/auth/webauthn/register/options")
    assert options.status_code == 503
    detail = options.json()["detail"]
    assert detail["code"] == GATEWAY_WEBAUTHN_REGISTRATION_DISABLED
    assert detail["ceremony_step"] == "register_options"
    assert detail["registration_minted"] is False
    assert detail["attestation_verified"] is False
    assert detail["next_action"] == "none"

    verify = client.post("/v1/auth/webauthn/register/verify")
    assert verify.status_code == 503
    vdetail = verify.json()["detail"]
    assert vdetail["ceremony_step"] == "register_verify"
    assert vdetail["registration_minted"] is False

def test_g154_openapi_1_3_4_documents_stub_schema() -> None:
    spec = _auth_spec()
    # G154 = 1.3.4；later WebAuthn deepen may bump patch while keeping stub schema
    assert str(spec["info"]["version"]).startswith("1.3.")
    schemas = spec["components"]["schemas"]
    assert "WebauthnCeremonyStubDetail" in schemas
    assert "WebauthnCeremonyStubError" in schemas
    detail = schemas["WebauthnCeremonyStubDetail"]
    assert detail["properties"]["registration_minted"].get("const") is False
    assert detail["properties"]["attestation_verified"].get("const") is False
    assert "register_options" in detail["properties"]["ceremony_step"]["enum"]
    body = AUTH_OPENAPI.read_text(encoding="utf-8")
    assert "G154" in body or "ceremony_step" in body

def test_g154_package_and_dal() -> None:
    assert sdk_version == "0.2.5"
    assert f'version = "{EXPECTED_PACKAGE}"' in PYPROJECT.read_text(encoding="utf-8")
    assert_current_baseline()
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-U026" in ledger
    assert "PHX-G154" in ledger
    html = TERMINAL_HTML.read_text(encoding="utf-8")
    js = TERMINAL_JS.read_text(encoding="utf-8")
    assert (
        "ceremony" in html.casefold()
        or "stub" in html.casefold()
        or "live mint" in html.casefold()
        or "g160" in html.casefold()
    )
    assert (
        "ceremony" in js.casefold()
        or "observability" in js.casefold()
        or "stub" in js.casefold()
        or "live mint" in js.casefold()
        or "webauthn_live_mint_ready" in js
    )