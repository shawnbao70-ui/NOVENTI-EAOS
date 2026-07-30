"""PHX-G452–G457 Batch K Ops / Tenant / Observability contracts."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from api.gateway import create_app

ROOT = Path(__file__).resolve().parents[2]
ROADMAP = ROOT / "docs" / "project" / "POST_CRM_VERTICAL_ROADMAP.md"
CHART = ROOT / "deploy" / "helm" / "eaos" / "Chart.yaml"
VALUES = ROOT / "deploy" / "helm" / "eaos" / "values.yaml"


def test_g452_health_release_adapters_live() -> None:
    client = TestClient(create_app())
    health = client.get("/v1/health")
    assert health.status_code == 200, health.text
    assert health.json().get("data") is not None
    release = client.get("/v1/release")
    assert release.status_code == 200, release.text
    adapters = client.get("/v1/adapters")
    assert adapters.status_code == 200, adapters.text
    assert adapters.json()["meta"]["openapi_inventory_product"]["full_openapi_http_complete"] is False


def test_g456_helm_security_defaults_present() -> None:
    chart = CHART.read_text(encoding="utf-8")
    values = VALUES.read_text(encoding="utf-8")
    assert "0.2.5" in chart
    assert "0.2.5" in values
    deploy_dir = ROOT / "deploy" / "helm" / "eaos" / "templates"
    blob = "\n".join(p.read_text(encoding="utf-8") for p in deploy_dir.glob("*.yaml"))
    assert "runAsNonRoot" in blob or "seccompProfile" in blob or "drop" in blob.casefold()


def test_g457_ops_hygiene_roadmap() -> None:
    roadmap = ROADMAP.read_text(encoding="utf-8")
    assert "TRACK-G452 COMPLETE" in roadmap
    assert "TRACK-G457 COMPLETE" in roadmap
