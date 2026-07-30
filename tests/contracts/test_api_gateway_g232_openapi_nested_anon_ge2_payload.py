"""PHX-G232 OpenAPI nested-anon≥2 payload named honesty contracts."""

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

PAIRS = (
    ("ai.openapi.yaml", "1.0.7", "ToolInvocationResult", "ToolInvocationPayload"),
    ("ops.openapi.yaml", {"1.0.42", "1.0.43", "1.0.44", "1.0.45"}, "HealthEnvelope", "HealthPayload"),
    ("ops.openapi.yaml", {"1.0.42", "1.0.43", "1.0.44", "1.0.45"}, "AdaptersEnvelope", "AdaptersMeta", "meta"),
    ("ops.openapi.yaml", {"1.0.42", "1.0.43", "1.0.44", "1.0.45"}, "ContextEchoEnvelope", "ContextEchoPayload"),
)

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g232_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0251-openapi-nested-anon-ge2-payload-named-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G232_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G232_ARCHITECTURE_GATE.md").is_file()

def test_g232_named_payload_refs() -> None:
    for row in PAIRS:
        name, version, envelope, payload = row[:4]
        field = row[4] if len(row) > 4 else "data"
        spec = _load(API / name)
        ver = str(spec["info"]["version"])
        if isinstance(version, set):
            first = next(iter(version))
            assert ver.startswith(".".join(str(first).split(".")[:2]) + ".")
        else:
            assert ver.startswith(".".join(str(version).split(".")[:2]) + ".")
        schemas = spec["components"]["schemas"]
        assert payload in schemas
        ref = schemas[envelope]["properties"][field].get("$ref", "")
        assert ref.endswith("/" + payload)

def test_g232_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g232" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert str(props["milestone"].get("const", "")).startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g232_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U105" in ledger
    assert ("PHX-G232" in tip or "PHX-G233" in tip) and (
        "PHX-G232" in manifest or "PHX-G233" in manifest
    ) and ("PHX-G2" in status)
