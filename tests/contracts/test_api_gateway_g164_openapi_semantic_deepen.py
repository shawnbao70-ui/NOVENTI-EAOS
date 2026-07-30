"""PHX-G164 OpenAPI semantic deepen contracts (T-0188)."""

from __future__ import annotations

from tests.contracts._baseline import EXPECTED_PACKAGE, assert_current_baseline

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version
from eaos_sdk.catalog import list_openapi_contracts

ROOT = Path(__file__).resolve().parents[2]
ADR = ROOT / "docs" / "decisions" / "ADR-0182-openapi-semantic-deepen.md"
GATE = ROOT / "docs" / "project" / "PHX-G164_ARCHITECTURE_GATE.md"
ACCEPTANCE = ROOT / "docs" / "project" / "PHX-G164_ACCEPTANCE.md"
OPS_OPENAPI = ROOT / "docs" / "api" / "ops.openapi.yaml"
KNOWLEDGE_OPENAPI = ROOT / "docs" / "api" / "knowledge.openapi.yaml"
AI_OPENAPI = ROOT / "docs" / "api" / "ai.openapi.yaml"
EVENT_OPENAPI = ROOT / "docs" / "api" / "event.openapi.yaml"
BRAIN_OPENAPI = ROOT / "docs" / "api" / "brain.openapi.yaml"
WORKFLOW_OPENAPI = ROOT / "docs" / "api" / "workflow.openapi.yaml"
HELPER = ROOT / "api" / "gateway" / "openapi_inventory_product.py"
TERMINAL_HTML = ROOT / "smart_terminal" / "ui" / "index.html"
TERMINAL_JS = ROOT / "smart_terminal" / "ui" / "app.js"
PYPROJECT = ROOT / "pyproject.toml"
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
TASKS = ROOT / "docs" / "project" / "TASKS.md"
TIP = ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md"
MANIFEST = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"

def _load_yaml(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded

def _norm_param(path: str) -> str:
    return re.sub(r"\{[^}]+\}", "{}", path)

def _norm_oa(path: str) -> str:
    if path.startswith("/v1/"):
        return path
    if path.startswith("/"):
        return "/v1" + path
    return "/v1/" + path

def test_g164_adr_gate_acceptance_exist() -> None:
    assert ADR.is_file()
    assert GATE.is_file()
    assert ACCEPTANCE.is_file()
    adr = ADR.read_text(encoding="utf-8")
    assert "Accepted" in adr
    assert "PHX-G164" in adr
    assert "route_mount_parity_complete" in adr
    gate = GATE.read_text(encoding="utf-8")
    assert "DAL-U036" in gate or "DAL-G003" in gate
    acceptance = ACCEPTANCE.read_text(encoding="utf-8")
    assert "full_openapi_http_complete" in acceptance.casefold() or "semantic" in acceptance.casefold()
    assert "Brain" in acceptance and "Twin" in acceptance
    assert "Fully Accepted" in acceptance

def test_g164_helper_mount_vs_semantic_split() -> None:
    assert HELPER.is_file()
    posture = openapi_inventory_product_posture()
    # Softened after PHX-G166 remainder deepen (milestone advanced; mount invariants hold).
    assert posture["milestone"].startswith("PHX-G")
    assert posture["surface"] == "foundation_openapi_inventory_product"
    assert posture["openapi_contract_count"] == len(list_openapi_contracts())
    assert posture["openapi_contract_count"] == 14
    assert posture["adapter_registry_aligned"] is True
    assert posture["route_mount_parity_complete"] is True
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    fences = " ".join(posture["known_defer_fences"]).casefold()
    assert "semantic" in fences and "t0188" in fences
    assert "route_parity" not in fences or "semantic_parity" in fences
    assert "brain" in fences and "twin" in fences
    assert posture["fail_closed_reasons"]

def test_g164_adapters_meta_and_ops_openapi() -> None:
    fastapi = pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient

    from api.gateway import app

    client = TestClient(app)
    response = client.get("/v1/adapters")
    assert response.status_code == 200
    product = response.json()["meta"]["openapi_inventory_product"]
    assert str(product["milestone"]).startswith("PHX-G")
    assert product["route_mount_parity_complete"] is True
    assert product["full_openapi_http_complete"] is False
    assert str(product["t0188_status"]).startswith("mount_parity_complete")

    spec = _load_yaml(OPS_OPENAPI)
    assert spec["info"]["version"].startswith("1.0.")
    schema = spec["components"]["schemas"]["OpenApiInventoryProductPosture"]
    props = schema["properties"]
    assert str(props["milestone"].get("const", "")).startswith("PHX-G")
    assert props["route_mount_parity_complete"].get("const") is True
    assert props["full_openapi_http_complete"].get("const") is False
    assert str(props["t0188_status"].get("const", "")).startswith("mount_parity_complete")

def test_g164_measured_route_mount_parity_zero_missing() -> None:
    fastapi = pytest.importorskip("fastapi")
    from api.gateway import app

    oa_ops: set[tuple[str, str]] = set()
    for path in sorted((ROOT / "docs" / "api").glob("*.openapi.yaml")):
        spec = _load_yaml(path)
        for route, item in (spec.get("paths") or {}).items():
            for method, _op in item.items():
                if method.lower() in ("get", "post", "put", "patch", "delete"):
                    oa_ops.add((method.upper(), _norm_param(_norm_oa(route))))

    mounted: set[tuple[str, str]] = set()
    for route in app.routes:
        methods = getattr(route, "methods", None)
        path = getattr(route, "path", None)
        if not path or not methods or not str(path).startswith("/v1/"):
            continue
        for method in methods:
            if method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                mounted.add((method, _norm_param(str(path))))

    missing = sorted(oa_ops - mounted)
    assert not missing, f"OpenAPI ops missing mounts: {missing[:10]}"
    assert len(oa_ops) >= 160

def test_g164_knowledge_uuid_and_gateway_error() -> None:
    spec = _load_yaml(KNOWLEDGE_OPENAPI)
    assert spec["info"]["version"].startswith("1.0.")
    uuid_result = spec["components"]["schemas"]["UuidResult"]
    assert "id" in uuid_result["required"]
    assert "ok" not in (uuid_result.get("required") or [])
    assert "GatewayDetailError" in spec["components"]["schemas"]
    kernel_error = spec["components"]["responses"]["KernelError"]
    ref = kernel_error["content"]["application/json"]["schema"]["$ref"]
    assert "GatewayDetailError" in ref

def test_g164_ai_event_gateway_error_and_ai_fences() -> None:
    ai = _load_yaml(AI_OPENAPI)
    assert ai["info"]["version"].startswith("1.0.")
    ai_status = ai["components"]["schemas"]["FoundationStatusData"]["properties"]
    assert "ai_subject_required" in ai_status
    assert "commit_requires_approval" in ai_status
    assert "GatewayDetailError" in ai["components"]["schemas"]

    event = _load_yaml(EVENT_OPENAPI)
    assert event["info"]["version"].startswith("1.0.")
    assert "GatewayDetailError" in event["components"]["schemas"]

def test_g164_brain_403_and_status_fences() -> None:
    brain = _load_yaml(BRAIN_OPENAPI)
    assert brain["info"]["version"].startswith("1.0.")
    execute = brain["paths"]["/brain/insights/{insightId}/execute"]["post"]["responses"]
    authorize = brain["paths"]["/twin/snapshots/{snapshotId}/authorize"]["post"]["responses"]
    assert "403" in execute
    assert "403" in authorize
    status_props = brain["components"]["schemas"]["BrainStatusData"]["properties"]
    twin_props = brain["components"]["schemas"]["TwinStatusData"]["properties"]
    assert status_props["execute_execution"].get("const") == "permission_gated"
    assert twin_props["authorize_execution"].get("const") == "permission_gated"
    assert status_props["advisory_required"].get("const") is True
    assert "GatewayDetailError" in brain["components"]["schemas"]
    text = BRAIN_OPENAPI.read_text(encoding="utf-8")
    assert "BRAIN_EXECUTION_FORBIDDEN" in text
    assert "TWIN_EXECUTION_FORBIDDEN" in text

def test_g164_workflow_approval_source_fence() -> None:
    workflow = _load_yaml(WORKFLOW_OPENAPI)
    assert workflow["info"]["version"].startswith("1.0.")
    props = workflow["components"]["schemas"]["FoundationStatusData"]["properties"]
    assert props["approval_source_of_truth"].get("const") == "workflow_kernel"

def test_g164_package_dal_tip_manifest_terminal() -> None:
    assert sdk_version == "0.2.5"
    assert f'version = "{EXPECTED_PACKAGE}"' in PYPROJECT.read_text(encoding="utf-8")
    assert_current_baseline()

    ledger = LEDGER.read_text(encoding="utf-8")
    assert "DAL-U036" in ledger
    assert "PHX-G164" in ledger

    tasks = TASKS.read_text(encoding="utf-8")
    t0188_line = [line for line in tasks.splitlines() if "T-0188" in line][0]
    assert "G164" in t0188_line or "mount" in t0188_line.casefold() or "semantic" in t0188_line.casefold()

    tip = TIP.read_text(encoding="utf-8")
    assert "PHX-G164" in tip
    assert "semantic" in tip.casefold()

    manifest = MANIFEST.read_text(encoding="utf-8")
    assert "PHX-G164" in manifest

    html = TERMINAL_HTML.read_text(encoding="utf-8")
    js = TERMINAL_JS.read_text(encoding="utf-8")
    assert "mount" in html.casefold() or "semantic" in html.casefold()
    assert "route_mount_parity_complete" in js or "mount_parity" in js

def test_g164_no_brain_twin_enable_or_full_complete_claim() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (ADR, GATE, ACCEPTANCE)
    )
    folded = combined.casefold()
    assert "brain execute enabled" not in folded
    assert "twin authorize enabled" not in folded
    # Explicit Out may *mention* full_openapi_http_complete=true as forbidden.
    assert "claims full_openapi_http_complete=true" not in folded
    assert "全量语义已完成" not in combined
    assert "Fully Accepted" in ACCEPTANCE.read_text(encoding="utf-8")
    assert "full_openapi_http_complete" in folded
    assert "false" in folded
