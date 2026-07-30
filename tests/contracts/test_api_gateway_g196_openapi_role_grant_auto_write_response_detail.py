"""PHX-G196 OpenAPI RoleGrant auto-write response/detail parity contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from api.gateway.role_grant_auto_write import (
    GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED,
    raise_role_grant_auto_write_disabled,
)
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
PERMISSION = ROOT / "docs" / "api" / "permission.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g196_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0215-openapi-role-grant-auto-write-response-detail-parity.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G196_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G196_ARCHITECTURE_GATE.md").is_file()

def test_g196_stub_detail_schema_matches_emit() -> None:
    spec = _load(PERMISSION)
    assert str(spec["info"]["version"]).startswith("1.1.")
    detail = spec["components"]["schemas"]["RoleGrantAutoWriteStubDetail"]
    assert detail.get("additionalProperties") is False
    assert detail["properties"]["milestone"]["const"] == "PHX-G161"
    assert set(detail["properties"]["next_action"]["enum"]) == {'none', 'configure_permission_role_grant_map'}
    required = set(detail["required"])
    assert "correlation_id" not in detail["properties"]

    client = TestClient(app)
    response = client.post(
        "/v1/permission/role-grants",
        json={
            "principal_id": "00000000-0000-4000-8000-000000000001",
            "roles": ["operator"],
        },
    )
    assert response.status_code == 503
    emit = response.json()["detail"]
    assert emit["code"] == GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED
    assert required <= set(emit)
    for key in required:
        assert key in detail["properties"]

def test_g196_mint_response_schema_closed() -> None:
    spec = _load(PERMISSION)
    mint = spec["components"]["schemas"]["RoleGrantAutoWriteMintResponse"]
    assert mint.get("additionalProperties") is False
    assert mint["properties"]["milestone"]["const"] == "PHX-G161"
    required = {'auto_write_step', 'grant_minted', 'cap_is_grant', 'title_is_permission', 'milestone', 'principal_id', 'roles_applied', 'grants', 'grant_count', 'audit_id'}
    assert required <= set(mint["required"])
    assert mint["properties"]["grants"]["items"] == {
        "$ref": "#/components/schemas/RoleGrantMintedGrant"
    }
    grant = spec["components"]["schemas"]["RoleGrantMintedGrant"]
    assert grant.get("additionalProperties") is False
    assert set(grant["required"]) == {'id', 'resource_type', 'actions', 'roles'}

def test_g196_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g196" in " ".join(posture["fail_closed_reasons"]).casefold()

    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g196_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U069" in ledger
    assert ("PHX-G18" in tip or "PHX-G19" in tip or "PHX-G20" in tip) and ("PHX-G18" in manifest or "PHX-G19" in manifest or "PHX-G20" in manifest) and ("PHX-G2" in status)
    # keep raise helper import exercised for contract surface stability
    assert callable(raise_role_grant_auto_write_disabled)
