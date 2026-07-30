"""PHX-G224 OpenAPI named success envelopes honesty contracts."""

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

ENVELOPES = (
    ("knowledge.openapi.yaml", {"1.0.7"}, "KnowledgeEntityListEnvelope", "/knowledge/entities", "get"),
    ("knowledge.openapi.yaml", {"1.0.7"}, "KnowledgeSearchEnvelope", "/knowledge/search", "get"),
    (
        "knowledge.openapi.yaml",
        {"1.0.7"},
        "KnowledgeProvenanceListEnvelope",
        "/knowledge/provenance/{subjectKind}/{subjectId}",
        "get",
    ),
    ("event.openapi.yaml", {"1.0.7", "1.0.8"}, "DeadLetterListEnvelope", "/events/dead-letters", "get"),
    ("package.openapi.yaml", {"1.0.8", "1.0.9", "1.0.10"}, "PackageSurfacesEnvelope", "/packages/surfaces", "get"),
)

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def _schema_ref(spec: dict, path: str, method: str) -> str:
    schema = spec["paths"][path][method]["responses"]["200"]["content"]["application/json"][
        "schema"
    ]
    ref = schema.get("$ref", "")
    assert ref.startswith("#/components/schemas/")
    return ref.rsplit("/", 1)[-1]

def test_g224_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0243-openapi-named-success-envelopes-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G224_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G224_ARCHITECTURE_GATE.md").is_file()

def test_g224_named_envelopes_and_path_refs() -> None:
    for name, version, schema_name, path, method in ENVELOPES:
        spec = _load(API / name)
        ver = str(spec["info"]["version"])
        if isinstance(version, set):
            prefix = next(iter(version)).rsplit(".", 1)[0] + "."
            assert ver.startswith(prefix) or ver in version
        else:
            prefix = str(version).rsplit(".", 1)[0] + "."
            assert ver.startswith(prefix) or ver == version
        assert schema_name in spec["components"]["schemas"]
        assert _schema_ref(spec, path, method) == schema_name
        props = spec["components"]["schemas"][schema_name]["properties"]
        assert "data" in props
        if schema_name != "PackageSurfacesEnvelope":
            assert props["ok"].get("const") is True

def test_g224_no_path_inline_list_success_in_targets() -> None:
    inline: list[str] = []
    for name, _version, _schema, path, method in ENVELOPES:
        spec = _load(API / name)
        schema = spec["paths"][path][method]["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        if "$ref" not in schema:
            inline.append(f"{name}:{path}")
    assert inline == []

def test_g224_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g224" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert str(props["milestone"]["const"]).startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g224_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U097" in ledger
    assert ("PHX-G224" in tip or "PHX-G225" in tip) and (
        "PHX-G224" in manifest or "PHX-G225" in manifest
    ) and ("PHX-G2" in status)
