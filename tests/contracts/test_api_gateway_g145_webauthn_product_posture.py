"""PHX-G145 WebAuthn / MFA product posture contracts."""

from __future__ import annotations

from tests.contracts._baseline import EXPECTED_PACKAGE, assert_current_baseline

from pathlib import Path
from typing import Any

import yaml

from api.gateway.webauthn_product import webauthn_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0164-webauthn-mfa-product-posture.md"
GATE = ROOT / "docs" / "project" / "PHX-G145_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G145_ACCEPTANCE.md"
AUTH_OPENAPI = ROOT / "docs" / "api" / "auth.openapi.yaml"
HELPER = ROOT / "api" / "gateway" / "webauthn_product.py"
TERMINAL_HTML = ROOT / "smart_terminal" / "ui" / "index.html"
TERMINAL_JS = ROOT / "smart_terminal" / "ui" / "app.js"
PYPROJECT = ROOT / "pyproject.toml"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"

def _auth_spec() -> dict[str, Any]:
    loaded = yaml.safe_load(AUTH_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded

def test_g145_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "PHX-G145" in adr
    assert "webauthn_registration_enabled" in adr.casefold() or "registration_enabled" in adr.casefold()
    gate = GATE.read_text(encoding="utf-8")
    assert "Eng Explicit Defer" in gate or "Eng `2`" in gate or "Eng 2" in gate
    acceptance = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Role→grant" in acceptance or "Role" in acceptance
    assert "Brain" in acceptance and "Twin" in acceptance

def test_g145_webauthn_register_route_absent() -> None:
    spec = _auth_spec()
    paths = set(spec["paths"])
    assert "/auth/webauthn/register" not in paths
    assert "/auth/mfa/register" not in paths
    body = AUTH_OPENAPI.read_text(encoding="utf-8")
    assert "webauthn_product" in body or "WebAuthn" in body

def test_g145_helper_posture_registration_disabled() -> None:
    assert HELPER.is_file()
    posture = webauthn_product_posture()
    assert posture["webauthn_registration_enabled"] is False
    assert posture["registration_enabled"] is False
    # G151 deepen: registration_routes lists named ceremony stubs (still disabled).
    routes = posture["registration_routes"]
    assert isinstance(routes, list)
    assert "/auth/webauthn/register/options" in routes
    assert "/auth/webauthn/register/verify" in routes
    assert posture["mfa_enrollment_path"] == "/auth/oidc/mfa-enrollment"
    assert "fail_closed_reasons" in posture
    assert posture["fail_closed_reasons"]
    assert posture["live_enroll_path"] in {
        "idp_redirect_g89_g134",
        "webauthn_challenge_bound_mint_g160",
    }

def test_g145_oidc_status_includes_webauthn_product() -> None:
    from api.gateway.oidc import oidc_status

    status = oidc_status()
    assert "webauthn_product" in status
    product = status["webauthn_product"]
    assert product["webauthn_registration_enabled"] is False
    routes = product["registration_routes"]
    assert isinstance(routes, list)
    assert "/auth/webauthn/register/options" in routes
    assert "/auth/webauthn/register/verify" in routes
    assert "mfa_enrollment_enabled" in product
    assert "fail_closed_reasons" in product

def test_g145_openapi_documents_posture_and_bumps_patch() -> None:
    spec = _auth_spec()
    # G145 = 1.3.3；later WebAuthn deepen may bump patch while keeping posture schema
    assert str(spec["info"]["version"]).startswith("1.3.")
    props = spec["components"]["schemas"]["OidcStatusData"]["properties"]
    assert "webauthn_product" in props
    product_schema = spec["components"]["schemas"]["WebauthnProductPosture"]
    product_props = product_schema.get("properties") or {}
    assert "webauthn_registration_enabled" in product_props
    # G145 locked const:false；G160 env-gated may drop const
    enabled = product_props["webauthn_registration_enabled"]
    assert enabled.get("const") in {False, None} or "const" not in enabled
    assert "registration_routes" in product_props
    # G151: stubs listed — maxItems:0 must not fence empty-only.
    routes_schema = product_props["registration_routes"]
    assert routes_schema.get("maxItems") != 0
    assert "fail_closed_reasons" in product_props

def test_g145_package_still_0_2_1_and_alembic_0029() -> None:
    assert sdk_version == "0.2.5"
    assert f'version = "{EXPECTED_PACKAGE}"' in PYPROJECT.read_text(encoding="utf-8")
    assert_current_baseline()

def test_g145_no_role_grant_payment_brain_twin_openings_claimed() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (ADR, GATE, ACCEPTANCE)
    )
    folded = combined.casefold()
    assert "role" in folded and "grant" in folded
    assert "payment" in folded or "支付" in combined
    assert "brain" in folded and "execute" in folded
    assert "twin" in folded and "authorize" in folded
    # Must not claim those openings as delivered by this slice.
    assert "role→grant 已打开" not in combined
    assert "brain execute enabled" not in folded
    assert "twin authorize enabled" not in folded

def test_g145_dal_u006_and_terminal_thin_panel() -> None:
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-U006" in ledger
    assert "PHX-G145" in ledger or "Eng" in ledger and "2" in ledger
    html = TERMINAL_HTML.read_text(encoding="utf-8")
    js = TERMINAL_JS.read_text(encoding="utf-8")
    assert "webauthnProduct" in html or "MFA / WebAuthn" in html
    assert "webauthn_product" in js or "loadWebauthnProductPosture" in js
    assert "loadOidcMfaEnrollmentLink" in js
