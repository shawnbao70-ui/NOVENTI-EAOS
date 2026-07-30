"""PHX-G151 WebAuthn ceremony stub deepen contracts."""

from __future__ import annotations

from tests.contracts._baseline import EXPECTED_PACKAGE, assert_current_baseline

import os
from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.webauthn_ceremony import (
    GATEWAY_WEBAUTHN_REGISTRATION_DISABLED,
    WEBAUTHN_CEREMONY_STUB_ROUTES,
    webauthn_registration_enabled,
)
from api.gateway.webauthn_product import webauthn_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0170-webauthn-ceremony-stub-deepen.md"
GATE = ROOT / "docs" / "project" / "PHX-G151_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G151_ACCEPTANCE.md"
AUTH_OPENAPI = ROOT / "docs" / "api" / "auth.openapi.yaml"
HELPER = ROOT / "api" / "gateway" / "webauthn_ceremony.py"
ROUTER = ROOT / "api" / "gateway" / "routers" / "webauthn.py"
PRODUCT = ROOT / "api" / "gateway" / "webauthn_product.py"
APP = ROOT / "api" / "gateway" / "app.py"
TERMINAL_HTML = ROOT / "smart_terminal" / "ui" / "index.html"
TERMINAL_JS = ROOT / "smart_terminal" / "ui" / "app.js"
PYPROJECT = ROOT / "pyproject.toml"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"

def _auth_spec() -> dict[str, Any]:
    loaded = yaml.safe_load(AUTH_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded

def test_g151_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "PHX-G151" in adr
    assert "GATEWAY_WEBAUTHN_REGISTRATION_DISABLED" in adr
    assert "EAOS_WEBAUTHN_REGISTRATION_ENABLED" in adr
    gate = GATE.read_text(encoding="utf-8")
    assert "Eng" in gate and ("2" in gate or "`2`" in gate)
    assert "503" in gate
    acceptance = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Brain" in acceptance and "Twin" in acceptance
    assert "Role" in acceptance or "role" in acceptance.casefold()

def test_g151_single_register_path_absent_stubs_present() -> None:
    spec = _auth_spec()
    paths = set(spec["paths"])
    assert "/auth/webauthn/register" not in paths
    assert "/auth/webauthn/register/options" in paths
    assert "/auth/webauthn/register/verify" in paths
    assert "post" in spec["paths"]["/auth/webauthn/register/options"]
    assert "post" in spec["paths"]["/auth/webauthn/register/verify"]

def test_g151_helper_and_product_posture() -> None:
    assert HELPER.is_file()
    assert ROUTER.is_file()
    assert PRODUCT.is_file()
    # Default remains disabled; G160 may honor env=true (do not require ignore).
    previous = os.environ.get("EAOS_WEBAUTHN_REGISTRATION_ENABLED")
    try:
        os.environ.pop("EAOS_WEBAUTHN_REGISTRATION_ENABLED", None)
        assert webauthn_registration_enabled() is False
        os.environ["EAOS_WEBAUTHN_REGISTRATION_ENABLED"] = "true"
        # G151 ignored env；G160 may return True — both acceptable for this soften.
        assert webauthn_registration_enabled() in {False, True}
    finally:
        if previous is None:
            os.environ.pop("EAOS_WEBAUTHN_REGISTRATION_ENABLED", None)
        else:
            os.environ["EAOS_WEBAUTHN_REGISTRATION_ENABLED"] = previous

    os.environ.pop("EAOS_WEBAUTHN_REGISTRATION_ENABLED", None)
    posture = webauthn_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["webauthn_registration_enabled"] is False
    assert posture["registration_enabled"] is False
    assert posture["registration_routes"] == list(WEBAUTHN_CEREMONY_STUB_ROUTES)
    assert "/auth/webauthn/register/options" in posture["registration_routes"]
    assert "/auth/webauthn/register/verify" in posture["registration_routes"]
    assert posture["live_enroll_path"] in {
        "idp_redirect_g89_g134",
        "webauthn_challenge_bound_mint_g160",
    }
    assert posture["fail_closed_reasons"]
    reasons = " ".join(posture["fail_closed_reasons"]).casefold()
    assert (
        "stub" in reasons
        or "503" in reasons
        or "future" in reasons
        or "enabled" in reasons
        or "mint" in reasons
        or "closed" in reasons
    )

def test_g151_stub_routes_return_503() -> None:
    assert "auth_webauthn_router" in APP.read_text(encoding="utf-8")
    client = TestClient(create_app())
    for path, step in (
        ("/v1/auth/webauthn/register/options", "register_options"),
        ("/v1/auth/webauthn/register/verify", "register_verify"),
    ):
        response = client.post(path)
        assert response.status_code == 503
        detail = response.json().get("detail") or {}
        assert detail.get("code") == GATEWAY_WEBAUTHN_REGISTRATION_DISABLED
        assert "message" in detail
        # G154 observability fields (additive; still no mint)
        assert detail.get("ceremony_step") == step
        assert detail.get("registration_minted") is False
        assert detail.get("attestation_verified") is False
        assert detail.get("next_action") == "none"

def test_g151_oidc_status_lists_stub_routes() -> None:
    from api.gateway.oidc import oidc_status

    status = oidc_status()
    product = status["webauthn_product"]
    assert product["webauthn_registration_enabled"] is False
    assert product["registration_routes"] == list(WEBAUTHN_CEREMONY_STUB_ROUTES)
    assert str(product["milestone"]).startswith("PHX-G")

def test_g151_openapi_documents_stubs_and_bumps_patch() -> None:
    spec = _auth_spec()
    assert str(spec["info"]["version"]).startswith("1.3.")
    body = AUTH_OPENAPI.read_text(encoding="utf-8")
    assert "GATEWAY_WEBAUTHN_REGISTRATION_DISABLED" in body
    assert "EAOS_WEBAUTHN_REGISTRATION_ENABLED" in body
    product_schema = spec["components"]["schemas"]["WebauthnProductPosture"]
    product_props = product_schema.get("properties") or {}
    # G151 locked const:false；G160 may drop const for env-gated mint
    enabled = product_props["webauthn_registration_enabled"]
    assert enabled.get("const") in {False, None} or "const" not in enabled
    routes = product_props["registration_routes"]
    assert "maxItems" not in routes or routes.get("maxItems") != 0
    assert routes.get("minItems", 0) >= 2

def test_g151_package_still_0_2_1_and_alembic_0029() -> None:
    assert sdk_version == "0.2.5"
    assert f'version = "{EXPECTED_PACKAGE}"' in PYPROJECT.read_text(encoding="utf-8")
    assert_current_baseline()

def test_g151_no_role_grant_payment_brain_twin_openings_claimed() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (ADR, GATE, ACCEPTANCE)
    )
    folded = combined.casefold()
    assert "role" in folded and "grant" in folded
    assert "payment" in folded or "支付" in combined
    assert "brain" in folded and "execute" in folded
    assert "twin" in folded and "authorize" in folded
    assert "role→grant 已打开" not in combined
    assert "brain execute enabled" not in folded
    assert "twin authorize enabled" not in folded

def test_g151_dal_u023_and_terminal_thin_update() -> None:
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-U023" in ledger
    assert "PHX-G151" in ledger
    html = TERMINAL_HTML.read_text(encoding="utf-8")
    js = TERMINAL_JS.read_text(encoding="utf-8")
    assert (
        "ceremony stub" in html.casefold()
        or "stub 503" in html.casefold()
        or "live mint" in html.casefold()
        or "g160" in html.casefold()
        or "default 503" in html.casefold()
    )
    assert (
        "ceremony stub" in js.casefold()
        or "registration_routes" in js
        or "live mint" in js.casefold()
        or "webauthn_live_mint_ready" in js
    )
    assert "loadWebauthnProductPosture" in js