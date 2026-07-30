"""PHX-G166 OpenAPI semantic remainder deepen contracts (T-0188)."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path
from typing import Any

import pytest
import yaml

from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0185-openapi-semantic-remainder-deepen.md"
GATE = ROOT / "docs" / "project" / "PHX-G166_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G166_ACCEPTANCE.md"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"
IDENTITY = ROOT / "docs" / "api" / "identity.openapi.yaml"
ORG = ROOT / "docs" / "api" / "organization.openapi.yaml"
PERM = ROOT / "docs" / "api" / "permission.openapi.yaml"
PACKAGE = ROOT / "docs" / "api" / "package.openapi.yaml"
TERMINAL = ROOT / "docs" / "api" / "terminal.openapi.yaml"
WORKFLOW = ROOT / "docs" / "api" / "workflow.openapi.yaml"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
TIP = ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md"
MANIFEST = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"
TASKS = ROOT / "docs" / "project" / "TASKS.md"
HTML = ROOT / "smart_terminal" / "ui" / "index.html"

def _load(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded

def _kernel_error_ref(spec: dict[str, Any], response_name: str = "KernelError") -> str:
    resp = spec["components"]["responses"][response_name]
    return resp["content"]["application/json"]["schema"]["$ref"]

def test_g166_adr_gate_acceptance() -> None:
    assert ADR.is_file() and GATE.is_file() and ACCEPTANCE.is_file()
    assert "Accepted" in ADR.read_text(encoding="utf-8")
    assert "PHX-G166" in GATE.read_text(encoding="utf-8")
    assert "Fully Accepted" in ACCEPTANCE.read_text(encoding="utf-8")
    assert "full_openapi_http_complete" in ACCEPTANCE.read_text(encoding="utf-8").casefold()

def test_g166_inventory_posture() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["route_mount_parity_complete"] is True
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    fences = " ".join(posture["known_defer_fences"]).casefold()
    assert "semantic" in fences and "t0188" in fences

def test_g166_adapters_meta_and_ops() -> None:
    fastapi = pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from api.gateway import app

    client = TestClient(app)
    response = client.get("/v1/adapters")
    assert response.status_code == 200
    product = response.json()["meta"]["openapi_inventory_product"]
    assert str(product["milestone"]).startswith("PHX-G")
    assert product["full_openapi_http_complete"] is False

    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert str(props["milestone"].get("const", "")).startswith("PHX-G")
    assert str(props["t0188_status"].get("const", "")).startswith("mount_parity_complete")

def test_g166_domains_use_gateway_detail_error() -> None:
    identity = _load(IDENTITY)
    assert identity["info"]["version"].startswith("1.0.")
    assert "GatewayDetailError" in identity["components"]["schemas"]
    assert "GatewayDetailError" in _kernel_error_ref(identity, "Error")

    org = _load(ORG)
    assert org["info"]["version"].startswith("1.0.")
    assert "GatewayDetailError" in _kernel_error_ref(org)

    perm = _load(PERM)
    assert perm["info"]["version"].startswith("1.1.")
    assert "GatewayDetailError" in _kernel_error_ref(perm)

    package = _load(PACKAGE)
    assert package["info"]["version"].startswith("1.0.")
    assert "GatewayDetailError" in _kernel_error_ref(package)
    assert "data" in package["components"]["schemas"]["UuidResult"]["required"]

    terminal = _load(TERMINAL)
    assert terminal["info"]["version"].startswith("1.1.")
    assert "GatewayDetailError" in _kernel_error_ref(terminal)
    assert "data" in terminal["components"]["schemas"]["UuidResult"]["required"]

    workflow = _load(WORKFLOW)
    assert workflow["info"]["version"].startswith("1.0.")
    assert "GatewayDetailError" in _kernel_error_ref(workflow)

def test_g166_package_dal_tip_manifest_terminal() -> None:
    assert sdk_version == "0.2.5"
    assert_current_baseline()
    assert "DAL-U039" in LEDGER.read_text(encoding="utf-8")
    assert "PHX-G166" in TIP.read_text(encoding="utf-8")
    assert "PHX-G166" in MANIFEST.read_text(encoding="utf-8")
    t0188 = [line for line in TASKS.read_text(encoding="utf-8").splitlines() if "T-0188" in line][0]
    assert "G166" in t0188 or "remainder" in t0188.casefold()
    html = HTML.read_text(encoding="utf-8")
    assert "G28" in html or "OpenAPI inventory" in html

def test_g166_no_full_complete_or_hold_enable() -> None:
    text = "\n".join(p.read_text(encoding="utf-8") for p in (ADR, GATE, ACCEPTANCE))
    folded = text.casefold()
    assert "brain execute enabled" not in folded
    assert "twin authorize enabled" not in folded
    assert "全量语义已完成" not in text
    assert "full_openapi_http_complete" in folded
    assert "false" in folded
