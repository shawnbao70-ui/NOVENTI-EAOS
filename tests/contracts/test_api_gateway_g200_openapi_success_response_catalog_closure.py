"""PHX-G200 OpenAPI success-response catalog closure honesty contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "docs" / "api"
OPS = API / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g200_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0219-openapi-success-response-catalog-closure-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G200_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G200_ARCHITECTURE_GATE.md").is_file()

def test_g200_catalog_success_responses_have_content_or_ref() -> None:
    missing: list[str] = []
    for path in sorted(API.glob("*.openapi.yaml")):
        spec = _load(path)
        for route, methods in (spec.get("paths") or {}).items():
            for method, op in methods.items():
                if method.startswith("x") or not isinstance(op, dict):
                    continue
                responses = op.get("responses") or {}
                for code in ("200", "201"):
                    resp = responses.get(code)
                    if not isinstance(resp, dict):
                        continue
                    if "content" not in resp and "$ref" not in resp:
                        missing.append(f"{path.name} {method.upper()} {route} {code}")
    assert missing == []

def test_g200_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g200" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    assert props["full_openapi_http_complete"]["const"] is False
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")
    assert meta["full_openapi_http_complete"] is False

def test_g200_ledger_tip_manifest_baseline() -> None:
    assert sdk_version == "0.2.5"
    assert_current_baseline()
    ledger = (ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md").read_text(
        encoding="utf-8"
    )
    tip = (ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md").read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(
        encoding="utf-8"
    )
    status = (ROOT / "docs" / "project" / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "DAL-U073" in ledger
    assert ("PHX-G20" in tip or "PHX-G2" in tip) and ("PHX-G20" in manifest or "PHX-G2" in manifest) and ("PHX-G2" in status)
