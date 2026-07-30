"""PHX-G147 OIDC login product surface contracts."""

from __future__ import annotations

from tests.contracts._baseline import EXPECTED_PACKAGE, assert_current_baseline

from pathlib import Path
from typing import Any

import yaml

from api.gateway.oidc_login_product import oidc_login_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0166-oidc-login-product-surface.md"
GATE = ROOT / "docs" / "project" / "PHX-G147_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G147_ACCEPTANCE.md"
AUTH_OPENAPI = ROOT / "docs" / "api" / "auth.openapi.yaml"
HELPER = ROOT / "api" / "gateway" / "oidc_login_product.py"
TERMINAL_HTML = ROOT / "smart_terminal" / "ui" / "index.html"
TERMINAL_JS = ROOT / "smart_terminal" / "ui" / "app.js"
PYPROJECT = ROOT / "pyproject.toml"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
TASKS = ROOT / "docs" / "project" / "TASKS.md"

def _auth_spec() -> dict[str, Any]:
    loaded = yaml.safe_load(AUTH_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded

def test_g147_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "PHX-G147" in adr
    assert "authorization_code_enabled" in adr.casefold()
    gate = GATE.read_text(encoding="utf-8")
    assert "DAL-G003" in gate or "DAL-U008" in gate
    assert "T-0189" in gate
    acceptance = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Brain" in acceptance and "Twin" in acceptance
    assert "WebAuthn" in acceptance or "webauthn" in acceptance.casefold()

def test_g147_helper_posture_live_routes_and_fail_closed() -> None:
    assert HELPER.is_file()
    posture = oidc_login_product_posture(authorization_code_enabled=False)
    assert posture["milestone"] == "PHX-G147"
    assert posture["authorization_code_enabled"] is False
    assert posture["fail_closed_when_unconfigured"] is True
    assert posture["fail_closed"] is True
    routes = posture["live_routes"]
    assert "/auth/oidc/login" in routes
    assert "/auth/oidc/callback" in routes
    assert "/auth/oidc/providers" in routes
    assert "/auth/oidc/refresh" in routes
    assert "/auth/oidc/logout" in routes
    assert "/auth/oidc/status" in routes
    assert posture["fail_closed_reasons"]
    reasons = " ".join(posture["fail_closed_reasons"]).casefold()
    assert "503" in reasons or "unconfigured" in reasons

    enabled = oidc_login_product_posture(authorization_code_enabled=True)
    assert enabled["authorization_code_enabled"] is True
    assert enabled["fail_closed"] is False
    assert enabled["fail_closed_when_unconfigured"] is True

def test_g147_oidc_status_includes_oidc_login_product() -> None:
    from api.gateway.oidc import oidc_status

    status = oidc_status()
    assert "oidc_login_product" in status
    product = status["oidc_login_product"]
    assert "authorization_code_enabled" in product
    assert product["live_routes"]
    assert product["fail_closed_when_unconfigured"] is True
    assert "fail_closed_reasons" in product
    assert product["milestone"] == "PHX-G147"
    # G145 additive field must remain.
    assert "webauthn_product" in status

def test_g147_openapi_documents_posture_and_bumps_patch() -> None:
    spec = _auth_spec()
    assert str(spec["info"]["version"]).startswith("1.3.")
    props = spec["components"]["schemas"]["OidcStatusData"]["properties"]
    assert "oidc_login_product" in props
    product_schema = spec["components"]["schemas"]["OidcLoginProductPosture"]
    product_props = product_schema.get("properties") or {}
    assert "authorization_code_enabled" in product_props
    assert "live_routes" in product_props
    assert "fail_closed_when_unconfigured" in product_props
    assert product_props["fail_closed_when_unconfigured"].get("const") is True
    assert "fail_closed_reasons" in product_props
    paths = set(spec["paths"])
    assert "/auth/webauthn/register" not in paths

def test_g147_package_still_0_2_1_and_alembic_0029() -> None:
    assert sdk_version == "0.2.5"
    assert f'version = "{EXPECTED_PACKAGE}"' in PYPROJECT.read_text(encoding="utf-8")
    assert_current_baseline()

def test_g147_no_webauthn_role_grant_payment_brain_twin_openings_claimed() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (ADR, GATE, ACCEPTANCE)
    )
    folded = combined.casefold()
    assert "webauthn" in folded or "ceremony" in folded
    assert "role" in folded and "grant" in folded
    assert "payment" in folded or "支付" in combined
    assert "brain" in folded and "execute" in folded
    assert "twin" in folded and "authorize" in folded
    assert "webauthn ceremony enabled" not in folded
    assert "role→grant 已打开" not in combined
    assert "brain execute enabled" not in folded
    assert "twin authorize enabled" not in folded

def test_g147_dal_u008_t0189_and_terminal_panel() -> None:
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-U008" in ledger
    assert "PHX-G147" in ledger
    tasks = TASKS.read_text(encoding="utf-8")
    assert "T-0189" in tasks
    assert "G147" in tasks
    assert "延后" not in [
        line for line in tasks.splitlines() if "T-0189" in line
    ][0]
    html = TERMINAL_HTML.read_text(encoding="utf-8")
    js = TERMINAL_JS.read_text(encoding="utf-8")
    assert "OIDC Login Product" in html
    assert "oidcLoginProduct" in html or "oidc_login_product" in js
    assert "loadOidcLoginProductPosture" in js or "oidc_login_product" in js
    assert "btnOidcLogin" in html
    assert "btnOidcRefresh" in html
    assert "btnOidcLogout" in html
    assert "oidcProviderLinks" in html
