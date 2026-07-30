"""Event Bus SQLAlchemy persistence, delivery, and replay contracts."""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Engine, create_engine, func, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.pool import StaticPool

from kernel.event_bus.handlers import EventHandlerRegistry
from kernel.event_bus.models import EventEnvelope
from kernel.identity.models import SubjectKind
from kernel.infrastructure.persistence import (
    EventDeliveryRecord,
    EventRecord,
    EventSubscriptionRecord,
    PermissionDecisionRecord,
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


def _event_foundation(
    engine: Engine,
    *,
    grant_actions: bool = True,
) -> tuple[ExecutionContext, TransactionalEventBus, EventHandlerRegistry]:
    governor = _context(platform=True)
    organization = TransactionalOrganizationService(
        create_session_factory(engine),
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name=str(uuid4()))
    assert tenant.data is not None
    provisional = _context(tenant.data)
    subject = TransactionalIdentityService(
        create_session_factory(engine)
    ).register_subject(
        provisional,
        subject_type=SubjectKind.SERVICE,
        display_name="Event Producer",
    )
    assert subject.data is not None
    context = _context(tenant.data, subject_id=subject.data)
    if grant_actions:
        permission = TransactionalPermissionService(
            create_session_factory(engine),
            grant_administrators={context.subject_id},
        )
        assert permission.grant(
            context,
            principal_subject_id=context.subject_id,
            resource_type="event_stream",
            actions={"subscribe", "publish", "read", "replay"},
        ).ok
    registry = EventHandlerRegistry()
    return (
        context,
        TransactionalEventBus(
            create_session_factory(engine),
            handler_registry=registry,
        ),
        registry,
    )


def test_event_schema_persists_jsonb_without_handler_callable() -> None:
    event_table = metadata.tables["kernel.events"]
    subscription_table = metadata.tables["kernel.event_subscriptions"]
    database_type = event_table.c.payload.type.dialect_impl(postgresql.dialect())
    assert isinstance(database_type, JSONB)
    assert "handler" not in subscription_table.c


def test_publish_persists_event_subscription_and_delivery() -> None:
    engine = _engine()
    context, bus, _ = _event_foundation(engine)
    received: list[EventEnvelope] = []
    subscribed = bus.subscribe(
        context,
        subscriber_id="billing",
        event_name="crm.customer.created",
        handler=received.append,
    )
    assert subscribed.ok
    published = bus.publish(
        context,
        event_name="crm.customer.created",
        schema_version="1.0",
        producer="crm",
        payload={"customer_id": "C-1"},
    )
    assert published.data is not None
    assert published.data.delivered_count == 1
    assert len(received) == 1

    event_id = published.data.event_id
    loaded = bus.get_event(context, event_id=event_id)
    assert loaded.data is not None
    assert loaded.data.payload["customer_id"] == "C-1"
    with engine.connect() as connection:
        assert connection.scalar(select(func.count()).select_from(EventRecord)) == 1
        assert (
            connection.scalar(
                select(func.count()).select_from(EventSubscriptionRecord)
            )
            == 1
        )
        assert (
            connection.scalar(select(EventDeliveryRecord.status))
            == "delivered"
        )


def test_failed_delivery_is_persisted_and_replay_can_succeed() -> None:
    engine = _engine()
    context, bus, registry = _event_foundation(engine)

    def fail(_: EventEnvelope) -> None:
        raise RuntimeError("transient")

    subscribed = bus.subscribe(
        context,
        subscriber_id="warehouse",
        event_name="crm.customer.created",
        handler=fail,
    )
    assert subscribed.data is not None
    published = bus.publish(
        context,
        event_name="crm.customer.created",
        schema_version="1",
        producer="crm",
        payload={},
    )
    assert published.data is not None
    assert published.data.failed_subscribers == ("warehouse",)
    registry.register(subscribed.data, lambda _: None)

    replayed = bus.replay(context, event_id=published.data.event_id)
    assert replayed.data is not None
    assert replayed.data.delivered_count == 1
    with engine.connect() as connection:
        row = connection.execute(
            select(
                EventDeliveryRecord.status,
                EventDeliveryRecord.attempt_count,
                EventDeliveryRecord.last_error_code,
            )
        ).one()
    assert row.status == "delivered"
    assert row.attempt_count == 2
    assert row.last_error_code is None


def test_permission_denial_is_audited_without_event_side_effect() -> None:
    engine = _engine()
    context, bus, _ = _event_foundation(engine, grant_actions=False)
    denied = bus.publish(
        context,
        event_name="crm.customer.created",
        schema_version="1",
        producer="crm",
        payload={},
    )
    assert not denied.ok
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    with engine.connect() as connection:
        assert connection.scalar(select(func.count()).select_from(EventRecord)) == 0
        assert (
            connection.scalar(
                select(func.count()).select_from(PermissionDecisionRecord)
            )
            == 1
        )
