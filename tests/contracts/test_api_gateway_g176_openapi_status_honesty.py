"""PHX-G176 OpenAPI platform IdP/roles status-code honesty contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
PLATFORM = ROOT / "docs" / "api" / "platform.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g176_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0195-openapi-platform-status-code-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G176_ACCEPTANCE.md").is_file()

def test_g176_platform_named_status_codes() -> None:
    spec = _load(PLATFORM)
    assert str(spec["info"]["version"]).startswith("1.0.")
    paths = spec["paths"]

    role_get = paths["/platform/roles"]["get"]["responses"]
    assert "401" in role_get and "503" in role_get
    role_post = paths["/platform/roles"]["post"]["responses"]
    assert "400" in role_post and "401" in role_post and "503" in role_post
    role_disable = paths["/platform/roles/{roleId}/disable"]["post"]["responses"]
    assert "404" in role_disable and "503" in role_disable

    issuer_post = paths["/platform/idp/issuers"]["post"]["responses"]
    assert "400" in issuer_post and "409" in issuer_post and "503" in issuer_post
    issuer_disable = paths["/platform/idp/issuers/{issuerId}/disable"]["post"][
        "responses"
    ]
    assert "404" in issuer_disable and "503" in issuer_disable

    bind_post = paths["/platform/idp/federation/tenants/{tenantId}/bindings"]["post"][
        "responses"
    ]
    assert "409" in bind_post and "400" in bind_post
    unbind = paths["/platform/idp/federation/bindings/{bindingId}/unbind"]["post"][
        "responses"
    ]
    assert "404" in unbind
    priority = paths["/platform/idp/federation/bindings/{bindingId}/priority"]["post"][
        "responses"
    ]
    assert "404" in priority and "400" in priority

    for code in ("400", "404", "409", "503"):
        if code in issuer_post:
            ref = issuer_post[code]["content"]["application/json"]["schema"]["$ref"]
            assert "GatewayDetailError" in ref

def test_g176_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    reasons = " ".join(posture["fail_closed_reasons"]).casefold()
    assert "g176" in reasons or "g177" in reasons or "g178" in reasons or "g179" in reasons or "g180" in reasons or "g181" in reasons or "g185" in reasons

    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    assert props["t0188_status"]["const"].startswith("mount_parity_complete")

    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g176_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U049" in ledger
    assert "PHX-G176" in tip
    assert "PHX-G176" in manifest
    assert "PHX-G176" in status or "PHX-G18" in status
