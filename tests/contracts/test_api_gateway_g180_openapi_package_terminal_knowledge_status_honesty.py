"""PHX-G180 OpenAPI Package/Terminal/Knowledge status-code honesty contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "docs" / "api" / "package.openapi.yaml"
TERMINAL = ROOT / "docs" / "api" / "terminal.openapi.yaml"
KNOWLEDGE = ROOT / "docs" / "api" / "knowledge.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def _assert_named(responses: dict, *codes: str) -> None:
    for code in codes:
        assert code in responses
        ref = responses[code]["content"]["application/json"]["schema"]["$ref"]
        expected = "HTTPValidationError" if code == "422" else "GatewayDetailError"
        assert expected in ref

def test_g180_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0199-openapi-package-terminal-knowledge-status-code-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G180_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G180_ARCHITECTURE_GATE.md").is_file()

def test_g180_package_named_status_codes() -> None:
    spec = _load(PACKAGE)
    assert spec["info"]["version"].startswith("1.0.")
    paths = spec["paths"]
    _assert_named(
        paths["/packages/manifests"]["post"]["responses"], "400", "401", "409", "503"
    )
    _assert_named(
        paths["/packages/installations"]["post"]["responses"],
        "400",
        "403",
        "404",
        "409",
        "503",
    )
    _assert_named(
        paths["/packages/actions/resolve"]["post"]["responses"],
        "400",
        "403",
        "404",
        "409",
        "422",
        "503",
    )

def test_g180_terminal_named_status_codes() -> None:
    spec = _load(TERMINAL)
    assert spec["info"]["version"].startswith("1.1.")
    paths = spec["paths"]
    _assert_named(
        paths["/terminal/sessions"]["post"]["responses"],
        "400",
        "401",
        "403",
        "422",
        "503",
    )
    _assert_named(
        paths["/terminal/previews/{previewId}/commits"]["post"]["responses"],
        "403",
        "404",
        "409",
        "503",
    )
    _assert_named(
        paths["/terminal/extensions"]["post"]["responses"],
        "400",
        "403",
        "409",
        "422",
        "503",
    )
    _assert_named(
        paths["/terminal/extensions/{extensionId}/actions"]["post"]["responses"],
        "400",
        "403",
        "404",
        "503",
    )

def test_g180_knowledge_named_status_codes() -> None:
    spec = _load(KNOWLEDGE)
    assert spec["info"]["version"].startswith("1.0.")
    paths = spec["paths"]
    _assert_named(
        paths["/knowledge/entities"]["post"]["responses"], "400", "403", "409", "503"
    )
    _assert_named(
        paths["/knowledge/entities/{entityId}"]["get"]["responses"], "404", "409", "503"
    )
    _assert_named(paths["/knowledge/links"]["post"]["responses"], "400", "404", "409", "503")
    search_method = "post" if "post" in paths["/knowledge/search"] else "get"
    _assert_named(paths["/knowledge/search"][search_method]["responses"], "400", "403", "503")

def test_g180_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    reasons = " ".join(posture["fail_closed_reasons"]).casefold()
    assert "g180" in reasons or "g181" in reasons or "g185" in reasons

    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    assert props["t0188_status"]["const"].startswith("mount_parity_complete")

    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g180_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U053" in ledger
    assert "PHX-G180" in tip
    assert "PHX-G180" in manifest
    assert "PHX-G180" in status or "PHX-G18" in status
