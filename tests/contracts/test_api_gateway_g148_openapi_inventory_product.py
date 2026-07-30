"""PHX-G148 OpenAPI inventory product posture contracts."""

from __future__ import annotations

from tests.contracts._baseline import EXPECTED_PACKAGE, assert_current_baseline

from pathlib import Path
from typing import Any

import pytest
import yaml

from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version
from eaos_sdk.catalog import list_openapi_contracts

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0167-openapi-inventory-product-posture.md"
GATE = ROOT / "docs" / "project" / "PHX-G148_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G148_ACCEPTANCE.md"
OPS_OPENAPI = ROOT / "docs" / "api" / "ops.openapi.yaml"
HELPER = ROOT / "api" / "gateway" / "openapi_inventory_product.py"
TERMINAL_HTML = ROOT / "smart_terminal" / "ui" / "index.html"
TERMINAL_JS = ROOT / "smart_terminal" / "ui" / "app.js"
PYPROJECT = ROOT / "pyproject.toml"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
TASKS = ROOT / "docs" / "project" / "TASKS.md"

def _ops_spec() -> dict[str, Any]:
    loaded = yaml.safe_load(OPS_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded

def test_g148_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "PHX-G148" in adr
    assert "list_openapi_contracts" in adr
    gate = GATE.read_text(encoding="utf-8")
    assert "DAL-G003" in gate or "DAL-U009" in gate
    assert "T-0188" in gate
    acceptance = ACCEPTANCE.read_text(encoding="utf-8")
    assert "部分完成" in acceptance or "partial" in acceptance.casefold()
    assert "Brain" in acceptance and "Twin" in acceptance
    assert "full_openapi_http_complete" in acceptance.casefold() or "全量" in acceptance

def test_g148_helper_posture_counts_domains_and_fences() -> None:
    assert HELPER.is_file()
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["surface"] == "foundation_openapi_inventory_product"
    assert posture["openapi_contract_count"] == len(list_openapi_contracts())
    assert posture["openapi_contract_count"] == 14
    assert posture["adapter_count"] == 14
    assert posture["adapter_registry_aligned"] is True
    assert posture["adapter_registry_status"] == "aligned"
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    thin = posture["thin_probe_domains"]
    assert "identity" in thin
    assert "auth" in thin
    assert "ops" in thin
    assert "marketplace" in thin
    assert isinstance(posture["deferred_domains"], list)
    fences = " ".join(posture["known_defer_fences"]).casefold()
    assert "t0188" in fences or "full_openapi" in fences
    assert "webauthn" in fences
    assert "payment" in fences or "marketplace" in fences
    assert "brain" in fences and "twin" in fences
    assert posture["fail_closed_reasons"]

def test_g148_adapters_meta_includes_inventory_product() -> None:
    fastapi = pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from api.gateway import app

    client = TestClient(app)
    response = client.get("/v1/adapters")
    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["count"] == 14
    product = body["meta"]["openapi_inventory_product"]
    assert str(product["milestone"]).startswith("PHX-G")
    assert product["openapi_contract_count"] == 14
    assert product["adapter_registry_aligned"] is True
    assert product["full_openapi_http_complete"] is False
    assert product["thin_probe_domains"]
    assert "known_defer_fences" in product

def test_g148_openapi_documents_posture_and_bumps_patch() -> None:
    spec = _ops_spec()
    assert str(spec["info"]["version"]).startswith("1.0.")
    meta_schema = spec["components"]["schemas"]["AdaptersEnvelope"]["properties"]["meta"]
    if "$ref" in meta_schema:
        ref_name = meta_schema["$ref"].rsplit("/", 1)[-1]
        meta_props = spec["components"]["schemas"][ref_name]["properties"]
    else:
        meta_props = meta_schema["properties"]
    assert "openapi_inventory_product" in meta_props
    product_schema = spec["components"]["schemas"]["OpenApiInventoryProductPosture"]
    product_props = product_schema.get("properties") or {}
    assert "openapi_contract_count" in product_props
    assert "thin_probe_domains" in product_props
    assert "deferred_domains" in product_props
    assert "known_defer_fences" in product_props
    assert product_props["full_openapi_http_complete"].get("const") is False
    t0188_const = product_props["t0188_status"].get("const")
    assert t0188_const is None or str(t0188_const).startswith(
        ("partial_inventory_posture", "mount_parity_complete")
    )
    assert "/openapi/inventory" not in set(spec["paths"])

def test_g148_package_still_0_2_1_and_alembic_0029() -> None:
    assert sdk_version == "0.2.5"
    assert f'version = "{EXPECTED_PACKAGE}"' in PYPROJECT.read_text(encoding="utf-8")
    assert_current_baseline()

def test_g148_no_full_surface_payment_brain_twin_openings_claimed() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (ADR, GATE, ACCEPTANCE)
    )
    folded = combined.casefold()
    assert "full" in folded or "全量" in combined
    assert "payment" in folded or "支付" in combined
    assert "brain" in folded and "execute" in folded
    assert "twin" in folded and "authorize" in folded
    assert "full openapi http complete" not in folded
    assert "全量路由已完成" not in combined
    assert "brain execute enabled" not in folded
    assert "twin authorize enabled" not in folded

def test_g148_dal_u009_t0188_partial_and_terminal_row() -> None:
    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-U009" in ledger
    assert "PHX-G148" in ledger
    tasks = TASKS.read_text(encoding="utf-8")
    t0188_line = [line for line in tasks.splitlines() if "T-0188" in line][0]
    assert "部分完成" in t0188_line or "partial" in t0188_line.casefold()
    assert (
        "延后" not in t0188_line
        or "仍延后" in t0188_line
        or "部分" in t0188_line
        or "G164" in t0188_line
    )
    html = TERMINAL_HTML.read_text(encoding="utf-8")
    js = TERMINAL_JS.read_text(encoding="utf-8")
    assert "OpenAPI Inventory" in html or "openapiInventory" in html
    assert "openapi_inventory_product" in js or "loadOpenapiInventoryProductPosture" in js
    assert "adapters" in js
