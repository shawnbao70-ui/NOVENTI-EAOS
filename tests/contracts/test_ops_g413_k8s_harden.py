"""PHX-G413 container/K8s harden thin contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOYMENT = ROOT / "deploy" / "helm" / "eaos" / "templates" / "gateway-deployment.yaml"
VALUES = ROOT / "deploy" / "helm" / "eaos" / "values.yaml"
DOCKERFILE = ROOT / "deploy" / "docker" / "Dockerfile"


def test_g413_gateway_pod_security_context() -> None:
    text = DEPLOYMENT.read_text(encoding="utf-8")
    assert "runAsNonRoot: true" in text
    assert "allowPrivilegeEscalation: false" in text
    assert "drop:" in text
    assert "ALL" in text
    assert "seccompProfile" in text
    assert "RuntimeDefault" in text
    assert "automountServiceAccountToken" in text
    assert "EAOS_ENV" in text


def test_g413_values_and_dockerfile_non_root() -> None:
    values = VALUES.read_text(encoding="utf-8")
    assert "runAsUser: 10001" in values
    assert "envProfile: production" in values
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    assert "USER 10001" in dockerfile
    assert "useradd -u 10001" in dockerfile
    assert "/v1/health" in DEPLOYMENT.read_text(encoding="utf-8")
