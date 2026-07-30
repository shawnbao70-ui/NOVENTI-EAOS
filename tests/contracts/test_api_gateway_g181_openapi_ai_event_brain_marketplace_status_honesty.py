"""PHX-G181 OpenAPI AI/Event/Brain/Marketplace status-code honesty contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
AI = ROOT / "docs" / "api" / "ai.openapi.yaml"
EVENT = ROOT / "docs" / "api" / "event.openapi.yaml"
BRAIN = ROOT / "docs" / "api" / "brain.openapi.yaml"
MARKET = ROOT / "docs" / "api" / "marketplace.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def _assert_named(responses: dict, *codes: str) -> None:
    for code in codes:
        assert code in responses
        ref = responses[code]["content"]["application/json"]["schema"]["$ref"]
        assert "GatewayDetailError" in ref

def test_g181_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0200-openapi-ai-event-brain-marketplace-status-code-honesty.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G181_ACCEPTANCE.md").is_file()

def test_g181_named_status_codes() -> None:
    ai = _load(AI)
    assert ai["info"]["version"].startswith("1.0.")
    paths = ai["paths"]
    # discover create run path
    create = next(p for p, ops in paths.items() if "post" in ops and ops["post"].get("operationId") == "createAgentRun")
    _assert_named(paths[create]["post"]["responses"], "400", "403", "503")

    event = _load(EVENT)
    assert event["info"]["version"].startswith("1.0.")
    pub = next(p for p, ops in event["paths"].items() if ops.get("post", {}).get("operationId") == "publishEvent")
    _assert_named(event["paths"][pub]["post"]["responses"], "400", "503")

    brain = _load(BRAIN)
    assert brain["info"]["version"].startswith("1.0.")
    auth = brain["paths"]["/twin/snapshots/{snapshotId}/authorize"]["post"]["responses"]
    assert "403" in auth and "503" in auth
    exe = brain["paths"]["/brain/insights/{insightId}/execute"]["post"]["responses"]
    assert "403" in exe and "503" in exe

    market = _load(MARKET)
    assert market["info"]["version"].startswith("1.2.")
    acquire = next(
        p
        for p, ops in market["paths"].items()
        if ops.get("post", {}).get("operationId") == "acquireMarketplaceListing"
    )
    _assert_named(market["paths"][acquire]["post"]["responses"], "400", "403", "404", "409", "503")
    host = next(
        p
        for p, ops in market["paths"].items()
        if ops.get("post", {}).get("operationId") == "hostAcquireMarketplaceListing"
    )
    _assert_named(market["paths"][host]["post"]["responses"], "400", "403", "404", "409", "503")

def test_g181_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    reasons = " ".join(posture["fail_closed_reasons"]).casefold()
    assert "g181" in reasons or "g185" in reasons

    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g181_ledger_tip_manifest_baseline() -> None:
    assert sdk_version == "0.2.5"
    assert_current_baseline()
    ledger = (ROOT / "docs" / "project" / "DELEGATED_AUTHORITY_LEDGER.md").read_text(encoding="utf-8")
    tip = (ROOT / "docs" / "project" / "ENG_SOFT_QUEUE_TIP.md").read_text(encoding="utf-8")
    manifest = (ROOT / "docs" / "release" / "RELEASE_MANIFEST.yaml").read_text(encoding="utf-8")
    status = (ROOT / "docs" / "project" / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    assert "DAL-U054" in ledger
    assert "PHX-G181" in tip and "PHX-G181" in manifest and ("PHX-G2" in status)
