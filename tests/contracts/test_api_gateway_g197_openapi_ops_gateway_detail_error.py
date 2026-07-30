"""PHX-G197 OpenAPI Ops GatewayDetailError KernelError parity contracts."""

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
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g197_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0216-openapi-ops-gateway-detail-error-parity.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G197_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G197_ARCHITECTURE_GATE.md").is_file()

def test_g197_ops_kernel_error_uses_gateway_detail() -> None:
    spec = _load(OPS)
    assert str(spec["info"]["version"]).startswith("1.0.")
    kernel = spec["components"]["responses"]["KernelError"]
    assert kernel["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/GatewayDetailError"
    }
    err = spec["components"]["schemas"]["ErrorResponse"]
    assert err.get("additionalProperties") is False
    assert "details" in err["properties"]
    assert set(err["required"]) == {'code', 'message'}
    detail_env = spec["components"]["schemas"]["GatewayDetailError"]
    assert detail_env.get("additionalProperties") is False
    assert detail_env["properties"]["detail"] == {
        "$ref": "#/components/schemas/ErrorResponse"
    }

def test_g197_context_echo_elevation_matches_schema() -> None:
    client = TestClient(app)
    subject = str(uuid4())
    tenant = str(uuid4())
    response = client.post(
        "/v1/context/echo",
        headers={
            "X-EAOS-Subject-Id": subject,
            "X-EAOS-Subject-Type": "human",
            "X-EAOS-Tenant-Id": tenant,
            "X-Correlation-ID": "g197-echo",
        },
        json={"tenant_id": tenant, "roles": ["admin"]},
    )
    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["code"] == "TERMINAL_CONTEXT_ELEVATION_DENIED"
    assert "message" in detail
    assert "fields" in detail["details"]
    assert "tenant_id" in detail["details"]["fields"]

def test_g197_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g197" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g197_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U070" in ledger
    assert ("PHX-G197" in tip or "PHX-G198" in tip) and ("PHX-G197" in manifest or "PHX-G198" in manifest) and ("PHX-G2" in status)
