"""PHX-G236 OpenAPI opaque auth array-item named honesty contracts."""

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

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g236_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0255-openapi-opaque-auth-array-items-named-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G236_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G236_ARCHITECTURE_GATE.md").is_file()

def test_g236_opaque_items_named_and_orphan_retired() -> None:
    auth = _load(API / "auth.openapi.yaml")
    assert str(auth["info"]["version"]).startswith("1.3.")
    schemas = auth["components"]["schemas"]
    assert "OidcLoginProviderPublicItem" in schemas
    assert "IdpRegistryIssuerStatusItem" in schemas
    assert "AuthStatusEnvelope" not in schemas
    assert "AuthStatusData" not in schemas

    login_items = schemas["OidcStatusData"]["properties"]["login_providers"]["items"]
    assert login_items["$ref"].endswith("/OidcLoginProviderPublicItem")
    providers_items = schemas["OidcProvidersPayload"]["properties"]["providers"]["items"]
    assert providers_items["$ref"].endswith("/OidcLoginProviderPublicItem")
    issuer_items = schemas["IdpRegistryStatusPosture"]["properties"]["issuers"]["items"]
    assert issuer_items["$ref"].endswith("/IdpRegistryIssuerStatusItem")

    provider_req = set(schemas["OidcLoginProviderPublicItem"]["required"])
    assert {"key", "issuer", "has_end_session"} <= provider_req
    issuer_req = set(schemas["IdpRegistryIssuerStatusItem"]["required"])
    assert {"id", "issuer", "jwks_url", "has_jwks_json", "status", "version"} <= issuer_req

def test_g236_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g236" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert str(props["milestone"].get("const", "")).startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g236_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U109" in ledger
    assert ("PHX-G236" in tip or "PHX-G237" in tip) and (
        "PHX-G236" in manifest or "PHX-G237" in manifest
    ) and ("PHX-G2" in status)
