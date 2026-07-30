"""Schema contracts for Shared Audit and Identity mappings."""

from __future__ import annotations

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB

from kernel.identity.models import Credential, Subject
from kernel.infrastructure.persistence import metadata


def test_domain_models_remain_orm_independent() -> None:
    assert not hasattr(Subject, "__table__")
    assert not hasattr(Credential, "__table__")


def test_tenant_scoped_identity_tables_require_tenant_id() -> None:
    for table_name in ("credentials", "sessions", "ai_assignments"):
        table = metadata.tables[f"kernel.{table_name}"]
        assert not table.c.tenant_id.nullable

    assert metadata.tables["kernel.subjects"].c.tenant_id.nullable


def test_external_reference_is_globally_unique() -> None:
    table = metadata.tables["kernel.subject_external_refs"]
    unique_columns = {
        tuple(column.name for column in constraint.columns)
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert ("system", "external_id") in unique_columns


def test_identity_enums_are_enforced_by_check_constraints() -> None:
    for table_name in ("subjects", "credentials", "ai_assignments"):
        table = metadata.tables[f"kernel.{table_name}"]
        assert any(
            isinstance(constraint, CheckConstraint)
            for constraint in table.constraints
        )


def test_active_ai_assignment_is_globally_unique() -> None:
    table = metadata.tables["kernel.ai_assignments"]
    index = next(
        candidate
        for candidate in table.indexes
        if candidate.name == "uq_ai_assignments_ai_active"
    )
    assert index.unique
    assert tuple(column.name for column in index.columns) == ("ai_subject_id",)
    assert index.dialect_options["postgresql"]["where"] is not None


def test_audit_details_use_postgresql_jsonb() -> None:
    table = metadata.tables["kernel.audit_events"]
    database_type = table.c.details.type.dialect_impl(postgresql.dialect())
    assert isinstance(database_type, JSONB)
    assert not table.c.details.nullable


def test_credential_secret_handle_has_no_database_default() -> None:
    column = metadata.tables["kernel.credentials"].c.secret_handle
    assert column.default is None
    assert column.server_default is None
