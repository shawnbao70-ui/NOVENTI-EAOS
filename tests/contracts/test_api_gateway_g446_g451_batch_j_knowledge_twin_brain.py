"""PHX-G446–G451 Batch J Knowledge + Twin/Brain advisory (execute/authorize closed)."""

from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.foundation_status import BrainStatusEnvelope, TwinStatusEnvelope
from api.gateway.schemas.knowledge import KnowledgeStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE = ROOT / "docs" / "api" / "knowledge.openapi.yaml"
ROADMAP = ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"


def test_g446_g447_knowledge_governance_deepen() -> None:
    response = TestClient(create_app()).get("/v1/knowledge/status")
    assert response.status_code == 200, response.text
    KnowledgeStatusEnvelope.model_validate(response.json())
    data = response.json()["data"]
    assert data["graph_write_engine"] is False
    assert data["sample_pack_is_not_runtime_graph"] is True
    assert data["sample_pack_not_complete_evidence"] is True
    assert data["execution_authority"] == "none"
    assert data["constitution_rewrite"] == "never"


def test_g446_g447_knowledge_openapi_parity() -> None:
    spec = yaml.safe_load(KNOWLEDGE.read_text(encoding="utf-8"))
    props = spec["components"]["schemas"]["KnowledgeStatusData"]["properties"]
    assert props["sample_pack_not_complete_evidence"]["const"] is True
    assert props["execution_authority"]["const"] == "none"


def test_g448_g449_twin_brain_advisory_closed() -> None:
    client = TestClient(create_app())
    twin = client.get("/v1/twin/status")
    assert twin.status_code == 200, twin.text
    TwinStatusEnvelope.model_validate(twin.json())
    td = twin.json()["data"]
    assert td["authorize_execution"] == "permission_gated"
    assert td["commercial_auto_write"] is False
    assert td["continuous_sync_daemon"] is False
    brain = client.get("/v1/brain/status")
    assert brain.status_code == 200, brain.text
    BrainStatusEnvelope.model_validate(brain.json())
    bd = brain.json()["data"]
    assert bd["execute_execution"] == "permission_gated"
    assert bd["confidence_drives_execution"] is False
    assert bd["commercial_auto_write"] is False


def test_g451_advisory_hygiene_roadmap() -> None:
    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "TRACK-G446 COMPLETE" in roadmap
    assert "TRACK-G451 COMPLETE" in roadmap
