"""PHX-G51 Kubernetes Helm Foundation documentation / artifact contracts."""

from __future__ import annotations

from pathlib import Path

import yaml

from tests.contracts._baseline import EXPECTED_PACKAGE

ROOT = Path(__file__).resolve().parents[2]
CHART_DIR = ROOT / "deploy" / "helm" / "eaos"
CHART = CHART_DIR / "Chart.yaml"
VALUES = CHART_DIR / "values.yaml"
TEMPLATES = CHART_DIR / "templates"
HELM_DOC = ROOT / "docs" / "release" / "HELM.md"
COMPOSE_DOC = ROOT / "docs" / "release" / "COMPOSE.md"
RUNBOOK = ROOT / "docs" / "release" / "OPERATIONS_RUNBOOK.md"
ADR = ROOT / "docs" / "decisions" / "ADR-0070-helm-foundation.md"

REQUIRED_TEMPLATES = (
    "_helpers.tpl",
    "secret.yaml",
    "gateway-deployment.yaml",
    "gateway-service.yaml",
    "postgres-statefulset.yaml",
    "postgres-service.yaml",
    "NOTES.txt",
)


def test_g51_helm_artifacts_exist() -> None:
    assert CHART.is_file()
    assert VALUES.is_file()
    assert HELM_DOC.is_file()
    assert ADR.is_file()
    for name in REQUIRED_TEMPLATES:
        assert (TEMPLATES / name).is_file(), name


def test_g51_chart_and_values_parse() -> None:
    chart = yaml.safe_load(CHART.read_text(encoding="utf-8"))
    assert chart["name"] == "eaos"
    assert chart["version"] == EXPECTED_PACKAGE
    assert str(chart["appVersion"]) == EXPECTED_PACKAGE

    values = yaml.safe_load(VALUES.read_text(encoding="utf-8"))
    assert values["replicaCount"] == 1
    assert values["gateway"]["requireJwt"] == "1"
    assert values["gateway"]["allowDevContextHeaders"] == "0"
    assert values["postgres"]["enabled"] is True
    assert "jwtSecret" in values["secrets"]
    assert "postgresPassword" in values["secrets"]
    assert "CHANGE_ME" in values["secrets"]["jwtSecret"]


def test_g51_gateway_template_has_security_baseline() -> None:
    text = (TEMPLATES / "gateway-deployment.yaml").read_text(encoding="utf-8")
    assert "kind: Deployment" in text
    assert "EAOS_REQUIRE_JWT" in text
    assert "EAOS_ALLOW_DEV_CONTEXT_HEADERS" in text
    assert "EAOS_JWT_SECRET" in text
    assert "EAOS_DATABASE_URL" in text
    assert "/v1/health" in text


def test_g51_secret_and_postgres_templates() -> None:
    secret = (TEMPLATES / "secret.yaml").read_text(encoding="utf-8")
    assert "kind: Secret" in secret
    assert "EAOS_JWT_SECRET" in secret
    assert "EAOS_DATABASE_URL" in secret
    postgres = (TEMPLATES / "postgres-statefulset.yaml").read_text(encoding="utf-8")
    assert "kind: StatefulSet" in postgres
    assert "postgres.enabled" in postgres
    helpers = (TEMPLATES / "_helpers.tpl").read_text(encoding="utf-8")
    assert "eaos.databaseUrl" in helpers
    assert "postgres.enabled=false" in helpers


def test_g51_docs_cross_link() -> None:
    helm_doc = HELM_DOC.read_text(encoding="utf-8")
    assert "deploy/helm/eaos" in helm_doc
    assert "PRODUCTION_TOPOLOGY.md" in helm_doc
    assert "0.2.0" in helm_doc
    assert "Ingress" in helm_doc
    runbook = RUNBOOK.read_text(encoding="utf-8")
    assert "HELM.md" in runbook or "deploy/helm" in runbook
    compose = COMPOSE_DOC.read_text(encoding="utf-8")
    assert "Helm" in compose or "HELM" in compose or "Kubernetes" in compose


def test_g51_adr_defers_mesh_and_payment() -> None:
    text = ADR.read_text(encoding="utf-8")
    folded = text.casefold()
    assert "service mesh" in folded or "mesh" in folded or "ingress" in folded
    assert "支付" in text or "payment" in folded
    assert "0.2.0" in text
