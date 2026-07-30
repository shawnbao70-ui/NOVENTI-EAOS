"""PHX-G440–G445 Batch I OpenAPI semantic remainder honesty."""

from __future__ import annotations

from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from api.gateway import create_app
from api.gateway.openapi_inventory_product import openapi_inventory_product_posture

ROOT = Path(__file__).resolve().parents[2]
OPS = ROOT / "docs" / "api" / "ops.openapi.yaml"
ROADMAP = ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"


def test_g443_semantic_remainder_honest_live() -> None:
    posture = openapi_inventory_product_posture()
    assert posture["full_openapi_http_complete"] is False
    assert posture["semantic_remainder_honest"] is True
    assert posture["route_mount_parity_complete"] is True
    body = TestClient(create_app()).get("/v1/adapters").json()
    product = body["meta"]["openapi_inventory_product"]
    assert product["full_openapi_http_complete"] is False
    assert product["semantic_remainder_honest"] is True


def test_g443_openapi_documents_honesty_field() -> None:
    spec = yaml.safe_load(OPS.read_text(encoding="utf-8"))
    props = spec["components"]["schemas"]["OpenApiInventoryProductPosture"]["properties"]
    assert props["full_openapi_http_complete"]["const"] is False
    assert props["semantic_remainder_honest"]["const"] is True


def test_g445_openapi_hygiene_roadmap() -> None:
    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "TRACK-G440 COMPLETE" in roadmap
    assert "TRACK-G445 COMPLETE" in roadmap
    assert "TRACK-BATCH-I-SEMANTIC-HONESTY COMPLETE" in roadmap
