"""PHX-G59 Service Mesh Foundation documentation / artifact contracts."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CHART_DIR = ROOT / "deploy" / "helm" / "eaos"
VALUES = CHART_DIR / "values.yaml"
DEPLOY_TPL = CHART_DIR / "templates" / "gateway-deployment.yaml"
SVC_TPL = CHART_DIR / "templates" / "gateway-service.yaml"
MESH_DOC = ROOT / "docs" / "release" / "MESH.md"
HELM_DOC = ROOT / "docs" / "release" / "HELM.md"
RUNBOOK = ROOT / "docs" / "release" / "OPERATIONS_RUNBOOK.md"
NOTES = CHART_DIR / "templates" / "NOTES.txt"
ADR = ROOT / "docs" / "decisions" / "ADR-0078-service-mesh-foundation.md"
GATE = ROOT / "docs" / "project" / "PHX-G59_ARCHITECTURE_GATE.md"
KEDA_DOC = ROOT / "docs" / "release" / "KEDA.md"


def test_g59_mesh_artifacts_exist() -> None:
    assert MESH_DOC.is_file()
    assert ADR.is_file()
    assert GATE.is_file()


def test_g59_mesh_disabled_by_default() -> None:
    values = yaml.safe_load(VALUES.read_text(encoding="utf-8"))
    mesh = values["mesh"]
    assert mesh["enabled"] is False
    assert mesh["injectLabelKey"] == "sidecar.istio.io/inject"
    assert mesh["injectLabelValue"] == "true"
    assert mesh["podLabels"] == {}
    assert mesh["podAnnotations"] == {}
    assert mesh["serviceAnnotations"] == {}


def test_g59_mesh_templates_wire_labels_annotations() -> None:
    deploy = DEPLOY_TPL.read_text(encoding="utf-8")
    assert "mesh.enabled" in deploy
    assert "injectLabelKey" in deploy
    assert "podAnnotations" in deploy
    assert "PeerAuthentication" not in deploy
    assert "VirtualService" not in deploy
    svc = SVC_TPL.read_text(encoding="utf-8")
    assert "mesh.enabled" in svc
    assert "serviceAnnotations" in svc


def test_g59_mesh_docs_cross_link() -> None:
    doc = MESH_DOC.read_text(encoding="utf-8")
    assert "mesh.enabled" in doc
    assert "0.2.0" in doc
    assert "PeerAuthentication" in doc or "mTLS" in doc
    assert "不安装" in doc or "not" in doc.casefold()
    helm = HELM_DOC.read_text(encoding="utf-8")
    assert "MESH.md" in helm or "mesh.enabled" in helm
    runbook = RUNBOOK.read_text(encoding="utf-8")
    assert "MESH.md" in runbook or "mesh.enabled" in runbook
    notes = NOTES.read_text(encoding="utf-8")
    assert "mesh.enabled" in notes
    keda = KEDA_DOC.read_text(encoding="utf-8")
    assert "Service Mesh" in keda or "MESH" in keda or "mesh" in keda.casefold()


def test_g59_adr_defers_control_plane_and_payment() -> None:
    text = ADR.read_text(encoding="utf-8")
    folded = text.casefold()
    assert "control" in folded or "控制面" in text or "install" in folded
    assert "支付" in text or "payment" in folded
    assert "0.2.0" in text
    assert "ADR-0090" in text or "G71" in text or "crd" in folded
