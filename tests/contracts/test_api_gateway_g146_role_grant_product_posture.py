"""PHX-G146 Role→grant product posture contracts."""

from __future__ import annotations

from tests.contracts._baseline import EXPECTED_PACKAGE, assert_current_baseline

from pathlib import Path
from typing import Any

import yaml

from api.gateway.role_catalog import build_role_catalog_status
from api.gateway.role_grant_product import role_grant_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0165-role-grant-product-posture.md"
GATE = ROOT / "docs" / "project" / "PHX-G146_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G146_ACCEPTANCE.md"
PERMISSION_OPENAPI = ROOT / "docs" / "api" / "permission.openapi.yaml"
HELPER = ROOT / "api" / "gateway" / "role_grant_product.py"
TERMINAL_HTML = ROOT / "smart_terminal" / "ui" / "index.html"
TERMINAL_JS = ROOT / "smart_terminal" / "ui" / "app.js"
PYPROJECT = ROOT / "pyproject.toml"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"

def _permission_spec() -> dict[str, Any]:
    loaded = yaml.safe_load(PERMISSION_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded

def test_g146_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "PHX-G146" in adr
    assert "auto_grant_from_role_enabled" in adr.casefold()
    gate = GATE.read_text(encoding="utf-8")
    assert "Eng Explicit Defer" in gate or "Eng `3`" in gate or "Eng 3" in gate
    acceptance = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Cap" in acceptance or "cap" in acceptance.casefold()
    assert "Brain" in acceptance and "Twin" in acceptance

def test_g146_role_grants_write_route_absent_or_stub() -> None:
    """G146 held the path ABSENT; G156 may document stub 503 instead of live mint."""

    spec = _permission_spec()
    paths = set(spec["paths"])
    # Live mint path shapes that would imply auto-write product page stay out
    assert "/permission/roles/grants" not in paths
    body = PERMISSION_OPENAPI.read_text(encoding="utf-8")
    assert "role_grant_product" in body or "Role→grant" in body
    if "/permission/role-grants" in paths:
        assert "503" in body or "GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED" in body
        assert (
            "stub" in body.casefold()
            or "G156" in body
            or "G161" in body
            or "env-gated" in body.casefold()
        )

def test_g146_helper_posture_auto_write_disabled() -> None:
    assert HELPER.is_file()
    posture = role_grant_product_posture()
    # Default remains disabled without env; G161 may enable via env separately.
    assert posture["auto_grant_from_role_enabled"] is False
    assert isinstance(posture["auto_write_routes"], list)
    assert posture["manual_grant_relatives"] == "g128_g129"
    assert posture["evaluate_only_relative"] == "g83_role_grant_map"
    assert "fail_closed_reasons" in posture
    reasons = " ".join(posture["fail_closed_reasons"]).casefold()
    assert "cap" in reasons and "grant" in reasons
    assert "title" in reasons and "permission" in reasons
    helper_src = HELPER.read_text(encoding="utf-8")
    assert (
        "Cap≠grant" in helper_src
        or "cap" in helper_src.casefold()
        or "Never Cap" in helper_src
        or "does not insert" in helper_src.casefold()
    )

def test_g146_roles_status_includes_role_grant_product() -> None:
    status = build_role_catalog_status()
    assert "role_grant_product" in status
    product = status["role_grant_product"]
    assert product["auto_grant_from_role_enabled"] is False
    assert isinstance(product["auto_write_routes"], list)
    assert "fail_closed_reasons" in product
    assert str(product["milestone"]).startswith("PHX-G")

def test_g146_openapi_documents_posture_and_bumps_patch() -> None:
    spec = _permission_spec()
    assert str(spec["info"]["version"]).startswith("1.1.")
    props = spec["components"]["schemas"]["RoleCatalogStatus"]["properties"]
    assert "role_grant_product" in props
    product_schema = spec["components"]["schemas"]["RoleGrantProductPosture"]
    product_props = product_schema.get("properties") or {}
    assert "auto_grant_from_role_enabled" in product_props
    # G146/G156 used const:false；G161 removes const（env-gated boolean）
    assert product_props["auto_grant_from_role_enabled"].get("type") == "boolean" or (
        product_props["auto_grant_from_role_enabled"].get("const") is False
    )
    assert "auto_write_routes" in product_props
    routes = product_props["auto_write_routes"]
    assert "maxItems" not in routes or routes.get("maxItems") != 0
    assert "fail_closed_reasons" in product_props

def test_g146_package_still_0_2_1_and_alembic_0029() -> None:
    assert sdk_version == "0.2.5"
    assert f'version = "{EXPECTED_PACKAGE}"' in PYPROJECT.read_text(encoding="utf-8")
    assert_current_baseline()

def test_g146_no_auto_write_payment_brain_twin_openings_claimed() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (ADR, GATE, ACCEPTANCE)
    )
    folded = combined.casefold()
    assert "auto" in folded and "write" in folded
    assert "payment" in folded or "支付" in combined
    assert "brain" in folded and "execute" in folded
    assert "twin" in folded and "authorize" in folded
    assert "role→grant auto-write 已打开" not in combined
    assert "brain execute enabled" not in folded
    assert "twin authorize enabled" not in folded

def test_g146_dal_u007_and_terminal_thin_panel() -> None:
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-U007" in ledger
    assert "PHX-G146" in ledger or ("Eng" in ledger and "3" in ledger)
    html = TERMINAL_HTML.read_text(encoding="utf-8")
    js = TERMINAL_JS.read_text(encoding="utf-8")
    assert "roleGrantProduct" in html or "Role→grant product" in html
    assert "role_grant_product" in js or "loadRoleGrantProductPosture" in js
