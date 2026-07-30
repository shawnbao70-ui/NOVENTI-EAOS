"""Transactional AI Runtime contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Engine, create_engine, select
from sqlalchemy.pool import StaticPool

from kernel.identity.models import SubjectKind
from kernel.infrastructure.persistence import (
    AIAgentRunRecord,
    AIMemoryEntryRecord,
    TransactionalAIRuntimeService,
    TransactionalIdentityService,
    TransactionalOrganizationService,
    TransactionalPermissionService,
    TransactionalWorkflowService,
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


def _foundation(engine: Engine) -> tuple[UUID, ExecutionContext, ExecutionContext]:
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
        display_name="Admin",
    )
    ai = identity.register_ai_employee(governor, display_name="Digital Employee")
    assert admin.data is not None and ai.data is not None
    assert identity.assign_ai_to_tenant(
        _context(tenant.data, subject_id=admin.data, subject_type=SubjectType.HUMAN),
        ai_subject_id=ai.data,
    ).ok
    return (
        tenant.data,
        _context(tenant.data, subject_id=admin.data, subject_type=SubjectType.HUMAN),
        _context(tenant.data, subject_id=ai.data, subject_type=SubjectType.AI_EMPLOYEE),
    )


def test_transactional_run_tool_and_memory_round_trip() -> None:
    engine = _engine()
    tenant_id, admin, ai = _foundation(engine)
    permission = TransactionalPermissionService(
        create_session_factory(engine),
        grant_administrators={admin.subject_id},
    )
    runtime = TransactionalAIRuntimeService(
        create_session_factory(engine),
        definition_administrators={admin.subject_id},
    )
    assert permission.grant(
        admin,
        principal_subject_id=ai.subject_id,
        resource_type="ai_run",
        actions={"create", "read"},
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=admin.subject_id,
        resource_type="tool",
        actions={"register"},
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=ai.subject_id,
        resource_type="tool",
        actions={"invoke_tool"},
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=ai.subject_id,
        resource_type="ai_memory",
        actions={"read", "write"},
    ).ok

    created = runtime.create_agent_run(ai, goal="Assist finance close")
    assert created.ok and created.data is not None
    assert runtime.register_tool(
        admin,
        name="report.summarize",
        description="Summarize report",
        high_impact=False,
    ).ok
    invoked = runtime.invoke_tool(
        ai,
        run_id=created.data,
        tool_name="report.summarize",
        arguments={"doc": "Q1"},
    )
    assert invoked.ok
    written = runtime.write_memory(
        ai,
        run_id=created.data,
        key="summary",
        value={"text": "ok"},
    )
    assert written.ok

    with create_session_factory(engine)() as session:
        run = session.scalar(
            select(AIAgentRunRecord).where(AIAgentRunRecord.id == created.data)
        )
        assert run is not None
        assert run.goal == "Assist finance close"
        memory = session.scalar(
            select(AIMemoryEntryRecord).where(
                AIMemoryEntryRecord.run_id == created.data
            )
        )
        assert memory is not None
        assert memory.key == "summary"
    assert tenant_id == ai.tenant_id


def test_transactional_tool_denied_without_grant() -> None:
    engine = _engine()
    _tenant_id, admin, ai = _foundation(engine)
    permission = TransactionalPermissionService(
        create_session_factory(engine),
        grant_administrators={admin.subject_id},
    )
    runtime = TransactionalAIRuntimeService(create_session_factory(engine))
    assert permission.grant(
        admin,
        principal_subject_id=ai.subject_id,
        resource_type="ai_run",
        actions={"create"},
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=admin.subject_id,
        resource_type="tool",
        actions={"register"},
    ).ok
    created = runtime.create_agent_run(ai, goal="Denied tool path")
    assert created.data is not None
    assert runtime.register_tool(
        admin,
        name="secret.write",
        description="Write",
        high_impact=False,
    ).ok
    denied = runtime.invoke_tool(
        ai,
        run_id=created.data,
        tool_name="secret.write",
    )
    assert denied.error_code == ErrorCode.AI_TOOL_DENIED
