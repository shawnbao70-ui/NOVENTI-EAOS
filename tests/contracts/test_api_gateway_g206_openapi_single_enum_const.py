"""PHX-G206 OpenAPI single-value enum const honesty contracts."""

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

TARGETS = (
    ("package.openapi.yaml", "ResolvedAction", "source", "package_manifest", {"1.0.6", "1.0.7", "1.0.8", "1.0.9", "1.0.10"}),
    ("permission.openapi.yaml", "RoleCatalogStatus", "catalog_store", "process_memory", {"1.1.12", "1.1.13", "1.1.14"}),
    (
        "permission.openapi.yaml",
        "RoleGrantAutoWriteMintResponse",
        "auto_write_step",
        "role_grants",
        {"1.1.12", "1.1.13", "1.1.14"},
    ),
    (
        "permission.openapi.yaml",
        "RoleGrantAutoWriteStubDetail",
        "auto_write_step",
        "role_grants",
        {"1.1.12", "1.1.13", "1.1.14"},
    ),
    ("terminal.openapi.yaml", "ApprovalPresentation", "source", "workflow", {"1.1.8", "1.1.9", "1.1.10", "1.1.11", "1.1.12"}),
)

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g206_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0225-openapi-single-enum-const-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G206_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G206_ARCHITECTURE_GATE.md").is_file()

def test_g206_single_enums_have_const() -> None:
    for name, schema_name, prop_name, const_value, version in TARGETS:
        spec = _load(API / name)
        ver = str(spec["info"]["version"])
        if isinstance(version, set):
            prefix = next(iter(version)).rsplit(".", 1)[0] + "."
            assert ver.startswith(prefix) or ver in version
        else:
            prefix = str(version).rsplit(".", 1)[0] + "."
            assert ver.startswith(prefix) or ver == version or ver in version
        prop = spec["components"]["schemas"][schema_name]["properties"][prop_name]
        assert prop.get("const") == const_value
        assert prop.get("enum") == [const_value]

def test_g206_catalog_has_zero_single_enum_without_const() -> None:
    missing: list[str] = []
    for path in sorted(API.glob("*.openapi.yaml")):
        schemas = _load(path).get("components", {}).get("schemas") or {}
        for schema_name, schema in schemas.items():
            if not isinstance(schema, dict):
                continue
            for prop_name, prop in (schema.get("properties") or {}).items():
                if (
                    isinstance(prop, dict)
                    and prop.get("enum")
                    and len(prop["enum"]) == 1
                    and "const" not in prop
                ):
                    missing.append(f"{path.name}:{schema_name}.{prop_name}")
    assert missing == []

def test_g206_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g206" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g206_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U079" in ledger
    assert ("PHX-G206" in tip or "PHX-G207" in tip or "PHX-G208" in tip) and (
        "PHX-G206" in manifest or "PHX-G207" in manifest or "PHX-G208" in manifest
    ) and ("PHX-G2" in status)