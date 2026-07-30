"""Foundation harden — Sample knowledge pack discoverability on /v1/adapters meta."""

from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.sample_knowledge_pack import sample_knowledge_pack_product_posture

ROOT = Path(__file__).resolve().parents[2]


def test_sample_knowledge_pack_posture_shape() -> None:
    posture = sample_knowledge_pack_product_posture()
    assert posture["surface"] == "foundation_sample_knowledge_pack"
    assert posture["milestone"] == "PHX-G293"
    assert posture["crud"] is False
    assert posture["brain_execute"] == "fail_closed"
    assert posture["twin_authorize"] == "fail_closed"
    assert (ROOT / posture["pack_path"]).is_dir()


def test_adapters_meta_includes_sample_knowledge_pack() -> None:
    body = TestClient(create_app()).get("/v1/adapters").json()
    product = body["meta"]["sample_knowledge_pack_product"]
    assert product["milestone"] == "PHX-G293"
    assert product["crud"] is False


def test_ops_openapi_documents_sample_knowledge_pack_meta() -> None:
    doc = yaml.safe_load(
        (ROOT / "docs" / "api" / "ops.openapi.yaml").read_text(encoding="utf-8")
    )
    meta = doc["components"]["schemas"]["AdaptersMeta"]
    assert "sample_knowledge_pack_product" in meta["required"]
    schema = doc["components"]["schemas"]["SampleKnowledgePackProductPosture"]
    assert schema.get("additionalProperties") is False
    assert schema["properties"]["crud"]["const"] is False
