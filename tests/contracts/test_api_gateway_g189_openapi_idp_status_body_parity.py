"""PHX-G189 OpenAPI IdP status body field parity contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.idp_status import idp_status
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
AUTH = ROOT / "docs" / "api" / "auth.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g189_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0208-openapi-idp-status-body-field-parity.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G189_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G189_ARCHITECTURE_GATE.md").is_file()

def test_g189_idp_status_schema_matches_emit() -> None:
    spec = _load(AUTH)
    assert str(spec["info"]["version"]).startswith("1.3.")
    path = spec["paths"]["/auth/idp/status"]["get"]
    assert (
        path["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
        == "#/components/schemas/IdpStatusEnvelope"
    )
    schema = spec["components"]["schemas"]["IdpStatusData"]
    jwt_schema = spec["components"]["schemas"]["IdpJwtAggregatePosture"]
    assert schema.get("additionalProperties") is False
    assert jwt_schema.get("additionalProperties") is False
    assert schema["properties"]["writable"]["const"] is False
    assert schema["properties"]["config_source"]["const"] == "environment+registry"
    assert schema["properties"]["oidc"].get("$ref") == "#/components/schemas/OidcStatusData" or schema["properties"]["oidc"].get("additionalProperties") is True

    emit = idp_status()
    assert set(schema["required"]) <= set(emit)
    assert set(jwt_schema["required"]) <= set(emit["jwt"])

    data = TestClient(app).get("/v1/auth/idp/status").json()["data"]
    assert data["writable"] is False
    assert data["config_source"] == "environment+registry"
    assert set(schema["required"]) <= set(data)
    assert "federation" in data and "registry" in data

def test_g189_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert (
        posture["t0188_status"].startswith("mount_parity_complete")
    )
    assert "g189" in " ".join(posture["fail_closed_reasons"]).casefold()

    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g189_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U062" in ledger
    assert ("PHX-G189" in tip or "PHX-G190" in tip) and ("PHX-G189" in manifest or "PHX-G190" in manifest) and ("PHX-G2" in status)
