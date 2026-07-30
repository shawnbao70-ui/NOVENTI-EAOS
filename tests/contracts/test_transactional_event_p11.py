"""Transactional Event outbox / DLQ contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Engine, create_engine, select
from sqlalchemy.pool import StaticPool

from kernel.event_bus.handlers import EventHandlerRegistry
from kernel.identity.models import SubjectKind
from kernel.infrastructure.persistence import (
    EventDeadLetterRecord,
    EventOutboxRecord,
    EventRecord,
    TransactionalEventBus,
    TransactionalIdentityService,
    TransactionalOrganizationService,
    TransactionalPermissionService,
    create_session_factory,
    metadata,
)
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


def _context(tenant_id=None, *, subject_id=None, platform=False) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id or uuid4(),
        subject_type=SubjectType.SERVICE,
        tenant_id=None if platform else (tenant_id or uuid4()),
        platform_scope=platform,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def _foundation(engine: Engine) -> tuple[UUID, ExecutionContext]:
    governor = _context(platform=True)
    organization = TransactionalOrganizationService(
        create_session_factory(engine),
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name=str(uuid4()))
    assert tenant.data is not None
    identity = TransactionalIdentityService(create_session_factory(engine))
    initial = _context(tenant.data)
    subject = identity.register_subject(
        initial,
        subject_type=SubjectKind.SERVICE,
        display_name="Event Operator",
    )
    assert subject.data is not None
    return tenant.data, _context(tenant.data, subject_id=subject.data)


def test_transactional_enqueue_then_dispatch_persists_event() -> None:
    engine = _engine()
    tenant_id, operator = _foundation(engine)
    registry = EventHandlerRegistry()
    bus = TransactionalEventBus(
        create_session_factory(engine),
        handler_registry=registry,
    )
    permission = TransactionalPermissionService(
        create_session_factory(engine),
        grant_administrators={operator.subject_id},
    )
    assert permission.grant(
        operator,
        principal_subject_id=operator.subject_id,
        resource_type="event_stream",
        actions={"publish", "subscribe", "dispatch", "read"},
    ).ok
    received: list[str] = []
    assert bus.subscribe(
        operator,
        subscriber_id="projection.tx",
        event_name="crm.order.created",
        handler=lambda event: received.append(event.event_name),
    ).ok
    enqueued = bus.enqueue(
        operator,
        event_name="crm.order.created",
        schema_version="1",
        producer="pkg.crm",
        payload={"order_id": "TX-1"},
    )
    assert enqueued.ok and enqueued.data is not None
    with create_session_factory(engine)() as session:
        outbox = session.scalar(
            select(EventOutboxRecord).where(EventOutboxRecord.id == enqueued.data)
        )
        assert outbox is not None
        assert outbox.status == "pending"
        assert session.scalar(select(EventRecord)) is None

    dispatched = bus.dispatch_due(operator, worker_id="tx-worker")
    assert dispatched.ok and dispatched.data is not None
    # Foundation (tenant/enterprise/grant) may leave catalog facts in outbox (PHX-E19).
    assert dispatched.data.outbox_dispatched >= 1
    assert received == ["crm.order.created"]
    with create_session_factory(engine)() as session:
        outbox = session.scalar(
            select(EventOutboxRecord).where(EventOutboxRecord.id == enqueued.data)
        )
        assert outbox is not None
        assert outbox.status == "dispatched"
        assert session.scalar(select(EventRecord)) is not None


def test_transactional_dead_letter_on_exhausted_retries() -> None:
    engine = _engine()
    tenant_id, operator = _foundation(engine)
    registry = EventHandlerRegistry()
    # Use low attempts via direct EventBus composition inside one UoW is hard;
    # publish sync with always-failing handler and max attempts via in-memory
    # path is covered elsewhere. Here verify DLQ table write via failing handler
    # with default max=5 would need 5 dispatch cycles — use a custom bus instance.
    from kernel.event_bus.bus import EventBus
    from kernel.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
    from kernel.infrastructure.persistence.event_repository import (
        SQLAlchemyEventRepository,
    )
    from kernel.infrastructure.persistence.permission_repository import (
        SQLAlchemyPermissionRepository,
    )
    from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
    from kernel.infrastructure.persistence.identity_permission import (
        SQLAlchemyPrincipalEligibility,
    )
    from kernel.permission.service import PermissionService

    permission = TransactionalPermissionService(
        create_session_factory(engine),
        grant_administrators={operator.subject_id},
    )
    assert permission.grant(
        operator,
        principal_subject_id=operator.subject_id,
        resource_type="event_stream",
        actions={"publish", "subscribe", "replay", "read"},
    ).ok

    def boom(_event) -> None:
        raise RuntimeError("nope")

    bus = TransactionalEventBus(
        create_session_factory(engine),
        handler_registry=registry,
    )
    assert bus.subscribe(
        operator,
        subscriber_id="projection.dlq",
        event_name="crm.order.boom",
        handler=boom,
    ).ok

    # Drive a one-attempt EventBus against the same SQLAlchemy session.
    with SQLAlchemyUnitOfWork(create_session_factory(engine)) as unit_of_work:
        event_repo = SQLAlchemyEventRepository(
            unit_of_work.session,
            tenant_id=tenant_id,
            handler_registry=registry,
        )
        permission_repo = SQLAlchemyPermissionRepository(
            unit_of_work.session,
            tenant_id=tenant_id,
        )
        audit = SQLAlchemyAuditLog(unit_of_work.session, tenant_id=tenant_id)
        inner = EventBus(
            PermissionService(
                repository=permission_repo,
                audit_log=audit,
                principal_eligibility=SQLAlchemyPrincipalEligibility(
                    unit_of_work.session
                ),
            ),
            repository=event_repo,
            audit_log=audit,
            max_delivery_attempts=1,
        )
        published = inner.publish(
            operator,
            event_name="crm.order.boom",
            schema_version="1",
            producer="pkg.crm",
            payload={"order_id": "BOOM"},
        )
        assert published.ok
        unit_of_work.commit()
        event_repo.activate_pending_handlers()

    with create_session_factory(engine)() as session:
        letters = list(session.scalars(select(EventDeadLetterRecord)))
        assert len(letters) == 1
        assert letters[0].subscriber_id == "projection.dlq"
        assert letters[0].reason == "RuntimeError"

    stats = bus.get_delivery_stats(operator)
    assert stats.ok and stats.data is not None
    assert stats.data.dead_letter_depth == 1
    assert tenant_id == operator.tenant_id


def test_enqueue_denied_without_publish() -> None:
    engine = _engine()
    _tenant_id, operator = _foundation(engine)
    bus = TransactionalEventBus(create_session_factory(engine))
    result = bus.enqueue(
        operator,
        event_name="crm.order.created",
        schema_version="1",
        producer="pkg.crm",
        payload={},
    )
    assert not result.ok
    assert result.error_code == ErrorCode.PERMISSION_DENIED
