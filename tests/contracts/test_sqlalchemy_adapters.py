"""Contracts for tenant-bound SQLAlchemy persistence adapters."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool

from kernel.identity.models import (
    AIAssignment,
    AssignmentMode,
    EntityStatus,
    ExternalRef,
    Session,
    Subject,
    SubjectKind,
)
from kernel.identity.repository import IdentityRepository
from kernel.infrastructure.persistence import (
    SQLAlchemyAuditLog,
    SQLAlchemyIdentityRepository,
    SQLAlchemyUnitOfWork,
    create_session_factory,
    metadata,
)
from kernel.shared.audit import AuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode, KernelError


def _engine() -> Engine:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        poolclass=StaticPool,
    )
    with engine.begin() as connection:
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS kernel")
        metadata.create_all(connection)
    return engine


def _subject(tenant_id: UUID | None, *, kind: SubjectKind = SubjectKind.HUMAN) -> Subject:
    now = datetime.now(timezone.utc)
    return Subject(
        id=uuid4(),
        tenant_id=tenant_id,
        subject_type=kind,
        display_name="Subject",
        status=EntityStatus.ACTIVE,
        is_platform_managed=tenant_id is None,
        created_at=now,
        updated_at=now,
        external_refs=[ExternalRef(system="test", external_id=str(uuid4()))],
    )


def _context(tenant_id: UUID) -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant_id,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def test_identity_adapter_satisfies_port_and_round_trips_subject() -> None:
    engine = _engine()
    factory = create_session_factory(engine)
    tenant_id = uuid4()
    subject = _subject(tenant_id)

    with SQLAlchemyUnitOfWork(factory) as unit_of_work:
        repository = SQLAlchemyIdentityRepository(
            unit_of_work.session,
            tenant_id=tenant_id,
        )
        assert isinstance(repository, IdentityRepository)
        repository.add_subject(subject)
        unit_of_work.commit()

    with SQLAlchemyUnitOfWork(factory) as unit_of_work:
        repository = SQLAlchemyIdentityRepository(
            unit_of_work.session,
            tenant_id=tenant_id,
        )
        loaded = repository.get_subject(subject.id)
        resolved = repository.find_by_external_ref(subject.external_refs[0])

    assert loaded == subject
    assert resolved == subject


def test_identity_adapter_hides_cross_tenant_subjects() -> None:
    engine = _engine()
    factory = create_session_factory(engine)
    tenant_a = uuid4()
    tenant_b = uuid4()
    subject = _subject(tenant_a)

    with SQLAlchemyUnitOfWork(factory) as unit_of_work:
        SQLAlchemyIdentityRepository(
            unit_of_work.session,
            tenant_id=tenant_a,
        ).add_subject(subject)
        unit_of_work.commit()

    with SQLAlchemyUnitOfWork(factory) as unit_of_work:
        repository = SQLAlchemyIdentityRepository(
            unit_of_work.session,
            tenant_id=tenant_b,
        )
        assert repository.get_subject(subject.id) is None
        with pytest.raises(KernelError) as error:
            repository.add_subject(_subject(tenant_a))
        assert error.value.code == ErrorCode.IDENTITY_CROSS_TENANT_FORBIDDEN


def test_global_ai_is_visible_but_not_writable_from_tenant_scope() -> None:
    engine = _engine()
    factory = create_session_factory(engine)
    ai = _subject(None, kind=SubjectKind.AI_EMPLOYEE)

    with SQLAlchemyUnitOfWork(factory) as unit_of_work:
        SQLAlchemyIdentityRepository(
            unit_of_work.session,
            tenant_id=None,
            platform_scope=True,
        ).add_subject(ai)
        unit_of_work.commit()

    with SQLAlchemyUnitOfWork(factory) as unit_of_work:
        repository = SQLAlchemyIdentityRepository(
            unit_of_work.session,
            tenant_id=uuid4(),
        )
        loaded = repository.get_subject(ai.id)
        assert loaded is not None
        loaded.status = EntityStatus.ARCHIVED
        with pytest.raises(KernelError) as error:
            repository.save_subject(loaded)
        assert error.value.code == ErrorCode.IDENTITY_CROSS_TENANT_FORBIDDEN


def test_session_and_assignment_updates_are_persisted() -> None:
    engine = _engine()
    factory = create_session_factory(engine)
    tenant_id = uuid4()
    ai = _subject(None, kind=SubjectKind.AI_EMPLOYEE)
    now = datetime.now(timezone.utc)
    session = Session(
        id=uuid4(),
        subject_id=ai.id,
        tenant_id=tenant_id,
        created_at=now,
        expires_at=now + timedelta(hours=1),
        correlation_id_at_issue=str(uuid4()),
    )
    assignment = AIAssignment(
        id=uuid4(),
        ai_subject_id=ai.id,
        tenant_id=tenant_id,
        mode=AssignmentMode.ASSIGN,
        management_policy="tenant_managed",
        created_at=now,
        effective_from=now,
    )

    with SQLAlchemyUnitOfWork(factory) as unit_of_work:
        platform_repository = SQLAlchemyIdentityRepository(
            unit_of_work.session,
            tenant_id=None,
            platform_scope=True,
        )
        platform_repository.add_subject(ai)
        platform_repository.add_session(session)
        platform_repository.add_assignment(assignment)
        unit_of_work.commit()

    with SQLAlchemyUnitOfWork(factory) as unit_of_work:
        repository = SQLAlchemyIdentityRepository(
            unit_of_work.session,
            tenant_id=tenant_id,
        )
        loaded_session = repository.get_session(session.id)
        assert loaded_session is not None
        loaded_session.revoked_at = now
        repository.save_session(loaded_session)
        loaded_assignment = repository.list_active_assignments(ai.id)[0]
        loaded_assignment.status = EntityStatus.ENDED
        loaded_assignment.effective_to = now
        repository.save_assignment(loaded_assignment)
        unit_of_work.commit()

    with SQLAlchemyUnitOfWork(factory) as unit_of_work:
        repository = SQLAlchemyIdentityRepository(
            unit_of_work.session,
            tenant_id=tenant_id,
        )
        persisted_session = repository.get_session(session.id)
        assert persisted_session is not None
        assert persisted_session.revoked_at is not None
        assert repository.list_active_assignments(ai.id) == []


def test_audit_adapter_is_tenant_isolated() -> None:
    engine = _engine()
    factory = create_session_factory(engine)
    tenant_a = uuid4()
    tenant_b = uuid4()
    context_a = _context(tenant_a)

    with SQLAlchemyUnitOfWork(factory) as unit_of_work:
        audit_log = SQLAlchemyAuditLog(
            unit_of_work.session,
            tenant_id=tenant_a,
        )
        assert isinstance(audit_log, AuditLog)
        event = audit_log.record(
            context_a,
            action="Test.Action",
            resource="test:1",
            result="ok",
        )
        unit_of_work.commit()

    with SQLAlchemyUnitOfWork(factory) as unit_of_work:
        own_events = SQLAlchemyAuditLog(
            unit_of_work.session,
            tenant_id=tenant_a,
        ).list_events()
        other_events = SQLAlchemyAuditLog(
            unit_of_work.session,
            tenant_id=tenant_b,
        ).list_events()

    assert [item.id for item in own_events] == [event.id]
    assert other_events == []


def test_audit_adapter_rejects_context_scope_mismatch() -> None:
    engine = _engine()
    factory = create_session_factory(engine)
    tenant_a = uuid4()

    with SQLAlchemyUnitOfWork(factory) as unit_of_work:
        audit_log = SQLAlchemyAuditLog(
            unit_of_work.session,
            tenant_id=tenant_a,
        )
        with pytest.raises(KernelError) as error:
            audit_log.record(
                _context(uuid4()),
                action="Test.Action",
                resource="test:1",
                result="forbidden",
            )
        assert error.value.code == ErrorCode.CTX_INVALID
