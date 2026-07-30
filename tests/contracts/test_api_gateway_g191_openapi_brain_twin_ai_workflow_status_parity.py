"""PHX-G191 OpenAPI Brain/Twin/AI/Workflow status body field parity contracts."""

from __future__ import annotations

from tests.contracts._baseline import assert_current_baseline

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture
from eaos_sdk import __version__ as sdk_version

ROOT = Path(__file__).resolve().parents[2]
BRAIN = ROOT / "docs" / "api" / "brain.openapi.yaml"
AI = ROOT / "docs" / "api" / "ai.openapi.yaml"
WORKFLOW = ROOT / "docs" / "api" / "workflow.openapi.yaml"
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"

def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def test_g191_docs_present() -> None:
    assert (
        ROOT
        / "docs"
        / "decisions"
        / "ADR-0210-openapi-brain-twin-ai-workflow-status-body-field-parity.md"
    ).is_file()
    assert (ROOT / "docs" / "project" / "PHX-G191_ACCEPTANCE.md").is_file()

def test_g191_brain_twin_schemas_match_runtime() -> None:
    spec = _load(BRAIN)
    assert str(spec["info"]["version"]).startswith("1.0.")
    assert (
        spec["paths"]["/twin/status"]["get"]["responses"]["200"]["content"][
            "application/json"
        ]["schema"]["$ref"]
        == "#/components/schemas/TwinStatusEnvelope"
    )
    assert (
        spec["paths"]["/brain/status"]["get"]["responses"]["200"]["content"][
            "application/json"
        ]["schema"]["$ref"]
        == "#/components/schemas/BrainStatusEnvelope"
    )
    twin_schema = spec["components"]["schemas"]["TwinStatusData"]
    brain_schema = spec["components"]["schemas"]["BrainStatusData"]
    assert twin_schema.get("additionalProperties") is False
    assert brain_schema.get("additionalProperties") is False
    assert twin_schema["properties"]["authorize_execution"]["const"] == "permission_gated"
    assert brain_schema["properties"]["execute_execution"]["const"] == "permission_gated"
    assert brain_schema["properties"]["advisory_required"]["const"] is True

    client = TestClient(app)
    twin = client.get("/v1/twin/status").json()["data"]
    brain = client.get("/v1/brain/status").json()["data"]
    assert set(twin_schema["required"]) <= set(twin)
    assert set(brain_schema["required"]) <= set(brain)
    assert twin["authorize_execution"] == "permission_gated"
    assert brain["execute_execution"] == "permission_gated"

def test_g191_ai_workflow_schemas_match_runtime() -> None:
    ai = _load(AI)
    wf = _load(WORKFLOW)
    assert str(ai["info"]["version"]).startswith("1.0.")
    assert str(wf["info"]["version"]).startswith("1.0.")
    ai_schema = ai["components"]["schemas"]["FoundationStatusData"]
    wf_schema = wf["components"]["schemas"]["FoundationStatusData"]
    assert ai_schema.get("additionalProperties") is False
    assert wf_schema.get("additionalProperties") is False
    assert ai_schema["properties"]["ai_subject_required"]["const"] is True
    assert ai_schema["properties"]["commit_requires_approval"]["const"] is True
    assert wf_schema["properties"]["approval_source_of_truth"]["const"] == "workflow_kernel"

    client = TestClient(app)
    ai_data = client.get("/v1/ai/status").json()["data"]
    wf_data = client.get("/v1/workflow/status").json()["data"]
    assert set(ai_schema["required"]) <= set(ai_data)
    assert set(wf_schema["required"]) <= set(wf_data)

def test_g191_inventory_and_ops() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["milestone"].startswith("PHX-G")
    assert posture["full_openapi_http_complete"] is False
    assert posture["t0188_status"].startswith("mount_parity_complete")
    assert "g191" in " ".join(posture["fail_closed_reasons"]).casefold()

    ops = _load(OPS)
    assert ops["info"]["version"].startswith("1.0.")
    props = ops["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["milestone"]["const"].startswith("PHX-G")
    meta = TestClient(app).get("/v1/adapters").json()["meta"]["openapi_inventory_product"]
    assert meta["milestone"].startswith("PHX-G")

def test_g191_ledger_tip_manifest_baseline() -> None:
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
    assert "DAL-U064" in ledger
    assert ("PHX-G191" in tip or "PHX-G192" in tip) and ("PHX-G191" in manifest or "PHX-G192" in manifest) and ("PHX-G2" in status)
