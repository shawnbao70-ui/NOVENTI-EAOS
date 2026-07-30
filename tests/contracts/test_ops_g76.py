"""PHX-G76 Deploy Region Identity documentation / artifact contracts."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CHART_DIR = ROOT / "deploy" / "helm" / "eaos"
VALUES = CHART_DIR / "values.yaml"
DEPLOY_TPL = CHART_DIR / "templates" / "gateway-deployment.yaml"
NOTES = CHART_DIR / "templates" / "NOTES.txt"
REGION_DOC = ROOT / "docs" / "release" / "REGION.md"
HELM_DOC = ROOT / "docs" / "release" / "HELM.md"
TOPOLOGY = ROOT / "docs" / "release" / "PRODUCTION_TOPOLOGY.md"
COMPOSE = ROOT / "deploy" / "docker" / "compose.yaml"
ENV_EXAMPLE = ROOT / "deploy" / "docker" / ".env.example"
ADR = ROOT / "docs" / "decisions" / "ADR-0095-deploy-region-identity.md"
GATE = ROOT / "docs" / "project" / "PHX-G76_ARCHITECTURE_GATE.md"


def test_g76_region_artifacts_exist() -> None:
    assert REGION_DOC.is_file()
    assert ADR.is_file()
    assert GATE.is_file()


def test_g76_region_empty_by_default() -> None:
    values = yaml.safe_load(VALUES.read_text(encoding="utf-8"))
    region = values["region"]
    assert region["id"] == ""
    assert region["labelPods"] is True


def test_g76_gateway_template_wires_env_and_label() -> None:
    text = DEPLOY_TPL.read_text(encoding="utf-8")
    assert "EAOS_DEPLOY_REGION" in text
    assert "region.id" in text
    assert "eaos.noventi.io/deploy-region" in text
    assert "multi_region_production_saas" not in text.casefold()


def test_g76_compose_and_docs() -> None:
    compose = COMPOSE.read_text(encoding="utf-8")
    assert "EAOS_DEPLOY_REGION" in compose
    env = ENV_EXAMPLE.read_text(encoding="utf-8")
    assert "EAOS_DEPLOY_REGION" in env
    doc = REGION_DOC.read_text(encoding="utf-8")
    assert "EAOS_DEPLOY_REGION" in doc
    assert "deploy_region" in doc
    assert "0.2.0" in ADR.read_text(encoding="utf-8") or "0.2.0" in doc
    assert "支付" in ADR.read_text(encoding="utf-8") or "payment" in ADR.read_text(
        encoding="utf-8"
    ).casefold()
    helm = HELM_DOC.read_text(encoding="utf-8")
    assert "region.id" in helm or "EAOS_DEPLOY_REGION" in helm
    topology = TOPOLOGY.read_text(encoding="utf-8")
    assert "EAOS_DEPLOY_REGION" in topology
    notes = NOTES.read_text(encoding="utf-8")
    assert "region.id" in notes or "EAOS_DEPLOY_REGION" in notes
    assert "failover" in doc.casefold() or "SaaS" in doc
