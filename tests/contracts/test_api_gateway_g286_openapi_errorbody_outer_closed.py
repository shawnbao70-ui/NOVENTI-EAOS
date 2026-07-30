"""PHX-G286 OpenAPI ErrorBody outer closed honesty."""

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

FILES = (
    "ai.openapi.yaml",
    "brain.openapi.yaml",
    "event.openapi.yaml",
    "identity.openapi.yaml",
    "knowledge.openapi.yaml",
    "marketplace.openapi.yaml",
    "package.openapi.yaml",
    "terminal.openapi.yaml",
)

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g286_docs_present() -> None:
    assert (
        ROOT / "docs" / "decisions" / "ADR-0305-openapi-errorbody-outer-closed.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G286_ACCEPTANCE.md").is_file()

def test_g286_errorbody_outers_closed() -> None:
    for name in FILES:
        schemas = _load(API / name)["components"]["schemas"]
        body = schemas["ErrorBody"]
        assert body.get("additionalProperties") is False, name
        assert set(body.get("required") or []) >= {"code", "message"}
        details = (body.get("properties") or {}).get("details") or {}
        # intentional residual: details remains composable (anyOf/object)
        assert details, name

def test_g286_admin_bind_single() -> None:
    js = (ROOT / "smart_terminal" / "ui" / "app.js").read_text(encoding="utf-8")
    assert js.count('bind("btnAdminOpenapiInventoryStatus"') == 1

def test_g286_ops_tip_parity() -> None:
    posture = openapi_inventory_product_posture()
    ops = _load(OPS)
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert posture["milestone"].startswith("PHX-G")
    assert str(props["milestone"].get("const", "")).startswith("PHX-G")
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert str(props["t0188_status"].get("const", "")).startswith("mount_parity_complete")
    assert ops["info"]["version"].startswith("1.0.")
    assert "g286" in " ".join(posture["fail_closed_reasons"]).casefold()
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False

def test_g286_baseline() -> None:
    assert sdk_version == "0.2.5"
    assert_current_baseline()
    assert "DAL-U159" in (
        ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
    ).read_text(encoding="utf-8")
