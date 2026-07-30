"""PHX-G72 Service Mesh Traffic CRD Foundation documentation / artifact contracts."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CHART_DIR = ROOT / "deploy" / "helm" / "eaos"
VALUES = CHART_DIR / "values.yaml"
VS_TPL = CHART_DIR / "templates" / "mesh-virtualservice.yaml"
DR_TPL = CHART_DIR / "templates" / "mesh-destinationrule.yaml"
DEPLOY_TPL = CHART_DIR / "templates" / "gateway-deployment.yaml"
MESH_DOC = ROOT / "docs" / "release" / "MESH.md"
HELM_DOC = ROOT / "docs" / "release" / "HELM.md"
NOTES = CHART_DIR / "templates" / "NOTES.txt"
ADR = ROOT / "docs" / "decisions" / "ADR-0091-mesh-traffic-crd-foundation.md"
GATE = ROOT / "docs" / "project" / "PHX-G72_ARCHITECTURE_GATE.md"


def test_g72_mesh_traffic_artifacts_exist() -> None:
    assert VS_TPL.is_file()
    assert DR_TPL.is_file()
    assert ADR.is_file()
    assert GATE.is_file()


def test_g72_mesh_traffic_disabled_by_default() -> None:
    values = yaml.safe_load(VALUES.read_text(encoding="utf-8"))
    traffic = values["mesh"]["traffic"]
    assert traffic["enabled"] is False
    assert traffic["vendor"] == "istio"
    assert traffic["tlsMode"] == "ISTIO_MUTUAL"
    assert traffic["host"] is None


def test_g72_vs_dr_template_guards() -> None:
    vs = VS_TPL.read_text(encoding="utf-8")
    dr = DR_TPL.read_text(encoding="utf-8")
    assert "VirtualService" in vs
    assert "DestinationRule" in dr
    assert "networking.istio.io/v1beta1" in vs
    assert "networking.istio.io/v1beta1" in dr
    assert "mesh.traffic.enabled" in vs
    assert "mesh.traffic.enabled" in dr
    assert "PHX-G72" in vs
    assert "ISTIO_MUTUAL" in dr
    deploy = DEPLOY_TPL.read_text(encoding="utf-8")
    assert "VirtualService" not in deploy
    assert "DestinationRule" not in deploy


def test_g72_docs_cross_link() -> None:
    doc = MESH_DOC.read_text(encoding="utf-8")
    assert "mesh.traffic.enabled" in doc
    assert "VirtualService" in doc
    assert "DestinationRule" in doc
    assert "PHX-G72" in doc
    assert "0.2.0" in doc
    helm = HELM_DOC.read_text(encoding="utf-8")
    assert "mesh.traffic.enabled" in helm
    notes = NOTES.read_text(encoding="utf-8")
    assert "mesh.traffic.enabled" in notes
    adr = ADR.read_text(encoding="utf-8")
    assert "支付" in adr or "payment" in adr.casefold()
    assert "0.2.0" in adr
    assert "istio" in adr.casefold()
