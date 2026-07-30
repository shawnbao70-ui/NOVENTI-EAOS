"""PHX-G204 OpenAPI error details fields[] known-shape honesty contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path
from uuid import uuid4

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

def test_g204_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0223-openapi-error-details-fields-shape-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G204_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G204_ARCHITECTURE_GATE.md").is_file()

def test_g204_catalog_details_document_fields() -> None:
    def _schema_has_fields(schemas: dict, node: dict, seen: set[str] | None = None) -> bool:
        seen = seen or set()
        if not isinstance(node, dict):
            return False
        props = (node.get("properties") or {})
        if "fields" in props:
            return props["fields"].get("type") == "array"
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            name = ref.rsplit("/", 1)[-1]
            if name in seen:
                return False
            seen.add(name)
            return _schema_has_fields(schemas, schemas.get(name) or {}, seen)
        for key in ("anyOf", "oneOf", "allOf"):
            for alt in node.get(key) or []:
                if _schema_has_fields(schemas, alt, seen):
                    return True
        return False

    missing: list[str] = []
    for path in sorted(API.glob("*.openapi.yaml")):
        schemas = _load(path).get("components", {}).get("schemas", {})
        for name in ("ErrorBody", "ErrorResponse"):
            schema = schemas.get(name)
            if not isinstance(schema, dict):
                continue
            details = (schema.get("properties") or {}).get("details") or {}
            if not _schema_has_fields(schemas, details):
                missing.append(f"{path.name}:{name}")
            else:
                # residual object branch may still allow additionalProperties
                props = details.get("properties") or {}
                if "fields" in props:
                    assert props["fields"]["type"] == "array"
                    assert details.get("additionalProperties") is True
    assert missing == []

def test_g204_elevation_fields_emit() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/context/echo",
        headers={
            "X-EAOS-Subject-Id": str(uuid4()),
            "X-EAOS-Subject-Type": "human",
            "X-EAOS-Tenant-Id": str(uuid4()),
            "X-Correlation-ID": "g204-echo",
        },
        json={"tenant_id": str(uuid4()), "roles": ["admin"]},
    )
    assert response.status_code == 400
    fields = response.json()["detail"]["details"]["fields"]
    assert isinstance(fields, list)
    assert "tenant_id" in fields
    assert fields == sorted(fields)

def test_g204_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g204" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g204_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U077" in ledger
    assert ("PHX-G204" in tip or "PHX-G205" in tip or "PHX-G206" in tip) and (
        "PHX-G204" in manifest or "PHX-G205" in manifest or "PHX-G206" in manifest
    ) and ("PHX-G2" in status)