"""Transactional Enterprise Brain & Twin contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Engine, create_engine, select
from sqlalchemy.pool import StaticPool

from kernel.identity.models import SubjectKind
from kernel.infrastructure.persistence import (
    BrainInsightRecord,
    TransactionalBrainService,
    TransactionalIdentityService,
    TransactionalOrganizationService,
    TransactionalPermissionService,
    TransactionalTwinService,
    TwinSnapshotRecord,
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


def _context(
    tenant_id=None,
    *,
    subject_id=None,
    subject_type=SubjectType.SERVICE,
    platform=False,
) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id or uuid4(),
        subject_type=subject_type,
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
    identity = TransactionalIdentityService(
        create_session_factory(engine),
        platform_governors={governor.subject_id},
    )
    assert identity.grant_platform_governor(
        governor,
        subject_id=governor.subject_id,
    ).ok
    initial = _context(tenant.data)
    admin = identity.register_subject(
        initial,
        subject_type=SubjectKind.HUMAN,
        display_name="Brain Admin",
    )
    assert admin.data is not None
    return (
        tenant.data,
        _context(tenant.data, subject_id=admin.data, subject_type=SubjectType.HUMAN),
    )


def test_transactional_twin_and_brain_round_trip() -> None:
    engine = _engine()
    _tenant_id, admin = _foundation(engine)
    factory = create_session_factory(engine)
    permission = TransactionalPermissionService(
        factory,
        grant_administrators={admin.subject_id},
    )
    twin = TransactionalTwinService(factory)
    brain = TransactionalBrainService(factory)
    for resource_type, actions in (
        ("twin_snapshot", {"write", "read"}),
        ("brain_insight", {"publish", "read"}),
    ):
        assert permission.grant(
            admin,
            principal_subject_id=admin.subject_id,
            resource_type=resource_type,
            actions=actions,
        ).ok

    snapshot = twin.upsert_snapshot(
        admin,
        entity_ref="fleet:truck-1",
        state={"location": "dock-3"},
        source_ref="gps",
        reason="heartbeat",
        confidence=0.99,
    )
    assert snapshot.ok and snapshot.data is not None
    insight = brain.publish_insight(
        admin,
        kind="insight",
        summary="Truck idle near dock-3",
        confidence=0.7,
        source_ref="brain:rules",
        reason="idle detection",
        twin_ref=snapshot.data,
    )
    assert insight.ok and insight.data is not None
    forbidden = brain.request_execution(admin, insight_id=insight.data)
    assert forbidden.error_code == ErrorCode.BRAIN_EXECUTION_FORBIDDEN

    with factory() as session:
        assert session.scalar(
            select(TwinSnapshotRecord).where(TwinSnapshotRecord.id == snapshot.data)
        ) is not None
        assert session.scalar(
            select(BrainInsightRecord).where(BrainInsightRecord.id == insight.data)
        ) is not None
