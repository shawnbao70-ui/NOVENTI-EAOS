"""Atomic command contracts for TransactionalIdentityService."""

from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

import pytest
from sqlalchemy import Engine, create_engine, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool

from kernel.identity.models import AssignmentMode, ExternalRef, SubjectKind
from kernel.infrastructure.persistence import (
    AIAssignmentRecord,
    AIEmployeeProfileRecord,
    AuditEventRecord,
    PlatformIdentityGovernorRecord,
    SubjectRecord,
    TransactionalIdentityService,
    create_session_factory,
    metadata,
)
from kernel.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode


def _engine() -> Engine:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        poolclass=StaticPool,
    )
    with engine.begin() as connection:
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS kernel")
        metadata.create_all(connection)
    return engine


def _tenant_context(tenant_id=None) -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.SERVICE,
        tenant_id=tenant_id or uuid4(),
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def _platform_context() -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.SERVICE,
        tenant_id=None,
        platform_scope=True,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def _count(engine: Engine, model: type) -> int:
    with engine.connect() as connection:
        return int(connection.scalar(select(func.count()).select_from(model)))


def test_successful_identity_command_commits_domain_and_audit_atomically() -> None:
    engine = _engine()
    service = TransactionalIdentityService(create_session_factory(engine))
    result = service.register_subject(
        _tenant_context(),
        subject_type=SubjectKind.HUMAN,
        display_name="Transactional User",
        external_refs=[ExternalRef(system="hr", external_id="TX-1")],
    )

    assert result.ok
    assert result.audit_id is not None
    assert _count(engine, SubjectRecord) == 1
    assert _count(engine, AuditEventRecord) == 1


def test_failed_identity_result_rolls_back_without_audit() -> None:
    engine = _engine()
    service = TransactionalIdentityService(create_session_factory(engine))
    result = service.register_subject(
        _tenant_context(),
        subject_type=SubjectKind.AI_EMPLOYEE,
        display_name="Forbidden",
    )

    assert not result.ok
    assert result.error_code == ErrorCode.IDENTITY_INVALID_TYPE
    assert _count(engine, SubjectRecord) == 0
    assert _count(engine, AuditEventRecord) == 0


def test_commit_conflict_rolls_back_domain_and_audit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = _engine()
    service = TransactionalIdentityService(create_session_factory(engine))

    def fail_commit(unit_of_work: SQLAlchemyUnitOfWork) -> None:
        raise IntegrityError("forced", {}, RuntimeError("forced"))

    monkeypatch.setattr(SQLAlchemyUnitOfWork, "commit", fail_commit)
    result = service.register_subject(
        _tenant_context(),
        subject_type=SubjectKind.HUMAN,
        display_name="Rolled Back",
    )

    assert not result.ok
    assert result.error_code == ErrorCode.IDENTITY_DUPLICATE
    assert _count(engine, SubjectRecord) == 0
    assert _count(engine, AuditEventRecord) == 0


def test_transactional_service_hides_cross_tenant_subject() -> None:
    engine = _engine()
    service = TransactionalIdentityService(create_session_factory(engine))
    tenant_a = uuid4()
    registered = service.register_subject(
        _tenant_context(tenant_a),
        subject_type=SubjectKind.HUMAN,
        display_name="Tenant A",
    )
    assert registered.data is not None

    resolved = service.resolve_subject(
        _tenant_context(uuid4()),
        subject_id=registered.data,
    )
    assert not resolved.ok
    assert resolved.error_code == ErrorCode.IDENTITY_NOT_FOUND


def test_transactional_session_validation_round_trip_and_revocation() -> None:
    engine = _engine()
    service = TransactionalIdentityService(create_session_factory(engine))
    registration_context = _tenant_context()
    registered = service.register_subject(
        registration_context,
        subject_type=SubjectKind.HUMAN,
        display_name="Session User",
    )
    assert registered.data is not None
    subject_context = replace(registration_context, subject_id=registered.data)
    credential = service.bind_credential(
        subject_context,
        subject_id=registered.data,
        credential_kind="password_hash",
        secret_handle="vault:transactional-session",
    )
    assert credential.data is not None
    created = service.create_session(
        subject_context,
        credential_id=credential.data,
    )
    assert created.data is not None
    session_id = created.data["session_id"]
    validated = service.validate_session(subject_context, session_id=session_id)
    assert validated.data is not None
    assert validated.data.subject_id == registered.data
    assert service.revoke_session(
        subject_context,
        session_id=session_id,
        reason="logout",
    ).ok
    revoked = service.validate_session(subject_context, session_id=session_id)
    assert revoked.error_code == ErrorCode.IDENTITY_SESSION_REVOKED


def test_transactional_revoked_credential_blocks_only_new_sessions() -> None:
    engine = _engine()
    service = TransactionalIdentityService(create_session_factory(engine))
    registration_context = _tenant_context()
    registered = service.register_subject(
        registration_context,
        subject_type=SubjectKind.HUMAN,
        display_name="Credential User",
    )
    assert registered.data is not None
    context = replace(registration_context, subject_id=registered.data)
    credential = service.bind_credential(
        context,
        subject_id=registered.data,
        credential_kind="key_handle",
        secret_handle="vault:transactional-credential",
    )
    assert credential.data is not None
    existing = service.create_session(context, credential_id=credential.data)
    assert existing.data is not None
    assert service.revoke_credential(
        context,
        credential_id=credential.data,
        reason="rotated",
    ).ok
    assert (
        service.create_session(
            context,
            credential_id=credential.data,
        ).error_code
        == ErrorCode.IDENTITY_CREDENTIAL_REVOKED
    )
    assert service.validate_session(
        context,
        session_id=existing.data["session_id"],
    ).ok


def test_platform_reassignment_is_atomic_and_tenant_reassignment_is_denied() -> None:
    engine = _engine()
    platform_context = _platform_context()
    service = TransactionalIdentityService(
        create_session_factory(engine),
        platform_governors={platform_context.subject_id},
    )
    ai = service.register_ai_employee(platform_context, display_name="AI")
    assert ai.data is not None
    tenant_a = uuid4()
    tenant_b = uuid4()
    assert service.assign_ai_to_tenant(
        _tenant_context(tenant_a),
        ai_subject_id=ai.data,
    ).ok

    denied = service.reassign_ai(
        _tenant_context(tenant_a),
        ai_subject_id=ai.data,
        to_tenant_id=tenant_b,
    )
    assert not denied.ok
    assert denied.error_code == ErrorCode.PERMISSION_DENIED

    moved = service.reassign_ai(
        platform_context,
        ai_subject_id=ai.data,
        to_tenant_id=tenant_b,
        mode=AssignmentMode.INHERIT,
    )
    assert moved.ok
    with engine.connect() as connection:
        lineage = connection.execute(
            select(AIAssignmentRecord.predecessor_assignment_id).where(
                AIAssignmentRecord.id == moved.data
            )
        ).scalar_one()
    assert lineage is not None


def test_invalid_persistence_scope_fails_closed() -> None:
    engine = _engine()
    service = TransactionalIdentityService(create_session_factory(engine))
    invalid_context = ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.SERVICE,
        tenant_id=uuid4(),
        platform_scope=True,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )

    result = service.register_ai_employee(invalid_context, display_name="Invalid")
    assert not result.ok
    assert result.error_code == ErrorCode.CTX_INVALID


def test_transactional_platform_scope_without_governor_rolls_back() -> None:
    engine = _engine()
    service = TransactionalIdentityService(create_session_factory(engine))
    result = service.register_ai_employee(
        _platform_context(),
        display_name="Unauthorized AI",
    )

    assert not result.ok
    assert result.error_code == ErrorCode.PERMISSION_DENIED
    assert _count(engine, SubjectRecord) == 0
    assert _count(engine, AuditEventRecord) == 0


def test_transactional_governor_authority_survives_service_recomposition() -> None:
    engine = _engine()
    bootstrap = _platform_context()
    session_factory = create_session_factory(engine)
    bootstrap_service = TransactionalIdentityService(
        session_factory,
        platform_governors={bootstrap.subject_id},
    )
    governor_id = uuid4()
    assert bootstrap_service.grant_platform_governor(
        bootstrap,
        subject_id=governor_id,
    ).ok

    recomposed = TransactionalIdentityService(session_factory)
    governor_context = ExecutionContext(
        subject_id=governor_id,
        subject_type=SubjectType.SERVICE,
        tenant_id=None,
        platform_scope=True,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )
    assert recomposed.register_ai_employee(
        governor_context,
        display_name="Persisted Authority AI",
    ).ok
    assert (
        recomposed.register_ai_employee(
            bootstrap,
            display_name="Bootstrap No Longer Authorized",
        ).error_code
        == ErrorCode.PERMISSION_DENIED
    )
    assert _count(engine, PlatformIdentityGovernorRecord) == 1


def test_transactional_ai_profile_round_trip_and_optimistic_lock() -> None:
    engine = _engine()
    context = _platform_context()
    service = TransactionalIdentityService(
        create_session_factory(engine),
        platform_governors={context.subject_id},
    )
    ai = service.register_ai_employee(
        context,
        display_name="Persistent Profile",
        capabilities_profile="capability://default/v1",
        owner_policy="policy://platform/v1",
    )
    assert ai.data

    updated = service.update_ai_profile(
        context,
        ai_subject_id=ai.data,
        expected_version=1,
        capabilities_profile="capability://default/v2",
        owner_policy="policy://platform/v1",
    )
    assert updated.data and updated.data.version == 2
    assert service.update_ai_profile(
        context,
        ai_subject_id=ai.data,
        expected_version=1,
        capabilities_profile="capability://stale",
        owner_policy="policy://platform/v1",
    ).error_code == ErrorCode.IDENTITY_AI_PROFILE_CONFLICT
    assert _count(engine, AIEmployeeProfileRecord) == 1
