"""Transactional Smart Terminal contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Engine, create_engine
from sqlalchemy.pool import StaticPool

from kernel.identity.models import SubjectKind
from kernel.infrastructure.persistence import (
    TerminalExtensionRecord,
    TerminalIntentRecord,
    TerminalPreviewRecord,
    TerminalSessionRecord,
    TransactionalIdentityService,
    TransactionalOrganizationService,
    TransactionalPermissionService,
    TransactionalSmartTerminalService,
    create_session_factory,
    metadata,
)
from smart_terminal.models import ExtensionStatus
from kernel.shared.context import ExecutionContext, SubjectType
from sqlalchemy import select


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
        display_name="Terminal Admin",
    )
    assert admin.data is not None
    return (
        tenant.data,
        _context(tenant.data, subject_id=admin.data, subject_type=SubjectType.HUMAN),
    )


def test_transactional_session_intent_preview_round_trip() -> None:
    engine = _engine()
    tenant_id, admin = _foundation(engine)
    factory = create_session_factory(engine)
    permission = TransactionalPermissionService(
        factory,
        grant_administrators={admin.subject_id},
    )
    terminal = TransactionalSmartTerminalService(
        factory,
        definition_administrators={admin.subject_id},
    )
    for resource_type, actions in (
        ("terminal_session", {"open", "read", "close"}),
        ("terminal_intent", {"compose", "read"}),
        ("terminal_preview", {"build", "read"}),
        ("terminal_approval", {"present", "request"}),
        ("terminal_commit", {"execute"}),
    ):
        assert permission.grant(
            admin,
            principal_subject_id=admin.subject_id,
            resource_type=resource_type,
            actions=actions,
        ).ok

    opened = terminal.open_session(admin)
    assert opened.ok and opened.data is not None
    intent = terminal.compose_intent(
        admin,
        terminal_session_id=opened.data,
        text="Prepare weekly ops brief",
    )
    assert intent.ok and intent.data is not None
    preview = terminal.build_preview(
        admin,
        intent_id=intent.data,
        action="ops.brief",
        resource_ref="ops:weekly",
        plan_version="v1",
        scope="tenant",
        impact_summary="Compose weekly brief",
        high_impact=False,
    )
    assert preview.ok and preview.data is not None
    committed = terminal.commit(admin, preview_id=preview.data)
    assert committed.ok and committed.data is not None

    with factory() as session:
        assert session.scalar(
            select(TerminalSessionRecord).where(TerminalSessionRecord.id == opened.data)
        ) is not None
        assert session.scalar(
            select(TerminalIntentRecord).where(TerminalIntentRecord.id == intent.data)
        ) is not None
        assert session.scalar(
            select(TerminalPreviewRecord).where(TerminalPreviewRecord.id == preview.data)
        ) is not None


def test_transactional_extension_sql_round_trip() -> None:
    engine = _engine()
    tenant_id, admin = _foundation(engine)
    factory = create_session_factory(engine)
    permission = TransactionalPermissionService(
        factory,
        grant_administrators={admin.subject_id},
    )
    terminal = TransactionalSmartTerminalService(
        factory,
        definition_administrators={admin.subject_id},
    )
    assert permission.grant(
        admin,
        principal_subject_id=admin.subject_id,
        resource_type="terminal_extension",
        actions={"register", "activate", "revoke", "read", "invoke"},
    ).ok

    created = terminal.register_extension(
        admin,
        extension_key="noventi.sql.panel",
        version="1.0.0",
        signature_ref="sig:sql:1",
        declared_actions=["panel.render"],
        allowed_surfaces=["extensions"],
        data_scope="tenant.demo",
    )
    assert created.ok and created.data is not None
    assert terminal.activate_extension(admin, extension_id=created.data).ok
    listed = terminal.list_extensions(admin)
    assert listed.ok and listed.data is not None
    assert len(listed.data) == 1
    assert listed.data[0].status == ExtensionStatus.ACTIVE
    invoked = terminal.invoke_extension_action(
        admin,
        extension_id=created.data,
        action="panel.render",
        surface="extensions",
    )
    assert invoked.ok and invoked.data is not None
    assert invoked.data["executed"] is False
    assert terminal.revoke_extension(admin, extension_id=created.data).ok

    with factory() as session:
        record = session.scalar(
            select(TerminalExtensionRecord).where(
                TerminalExtensionRecord.id == created.data,
                TerminalExtensionRecord.tenant_id == tenant_id,
            )
        )
        assert record is not None
        assert record.status == ExtensionStatus.REVOKED.value
        assert record.extension_key == "noventi.sql.panel"
        assert record.version >= 2
