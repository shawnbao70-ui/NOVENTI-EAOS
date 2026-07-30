"""PHX-G58 KEDA Foundation documentation / artifact contracts."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CHART_DIR = ROOT / "deploy" / "helm" / "eaos"
VALUES = CHART_DIR / "values.yaml"
KEDA_TPL = CHART_DIR / "templates" / "keda-scaledobject.yaml"
DEPLOY_TPL = CHART_DIR / "templates" / "gateway-deployment.yaml"
KEDA_DOC = ROOT / "docs" / "release" / "KEDA.md"
HPA_DOC = ROOT / "docs" / "release" / "HPA.md"
VPA_DOC = ROOT / "docs" / "release" / "VPA.md"
HELM_DOC = ROOT / "docs" / "release" / "HELM.md"
RUNBOOK = ROOT / "docs" / "release" / "OPERATIONS_RUNBOOK.md"
NOTES = CHART_DIR / "templates" / "NOTES.txt"
ADR = ROOT / "docs" / "decisions" / "ADR-0077-keda-foundation.md"
GATE = ROOT / "docs" / "project" / "PHX-G58_ARCHITECTURE_GATE.md"


def test_g58_keda_artifacts_exist() -> None:
    assert KEDA_TPL.is_file()
    assert KEDA_DOC.is_file()
    assert ADR.is_file()
    assert GATE.is_file()


def test_g58_keda_disabled_by_default() -> None:
    values = yaml.safe_load(VALUES.read_text(encoding="utf-8"))
    keda = values["keda"]
    assert keda["enabled"] is False
    assert keda["minReplicaCount"] == 1
    assert keda["maxReplicaCount"] == 3
    assert keda["cpu"]["targetUtilizationPercentage"] == 70


def test_g58_keda_template_mutex_and_api() -> None:
    text = KEDA_TPL.read_text(encoding="utf-8")
    assert "keda.enabled" in text
    assert "keda.sh/v1alpha1" in text
    assert "kind: ScaledObject" in text
    assert "cannot both be enabled" in text
    assert "autoscaling" in text
    assert "vpa" in text
    assert "type: cpu" in text
    deploy = DEPLOY_TPL.read_text(encoding="utf-8")
    assert "keda.enabled" in deploy


def test_g58_keda_docs_cross_link() -> None:
    doc = KEDA_DOC.read_text(encoding="utf-8")
    assert "keda.enabled" in doc
    assert "互斥" in doc or "mutual" in doc.casefold()
    assert "HPA.md" in doc
    assert "VPA.md" in doc
    assert "0.2.0" in doc
    helm = HELM_DOC.read_text(encoding="utf-8")
    assert "KEDA.md" in helm or "keda" in helm.casefold()
    runbook = RUNBOOK.read_text(encoding="utf-8")
    assert "KEDA.md" in runbook or "keda.enabled" in runbook
    notes = NOTES.read_text(encoding="utf-8")
    assert "keda.enabled" in notes
    hpa = HPA_DOC.read_text(encoding="utf-8")
    assert "KEDA" in hpa or "keda" in hpa
    vpa = VPA_DOC.read_text(encoding="utf-8")
    assert "KEDA" in vpa or "keda" in vpa


def test_g58_adr_defers_mesh_and_payment() -> None:
    text = ADR.read_text(encoding="utf-8")
    folded = text.casefold()
    assert "service mesh" in folded or "mesh" in folded
    assert "支付" in text or "payment" in folded
    assert "0.2.0" in text
