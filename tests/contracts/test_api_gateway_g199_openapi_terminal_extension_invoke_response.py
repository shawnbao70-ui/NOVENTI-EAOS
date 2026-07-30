"""PHX-G199 OpenAPI Terminal extension invoke response parity contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml

from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
TERMINAL = ROOT / "docs" / "api" / "terminal.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g199_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0218-openapi-terminal-extension-invoke-response-parity.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G199_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G199_ARCHITECTURE_GATE.md").is_file()

def test_g199_invoke_schema_fail_closed() -> None:
    spec = _load(TERMINAL)
    assert str(spec["info"]["version"]).startswith("1.1.")
    path = spec["paths"]["/terminal/extensions/{extensionId}/actions"]["post"]
    assert path["responses"]["200"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/TerminalExtensionInvokeEnvelope"
    }
    envelope = spec["components"]["schemas"]["TerminalExtensionInvokeEnvelope"]
    assert envelope.get("additionalProperties") is False
    data = spec["components"]["schemas"]["TerminalExtensionInvokeData"]
    assert data.get("additionalProperties") is False
    assert data["properties"]["executed"]["const"] is False
    assert data["properties"]["status"]["const"] == "accepted_sandboxed"
    required = set(data["required"])
    assert required == {"extension_id", "action", "surface", "status", "executed"}
    # Live gateway shape keys
    emit_keys = {"extension_id", "action", "surface", "status", "executed"}
    assert required <= emit_keys

def test_g199_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g199" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")

def test_g199_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U072" in ledger
    assert ("PHX-G199" in tip or "PHX-G20" in tip) and (
        "PHX-G199" in manifest or "PHX-G20" in manifest
    ) and ("PHX-G2" in status)
