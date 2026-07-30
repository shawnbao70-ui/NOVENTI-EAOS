"""Contracts for SQLAlchemy metadata and Alembic baseline."""

from __future__ import annotations

import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

from kernel.infrastructure.persistence import Base, metadata
from kernel.infrastructure.persistence.configuration import database_url_from_environment
from kernel.infrastructure.persistence.metadata import NAMING_CONVENTION


def test_shared_metadata_has_deterministic_naming_convention() -> None:
    assert Base.metadata is metadata
    assert metadata.naming_convention == NAMING_CONVENTION
    assert set(NAMING_CONVENTION) == {"ix", "uq", "ck", "fk", "pk"}


def test_metadata_contains_only_approved_foundation_tables() -> None:
    assert set(metadata.tables) == {
        "kernel.ai_agent_runs",
        "kernel.ai_assignments",
        "kernel.ai_employee_profiles",
        "kernel.ai_memory_entries",
        "kernel.ai_tool_declarations",
        "kernel.audit_events",
        "kernel.credentials",
        "kernel.event_deliveries",
        "kernel.event_subscriptions",
        "kernel.events",
        "kernel.enterprises",
        "kernel.grants",
        "kernel.idp_issuer_bindings",
        "kernel.eaos_declared_roles",
        "kernel.memberships",
        "kernel.oidc_refresh_bindings",
        "kernel.tenant_idp_bindings",
        "kernel.org_units",
        "kernel.permission_decisions",
        "kernel.platform_identity_governors",
        "kernel.policies",
        "kernel.policy_rules",
        "kernel.sessions",
        "kernel.subject_external_refs",
        "kernel.subjects",
        "kernel.tenants",
        "kernel.event_dead_letters",
        "kernel.event_outbox",
        "kernel.knowledge_entities",
        "kernel.knowledge_links",
        "kernel.knowledge_provenance",
        "kernel.brain_insights",
        "kernel.marketplace_acquisitions",
        "kernel.marketplace_disputes",
        "kernel.marketplace_invoices",
        "kernel.marketplace_listing_pricing",
        "kernel.marketplace_listing_revenue_share",
        "kernel.marketplace_listings",
        "kernel.package_installations",
        "kernel.package_manifests",
        "kernel.terminal_extensions",
        "kernel.terminal_intents",
        "kernel.terminal_previews",
        "kernel.terminal_sessions",
        "kernel.twin_snapshots",
        "kernel.workflow_definitions",
        "kernel.workflow_history",
        "kernel.workflow_instances",
        "kernel.workflow_signal_receipts",
        "kernel.workflow_tasks",
    }


def test_alembic_has_one_linear_schema_head() -> None:
    config = Config("alembic.ini")
    scripts = ScriptDirectory.from_config(config)
    head = scripts.get_current_head()
    revision = scripts.get_revision(head)

    assert head == "0064_purchase_three_way_match_g334"
    assert revision is not None
    assert revision.down_revision == "0063_purchase_goods_receipt_inventory_g333"


def test_database_url_is_required(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EAOS_DATABASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="EAOS_DATABASE_URL is required"):
        database_url_from_environment()


def test_database_url_rejects_non_postgresql_driver(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("EAOS_DATABASE_URL", "sqlite+pysqlite:///:memory:")

    with pytest.raises(RuntimeError, match="must use postgresql\\+psycopg"):
        database_url_from_environment()


def test_database_url_accepts_psycopg_driver(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = "postgresql+psycopg://eaos:secret@localhost/eaos"
    monkeypatch.setenv("EAOS_DATABASE_URL", expected)

    assert database_url_from_environment() == expected


def test_alembic_upgrade_compiles_offline(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setenv(
        "EAOS_DATABASE_URL",
        "postgresql+psycopg://localhost/eaos",
    )
    config = Config("alembic.ini")

    command.upgrade(config, "head", sql=True)

    sql = capsys.readouterr().out
    assert "CREATE SCHEMA IF NOT EXISTS kernel" in sql
    assert "CREATE TABLE kernel.subjects" in sql
    assert "CREATE TABLE kernel.audit_events" in sql
    assert "CREATE TABLE kernel.tenants" in sql
    assert "CREATE TABLE kernel.grants" in sql
    assert "CREATE TABLE kernel.workflow_instances" in sql
    assert "CREATE TABLE kernel.knowledge_entities" in sql
    assert "CREATE TABLE kernel.event_outbox" in sql
    assert "CREATE TABLE kernel.ai_agent_runs" in sql
    assert "CREATE TABLE kernel.terminal_sessions" in sql
    assert "CREATE TABLE kernel.terminal_extensions" in sql
    assert "CREATE TABLE kernel.package_manifests" in sql
    assert "CREATE TABLE kernel.twin_snapshots" in sql
    assert "CREATE TABLE kernel.brain_insights" in sql
    assert "CREATE TABLE kernel.marketplace_listings" in sql
    assert "CREATE TABLE kernel.events" in sql
    assert "ck_subjects_subject_type_valid" in sql
    assert "ck_subjects_ck_subjects" not in sql
