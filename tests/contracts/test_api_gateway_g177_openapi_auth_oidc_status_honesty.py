"""PHX-G177 OpenAPI Auth OIDC status-code honesty contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
AUTH = ROOT / "docs" / "api" / "auth.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def _detail_ref(responses: dict, code: str) -> str:
    return responses[code]["content"]["application/json"]["schema"]["$ref"]

def test_g177_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0196-openapi-auth-oidc-status-code-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G177_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G177_ARCHITECTURE_GATE.md").is_file()

def test_g177_auth_oidc_named_status_codes() -> None:
    spec = _load(AUTH)
    assert str(spec["info"]["version"]).startswith("1.3.")
    paths = spec["paths"]

    login = paths["/auth/oidc/login"]["get"]["responses"]
    assert "400" in login and "503" in login
    assert "GatewayDetailError" in _detail_ref(login, "400")
    assert "GatewayDetailError" in _detail_ref(login, "503")

    callback = paths["/auth/oidc/callback"]["get"]["responses"]
    for code in ("400", "401", "403", "502", "503"):
        assert code in callback
        assert "GatewayDetailError" in _detail_ref(callback, code)

    refresh = paths["/auth/oidc/refresh"]["post"]["responses"]
    for code in ("400", "401", "502", "503"):
        assert code in refresh
        assert "GatewayDetailError" in _detail_ref(refresh, code)

    logout = paths["/auth/oidc/logout"]["post"]["responses"]
    for code in ("400", "401", "503"):
        assert code in logout
        assert "GatewayDetailError" in _detail_ref(logout, code)

def test_g177_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    reasons = " ".join(posture["fail_closed_reasons"]).casefold()
    assert "g177" in reasons or "g178" in reasons or "g179" in reasons or "g180" in reasons or "g181" in reasons or "g185" in reasons

    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    assert props["t0188_status"]["const"].startswith("mount_parity_complete")

    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g177_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U050" in ledger
    assert "PHX-G177" in tip
    assert "PHX-G177" in manifest
    assert "PHX-G177" in status or "PHX-G18" in status
