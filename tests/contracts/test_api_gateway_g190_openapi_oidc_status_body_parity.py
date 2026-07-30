"""PHX-G190 OpenAPI OIDC status body field parity contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.oidc import oidc_status
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
AUTH = ROOT / "docs" / "api" / "auth.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g190_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0209-openapi-oidc-status-body-field-parity.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G190_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G190_ARCHITECTURE_GATE.md").is_file()

def test_g190_oidc_status_schema_matches_emit() -> None:
    spec = _load(AUTH)
    assert str(spec["info"]["version"]).startswith("1.3.")
    path = spec["paths"]["/auth/oidc/status"]["get"]
    assert (
        path["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
        == "#/components/schemas/OidcStatusEnvelope"
    )
    schema = spec["components"]["schemas"]["OidcStatusData"]
    assert schema.get("additionalProperties") is False
    idp_oidc = spec["components"]["schemas"]["IdpStatusData"]["properties"]["oidc"]
    assert idp_oidc["$ref"] == "#/components/schemas/OidcStatusData"

    emit = oidc_status()
    required = set(schema["required"])
    assert required <= set(emit)
    assert set(emit) <= set(schema["properties"])

    data = TestClient(app).get("/v1/auth/oidc/status").json()["data"]
    assert required <= set(data)
    assert "oidc_login_product" in data and "webauthn_product" in data
    idp = TestClient(app).get("/v1/auth/idp/status").json()["data"]
    assert required <= set(idp["oidc"])

def test_g190_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g190" in " ".join(posture["fail_closed_reasons"]).casefold()

    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g190_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U063" in ledger
    assert ("PHX-G18" in tip or "PHX-G19" in tip or "PHX-G20" in tip) and ("PHX-G18" in manifest or "PHX-G19" in manifest or "PHX-G20" in manifest) and ("PHX-G2" in status)
