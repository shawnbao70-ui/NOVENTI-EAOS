"""PHX-G71 Service Mesh Policy CRD Foundation documentation / artifact contracts."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CHART_DIR = ROOT / "deploy" / "helm" / "eaos"
VALUES = CHART_DIR / "values.yaml"
PA_TPL = CHART_DIR / "templates" / "mesh-peerauthentication.yaml"
DEPLOY_TPL = CHART_DIR / "templates" / "gateway-deployment.yaml"
MESH_DOC = ROOT / "docs" / "release" / "MESH.md"
HELM_DOC = ROOT / "docs" / "release" / "HELM.md"
NOTES = CHART_DIR / "templates" / "NOTES.txt"
ADR = ROOT / "docs" / "decisions" / "ADR-0090-mesh-policy-crd-foundation.md"
GATE = ROOT / "docs" / "project" / "PHX-G71_ARCHITECTURE_GATE.md"


def test_g71_mesh_policy_artifacts_exist() -> None:
    assert PA_TPL.is_file()
    assert ADR.is_file()
    assert GATE.is_file()
    assert MESH_DOC.is_file()


def test_g71_mesh_policy_disabled_by_default() -> None:
    values = yaml.safe_load(VALUES.read_text(encoding="utf-8"))
    policy = values["mesh"]["policy"]
    assert policy["enabled"] is False
    assert policy["vendor"] == "istio"
    assert policy["mtlsMode"] == "STRICT"


def test_g71_peerauthentication_template_guards() -> None:
    text = PA_TPL.read_text(encoding="utf-8")
    assert "PeerAuthentication" in text
    assert "security.istio.io/v1beta1" in text
    assert "mesh.policy.enabled" in text
    assert "mesh.enabled" in text
    assert "PHX-G71" in text
    assert "STRICT" in text
    assert "vendor" in text
    # Keep inject-only deployment free of CRDs
    deploy = DEPLOY_TPL.read_text(encoding="utf-8")
    assert "PeerAuthentication" not in deploy


def test_g71_docs_cross_link() -> None:
    doc = MESH_DOC.read_text(encoding="utf-8")
    assert "mesh.policy.enabled" in doc
    assert "PeerAuthentication" in doc
    assert "0.2.0" in doc
    assert "PHX-G71" in doc
    helm = HELM_DOC.read_text(encoding="utf-8")
    assert "mesh.policy.enabled" in helm or "PeerAuthentication" in helm
    notes = NOTES.read_text(encoding="utf-8")
    assert "mesh.policy.enabled" in notes
    adr = ADR.read_text(encoding="utf-8")
    assert "支付" in adr or "payment" in adr.casefold()
    assert "0.2.0" in adr
    assert "istio" in adr.casefold()
