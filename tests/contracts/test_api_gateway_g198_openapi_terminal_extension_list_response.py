"""PHX-G198 OpenAPI Terminal extension list response parity contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml

from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from api.gateway.serializers.terminal import serialize_extension
from eaos_sdk import __version__ as sdk_version
from smart_terminal.models import ExtensionStatus, TerminalExtension

ROOT = Path(__file__).resolve().parents[2]
TERMINAL = ROOT / "docs" / "api" / "terminal.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g198_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0217-openapi-terminal-extension-list-response-parity.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G198_ACCEPTANCE.md").is_file()
    assert (ROOT / "docs" / "project" / "PHX-G198_ARCHITECTURE_GATE.md").is_file()

def test_g198_list_schema_matches_serializer() -> None:
    spec = _load(TERMINAL)
    assert str(spec["info"]["version"]).startswith("1.1.")
    path = spec["paths"]["/terminal/extensions"]["get"]
    assert path["responses"]["200"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/TerminalExtensionListEnvelope"
    }
    envelope = spec["components"]["schemas"]["TerminalExtensionListEnvelope"]
    assert envelope.get("additionalProperties") is False
    assert envelope["properties"]["data"]["items"] == {
        "$ref": "#/components/schemas/TerminalExtensionEntry"
    }
    entry = spec["components"]["schemas"]["TerminalExtensionEntry"]
    assert entry.get("additionalProperties") is False
    required = set(entry["required"])
    assert entry["properties"]["status"]["enum"] == [
        "registered",
        "active",
        "revoked",
    ]

    from datetime import datetime, timezone
    from uuid import uuid4

    now = datetime.now(timezone.utc)
    sample = TerminalExtension(
        id=uuid4(),
        tenant_id=uuid4(),
        extension_key="demo.ext",
        version="1.0.0",
        signature_ref=None,
        status=ExtensionStatus.REGISTERED,
        declared_capabilities=frozenset({"read"}),
        declared_actions=frozenset({"ping"}),
        allowed_surfaces=frozenset({"admin"}),
        data_scope="tenant",
        created_at=now,
        updated_at=now,
    )
    emit = serialize_extension(sample)
    assert required <= set(emit)
    for key in required:
        assert key in entry["properties"]

def test_g198_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g198" in " ".join(posture["fail_closed_reasons"]).casefold()
    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")

def test_g198_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U071" in ledger
    assert ("PHX-G19" in tip or "PHX-G20" in tip) and (
        "PHX-G19" in manifest or "PHX-G20" in manifest
    ) and ("PHX-G2" in status)
