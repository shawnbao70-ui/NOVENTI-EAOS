"""Identity ↔ Organization L2 eligibility and atomic reassignment contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Engine, create_engine, select
from sqlalchemy.pool import StaticPool

from kernel.identity.models import AssignmentMode, SubjectKind
from kernel.infrastructure.persistence import (
    AIAssignmentRecord,
    MembershipRecord,
    TransactionalIdentityOrganizationCoordinator,
    TransactionalIdentityService,
    TransactionalOrganizationService,
    create_session_factory,
    metadata,
)
from kernel.organization.models import OrganizationStatus
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
    *,
    subject_id: UUID | None = None,
    tenant_id: UUID | None = None,
    platform: bool = False,
) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id or uuid4(),
        subject_type=SubjectType.SERVICE,
        tenant_id=None if platform else tenant_id,
        platform_scope=platform,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def test_l2_membership_requires_active_same_tenant_identity() -> None:
    engine = _engine()
    factory = create_session_factory(engine)
    governor = _context(platform=True)
    organization = TransactionalOrganizationService(
        factory,
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name="L2 Tenant")
    assert tenant.data
    tenant_context = _context(tenant_id=tenant.data)
    identity = TransactionalIdentityService(factory)
    subject = identity.register_subject(
        tenant_context,
        subject_type=SubjectKind.HUMAN,
        display_name="Eligible",
    )
    assert subject.data
    coordinator = TransactionalIdentityOrganizationCoordinator(factory)

    assert coordinator.add_membership(
        tenant_context,
        subject_id=subject.data,
    ).ok
    denied = coordinator.add_membership(
        tenant_context,
        subject_id=uuid4(),
    )
    assert denied.error_code == ErrorCode.ORG_SUBJECT_INELIGIBLE


def test_l2_ai_reassignment_ends_old_memberships_atomically() -> None:
    engine = _engine()
    factory = create_session_factory(engine)
    governor = _context(platform=True)
    governors = {governor.subject_id}
    organization = TransactionalOrganizationService(
        factory,
        platform_governors=governors,
    )
    tenant_a = organization.create_tenant(governor, legal_name="Tenant A")
    tenant_b = organization.create_tenant(governor, legal_name="Tenant B")
    assert tenant_a.data and tenant_b.data
    identity = TransactionalIdentityService(
        factory,
        platform_governors=governors,
    )
    ai = identity.register_ai_employee(governor, display_name="L2 AI")
    assert ai.data
    assert identity.assign_ai_to_tenant(
        _context(tenant_id=tenant_a.data),
        ai_subject_id=ai.data,
    ).ok
    coordinator = TransactionalIdentityOrganizationCoordinator(
        factory,
        platform_governors=governors,
    )
    assert coordinator.add_membership(
        _context(tenant_id=tenant_a.data),
        subject_id=ai.data,
        membership_role_label="digital_employee",
    ).ok

    moved = coordinator.reassign_ai(
        governor,
        ai_subject_id=ai.data,
        to_tenant_id=tenant_b.data,
        mode=AssignmentMode.INHERIT,
    )
    assert moved.ok
    with engine.connect() as connection:
        membership_status = connection.scalar(
            select(MembershipRecord.status).where(
                MembershipRecord.subject_id == ai.data
            )
        )
        active_tenant = connection.scalar(
            select(AIAssignmentRecord.tenant_id).where(
                AIAssignmentRecord.ai_subject_id == ai.data,
                AIAssignmentRecord.status == "active",
            )
        )
    assert membership_status == OrganizationStatus.ENDED.value
    assert active_tenant == tenant_b.data
