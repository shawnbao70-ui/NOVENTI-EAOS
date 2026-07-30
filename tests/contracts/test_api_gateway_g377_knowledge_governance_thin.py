"""PHX-G377 Knowledge governance thin honesty HTTP contracts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.schemas.knowledge import KnowledgeStatusEnvelope

ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_OPENAPI = ROOT / "docs" / "api" / "knowledge.openapi.yaml"

# Existing shipped entity CRUD / search / provenance surfaces (not invent).
_ALLOWED_KNOWLEDGE_PATHS = {
    "/v1/knowledge/status",
    "/v1/knowledge/entities",
    "/v1/knowledge/entities/{entity_id}",
    "/v1/knowledge/entities/{entity_id}/archive",
    "/v1/knowledge/entities/{entity_id}/share",
    "/v1/knowledge/links",
    "/v1/knowledge/search",
    "/v1/knowledge/provenance/{subject_kind}/{subject_id}",
}


def _client() -> TestClient:
    return TestClient(create_app())


def _load_openapi() -> dict[str, Any]:
    loaded = yaml.safe_load(KNOWLEDGE_OPENAPI.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_g377_knowledge_status_governance_honesty_flags() -> None:
    response = _client().get("/v1/knowledge/status")
    assert response.status_code == 200, response.text
    body = response.json()
    KnowledgeStatusEnvelope.model_validate(body)
    data = body["data"]
    assert data["writable"] is False
    assert data["graph_write_engine"] is False
    assert data["constitution_rewrite"] == "never"
    assert data["sample_pack_is_not_runtime_graph"] is True
    assert data["execution_authority"] == "none"
    assert data["sample_knowledge_pack_product"]["crud"] is False


def test_g377_no_graph_write_invent_routes() -> None:
    client = _client()
    openapi = client.get("/openapi.json").json()
    paths = openapi["paths"]
    assert "/v1/knowledge/status" in paths
    assert "get" in paths["/v1/knowledge/status"]
    for path in paths:
        if not path.startswith("/v1/knowledge"):
            continue
        assert path in _ALLOWED_KNOWLEDGE_PATHS, f"unexpected knowledge invent path: {path}"
        lowered = path.casefold()
        assert "graph/write" not in lowered
        assert "graph-write" not in lowered
        assert "/constitution" not in lowered
        assert "rewrite" not in lowered


def test_g377_knowledge_openapi_documents_governance_flags() -> None:
    spec = _load_openapi()
    assert str(spec["info"]["version"]).startswith("1.0.")
    path = spec["paths"]["/knowledge/status"]["get"]
    assert path["operationId"] == "getKnowledgeStatus"
    schema = path["responses"]["200"]["content"]["application/json"]["schema"]
    assert schema["$ref"].endswith("KnowledgeStatusEnvelope")
    data = spec["components"]["schemas"]["KnowledgeStatusData"]
    props = data["properties"]
    assert props["graph_write_engine"]["const"] is False
    assert props["constitution_rewrite"]["const"] == "never"
    assert props["sample_pack_is_not_runtime_graph"]["const"] is True
    assert props["execution_authority"]["const"] == "none"
    required = set(data["required"])
    assert {
        "graph_write_engine",
        "constitution_rewrite",
        "sample_pack_is_not_runtime_graph",
        "execution_authority",
    } <= required
