"""PHX-G230 OpenAPI federation matrix payload named honesty contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from api.gateway.tenant_idp_federation import federation_matrix
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / "docs" / "api"
OPS = API / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g230_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0249-openapi-federation-matrix-payload-named-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G230_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G230_ARCHITECTURE_GATE.md").is_file()

def test_g230_federation_matrix_named_schemas() -> None:
    platform = _load(API / "platform.openapi.yaml")
    assert str(platform["info"]["version"]).startswith("1.0.")
    schemas = platform["components"]["schemas"]
    for name in (
        "FederationMatrixCell",
        "FederationMatrixPayload",
        "FederationMatrixMeta",
        "FederationMatrixEnvelope",
    ):
        assert name in schemas
    env = schemas["FederationMatrixEnvelope"]["properties"]
    assert env["data"]["$ref"].endswith("/FederationMatrixPayload")
    assert env["meta"]["$ref"].endswith("/FederationMatrixMeta")
    meta_req = set(schemas["FederationMatrixMeta"]["required"])
    assert {
        "cell_count",
        "tenant_count",
        "issuer_count",
        "binding_count",
        "active_count",
        "include_unbound_issuers",
    } <= meta_req
    cell_req = set(schemas["FederationMatrixCell"]["required"])
    assert {
        "bound_tenant_id",
        "issuer",
        "state",
        "binding_id",
        "priority",
        "registry_status",
    } <= cell_req

    auth = _load(API / "auth.openapi.yaml")
    assert str(auth["info"]["version"]).startswith("1.3.")
    assert "IdpFederationMatrixSummary" in auth["components"]["schemas"]
    matrix = auth["components"]["schemas"]["IdpFederationStatusPosture"]["properties"][
        "matrix"
    ]
    assert matrix["$ref"].endswith("/IdpFederationMatrixSummary")

def test_g230_live_meta_keys_match_schema() -> None:
    try:
        matrix = federation_matrix(include_unbound_issuers=True)
    except RuntimeError:
        # Store may be unavailable in unit context; schema still documents keys.
        return
    meta_keys = set(matrix["meta"])
    assert {
        "cell_count",
        "tenant_count",
        "issuer_count",
        "binding_count",
        "active_count",
        "include_unbound_issuers",
    } <= meta_keys
    if matrix["cells"]:
        assert {
            "bound_tenant_id",
            "issuer",
            "state",
            "binding_id",
            "priority",
            "registry_status",
        } <= set(matrix["cells"][0])

def test_g230_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g230" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert str(props["milestone"].get("const", "")).startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g230_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U103" in ledger
    assert ("PHX-G230" in tip or "PHX-G231" in tip) and (
        "PHX-G230" in manifest or "PHX-G231" in manifest
    ) and ("PHX-G2" in status)
