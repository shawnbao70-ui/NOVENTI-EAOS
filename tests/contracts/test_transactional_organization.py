"""Organization SQLAlchemy schema, isolation, and transaction contracts."""

from __future__ import annotations

from uuid import uuid4

from sqlalchemy import Engine, create_engine, func, select
from sqlalchemy.pool import StaticPool

from kernel.identity.models import SubjectKind
from kernel.infrastructure.persistence import (
    AuditEventRecord,
    EnterpriseRecord,
    MembershipRecord,
    OrganizationUnitRecord,
    TenantRecord,
    TransactionalIdentityService,
    TransactionalOrganizationService,
    create_session_factory,
    metadata,
)
from kernel.organization.models import OrganizationStatus, UnitType
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


def _organization_service(
    engine: Engine,
) -> tuple[TransactionalOrganizationService, ExecutionContext]:
    governor_context = _context(platform=True)
    service = TransactionalOrganizationService(
        create_session_factory(engine),
        platform_governors={governor_context.subject_id},
    )
    return service, governor_context


def test_organization_schema_has_composite_tenant_foreign_keys() -> None:
    unit_table = metadata.tables["kernel.org_units"]
    membership_table = metadata.tables["kernel.memberships"]
    unit_foreign_keys = {
        tuple(element.parent.name for element in constraint.elements)
        for constraint in unit_table.foreign_key_constraints
    }
    membership_foreign_keys = {
        tuple(element.parent.name for element in constraint.elements)
        for constraint in membership_table.foreign_key_constraints
    }
    assert ("parent_unit_id", "tenant_id") in unit_foreign_keys
    assert ("org_unit_id", "tenant_id") in membership_foreign_keys


def test_transactional_organization_round_trip_is_atomic() -> None:
    engine = _engine()
    organization, governor_context = _organization_service(engine)
    created = organization.create_tenant(
        governor_context,
        legal_name="Organization A",
    )
    assert created.data is not None
    tenant_id = created.data
    tenant_context = _context(tenant_id)

    identity = TransactionalIdentityService(create_session_factory(engine))
    subject = identity.register_subject(
        tenant_context,
        subject_type=SubjectKind.HUMAN,
        display_name="Member",
    )
    assert subject.data is not None
    unit = organization.upsert_unit(
        tenant_context,
        unit_type=UnitType.DEPARTMENT,
        name="Engineering",
    )
    assert unit.data is not None
    membership = organization.add_membership(
        tenant_context,
        subject_id=subject.data,
        org_unit_id=unit.data,
        membership_role_label="member",
    )
    assert membership.ok

    listed = organization.list_memberships(tenant_context)
    assert listed.ok
    assert len(listed.data or []) == 1
    with engine.connect() as connection:
        assert connection.scalar(select(func.count()).select_from(TenantRecord)) == 1
        assert (
            connection.scalar(select(func.count()).select_from(EnterpriseRecord))
            == 1
        )
        assert (
            connection.scalar(select(func.count()).select_from(OrganizationUnitRecord))
            == 1
        )
        assert (
            connection.scalar(select(func.count()).select_from(MembershipRecord))
            == 1
        )
        assert connection.scalar(select(func.count()).select_from(AuditEventRecord)) == 4


def test_organization_repository_hides_cross_tenant_data() -> None:
    engine = _engine()
    organization, governor_context = _organization_service(engine)
    created = organization.create_tenant(governor_context, legal_name="Tenant A")
    assert created.data is not None

    hidden = organization.get_tenant(
        _context(uuid4()),
        tenant_id=created.data,
    )
    assert not hidden.ok
    assert hidden.error_code == ErrorCode.ORG_TENANT_NOT_FOUND


def test_tenant_status_update_persists_and_blocks_units() -> None:
    engine = _engine()
    organization, governor_context = _organization_service(engine)
    created = organization.create_tenant(governor_context, legal_name="Tenant A")
    assert created.data is not None
    assert organization.suspend_tenant(
        governor_context,
        tenant_id=created.data,
        reason="test",
        expected_version=1,
    ).ok

    tenant = organization.get_tenant(
        governor_context,
        tenant_id=created.data,
    )
    assert tenant.data is not None
    assert tenant.data.status == OrganizationStatus.SUSPENDED
    denied = organization.upsert_unit(
        _context(created.data),
        unit_type=UnitType.DEPARTMENT,
        name="Blocked",
    )
    assert not denied.ok
    assert denied.error_code == ErrorCode.ORG_TENANT_SUSPENDED


def test_platform_scope_without_governor_cannot_create_tenant() -> None:
    engine = _engine()
    service = TransactionalOrganizationService(create_session_factory(engine))
    result = service.create_tenant(
        _context(platform=True),
        legal_name="Unauthorized",
    )

    assert not result.ok
    assert result.error_code == ErrorCode.PERMISSION_DENIED
    with engine.connect() as connection:
        assert connection.scalar(select(func.count()).select_from(TenantRecord)) == 0
        assert connection.scalar(select(func.count()).select_from(AuditEventRecord)) == 0


def test_transactional_unit_update_uses_optimistic_lock() -> None:
    engine = _engine()
    organization, governor_context = _organization_service(engine)
    tenant = organization.create_tenant(governor_context, legal_name="Tenant A")
    assert tenant.data is not None
    context = _context(tenant.data)
    unit = organization.upsert_unit(
        context,
        unit_type=UnitType.DEPARTMENT,
        name="Engineering",
    )
    assert unit.data is not None
    assert organization.upsert_unit(
        context,
        unit_id=unit.data,
        unit_type=UnitType.DEPARTMENT,
        name="Product Engineering",
        expected_version=1,
    ).ok

    stale = organization.upsert_unit(
        context,
        unit_id=unit.data,
        unit_type=UnitType.DEPARTMENT,
        name="Stale Update",
        expected_version=1,
    )

    assert stale.error_code == ErrorCode.ORG_VERSION_CONFLICT
