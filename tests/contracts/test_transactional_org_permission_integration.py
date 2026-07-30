"""Transactional Organization ↔ Permission boundary contracts."""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Engine, create_engine, func, select
from sqlalchemy.pool import StaticPool

from kernel.identity.models import SubjectKind
from kernel.infrastructure.persistence import (
    GrantRecord,
    MembershipRecord,
    PermissionDecisionRecord,
    TransactionalIdentityService,
    TransactionalOrganizationService,
    TransactionalPermissionService,
    create_session_factory,
    metadata,
)
from kernel.permission.models import PermissionEffect, Resource
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


def _context(tenant_id=None, *, subject_id=None, platform=False) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id or uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=None if platform else (tenant_id or uuid4()),
        platform_scope=platform,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def test_persisted_membership_role_never_grants_permission_implicitly() -> None:
    engine = _engine()
    session_factory = create_session_factory(engine)
    governor = _context(platform=True)
    organization = TransactionalOrganizationService(
        session_factory,
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(
        governor,
        legal_name="Transactional Boundary Tenant",
    )
    assert tenant.data is not None

    provisional = _context(tenant.data)
    identity = TransactionalIdentityService(session_factory)
    administrator = identity.register_subject(
        provisional,
        subject_type=SubjectKind.HUMAN,
        display_name="Grant Administrator",
    )
    member = identity.register_subject(
        provisional,
        subject_type=SubjectKind.HUMAN,
        display_name="Organization Administrator",
    )
    assert administrator.data is not None
    assert member.data is not None
    tenant_context = _context(tenant.data, subject_id=administrator.data)

    membership = organization.add_membership(
        tenant_context,
        subject_id=member.data,
        membership_role_label="administrator",
    )
    assert membership.ok
    permission = TransactionalPermissionService(
        session_factory,
        grant_administrators={administrator.data},
    )
    resource = Resource(
        tenant_id=tenant.data,
        resource_type="tenant_settings",
    )
    denied = permission.evaluate(
        tenant_context,
        principal_subject_id=member.data,
        action="write",
        resource=resource,
    )
    assert denied.data is not None
    assert denied.data.effect == PermissionEffect.DENY

    granted = permission.grant(
        tenant_context,
        principal_subject_id=member.data,
        resource_type="tenant_settings",
        actions={"write"},
    )
    assert granted.ok
    allowed = permission.evaluate(
        tenant_context,
        principal_subject_id=member.data,
        action="write",
        resource=resource,
    )
    assert allowed.data is not None
    assert allowed.data.effect == PermissionEffect.ALLOW

    with engine.connect() as connection:
        assert connection.scalar(select(func.count()).select_from(MembershipRecord)) == 1
        assert connection.scalar(select(func.count()).select_from(GrantRecord)) == 1
        assert (
            connection.scalar(
                select(func.count()).select_from(PermissionDecisionRecord)
            )
            == 2
        )
