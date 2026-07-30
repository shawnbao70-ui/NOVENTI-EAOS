"""PHX-G188 OpenAPI JWT status body field parity contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.auth_jwt import jwt_status_view
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
AUTH = ROOT / "docs" / "api" / "auth.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g188_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0207-openapi-jwt-status-body-field-parity.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G188_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G188_ARCHITECTURE_GATE.md").is_file()

def test_g188_jwt_status_schema_matches_emit() -> None:
    spec = _load(AUTH)
    assert str(spec["info"]["version"]).startswith("1.3.")
    path = spec["paths"]["/auth/jwt/status"]["get"]
    assert (
        path["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
        == "#/components/schemas/JwtStatusEnvelope"
    )
    schema = spec["components"]["schemas"]["JwtStatusData"]
    denylist = spec["components"]["schemas"]["JwtDenylistPosture"]
    assert schema.get("additionalProperties") is False
    assert denylist.get("additionalProperties") is False
    assert schema["properties"]["writable"]["const"] is False

    emit = jwt_status_view()
    required = set(schema["required"])
    assert required <= set(emit)
    assert set(emit) - {'denylist'} <= set(schema["properties"])
    assert set(denylist["required"]) <= set(emit["denylist"])

    data = TestClient(app).get("/v1/auth/jwt/status").json()["data"]
    assert data["writable"] is False
    assert "jti" not in str(data).casefold() or "runtime_revoked_count" in data
    assert set(schema["required"]) <= set(data)

def test_g188_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert (
        posture["t0188_status"].startswith("mount_parity_complete")
    )
    assert "g188" in " ".join(posture["fail_closed_reasons"]).casefold()

    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g188_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U061" in ledger
    assert ("PHX-G188" in tip or "PHX-G189" in tip) and ("PHX-G188" in manifest or "PHX-G189" in manifest) and ("PHX-G2" in status)
