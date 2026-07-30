"""Permission SQLAlchemy schema, default-deny, and transaction contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Engine, create_engine, func, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.pool import StaticPool

from kernel.identity.models import SubjectKind
from kernel.infrastructure.persistence import (
    AuditEventRecord,
    GrantRecord,
    PermissionDecisionRecord,
    TransactionalIdentityService,
    TransactionalOrganizationService,
    TransactionalPermissionService,
    create_session_factory,
    metadata,
)
from kernel.permission.models import PermissionEffect, PolicyRule, Resource, ScopeLevel
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


def _tenant_and_principal(engine: Engine) -> tuple[UUID, UUID]:
    governor = _context(platform=True)
    organization = TransactionalOrganizationService(
        create_session_factory(engine),
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name=str(uuid4()))
    assert tenant.data is not None
    tenant_context = _context(tenant.data)
    principal = TransactionalIdentityService(
        create_session_factory(engine)
    ).register_subject(
        tenant_context,
        subject_type=SubjectKind.HUMAN,
        display_name="Principal",
    )
    assert principal.data is not None
    return tenant.data, principal.data


def test_permission_schema_uses_jsonb_and_active_uniqueness() -> None:
    table = metadata.tables["kernel.grants"]
    database_type = table.c.actions.type.dialect_impl(postgresql.dialect())
    assert isinstance(database_type, JSONB)
    index = next(
        candidate
        for candidate in table.indexes
        if candidate.name == "uq_grants_equivalent_active"
    )
    assert index.unique
    assert index.dialect_options["postgresql"]["where"] is not None


def test_default_deny_decision_and_audit_are_committed() -> None:
    engine = _engine()
    tenant_id, principal_id = _tenant_and_principal(engine)
    context = _context(tenant_id)
    service = TransactionalPermissionService(create_session_factory(engine))
    decision = service.evaluate(
        context,
        principal_subject_id=principal_id,
        action="read",
        resource=Resource(tenant_id=tenant_id, resource_type="document"),
    )

    assert decision.ok
    assert decision.data is not None
    assert decision.data.effect == PermissionEffect.DENY
    assert decision.data.reason_code == ErrorCode.PERMISSION_DENIED.value
    with engine.connect() as connection:
        assert (
            connection.scalar(
                select(func.count()).select_from(PermissionDecisionRecord)
            )
            == 1
        )


def test_grant_allow_revoke_and_deny_persist_atomically() -> None:
    engine = _engine()
    tenant_id, principal_id = _tenant_and_principal(engine)
    administrator_context = _context(tenant_id)
    service = TransactionalPermissionService(
        create_session_factory(engine),
        grant_administrators={administrator_context.subject_id},
    )
    resource = Resource(tenant_id=tenant_id, resource_type="document")
    granted = service.grant(
        administrator_context,
        principal_subject_id=principal_id,
        resource_type="document",
        actions={"read"},
    )
    assert granted.data is not None
    allowed = service.evaluate(
        administrator_context,
        principal_subject_id=principal_id,
        action="read",
        resource=resource,
    )
    assert allowed.data is not None
    assert allowed.data.effect == PermissionEffect.ALLOW
    assert service.revoke(
        administrator_context,
        grant_id=granted.data,
        reason="test",
        expected_version=1,
    ).ok
    denied = service.evaluate(
        administrator_context,
        principal_subject_id=principal_id,
        action="read",
        resource=resource,
    )
    assert denied.data is not None
    assert denied.data.effect == PermissionEffect.DENY

    with engine.connect() as connection:
        assert connection.scalar(select(GrantRecord.status)) == "revoked"


def test_cross_tenant_evaluation_fails_without_decision_side_effect() -> None:
    engine = _engine()
    tenant_id, principal_id = _tenant_and_principal(engine)
    context = _context(tenant_id)
    service = TransactionalPermissionService(create_session_factory(engine))
    before = 0
    with engine.connect() as connection:
        before = int(
            connection.scalar(
                select(func.count()).select_from(PermissionDecisionRecord)
            )
        )
    result = service.evaluate(
        context,
        principal_subject_id=principal_id,
        action="read",
        resource=Resource(tenant_id=uuid4(), resource_type="document"),
    )
    assert not result.ok
    assert result.error_code == ErrorCode.PERMISSION_CROSS_TENANT_FORBIDDEN
    with engine.connect() as connection:
        after = int(
            connection.scalar(
                select(func.count()).select_from(PermissionDecisionRecord)
            )
        )
    assert after == before


def test_policy_deny_overrides_grant_on_sqlite() -> None:
    engine = _engine()
    tenant_id, principal_id = _tenant_and_principal(engine)
    administrator_context = _context(tenant_id)
    service = TransactionalPermissionService(
        create_session_factory(engine),
        grant_administrators={administrator_context.subject_id},
    )
    assert service.grant(
        administrator_context,
        principal_subject_id=principal_id,
        resource_type="document",
        actions={"read"},
        scope_level=ScopeLevel.TENANT,
    ).ok
    created = service.create_policy(
        administrator_context,
        name="deny-document-read",
        policy_version="1",
        rules=[
            PolicyRule(
                id=uuid4(),
                effect=PermissionEffect.DENY,
                resource_type="document",
                actions=frozenset({"read"}),
                scope_level=ScopeLevel.TENANT,
            )
        ],
    )
    assert created.data is not None
    assert service.activate_policy(
        administrator_context,
        policy_id=created.data,
        expected_version=1,
    ).ok

    decision = service.evaluate(
        administrator_context,
        principal_subject_id=principal_id,
        action="read",
        resource=Resource(tenant_id=tenant_id, resource_type="document"),
    )

    assert decision.data is not None
    assert decision.data.effect == PermissionEffect.DENY
    assert decision.data.reason_code == ErrorCode.PERMISSION_DENIED.value


def test_non_administrator_grant_is_denied_without_residue() -> None:
    engine = _engine()
    tenant_id, principal_id = _tenant_and_principal(engine)
    service = TransactionalPermissionService(create_session_factory(engine))
    before_audits = 0
    with engine.connect() as connection:
        before_audits = int(
            connection.scalar(select(func.count()).select_from(AuditEventRecord))
        )
    result = service.grant(
        _context(tenant_id),
        principal_subject_id=principal_id,
        resource_type="document",
        actions={"read"},
    )

    assert not result.ok
    assert result.error_code == ErrorCode.PERMISSION_DENIED
    with engine.connect() as connection:
        assert connection.scalar(select(func.count()).select_from(GrantRecord)) == 0
        assert (
            connection.scalar(select(func.count()).select_from(AuditEventRecord))
            == before_audits
        )
