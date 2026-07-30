"""PHX-G218 OpenAPI named Details $ref composition honesty contracts."""

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

def _refs(details: dict) -> set[str]:
    refs = set()
    for item in details.get("anyOf") or []:
        if isinstance(item, dict) and "$ref" in item:
            refs.add(item["$ref"].rsplit("/", 1)[-1])
    return refs

def test_g218_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0237-openapi-named-details-ref-composition-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G218_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G218_ARCHITECTURE_GATE.md").is_file()

def test_g218_named_details_anyof_refs() -> None:
    auth = _load(API / "auth.openapi.yaml")
    assert str(auth["info"]["version"]).startswith("1.3.")
    auth_refs = _refs(auth["components"]["schemas"]["ErrorResponse"]["properties"]["details"])
    assert auth_refs == {
        "OidcRequiredClaimMissingDetails",
        "OidcRoleRequiredDetails",
        "OidcAmrRequiredDetails",
        "OidcAcrRequiredDetails",
    }

    market = _load(API / "marketplace.openapi.yaml")
    assert str(market["info"]["version"]).startswith("1.2.")
    assert _refs(market["components"]["schemas"]["ErrorBody"]["properties"]["details"]) == {
        "HostAcquireAllowlistDenialDetails"
    }

    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    assert _refs(ops["components"]["schemas"]["ErrorResponse"]["properties"]["details"]) == {
        "ContextElevationDenialDetails"
    }

    terminal = _load(API / "terminal.openapi.yaml")
    assert str(terminal["info"]["version"]).startswith("1.1.")
    assert _refs(
        terminal["components"]["schemas"]["ErrorBody"]["properties"]["details"]
    ) == {"ContextElevationDenialDetails"}

def test_g218_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert (
        posture["t0188_status"].startswith("mount_parity_complete")
    )
    assert "g218" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert str(props["milestone"].get("const", "")).startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g218_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U091" in ledger
    assert ("PHX-G218" in tip or "PHX-G219" in tip or "PHX-G220" in tip or "PHX-G222" in tip or "PHX-G223" in tip) and (
        "PHX-G218" in manifest or "PHX-G219" in manifest or "PHX-G220" in manifest or "PHX-G222" in manifest or "PHX-G223" in manifest
    ) and ("PHX-G2" in status)
