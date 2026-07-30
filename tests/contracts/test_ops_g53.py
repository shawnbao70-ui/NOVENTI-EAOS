"""PHX-G53 HPA Foundation documentation / artifact contracts."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CHART_DIR = ROOT / "deploy" / "helm" / "eaos"
VALUES = CHART_DIR / "values.yaml"
HPA_TPL = CHART_DIR / "templates" / "hpa.yaml"
GATEWAY_TPL = CHART_DIR / "templates" / "gateway-deployment.yaml"
HPA_DOC = ROOT / "docs" / "release" / "HPA.md"
HELM_DOC = ROOT / "docs" / "release" / "HELM.md"
RUNBOOK = ROOT / "docs" / "release" / "OPERATIONS_RUNBOOK.md"
ADR = ROOT / "docs" / "decisions" / "ADR-0072-hpa-foundation.md"


def test_g53_hpa_artifacts_exist() -> None:
    assert HPA_TPL.is_file()
    assert HPA_DOC.is_file()
    assert ADR.is_file()


def test_g53_autoscaling_disabled_by_default() -> None:
    values = yaml.safe_load(VALUES.read_text(encoding="utf-8"))
    auto = values["autoscaling"]
    assert auto["enabled"] is False
    assert auto["minReplicas"] == 1
    assert auto["maxReplicas"] == 3
    assert auto["targetCPUUtilizationPercentage"] == 70


def test_g53_hpa_template_contract() -> None:
    text = HPA_TPL.read_text(encoding="utf-8")
    assert "autoscaling.enabled" in text
    assert "autoscaling/v2" in text
    assert "kind: HorizontalPodAutoscaler" in text
    assert "scaleTargetRef" in text
    assert "targetCPUUtilizationPercentage" in text
    gateway = GATEWAY_TPL.read_text(encoding="utf-8")
    assert "autoscaling.enabled" in gateway
    assert "replicaCount" in gateway


def test_g53_hpa_docs_cross_link() -> None:
    doc = HPA_DOC.read_text(encoding="utf-8")
    assert "autoscaling.enabled" in doc
    assert "metrics-server" in doc.casefold()
    assert "0.2.0" in doc
    assert "HELM.md" in doc
    helm = HELM_DOC.read_text(encoding="utf-8")
    assert "HPA.md" in helm or "autoscaling" in helm.casefold()
    runbook = RUNBOOK.read_text(encoding="utf-8")
    assert "HPA.md" in runbook or "autoscaling" in runbook.casefold()


def test_g53_adr_defers_mesh_and_payment() -> None:
    text = ADR.read_text(encoding="utf-8")
    folded = text.casefold()
    assert "service mesh" in folded or "mesh" in folded or "vpa" in folded
    assert "支付" in text or "payment" in folded
    assert "0.2.0" in text
