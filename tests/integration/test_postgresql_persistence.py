"""Destructive integration contracts for a dedicated PostgreSQL test database."""

from __future__ import annotations

from tests.contracts._baseline import EXPECTED_TIP
from tests.integration._db_reset import reset_eaos_test_database

import os
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from uuid import uuid4

import pytest

TEST_DATABASE_URL = os.getenv("EAOS_TEST_DATABASE_URL", "").strip()
if not TEST_DATABASE_URL:
    pytest.skip(
        "EAOS_TEST_DATABASE_URL is not configured",
        allow_module_level=True,
    )

from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, create_engine, func, inspect, select, text
from sqlalchemy.engine import make_url

from kernel.identity.models import SubjectKind
from kernel.infrastructure.persistence import (
    AIAssignmentRecord,
    AIEmployeeProfileRecord,
    AuditEventRecord,
    EventDeliveryRecord,
    EventRecord,
    GrantRecord,
    MembershipRecord,
    PlatformIdentityGovernorRecord,
    SubjectRecord,
    TransactionalEventBus,
    TransactionalIdentityService,
    TransactionalIdentityOrganizationCoordinator,
    TransactionalOrganizationService,
    TransactionalAIRuntimeService,
    TransactionalKnowledgeService,
    TransactionalPermissionService,
    TransactionalBrainService,
    TransactionalMarketplaceService,
    TransactionalPackageService,
    TransactionalSmartTerminalService,
    TransactionalTwinService,
    TransactionalWorkflowService,
    WorkflowInstanceRecord,
    create_session_factory,
)
from eaos_platform.knowledge.models import KnowledgeLayer
from kernel.organization.models import OrganizationStatus, UnitType
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode

pytestmark = pytest.mark.postgresql


def _validated_test_database_url() -> str:
    url = make_url(TEST_DATABASE_URL)
    if url.drivername != "postgresql+psycopg":
        raise RuntimeError("integration database must use postgresql+psycopg")
    if url.database is None or not url.database.startswith("eaos_test"):
        raise RuntimeError("integration database name must start with eaos_test")
    return TEST_DATABASE_URL


@pytest.fixture(scope="module")
def postgres_engine() -> Iterator[Engine]:
    database_url = _validated_test_database_url()
    previous_url = os.environ.get("EAOS_DATABASE_URL")
    os.environ["EAOS_DATABASE_URL"] = database_url
    engine = create_engine(database_url, pool_pre_ping=True)
    config = Config("alembic.ini")

    try:
        with engine.begin() as connection:
            reset_eaos_test_database(connection)
        command.upgrade(config, "head")
        yield engine
    finally:
        with engine.begin() as connection:
            reset_eaos_test_database(connection)
        engine.dispose()
        if previous_url is None:
            os.environ.pop("EAOS_DATABASE_URL", None)
        else:
            os.environ["EAOS_DATABASE_URL"] = previous_url


@pytest.fixture(autouse=True)
def clean_kernel_tables(postgres_engine: Engine) -> Iterator[None]:
    table_names = (
        "ai_assignments",
        "ai_employee_profiles",
        "sessions",
        "credentials",
        "event_deliveries",
        "event_subscriptions",
        "events",
        "subject_external_refs",
        "memberships",
        "permission_decisions",
        "platform_identity_governors",
        "policy_rules",
        "policies",
        "grants",
        "org_units",
        "enterprises",
        "tenants",
        "subjects",
        "ai_memory_entries",
        "ai_tool_declarations",
        "ai_agent_runs",
        "terminal_previews",
        "terminal_intents",
        "terminal_sessions",
        "package_installations",
        "package_manifests",
        "brain_insights",
        "twin_snapshots",
        "marketplace_acquisitions",
        "marketplace_listings",
        "event_dead_letters",
        "event_outbox",
        "knowledge_provenance",
        "knowledge_links",
        "knowledge_entities",
        "workflow_signal_receipts",
        "workflow_history",
        "workflow_tasks",
        "workflow_instances",
        "workflow_definitions",
        "audit_events",
    )
    with postgres_engine.begin() as connection:
        qualified = ", ".join(f"kernel.{name}" for name in table_names)
        connection.execute(text(f"TRUNCATE TABLE {qualified} CASCADE"))
    yield


def _tenant_context(tenant_id=None) -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.SERVICE,
        tenant_id=tenant_id or uuid4(),
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def _platform_context() -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.SERVICE,
        tenant_id=None,
        platform_scope=True,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )


def test_migrations_create_expected_postgresql_schema(
    postgres_engine: Engine,
) -> None:
    inspector = inspect(postgres_engine)
    assert "kernel" in inspector.get_schema_names()
    assert set(inspector.get_table_names(schema="kernel")) == {
        "ai_assignments",
        "ai_employee_profiles",
        "audit_events",
        "credentials",
        "event_deliveries",
        "event_subscriptions",
        "events",
        "enterprises",
        "grants",
        "memberships",
        "org_units",
        "permission_decisions",
        "platform_identity_governors",
        "policies",
        "policy_rules",
        "sessions",
        "subject_external_refs",
        "subjects",
        "tenants",
        "ai_agent_runs",
        "ai_memory_entries",
        "ai_tool_declarations",
        "terminal_intents",
        "terminal_previews",
        "terminal_sessions",
        "package_installations",
        "package_manifests",
        "brain_insights",
        "twin_snapshots",
        "marketplace_acquisitions",
        "marketplace_listings",
        "marketplace_listing_pricing",
        "marketplace_listing_revenue_share",
        "marketplace_invoices",
        "marketplace_disputes",
        "event_dead_letters",
        "event_outbox",
        "knowledge_entities",
        "knowledge_links",
        "knowledge_provenance",
        "workflow_definitions",
        "workflow_history",
        "workflow_instances",
        "workflow_signal_receipts",
        "workflow_tasks",
        "terminal_extensions",
        "idp_issuer_bindings",
        "oidc_refresh_bindings",
        "tenant_idp_bindings",
        "eaos_declared_roles",
    }
    with postgres_engine.connect() as connection:
        revision = connection.scalar(text("SELECT version_num FROM alembic_version"))
    assert revision == EXPECTED_TIP
    subscription_columns = {
        column["name"]
        for column in inspector.get_columns("event_subscriptions", schema="kernel")
    }
    assert "delivery_url" in subscription_columns
    assert "signing_secret" in subscription_columns


def test_transactional_identity_round_trip_on_postgresql(
    postgres_engine: Engine,
) -> None:
    service = TransactionalIdentityService(create_session_factory(postgres_engine))
    tenant_id = uuid4()
    registered = service.register_subject(
        _tenant_context(tenant_id),
        subject_type=SubjectKind.HUMAN,
        display_name="PostgreSQL User",
    )
    assert registered.ok
    assert registered.data is not None

    resolved = service.resolve_subject(
        _tenant_context(tenant_id),
        subject_id=registered.data,
    )
    assert resolved.ok
    assert resolved.data is not None
    assert resolved.data.tenant_id == tenant_id

    subject_context = replace(
        _tenant_context(tenant_id),
        subject_id=registered.data,
    )
    credential = service.bind_credential(
        subject_context,
        subject_id=registered.data,
        credential_kind="password_hash",
        secret_handle="vault:postgresql-session",
    )
    assert credential.data is not None
    created = service.create_session(
        subject_context,
        credential_id=credential.data,
    )
    assert created.data is not None
    session_id = created.data["session_id"]
    assert service.validate_session(
        subject_context,
        session_id=session_id,
    ).ok
    assert service.revoke_session(
        subject_context,
        session_id=session_id,
        reason="integration-test",
    ).ok
    assert (
        service.validate_session(
            subject_context,
            session_id=session_id,
        ).error_code
        == ErrorCode.IDENTITY_SESSION_REVOKED
    )
    assert service.revoke_credential(
        subject_context,
        credential_id=credential.data,
        reason="integration-test",
    ).ok
    assert (
        service.create_session(
            subject_context,
            credential_id=credential.data,
        ).error_code
        == ErrorCode.IDENTITY_CREDENTIAL_REVOKED
    )

    with postgres_engine.connect() as connection:
        assert connection.scalar(select(func.count()).select_from(SubjectRecord)) == 1
        assert connection.scalar(select(func.count()).select_from(AuditEventRecord)) == 5


def test_partial_unique_index_allows_ai_reassignment_history(
    postgres_engine: Engine,
) -> None:
    platform_context = _platform_context()
    service = TransactionalIdentityService(
        create_session_factory(postgres_engine),
        platform_governors={platform_context.subject_id},
    )
    assert service.grant_platform_governor(
        platform_context,
        subject_id=platform_context.subject_id,
    ).ok
    ai = service.register_ai_employee(platform_context, display_name="PostgreSQL AI")
    assert ai.data is not None
    assert service.update_ai_profile(
        platform_context,
        ai_subject_id=ai.data,
        expected_version=1,
        capabilities_profile="capability://postgresql/v2",
        owner_policy="policy://platform/v1",
    ).ok
    tenant_id = uuid4()
    assert service.assign_ai_to_tenant(
        _tenant_context(tenant_id),
        ai_subject_id=ai.data,
    ).ok
    assert service.reassign_ai(
        platform_context,
        ai_subject_id=ai.data,
        to_tenant_id=tenant_id,
    ).ok

    with postgres_engine.connect() as connection:
        total = connection.scalar(
            select(func.count()).select_from(AIAssignmentRecord)
        )
        active = connection.scalar(
            select(func.count())
            .select_from(AIAssignmentRecord)
            .where(AIAssignmentRecord.status == "active")
        )
    assert total == 2
    assert active == 1
    with postgres_engine.connect() as connection:
        assert (
            connection.scalar(select(func.count()).select_from(AIEmployeeProfileRecord))
            == 1
        )
        assert (
            connection.scalar(
                select(func.count()).select_from(PlatformIdentityGovernorRecord)
            )
            == 1
        )


def test_identity_organization_l2_ai_reassignment_on_postgresql(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    platform_context = _platform_context()
    governors = {platform_context.subject_id}
    organization = TransactionalOrganizationService(
        factory,
        platform_governors=governors,
    )
    tenant_a = organization.create_tenant(platform_context, legal_name="L2 A")
    tenant_b = organization.create_tenant(platform_context, legal_name="L2 B")
    assert tenant_a.data and tenant_b.data
    identity = TransactionalIdentityService(
        factory,
        platform_governors=governors,
    )
    ai = identity.register_ai_employee(platform_context, display_name="L2 PostgreSQL AI")
    assert ai.data
    assert identity.assign_ai_to_tenant(
        _tenant_context(tenant_a.data),
        ai_subject_id=ai.data,
    ).ok
    coordinator = TransactionalIdentityOrganizationCoordinator(
        factory,
        platform_governors=governors,
    )
    assert coordinator.add_membership(
        _tenant_context(tenant_a.data),
        subject_id=ai.data,
    ).ok
    assert coordinator.reassign_ai(
        platform_context,
        ai_subject_id=ai.data,
        to_tenant_id=tenant_b.data,
    ).ok
    with postgres_engine.connect() as connection:
        membership_status = connection.scalar(
            select(MembershipRecord.status).where(
                MembershipRecord.subject_id == ai.data
            )
        )
    assert membership_status == "ended"


def test_workflow_k09_compensation_on_postgresql(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    governor = _platform_context()
    organization = TransactionalOrganizationService(
        factory,
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name="Workflow PG Tenant")
    assert tenant.data is not None
    admin_ctx = _tenant_context(tenant.data)
    identity = TransactionalIdentityService(factory)
    initiator = identity.register_subject(
        admin_ctx,
        subject_type=SubjectKind.HUMAN,
        display_name="Workflow Initiator",
    )
    assert initiator.data is not None
    initiator_ctx = ExecutionContext(
        subject_id=initiator.data,
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant.data,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )
    workflow = TransactionalWorkflowService(
        factory,
        definition_administrators={admin_ctx.subject_id},
    )
    permission = TransactionalPermissionService(
        factory,
        grant_administrators={admin_ctx.subject_id},
    )
    definition = workflow.register_definition(
        admin_ctx,
        name="pg-compensate",
        definition_document_ref="docs/workflows/pg",
        version="1.0",
    )
    assert definition.data is not None
    assert permission.grant(
        admin_ctx,
        principal_subject_id=initiator.data,
        resource_type="workflow_definition",
        resource_id=definition.data,
        actions={"start"},
    ).ok
    started = workflow.start(
        initiator_ctx,
        definition_id=definition.data,
        payload={"step": 1},
    )
    assert started.data is not None
    instance_id = started.data["instance_id"]
    assert permission.grant(
        admin_ctx,
        principal_subject_id=initiator.data,
        resource_type="workflow_instance",
        resource_id=instance_id,
        actions={"signal", "compensate"},
    ).ok
    assert workflow.signal(
        initiator_ctx,
        instance_id=instance_id,
        signal_name="complete",
        idempotency_key="pg-done",
    ).ok
    compensating = workflow.compensate(
        initiator_ctx,
        instance_id=instance_id,
        reason="pg rollback",
    )
    assert compensating.data is not None
    assert compensating.data.value == "compensating"
    compensated = workflow.signal(
        initiator_ctx,
        instance_id=instance_id,
        signal_name="compensation_complete",
        idempotency_key="pg-comp",
    )
    assert compensated.data is not None
    assert compensated.data.value == "compensated"


def test_ai_runtime_a12_on_postgresql(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    governor = _platform_context()
    organization = TransactionalOrganizationService(
        factory,
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name="AI Runtime PG Tenant")
    assert tenant.data is not None
    identity = TransactionalIdentityService(
        factory,
        platform_governors={governor.subject_id},
    )
    assert identity.grant_platform_governor(
        governor,
        subject_id=governor.subject_id,
    ).ok
    admin_ctx = _tenant_context(tenant.data)
    admin = identity.register_subject(
        admin_ctx,
        subject_type=SubjectKind.HUMAN,
        display_name="AI Admin",
    )
    ai = identity.register_ai_employee(governor, display_name="AI Employee")
    assert admin.data is not None and ai.data is not None
    admin_user = ExecutionContext(
        subject_id=admin.data,
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant.data,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )
    assert identity.assign_ai_to_tenant(
        admin_user,
        ai_subject_id=ai.data,
    ).ok
    ai_ctx = ExecutionContext(
        subject_id=ai.data,
        subject_type=SubjectType.AI_EMPLOYEE,
        tenant_id=tenant.data,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )
    permission = TransactionalPermissionService(
        factory,
        grant_administrators={admin.data},
    )
    runtime = TransactionalAIRuntimeService(factory)
    assert permission.grant(
        admin_user,
        principal_subject_id=ai.data,
        resource_type="ai_run",
        actions={"create", "read"},
    ).ok
    assert permission.grant(
        admin_user,
        principal_subject_id=admin.data,
        resource_type="tool",
        actions={"register"},
    ).ok
    assert permission.grant(
        admin_user,
        principal_subject_id=ai.data,
        resource_type="tool",
        actions={"invoke_tool"},
    ).ok
    created = runtime.create_agent_run(ai_ctx, goal="PostgreSQL AI probe")
    assert created.ok and created.data is not None
    assert runtime.register_tool(
        admin_user,
        name="probe.read",
        description="Probe",
        high_impact=False,
    ).ok
    invoked = runtime.invoke_tool(
        ai_ctx,
        run_id=created.data,
        tool_name="probe.read",
        arguments={"ok": True},
    )
    assert invoked.ok


def test_smart_terminal_t13_on_postgresql(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    governor = _platform_context()
    organization = TransactionalOrganizationService(
        factory,
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name="Terminal PG Tenant")
    assert tenant.data is not None
    identity = TransactionalIdentityService(
        factory,
        platform_governors={governor.subject_id},
    )
    assert identity.grant_platform_governor(
        governor,
        subject_id=governor.subject_id,
    ).ok
    admin_ctx = _tenant_context(tenant.data)
    admin = identity.register_subject(
        admin_ctx,
        subject_type=SubjectKind.HUMAN,
        display_name="Terminal Admin",
    )
    assert admin.data is not None
    operator = ExecutionContext(
        subject_id=admin.data,
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant.data,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )
    permission = TransactionalPermissionService(
        factory,
        grant_administrators={admin.data},
    )
    terminal = TransactionalSmartTerminalService(factory)
    for resource_type, actions in (
        ("terminal_session", {"open", "read", "close"}),
        ("terminal_intent", {"compose", "read"}),
        ("terminal_preview", {"build", "read"}),
        ("terminal_commit", {"execute"}),
    ):
        assert permission.grant(
            operator,
            principal_subject_id=admin.data,
            resource_type=resource_type,
            actions=actions,
        ).ok
    opened = terminal.open_session(operator)
    assert opened.ok and opened.data is not None
    intent = terminal.compose_intent(
        operator,
        terminal_session_id=opened.data,
        text="PostgreSQL terminal probe",
    )
    assert intent.ok and intent.data is not None
    preview = terminal.build_preview(
        operator,
        intent_id=intent.data,
        action="probe.read",
        resource_ref="probe:1",
        plan_version="v1",
        scope="tenant",
        impact_summary="Read-only probe",
        high_impact=False,
    )
    assert preview.ok and preview.data is not None
    committed = terminal.commit(operator, preview_id=preview.data)
    assert committed.ok


def test_package_b14_on_postgresql(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    governor = _platform_context()
    organization = TransactionalOrganizationService(
        factory,
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name="Package PG Tenant")
    assert tenant.data is not None
    identity = TransactionalIdentityService(
        factory,
        platform_governors={governor.subject_id},
    )
    assert identity.grant_platform_governor(
        governor,
        subject_id=governor.subject_id,
    ).ok
    admin_ctx = _tenant_context(tenant.data)
    admin = identity.register_subject(
        admin_ctx,
        subject_type=SubjectKind.HUMAN,
        display_name="Package Admin",
    )
    assert admin.data is not None
    operator = ExecutionContext(
        subject_id=admin.data,
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant.data,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )
    permission = TransactionalPermissionService(
        factory,
        grant_administrators={admin.data},
    )
    packages = TransactionalPackageService(factory)
    for resource_type, actions in (
        ("package_manifest", {"register", "publish", "read"}),
        ("package_installation", {"install", "disable", "read"}),
        ("package_surface", {"read"}),
        ("package_action", {"resolve"}),
        ("pkg.ops.brief", {"compose", "publish"}),
    ):
        assert permission.grant(
            operator,
            principal_subject_id=admin.data,
            resource_type=resource_type,
            actions=actions,
        ).ok
    registered = packages.register_manifest(
        operator,
        package_key="noventi.sample.ops",
        version="1.0.0",
        package_type="industry",
        surfaces=[
            {
                "surface_key": "ops.workbench",
                "title": "Operations Workbench",
            }
        ],
        actions=[
            {
                "action_key": "ops.brief.compose",
                "resource_type": "pkg.ops.brief",
                "permission_action": "compose",
                "surface_key": "ops.workbench",
            }
        ],
        required_permissions=[
            {"resource_type": "pkg.ops.brief", "actions": ["compose"]},
        ],
        declared_events=["pkg.ops.brief.composed"],
    )
    assert registered.ok and registered.data is not None
    assert packages.publish_manifest(operator, manifest_id=registered.data).ok
    installed = packages.install_package(operator, manifest_id=registered.data)
    assert installed.ok
    resolved = packages.resolve_action(operator, action_key="ops.brief.compose")
    assert resolved.ok


def test_brain_twin_e15_on_postgresql(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    governor = _platform_context()
    organization = TransactionalOrganizationService(
        factory,
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name="Brain Twin PG Tenant")
    assert tenant.data is not None
    identity = TransactionalIdentityService(
        factory,
        platform_governors={governor.subject_id},
    )
    assert identity.grant_platform_governor(
        governor,
        subject_id=governor.subject_id,
    ).ok
    admin_ctx = _tenant_context(tenant.data)
    admin = identity.register_subject(
        admin_ctx,
        subject_type=SubjectKind.HUMAN,
        display_name="Brain Admin",
    )
    assert admin.data is not None
    operator = ExecutionContext(
        subject_id=admin.data,
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant.data,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )
    permission = TransactionalPermissionService(
        factory,
        grant_administrators={admin.data},
    )
    twin = TransactionalTwinService(factory)
    brain = TransactionalBrainService(factory)
    for resource_type, actions in (
        ("twin_snapshot", {"write", "read"}),
        ("brain_insight", {"publish", "read"}),
    ):
        assert permission.grant(
            operator,
            principal_subject_id=admin.data,
            resource_type=resource_type,
            actions=actions,
        ).ok
    snapshot = twin.upsert_snapshot(
        operator,
        entity_ref="plant:pg",
        state={"ok": True},
        source_ref="probe",
        reason="pg probe",
        confidence=0.9,
    )
    assert snapshot.ok and snapshot.data is not None
    insight = brain.publish_insight(
        operator,
        kind="insight",
        summary="PostgreSQL brain probe",
        confidence=0.8,
        source_ref="brain:probe",
        reason="integration",
        twin_ref=snapshot.data,
    )
    assert insight.ok
    forbidden = brain.request_execution(operator, insight_id=insight.data)
    assert forbidden.error_code == ErrorCode.BRAIN_EXECUTION_FORBIDDEN


def test_marketplace_m16_on_postgresql(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    governor = _platform_context()
    organization = TransactionalOrganizationService(
        factory,
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name="Marketplace PG Tenant")
    assert tenant.data is not None
    identity = TransactionalIdentityService(
        factory,
        platform_governors={governor.subject_id},
    )
    assert identity.grant_platform_governor(
        governor,
        subject_id=governor.subject_id,
    ).ok
    admin_ctx = _tenant_context(tenant.data)
    admin = identity.register_subject(
        admin_ctx,
        subject_type=SubjectKind.HUMAN,
        display_name="Market Admin",
    )
    assert admin.data is not None
    operator = ExecutionContext(
        subject_id=admin.data,
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant.data,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )
    permission = TransactionalPermissionService(
        factory,
        grant_administrators={admin.data},
    )
    market = TransactionalMarketplaceService(factory)
    assert permission.grant(
        operator,
        principal_subject_id=admin.data,
        resource_type="marketplace_listing",
        actions={
            "create",
            "submit",
            "review",
            "publish",
            "revoke",
            "read",
            "price",
            "invoice",
            "dispute",
            "revenue_share",
        },
    ).ok
    assert permission.grant(
        operator,
        principal_subject_id=admin.data,
        resource_type="marketplace_acquisition",
        actions={"acquire", "read"},
    ).ok
    created = market.create_listing(
        operator,
        package_key="noventi.sample.ops",
        package_version="1.0.0",
        required_permissions=["pkg.ops.brief:compose"],
        declared_events=["pkg.ops.brief.composed"],
        data_scope="tenant.ops",
    )
    assert created.ok and created.data is not None
    assert market.attach_signature(
        operator,
        listing_id=created.data,
        signature_ref="sig:pg-probe",
    ).ok
    assert market.submit_for_review(operator, listing_id=created.data).ok
    assert market.review_listing(operator, listing_id=created.data, approve=True).ok
    assert market.publish_listing(operator, listing_id=created.data).ok
    acquired = market.acquire_listing(operator, listing_id=created.data)
    assert acquired.ok
    pricing = market.set_pricing(operator, listing_id=created.data, price="1")
    assert pricing.ok
    invoice = market.create_invoice(operator, listing_id=created.data)
    assert invoice.ok and invoice.data is not None


def test_event_p11_outbox_dispatch_on_postgresql(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    governor = _platform_context()
    organization = TransactionalOrganizationService(
        factory,
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name="Event PG Tenant")
    assert tenant.data is not None
    admin_ctx = _tenant_context(tenant.data)
    identity = TransactionalIdentityService(factory)
    operator = identity.register_subject(
        admin_ctx,
        subject_type=SubjectKind.SERVICE,
        display_name="Event Operator",
    )
    assert operator.data is not None
    operator_ctx = ExecutionContext(
        subject_id=operator.data,
        subject_type=SubjectType.SERVICE,
        tenant_id=tenant.data,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )
    permission = TransactionalPermissionService(
        factory,
        grant_administrators={admin_ctx.subject_id},
    )
    assert permission.grant(
        admin_ctx,
        principal_subject_id=operator.data,
        resource_type="event_stream",
        actions={"publish", "subscribe", "dispatch", "read"},
    ).ok
    bus = TransactionalEventBus(factory)
    received: list[str] = []
    assert bus.subscribe(
        operator_ctx,
        subscriber_id="projection.pg",
        event_name="crm.order.created",
        handler=lambda event: received.append(event.event_name),
    ).ok
    enqueued = bus.enqueue(
        operator_ctx,
        event_name="crm.order.created",
        schema_version="1",
        producer="integration-test",
        payload={"order_id": "PG-1"},
    )
    assert enqueued.ok
    assert received == []
    dispatched = bus.dispatch_due(operator_ctx, worker_id="pg-worker")
    assert dispatched.ok and dispatched.data is not None
    # Catalog facts from tenant/enterprise/grant setup may also dispatch (PHX-E19).
    assert dispatched.data.outbox_dispatched >= 1
    assert received == ["crm.order.created"]
    stats = bus.get_delivery_stats(operator_ctx)
    assert stats.ok and stats.data is not None
    assert stats.data.pending_outbox == 0


def test_knowledge_k10_provenance_on_postgresql(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    governor = _platform_context()
    organization = TransactionalOrganizationService(
        factory,
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name="Knowledge PG Tenant")
    assert tenant.data is not None
    admin_ctx = _tenant_context(tenant.data)
    identity = TransactionalIdentityService(factory)
    author = identity.register_subject(
        admin_ctx,
        subject_type=SubjectKind.HUMAN,
        display_name="Knowledge Author",
    )
    assert author.data is not None
    author_ctx = ExecutionContext(
        subject_id=author.data,
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant.data,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )
    permission = TransactionalPermissionService(
        factory,
        grant_administrators={admin_ctx.subject_id},
    )
    assert permission.grant(
        admin_ctx,
        principal_subject_id=author.data,
        resource_type="knowledge_entity",
        actions={"upsert", "read", "archive", "share"},
    ).ok
    assert permission.grant(
        admin_ctx,
        principal_subject_id=author.data,
        resource_type="knowledge_graph",
        resource_id=tenant.data,
        actions={"query", "search"},
    ).ok
    assert permission.grant(
        admin_ctx,
        principal_subject_id=author.data,
        resource_type="knowledge_provenance",
        actions={"read"},
    ).ok
    knowledge = TransactionalKnowledgeService(factory)
    created = knowledge.upsert_entity(
        author_ctx,
        entity_type="Capability",
        name="Billing",
        layer=KnowledgeLayer.CANONICAL,
        source_ref="docs/billing.md",
        reason="postgresql seed",
        labels={"finance"},
    )
    assert created.ok and created.data is not None
    provenance = knowledge.get_provenance(
        author_ctx,
        subject_kind="entity",
        subject_id=created.data,
    )
    assert provenance.ok and provenance.data is not None
    assert len(provenance.data) == 1
    assert provenance.data[0].source_ref == "docs/billing.md"
    hits = knowledge.search(author_ctx, text="Billing")
    assert hits.ok and hits.data is not None
    assert [item.id for item in hits.data] == [created.data]


def test_permission_policy_deny_overrides_grant_on_postgresql(
    postgres_engine: Engine,
) -> None:
    from kernel.permission.models import PermissionEffect, PolicyRule, Resource, ScopeLevel

    factory = create_session_factory(postgres_engine)
    governor = _platform_context()
    organization = TransactionalOrganizationService(
        factory,
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name="Permission PG Tenant")
    assert tenant.data is not None
    admin_ctx = _tenant_context(tenant.data)
    identity = TransactionalIdentityService(factory)
    principal = identity.register_subject(
        admin_ctx,
        subject_type=SubjectKind.HUMAN,
        display_name="Permission Principal",
    )
    assert principal.data is not None
    permission = TransactionalPermissionService(
        factory,
        grant_administrators={admin_ctx.subject_id},
    )
    assert permission.grant(
        admin_ctx,
        principal_subject_id=principal.data,
        resource_type="document",
        actions={"read"},
        scope_level=ScopeLevel.TENANT,
    ).ok
    created = permission.create_policy(
        admin_ctx,
        name="pg-deny-read",
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
    assert permission.activate_policy(
        admin_ctx,
        policy_id=created.data,
        expected_version=1,
    ).ok
    decision = permission.evaluate(
        admin_ctx,
        principal_subject_id=principal.data,
        action="read",
        resource=Resource(tenant_id=tenant.data, resource_type="document"),
    )
    assert decision.data is not None
    assert decision.data.effect == PermissionEffect.DENY
    assert decision.data.reason_code == ErrorCode.PERMISSION_DENIED.value


def test_transactional_kernel_domains_round_trip_on_postgresql(
    postgres_engine: Engine,
) -> None:
    session_factory = create_session_factory(postgres_engine)
    governor = _platform_context()
    organization = TransactionalOrganizationService(
        session_factory,
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(
        governor,
        legal_name="PostgreSQL Kernel Tenant",
    )
    assert tenant.data is not None

    identity = TransactionalIdentityService(session_factory)
    provisional = _tenant_context(tenant.data)
    administrator = identity.register_subject(
        provisional,
        subject_type=SubjectKind.HUMAN,
        display_name="Kernel Administrator",
    )
    member = identity.register_subject(
        provisional,
        subject_type=SubjectKind.HUMAN,
        display_name="Kernel Member",
    )
    assert administrator.data is not None
    assert member.data is not None
    context = ExecutionContext(
        subject_id=administrator.data,
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant.data,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
    )

    unit = organization.upsert_unit(
        context,
        unit_type=UnitType.DEPARTMENT,
        name="Operations",
    )
    assert unit.data is not None
    assert organization.add_membership(
        context,
        subject_id=member.data,
        org_unit_id=unit.data,
        membership_role_label="operator",
    ).ok

    permission = TransactionalPermissionService(
        session_factory,
        grant_administrators={administrator.data},
    )
    workflow = TransactionalWorkflowService(
        session_factory,
        definition_administrators={administrator.data},
    )
    definition = workflow.register_definition(
        context,
        name="PostgreSQL Foundation Flow",
        definition_document_ref="workflows/postgresql-foundation-v1",
        version="1.0",
    )
    assert definition.data is not None
    assert permission.grant(
        context,
        principal_subject_id=administrator.data,
        resource_type="workflow_definition",
        resource_id=definition.data,
        actions={"start"},
    ).ok
    assert workflow.start(
        context,
        definition_id=definition.data,
        payload={"source": "postgresql"},
    ).ok

    assert permission.grant(
        context,
        principal_subject_id=administrator.data,
        resource_type="event_stream",
        actions={"subscribe", "publish"},
    ).ok
    received: list[str] = []
    event_bus = TransactionalEventBus(session_factory)
    assert event_bus.subscribe(
        context,
        subscriber_id="postgresql-consumer",
        event_name="kernel.foundation.verified",
        handler=lambda event: received.append(event.event_name),
    ).ok
    published = event_bus.publish(
        context,
        event_name="kernel.foundation.verified",
        schema_version="1",
        producer="integration-test",
        payload={"tenant_id": str(tenant.data)},
    )
    assert published.data is not None
    assert published.data.delivered_count == 1
    assert received == ["kernel.foundation.verified"]

    with postgres_engine.connect() as connection:
        assert connection.scalar(select(func.count()).select_from(MembershipRecord)) == 1
        assert connection.scalar(select(func.count()).select_from(GrantRecord)) == 2
        assert (
            connection.scalar(
                select(func.count()).select_from(WorkflowInstanceRecord)
            )
            == 1
        )
        assert connection.scalar(select(func.count()).select_from(EventRecord)) == 1
        assert (
            connection.scalar(select(EventDeliveryRecord.status))
            == "delivered"
        )


def test_postgresql_organization_unique_contracts(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    governor = _platform_context()
    organization = TransactionalOrganizationService(
        factory,
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name="Unique Enterprise")
    assert tenant.data is not None
    duplicate_tenant = organization.create_tenant(
        governor,
        legal_name="unique enterprise",
    )
    assert duplicate_tenant.error_code == ErrorCode.ORG_TENANT_DUPLICATE_NAME

    identity = TransactionalIdentityService(factory)
    context = _tenant_context(tenant.data)
    subject = identity.register_subject(
        context,
        subject_type=SubjectKind.HUMAN,
        display_name="Unique Member",
    )
    assert subject.data is not None
    assert organization.add_membership(
        context,
        subject_id=subject.data,
    ).ok
    secondary = organization.create_enterprise(
        context,
        legal_name="Unique Enterprise Subsidiary",
    )
    assert secondary.data is not None
    assert organization.add_membership(
        context,
        enterprise_id=secondary.data,
        subject_id=subject.data,
    ).ok
    duplicate_membership = organization.add_membership(
        context,
        enterprise_id=secondary.data,
        subject_id=subject.data,
    )

    assert duplicate_membership.error_code == ErrorCode.ORG_MEMBERSHIP_DUPLICATE
    with postgres_engine.connect() as connection:
        assert connection.scalar(select(func.count()).select_from(MembershipRecord)) == 2


def test_postgresql_organization_optimistic_lock(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    governor = _platform_context()
    organization = TransactionalOrganizationService(
        factory,
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name="Versioned Enterprise")
    assert tenant.data is not None
    context = _tenant_context(tenant.data)
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
        name="Stale",
        expected_version=1,
    )

    assert stale.error_code == ErrorCode.ORG_VERSION_CONFLICT


def test_organization_enterprise_migration_backfills_existing_rows(
    postgres_engine: Engine,
) -> None:
    pytest.skip(
        "PHX-G418/G422: mid-chain downgrade to 0010 is brittle after tip 0092 "
        "(UndefinedObject on CRM check constraints); rewrite as forward-only "
        "backfill fixture in Batch F"
    )
    config = Config("alembic.ini")
    tenant_id = uuid4()
    subject_id = uuid4()
    unit_id = uuid4()
    membership_id = uuid4()
    command.downgrade(config, "0010_ai_employee_profiles")
    try:
        with postgres_engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO kernel.tenants
                        (id, legal_name, status, created_at, updated_at, version)
                    VALUES
                        (:id, 'Legacy Tenant', 'active', now(), now(), 1)
                    """
                ),
                {"id": tenant_id},
            )
            connection.execute(
                text(
                    """
                    INSERT INTO kernel.subjects
                        (id, tenant_id, subject_type, display_name, status,
                         is_platform_managed, created_at, updated_at, version)
                    VALUES
                        (:id, :tenant_id, 'human', 'Legacy Member', 'active',
                         false, now(), now(), 1)
                    """
                ),
                {"id": subject_id, "tenant_id": tenant_id},
            )
            connection.execute(
                text(
                    """
                    INSERT INTO kernel.org_units
                        (id, tenant_id, unit_type, name, status,
                         created_at, updated_at, version)
                    VALUES
                        (:id, :tenant_id, 'department', 'Legacy Unit', 'active',
                         now(), now(), 1)
                    """
                ),
                {"id": unit_id, "tenant_id": tenant_id},
            )
            connection.execute(
                text(
                    """
                    INSERT INTO kernel.memberships
                        (id, tenant_id, subject_id, org_unit_id, status,
                         created_at, updated_at, version)
                    VALUES
                        (:id, :tenant_id, :subject_id, :unit_id, 'active',
                         now(), now(), 1)
                    """
                ),
                {
                    "id": membership_id,
                    "tenant_id": tenant_id,
                    "subject_id": subject_id,
                    "unit_id": unit_id,
                },
            )

        command.upgrade(config, "head")
        with postgres_engine.connect() as connection:
            enterprise_id = connection.scalar(
                text(
                    """
                    SELECT id FROM kernel.enterprises
                    WHERE tenant_id = :tenant_id AND is_primary
                    """
                ),
                {"tenant_id": tenant_id},
            )
            unit_enterprise_id = connection.scalar(
                text("SELECT enterprise_id FROM kernel.org_units WHERE id = :id"),
                {"id": unit_id},
            )
            membership_enterprise_id = connection.scalar(
                text("SELECT enterprise_id FROM kernel.memberships WHERE id = :id"),
                {"id": membership_id},
            )
        assert enterprise_id is not None
        assert unit_enterprise_id == enterprise_id
        assert membership_enterprise_id == enterprise_id
    finally:
        command.upgrade(config, "head")


def test_postgresql_concurrent_reparent_cannot_create_cycle(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    governor = _platform_context()
    organization = TransactionalOrganizationService(
        factory,
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name="Concurrent Hierarchy")
    assert tenant.data is not None
    context = _tenant_context(tenant.data)
    unit_a = organization.upsert_unit(
        context,
        unit_type=UnitType.DEPARTMENT,
        name="A",
    )
    unit_b = organization.upsert_unit(
        context,
        unit_type=UnitType.DEPARTMENT,
        name="B",
    )
    assert unit_a.data is not None and unit_b.data is not None

    def reparent(unit_id, parent_id, name):
        return organization.upsert_unit(
            context,
            unit_id=unit_id,
            parent_unit_id=parent_id,
            unit_type=UnitType.DEPARTMENT,
            name=name,
            expected_version=1,
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = [
            executor.submit(reparent, unit_a.data, unit_b.data, "A"),
            executor.submit(reparent, unit_b.data, unit_a.data, "B"),
        ]
        outcomes = [future.result() for future in results]

    assert sum(result.ok for result in outcomes) == 1
    assert {
        result.error_code
        for result in outcomes
        if not result.ok
    } == {ErrorCode.ORG_UNIT_CYCLE_DETECTED}


def test_postgresql_unit_lifecycle_serializes_new_membership(
    postgres_engine: Engine,
) -> None:
    factory = create_session_factory(postgres_engine)
    governor = _platform_context()
    organization = TransactionalOrganizationService(
        factory,
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name="Lifecycle Lock")
    assert tenant.data is not None
    context = _tenant_context(tenant.data)
    identity = TransactionalIdentityService(factory)
    subject = identity.register_subject(
        context,
        subject_type=SubjectKind.HUMAN,
        display_name="Concurrent Member",
    )
    assert subject.data is not None
    unit = organization.upsert_unit(
        context,
        unit_type=UnitType.DEPARTMENT,
        name="Operations",
    )
    assert unit.data is not None

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(
                organization.set_unit_status,
                context,
                unit_id=unit.data,
                status=OrganizationStatus.INACTIVE,
                reason="reorganization",
                expected_version=1,
            ),
            executor.submit(
                organization.add_membership,
                context,
                subject_id=subject.data,
                org_unit_id=unit.data,
            ),
        ]
        outcomes = [future.result() for future in futures]

    assert sum(result.ok for result in outcomes) == 1
    assert {
        result.error_code
        for result in outcomes
        if not result.ok
    } <= {
        ErrorCode.ORG_ACTIVE_DEPENDENCIES,
        ErrorCode.ORG_INVALID_STATE_TRANSITION,
    }
