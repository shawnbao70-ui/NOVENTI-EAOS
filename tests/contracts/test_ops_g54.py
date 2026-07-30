"""PHX-G54 VPA Foundation documentation / artifact contracts."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CHART_DIR = ROOT / "deploy" / "helm" / "eaos"
VALUES = CHART_DIR / "values.yaml"
VPA_TPL = CHART_DIR / "templates" / "vpa.yaml"
VPA_DOC = ROOT / "docs" / "release" / "VPA.md"
HPA_DOC = ROOT / "docs" / "release" / "HPA.md"
HELM_DOC = ROOT / "docs" / "release" / "HELM.md"
RUNBOOK = ROOT / "docs" / "release" / "OPERATIONS_RUNBOOK.md"
ADR = ROOT / "docs" / "decisions" / "ADR-0073-vpa-foundation.md"


def test_g54_vpa_artifacts_exist() -> None:
    assert VPA_TPL.is_file()
    assert VPA_DOC.is_file()
    assert ADR.is_file()


def test_g54_vpa_disabled_by_default() -> None:
    values = yaml.safe_load(VALUES.read_text(encoding="utf-8"))
    vpa = values["vpa"]
    assert vpa["enabled"] is False
    assert vpa["updateMode"] == "Off"
    assert "cpu" in vpa["controlledResources"]
    assert "memory" in vpa["controlledResources"]


def test_g54_vpa_template_mutex_and_api() -> None:
    text = VPA_TPL.read_text(encoding="utf-8")
    assert "vpa.enabled" in text
    assert "autoscaling.k8s.io/v1" in text
    assert "kind: VerticalPodAutoscaler" in text
    assert "cannot both be enabled" in text
    assert "updateMode" in text
    assert "controlledResources" in text


def test_g54_vpa_docs_cross_link() -> None:
    doc = VPA_DOC.read_text(encoding="utf-8")
    assert "vpa.enabled" in doc
    assert "互斥" in doc or "mutual" in doc.casefold()
    assert "HPA.md" in doc
    assert "0.2.0" in doc
    hpa = HPA_DOC.read_text(encoding="utf-8")
    assert "VPA" in hpa or "vpa" in hpa
    helm = HELM_DOC.read_text(encoding="utf-8")
    assert "VPA.md" in helm or "vpa" in helm.casefold()
    runbook = RUNBOOK.read_text(encoding="utf-8")
    assert "VPA.md" in runbook or "vpa.enabled" in runbook


def test_g54_adr_defers_mesh_and_payment() -> None:
    text = ADR.read_text(encoding="utf-8")
    folded = text.casefold()
    assert "service mesh" in folded or "mesh" in folded or "keda" in folded
    assert "支付" in text or "payment" in folded
    assert "0.2.0" in text
