"""PHX-G50 Docker Compose Foundation documentation / artifact contracts."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
COMPOSE = ROOT / "deploy" / "docker" / "compose.yaml"
DOCKERFILE = ROOT / "deploy" / "docker" / "Dockerfile"
ENTRYPOINT = ROOT / "deploy" / "docker" / "entrypoint.py"
ENV_EXAMPLE = ROOT / "deploy" / "docker" / ".env.example"
COMPOSE_DOC = ROOT / "docs" / "release" / "COMPOSE.md"
TOPOLOGY = ROOT / "docs" / "release" / "PRODUCTION_TOPOLOGY.md"
RUNBOOK = ROOT / "docs" / "release" / "OPERATIONS_RUNBOOK.md"
ADR = ROOT / "docs" / "decisions" / "ADR-0069-docker-compose-foundation.md"
DOCKERIGNORE = ROOT / ".dockerignore"


def test_g50_compose_artifacts_exist() -> None:
    assert COMPOSE.is_file()
    assert DOCKERFILE.is_file()
    assert ENTRYPOINT.is_file()
    assert ENV_EXAMPLE.is_file()
    assert COMPOSE_DOC.is_file()
    assert ADR.is_file()
    assert DOCKERIGNORE.is_file()


def test_g50_compose_defines_db_and_gateway() -> None:
    document = yaml.safe_load(COMPOSE.read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    services = document["services"]
    assert "db" in services
    assert "gateway" in services
    assert services["db"]["image"].startswith("postgres:")
    gateway = services["gateway"]
    assert gateway["build"]["dockerfile"] == "deploy/docker/Dockerfile"
    env = gateway["environment"]
    assert env["EAOS_REQUIRE_JWT"] == "1"
    assert env["EAOS_ALLOW_DEV_CONTEXT_HEADERS"] == "0"
    assert "EAOS_DATABASE_URL" in env
    assert "EAOS_JWT_SECRET" in env
    assert gateway["depends_on"]["db"]["condition"] == "service_healthy"


def test_g50_dockerfile_and_entrypoint_contract() -> None:
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    assert "python:3.12" in dockerfile
    assert '".[persistence,api]"' in dockerfile or ".[persistence,api]" in dockerfile
    assert "entrypoint.py" in dockerfile
    entry = ENTRYPOINT.read_text(encoding="utf-8")
    assert "alembic" in entry
    assert "upgrade" in entry
    assert "uvicorn" in entry
    assert "EAOS_DATABASE_URL" in entry


def test_g50_env_example_has_required_keys_without_real_secrets() -> None:
    text = ENV_EXAMPLE.read_text(encoding="utf-8")
    for key in (
        "POSTGRES_PASSWORD",
        "EAOS_JWT_SECRET",
        "EAOS_JWT_ISSUER",
        "EAOS_JWT_AUDIENCE",
    ):
        assert key in text
    assert "change-me" in text.casefold()


def test_g50_docs_cross_link_topology_and_runbook() -> None:
    compose_doc = COMPOSE_DOC.read_text(encoding="utf-8")
    assert "deploy/docker/compose.yaml" in compose_doc
    assert "PRODUCTION_TOPOLOGY.md" in compose_doc
    assert "0.2.0" in compose_doc
    runbook = RUNBOOK.read_text(encoding="utf-8")
    assert "COMPOSE.md" in runbook or "deploy/docker" in runbook
    topology = TOPOLOGY.read_text(encoding="utf-8")
    assert "Compose" in topology or "compose" in topology


def test_g50_adr_defers_k8s_and_payment() -> None:
    text = ADR.read_text(encoding="utf-8")
    folded = text.casefold()
    assert "kubernetes" in folded or "k8s" in folded
    assert "支付" in text or "payment" in folded
    assert "0.2.0" in text
