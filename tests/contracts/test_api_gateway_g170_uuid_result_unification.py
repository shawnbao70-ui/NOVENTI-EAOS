"""PHX-G170 UuidResult dialect unification contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path
from uuid import uuid4

import pytest
import yaml

from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from api.gateway.serializers.common import uuid_result
from eaos_sdk import __version__ as sdk_version

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.demo import create_demo_app
from api.gateway.auth_jwt import JwtSettings
from api.gateway.context import configure_jwt_settings

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md"
TIP = ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md"
MANIFEST = ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml"
PACKAGE = ROOT / "docs" / "api" / "package.openapi.yaml"
TERMINAL = ROOT / "docs" / "api" / "terminal.openapi.yaml"
KNOWLEDGE = ROOT / "docs" / "api" / "knowledge.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

@pytest.fixture(autouse=True)
def _reset() -> None:
    configure_jwt_settings(
        JwtSettings(
            secret="",
            issuer=None,
            audience="eaos-api",
            allow_dev_headers=True,
            require_jwt=False,
        )
    )
    yield

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g170_docs_present() -> None:
    assert (
        ROOT / "docs" / "decisions" / "ADR-0189-uuid-result-dialect-unification.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G170_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G170_ARCHITECTURE_GATE.md").is_file()

def test_g170_common_uuid_result_dual_keys() -> None:
    rid = uuid4()
    audit = uuid4()
    plain = uuid_result(rid, audit_id=audit)
    assert plain["id"] == str(rid)
    assert plain["data"] == str(rid)
    assert plain["audit_id"] == str(audit)
    ok_shape = uuid_result(rid, ok=True)
    assert ok_shape["ok"] is True
    assert ok_shape["id"] == ok_shape["data"] == str(rid)

def test_g170_openapi_and_inventory() -> None:
    for path in (PACKAGE, TERMINAL, KNOWLEDGE):
        required = _load(path)["components"]["schemas"]["UuidResult"]["required"]
        assert "id" in required and "data" in required

    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert posture["full_openapi_http_complete"] is False
    fences = " ".join(posture["known_defer_fences"]).casefold()
    assert "uuid_result_dialect_unification" not in fences

    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    assert props["t0188_status"]["const"].startswith("mount_parity_complete")

    client = TestClient(app)
    meta = client.get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g170_demo_terminal_create_emits_dual_keys() -> None:
    demo = create_demo_app()
    client = TestClient(demo)
    headers = {
        "X-EAOS-Subject-Id": str(demo.state.demo_seeded_subject_id),
        "X-EAOS-Tenant-Id": str(demo.state.demo_seeded_tenant_id),
        "X-EAOS-Subject-Type": "human",
        "X-Correlation-Id": str(uuid4()),
    }
    created = client.post(
        "/v1/terminal/sessions",
        headers=headers,
        json={},
    )
    assert created.status_code in {200, 201}
    body = created.json()
    assert body["id"] == body["data"]

def test_g170_ledger_tip_manifest_baseline() -> None:
    assert sdk_version == "0.2.5"
    assert_current_baseline()
    assert "DAL-U043" in LEDGER.read_text(encoding="utf-8")
    assert "PHX-G170" in TIP.read_text(encoding="utf-8")
    assert "PHX-G170" in MANIFEST.read_text(encoding="utf-8")
