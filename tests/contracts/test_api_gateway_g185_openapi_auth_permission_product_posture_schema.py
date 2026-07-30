"""PHX-G185 OpenAPI Auth/Permission product-posture schema parity contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from api.gateway.role_grant_product import role_grant_product_posture
from api.gateway.webauthn_product import webauthn_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
AUTH = ROOT / "docs" / "api" / "auth.openapi.yaml"
PERMISSION = ROOT / "docs" / "api" / "permission.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g185_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0204-openapi-auth-permission-product-posture-schema-parity.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G185_ACCEPTANCE.md").is_file()

def test_g185_webauthn_product_schema_matches_emit() -> None:
    spec = _load(AUTH)
    assert str(spec["info"]["version"]).startswith("1.3.")
    schema = spec["components"]["schemas"]["WebauthnProductPosture"]
    assert schema.get("additionalProperties") is False
    assert schema["properties"]["milestone"]["const"] == "PHX-G160"
    assert schema["properties"]["surface"]["const"] == "foundation_mfa_webauthn_product"
    required = set(schema["required"])
    emit = webauthn_product_posture()
    assert required <= set(emit)
    for key in required:
        assert key in schema["properties"]

def test_g185_role_grant_product_schema_matches_emit() -> None:
    spec = _load(PERMISSION)
    assert str(spec["info"]["version"]).startswith("1.1.")
    schema = spec["components"]["schemas"]["RoleGrantProductPosture"]
    assert schema.get("additionalProperties") is False
    assert schema["properties"]["milestone"]["const"] == "PHX-G161"
    assert schema["properties"]["surface"]["const"] == "foundation_role_grant_product"
    required = set(schema["required"])
    emit = role_grant_product_posture()
    assert required <= set(emit)
    for key in required:
        assert key in schema["properties"]

def test_g185_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g185" in " ".join(posture["fail_closed_reasons"]).casefold()

    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g185_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U058" in ledger
    assert ("PHX-G18" in tip or "PHX-G19" in tip or "PHX-G20" in tip) and ("PHX-G18" in manifest or "PHX-G19" in manifest or "PHX-G20" in manifest) and ("PHX-G2" in status)
