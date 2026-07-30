"""PHX-G73 Service Mesh AuthorizationPolicy Foundation documentation / artifact contracts."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CHART_DIR = ROOT / "deploy" / "helm" / "eaos"
VALUES = CHART_DIR / "values.yaml"
AUTHZ_TPL = CHART_DIR / "templates" / "mesh-authorizationpolicy.yaml"
DEPLOY_TPL = CHART_DIR / "templates" / "gateway-deployment.yaml"
MESH_DOC = ROOT / "docs" / "release" / "MESH.md"
HELM_DOC = ROOT / "docs" / "release" / "HELM.md"
NOTES = CHART_DIR / "templates" / "NOTES.txt"
ADR = ROOT / "docs" / "decisions" / "ADR-0092-mesh-authz-crd-foundation.md"
GATE = ROOT / "docs" / "project" / "PHX-G73_ARCHITECTURE_GATE.md"


def test_g73_mesh_authz_artifacts_exist() -> None:
    assert AUTHZ_TPL.is_file()
    assert ADR.is_file()
    assert GATE.is_file()


def test_g73_mesh_authz_disabled_by_default() -> None:
    values = yaml.safe_load(VALUES.read_text(encoding="utf-8"))
    authz = values["mesh"]["authz"]
    assert authz["enabled"] is False
    assert authz["vendor"] == "istio"
    assert authz["action"] == "ALLOW"
    assert authz["paths"] == ["*"]


def test_g73_authorizationpolicy_template_guards() -> None:
    text = AUTHZ_TPL.read_text(encoding="utf-8")
    assert "AuthorizationPolicy" in text
    assert "security.istio.io/v1beta1" in text
    assert "mesh.authz.enabled" in text
    assert "mesh.enabled" in text
    assert "PHX-G73" in text
    assert 'principals' in text
    assert '"*"' in text or "'*'" in text
    deploy = DEPLOY_TPL.read_text(encoding="utf-8")
    assert "AuthorizationPolicy" not in deploy


def test_g73_docs_cross_link() -> None:
    doc = MESH_DOC.read_text(encoding="utf-8")
    assert "mesh.authz.enabled" in doc
    assert "AuthorizationPolicy" in doc
    assert "PHX-G73" in doc
    assert "0.2.0" in doc
    assert "JWT" in doc or "jwt" in doc.casefold()
    helm = HELM_DOC.read_text(encoding="utf-8")
    assert "mesh.authz.enabled" in helm
    notes = NOTES.read_text(encoding="utf-8")
    assert "mesh.authz" in notes
    adr = ADR.read_text(encoding="utf-8")
    assert "支付" in adr or "payment" in adr.casefold()
    assert "0.2.0" in adr
    assert "istio" in adr.casefold()
