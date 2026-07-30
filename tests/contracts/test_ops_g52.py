"""PHX-G52 Ingress / TLS Foundation documentation / artifact contracts."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CHART_DIR = ROOT / "deploy" / "helm" / "eaos"
VALUES = CHART_DIR / "values.yaml"
INGRESS_TPL = CHART_DIR / "templates" / "ingress.yaml"
INGRESS_DOC = ROOT / "docs" / "release" / "INGRESS.md"
HELM_DOC = ROOT / "docs" / "release" / "HELM.md"
RUNBOOK = ROOT / "docs" / "release" / "OPERATIONS_RUNBOOK.md"
ADR = ROOT / "docs" / "decisions" / "ADR-0071-ingress-tls-foundation.md"


def test_g52_ingress_artifacts_exist() -> None:
    assert INGRESS_TPL.is_file()
    assert INGRESS_DOC.is_file()
    assert ADR.is_file()
    assert VALUES.is_file()


def test_g52_ingress_disabled_by_default() -> None:
    values = yaml.safe_load(VALUES.read_text(encoding="utf-8"))
    ingress = values["ingress"]
    assert ingress["enabled"] is False
    assert ingress["className"] == "nginx"
    assert ingress["certManager"]["enabled"] is False
    assert ingress["hosts"][0]["host"]
    assert ingress["hosts"][0]["paths"][0]["path"] == "/"
    assert ingress["hosts"][0]["paths"][0]["pathType"] == "Prefix"


def test_g52_ingress_template_contract() -> None:
    text = INGRESS_TPL.read_text(encoding="utf-8")
    assert "ingress.enabled" in text
    assert "networking.k8s.io/v1" in text
    assert "kind: Ingress" in text
    assert "cert-manager.io/cluster-issuer" in text
    assert "ingressClassName" in text
    assert "eaos.gateway.fullname" in text
    assert "pathType" in text


def test_g52_ingress_docs_cross_link() -> None:
    doc = INGRESS_DOC.read_text(encoding="utf-8")
    assert "ingress.enabled" in doc
    assert "cert-manager" in doc.casefold()
    assert "0.2.0" in doc
    assert "HELM.md" in doc
    helm = HELM_DOC.read_text(encoding="utf-8")
    assert "INGRESS.md" in helm or "ingress" in helm.casefold()
    runbook = RUNBOOK.read_text(encoding="utf-8")
    assert "INGRESS.md" in runbook or "ingress" in runbook.casefold()


def test_g52_adr_defers_controller_install_and_payment() -> None:
    text = ADR.read_text(encoding="utf-8")
    folded = text.casefold()
    assert "ingress controller" in folded or "不安装" in text
    assert "支付" in text or "payment" in folded
    assert "0.2.0" in text
