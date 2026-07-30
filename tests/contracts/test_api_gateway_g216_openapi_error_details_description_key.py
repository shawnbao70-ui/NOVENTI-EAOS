"""PHX-G216 OpenAPI ErrorResponse.details description-key honesty contracts."""

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
    "organization.openapi.yaml": {"1.0.6", "1.0.7", "1.0.8", "1.0.9"},
    "permission.openapi.yaml": {"1.1.13", "1.1.14"},
    "platform.openapi.yaml": {"1.0.5", "1.0.6"},
    "workflow.openapi.yaml": {"1.0.8", "1.0.9"},
}

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g216_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0235-openapi-error-details-description-key-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G216_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G216_ARCHITECTURE_GATE.md").is_file()

def test_g216_single_details_description_key() -> None:
    for name, version in TARGETS.items():
        path = API / name
        text = path.read_text(encoding="utf-8")
        # G216 removed duplicate sibling description; G220 may compose via anyOf.
        assert "G202/G204/G216" in text or "G216" in text or "G220" in text
        assert "PHX-G202 inventory" not in text or name == "ops.openapi.yaml"
        assert text.count(
            "Optional structured denial context from live gateway emit"
        ) == 0
        spec = _load(path)
        ver = str(spec["info"]["version"])
        _allowed = version
        prefix = next(iter(_allowed) if isinstance(_allowed, (set, frozenset)) else [_allowed]).rsplit(".", 1)[0] + "."
        assert ver.startswith(prefix) or ver in _allowed
        details = spec["components"]["schemas"]["ErrorResponse"]["properties"]["details"]
        if "anyOf" in details:
            refs = {
                item.get("$ref", "").rsplit("/", 1)[-1]
                for item in details["anyOf"]
                if isinstance(item, dict)
            }
            assert "ContextElevationDenialDetails" in refs
        else:
            assert "fields" in details["properties"]
            assert details["additionalProperties"] is True
        assert "G216" in details.get("description", "") or "G220" in details.get(
            "description", ""
        )

def test_g216_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g216" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert str(props["milestone"]["const"]).startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g216_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U089" in ledger
    assert ("PHX-G216" in tip or "PHX-G217" in tip or "PHX-G218" in tip or "PHX-G220" in tip or "PHX-G222" in tip or "PHX-G223" in tip) and (
        "PHX-G216" in manifest
        or "PHX-G217" in manifest
        or "PHX-G218" in manifest
        or "PHX-G220" in manifest
        or "PHX-G222" in manifest
        or "PHX-G223" in manifest
    ) and ("PHX-G2" in status)
