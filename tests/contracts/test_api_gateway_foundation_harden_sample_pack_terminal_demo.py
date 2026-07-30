"""Foundation harden — Terminal/demo sample-pack discoverability (G293 deepen)."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from api.gateway.demo import create_demo_app
from api.gateway.sample_knowledge_pack import SAMPLE_PACK_PATH

ROOT = Path(__file__).resolve().parents[2]
UI = ROOT / "smart_terminal" / "ui"


def test_terminal_ui_wires_sample_pack_controls() -> None:
    html = (UI / "index.html").read_text(encoding="utf-8")
    js = (UI / "app.js").read_text(encoding="utf-8")
    assert "sampleKnowledgePackProductRow" in html
    assert "btnAdminSampleKnowledgePackStatus" in html
    assert "loadSampleKnowledgePackProductPosture" in js
    assert "sample_knowledge_pack_product" in js


def test_demo_bootstrap_includes_sample_pack_pointer() -> None:
    client = TestClient(create_demo_app())
    response = client.get("/v1/demo/bootstrap")
    assert response.status_code == 200, response.text
    data = response.json()["data"]
    assert data["available"] is True
    assert data["sample_knowledge_pack_path"] == SAMPLE_PACK_PATH
    assert data["sample_knowledge_pack_milestone"] == "PHX-G293"
    assert data["sample_knowledge_pack_url"].endswith("INDEX.md")


def test_demo_serves_sample_pack_index_readonly() -> None:
    client = TestClient(create_demo_app())
    response = client.get("/v1/demo/sample-pack/INDEX.md")
    assert response.status_code == 200, response.text
    text = response.text
    assert "PHX-G290" in text or "G290" in text
    assert "Assembles" in text or "sample-pack" in text.lower()
