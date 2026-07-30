"""Transactional domain event outbox contracts for PHX-E19."""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Engine, create_engine, func, select
from sqlalchemy.pool import StaticPool

from kernel.infrastructure.persistence import (
    EventOutboxRecord,
    TransactionalOrganizationService,
    create_session_factory,
    metadata,
)
from kernel.shared.context import ExecutionContext, SubjectType


def _engine() -> Engine:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        poolclass=StaticPool,
    )
    with engine.begin() as connection:
        connection.exec_driver_sql("ATTACH DATABASE ':memory:' AS kernel")
        metadata.create_all(connection)
    return engine


def _context(*, platform: bool = False, tenant_id=None, subject_id=None) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id or uuid4(),
        subject_type=SubjectType.SERVICE,
        tenant_id=None if platform else (tenant_id or uuid4()),
        platform_scope=platform,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def test_transactional_create_tenant_writes_outbox_in_same_session() -> None:
    engine = _engine()
    governor = _context(platform=True)
    organization = TransactionalOrganizationService(
        create_session_factory(engine),
        platform_governors={governor.subject_id},
    )
    created = organization.create_tenant(governor, legal_name="Transactional Tenant")
    assert created.ok and created.data is not None

    with engine.connect() as connection:
        rows = connection.execute(
            select(EventOutboxRecord.event_name, EventOutboxRecord.producer).where(
                EventOutboxRecord.tenant_id == created.data
            )
        ).all()
        assert len(rows) == 2
        assert {row.event_name for row in rows} == {
            "organization.tenant.created",
            "organization.enterprise.created",
        }
        assert all(row.producer == "organization.kernel" for row in rows)
        assert (
            connection.scalar(select(func.count()).select_from(EventOutboxRecord)) == 2
        )


def test_transactional_create_enterprise_writes_outbox_in_same_session() -> None:
    engine = _engine()
    governor = _context(platform=True)
    organization = TransactionalOrganizationService(
        create_session_factory(engine),
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name="Tenant With Secondary")
    assert tenant.data is not None
    tenant_ctx = _context(tenant_id=tenant.data)
    enterprise = organization.create_enterprise(
        tenant_ctx,
        legal_name="Secondary Enterprise",
    )
    assert enterprise.ok

    with engine.connect() as connection:
        rows = connection.execute(
            select(EventOutboxRecord.event_name).where(
                EventOutboxRecord.event_name == "organization.enterprise.created",
                EventOutboxRecord.tenant_id == tenant.data,
            )
        ).all()
        assert len(rows) == 2
