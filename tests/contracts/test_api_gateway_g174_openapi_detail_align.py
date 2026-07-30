"""PHX-G174 OpenAPI auth/marketplace/platform GatewayDetailError align."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
AUTH = ROOT / "docs" / "api" / "auth.openapi.yaml"
PLATFORM = ROOT / "docs" / "api" / "platform.openapi.yaml"
MARKETPLACE = ROOT / "docs" / "api" / "marketplace.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def _kernel_error_ref(spec: dict) -> str:
    schema = spec["components"]["responses"]["KernelError"]["content"][
        "application/json"
    ]["schema"]
    return schema.get("$ref", "")

def test_g174_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0193-openapi-auth-marketplace-platform-detail.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G174_ACCEPTANCE.md").is_file()

def test_g174_domains_use_gateway_detail_error() -> None:
    auth = _load(AUTH)
    assert auth["info"]["version"] .startswith("1.3.")
    assert "GatewayDetailError" in _kernel_error_ref(auth)

    platform = _load(PLATFORM)
    assert platform["info"]["version"] .startswith("1.0.")
    assert "GatewayDetailError" in _kernel_error_ref(platform)

    marketplace = _load(MARKETPLACE)
    assert marketplace["info"]["version"] .startswith("1.2.")
    assert "GatewayDetailError" in marketplace["components"]["schemas"]
    assert "GatewayDetailError" in _kernel_error_ref(marketplace)

def test_g174_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    reasons = " ".join(posture["fail_closed_reasons"]).casefold()
    assert "g174" in reasons or "g176" in reasons or "g177" in reasons or "g178" in reasons or "g179" in reasons or "g180" in reasons or "g181" in reasons or "g185" in reasons

    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    assert props["t0188_status"]["const"].startswith("mount_parity_complete")

    client = TestClient(app)
    meta = client.get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g174_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U047" in ledger
    # Tip/manifest tip may advance past G174; keep G174 as historical floor.
    assert "PHX-G174" in tip or "PHX-G18" in tip
    assert "PHX-G174" in manifest or "PHX-G18" in manifest
    assert "PHX-G174" in status or "PHX-G18" in status
