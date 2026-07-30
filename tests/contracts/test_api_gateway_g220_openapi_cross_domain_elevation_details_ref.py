"""PHX-G220 OpenAPI cross-domain elevation details $ref honesty contracts."""

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

TARGETS = {
    "ai.openapi.yaml": ("ErrorBody", {"1.0.6", "1.0.7"}),
    "brain.openapi.yaml": ("ErrorBody", "1.0.6"),
    "event.openapi.yaml": ("ErrorBody", {"1.0.6", "1.0.7", "1.0.8"}),
    "identity.openapi.yaml": ("ErrorBody", "1.0.6"),
    "knowledge.openapi.yaml": ("ErrorBody", {"1.0.6", "1.0.7"}),
    "organization.openapi.yaml": ("ErrorResponse", {"1.0.7", "1.0.8", "1.0.9"}),
    "package.openapi.yaml": ("ErrorBody", {"1.0.7", "1.0.8", "1.0.9", "1.0.10"}),
    "permission.openapi.yaml": ("ErrorResponse", "1.1.14"),
    "platform.openapi.yaml": ("ErrorResponse", "1.0.6"),
    "workflow.openapi.yaml": ("ErrorResponse", "1.0.9"),
}

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def _refs(details: dict) -> set[str]:
    refs = set()
    for item in details.get("anyOf") or []:
        if isinstance(item, dict) and "$ref" in item:
            refs.add(item["$ref"].rsplit("/", 1)[-1])
    return refs

def test_g220_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0239-openapi-cross-domain-elevation-details-ref-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G220_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G220_ARCHITECTURE_GATE.md").is_file()

def test_g220_cross_domain_elevation_anyof() -> None:
    for name, (schema_name, version) in TARGETS.items():
        spec = _load(API / name)
        ver = str(spec["info"]["version"])
        if isinstance(version, set):
            prefix = next(iter(version)).rsplit(".", 1)[0] + "."
            assert ver.startswith(prefix) or ver in version
        else:
            prefix = str(version).rsplit(".", 1)[0] + "."
            assert ver.startswith(prefix) or ver == version
        schemas = spec["components"]["schemas"]
        assert "ContextElevationDenialDetails" in schemas
        details = schemas[schema_name]["properties"]["details"]
        assert "ContextElevationDenialDetails" in _refs(details)
    # identity also has ErrorResponse
    identity = _load(API / "identity.openapi.yaml")
    assert "ContextElevationDenialDetails" in _refs(
        identity["components"]["schemas"]["ErrorResponse"]["properties"]["details"]
    )

def test_g220_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g220" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert str(props["milestone"]["const"]).startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g220_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U093" in ledger
    assert ("PHX-G220" in tip or "PHX-G221" in tip or "PHX-G222" in tip or "PHX-G223" in tip) and (
        "PHX-G220" in manifest or "PHX-G221" in manifest or "PHX-G222" in manifest or "PHX-G223" in manifest
    ) and ("PHX-G2" in status)
