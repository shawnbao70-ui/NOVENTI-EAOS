"""PHX-G49 production topology / runbook documentation contracts."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOPOLOGY = ROOT / "docs" / "release" / "PRODUCTION_TOPOLOGY.md"
RUNBOOK = ROOT / "docs" / "release" / "OPERATIONS_RUNBOOK.md"
CHECKLIST = ROOT / "docs" / "release" / "RELEASE_CHECKLIST.md"
ADR = ROOT / "docs" / "decisions" / "ADR-0068-production-deploy-topology.md"
GATE = ROOT / "docs" / "project" / "PHX-G49_ARCHITECTURE_GATE.md"


def test_g49_topology_docs_exist() -> None:
    assert TOPOLOGY.is_file()
    assert RUNBOOK.is_file()
    assert CHECKLIST.is_file()
    assert ADR.is_file()
    assert GATE.is_file()


def test_g49_topology_has_required_sections() -> None:
    text = TOPOLOGY.read_text(encoding="utf-8")
    required = [
        "Reference topology (single host)",
        "Production security baseline",
        "Bootstrap sequence",
        "Secret rotation",
        "Explicit non-goals",
        "EAOS_DATABASE_URL",
        "EAOS_REQUIRE_JWT",
        "EAOS_ALLOW_DEV_CONTEXT_HEADERS",
        "0049_finance_commission_ledger_g314",
        "uvicorn api.gateway.app:app",
        "/v1/health",
    ]
    for needle in required:
        assert needle in text, needle


def test_g49_runbook_links_topology_and_prod_start() -> None:
    text = RUNBOOK.read_text(encoding="utf-8")
    assert "PRODUCTION_TOPOLOGY.md" in text
    assert "Production start (single-host)" in text
    assert "EAOS_REQUIRE_JWT=1" in text
    assert "EAOS_ALLOW_DEV_CONTEXT_HEADERS=0" in text
    assert "Kubernetes" in text or "Helm" in text
    assert "COMPOSE.md" in text or "deploy/docker" in text


def test_g49_checklist_mentions_topology() -> None:
    text = CHECKLIST.read_text(encoding="utf-8")
    assert "PRODUCTION_TOPOLOGY.md" in text


def test_g49_adr_defers_containers_and_payment() -> None:
    text = ADR.read_text(encoding="utf-8").casefold()
    assert "docker" in text or "kubernetes" in text
    assert "支付" in ADR.read_text(encoding="utf-8") or "payment" in text
    assert "0.2.0" in ADR.read_text(encoding="utf-8")
