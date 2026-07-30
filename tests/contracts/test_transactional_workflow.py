"""Workflow SQLAlchemy state-machine, idempotency, and transaction contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy import Engine, create_engine, func, select
from sqlalchemy.pool import StaticPool

from kernel.identity.models import SubjectKind
from kernel.infrastructure.persistence import (
    PermissionDecisionRecord,
    TransactionalIdentityService,
    TransactionalOrganizationService,
    TransactionalPermissionService,
    TransactionalWorkflowService,
    WorkflowHistoryRecord,
    WorkflowInstanceRecord,
    WorkflowSignalReceiptRecord,
    WorkflowTaskRecord,
    create_session_factory,
    metadata,
)
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from kernel.workflow.models import WorkflowStatus


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
    approval_ref: str | None = None,
) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id or uuid4(),
        subject_type=subject_type,
        tenant_id=None if platform else (tenant_id or uuid4()),
        platform_scope=platform,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        approval_ref=approval_ref,
    )


def _foundation(engine: Engine) -> tuple[UUID, ExecutionContext, ExecutionContext]:
    governor = _context(platform=True)
    organization = TransactionalOrganizationService(
        create_session_factory(engine),
        platform_governors={governor.subject_id},
    )
    tenant = organization.create_tenant(governor, legal_name=str(uuid4()))
    assert tenant.data is not None
    identity = TransactionalIdentityService(create_session_factory(engine))
    initial_context = _context(tenant.data)
    initiator = identity.register_subject(
        initial_context,
        subject_type=SubjectKind.HUMAN,
        display_name="Initiator",
    )
    approver = identity.register_subject(
        initial_context,
        subject_type=SubjectKind.HUMAN,
        display_name="Approver",
    )
    assert initiator.data is not None
    assert approver.data is not None
    return (
        tenant.data,
        _context(tenant.data, subject_id=initiator.data),
        _context(tenant.data, subject_id=approver.data),
    )


def _definition_and_start_grant(
    engine: Engine,
    tenant_id: UUID,
    initiator_context: ExecutionContext,
) -> tuple[TransactionalWorkflowService, TransactionalPermissionService, UUID]:
    workflow = TransactionalWorkflowService(
        create_session_factory(engine),
        definition_administrators={initiator_context.subject_id},
    )
    definition = workflow.register_definition(
        initiator_context,
        name="Transactional Flow",
        definition_document_ref="workflows/transactional-v1",
        version="1.0",
    )
    assert definition.data is not None
    permission = TransactionalPermissionService(
        create_session_factory(engine),
        grant_administrators={initiator_context.subject_id},
    )
    assert permission.grant(
        initiator_context,
        principal_subject_id=initiator_context.subject_id,
        resource_type="workflow_definition",
        resource_id=definition.data,
        actions={"start"},
    ).ok
    return workflow, permission, definition.data


def _register_ai(engine: Engine) -> UUID:
    governor = _context(platform=True)
    registered = TransactionalIdentityService(
        create_session_factory(engine),
        platform_governors={governor.subject_id},
    ).register_ai_employee(
        governor,
        display_name="Approval-bound AI",
    )
    assert registered.data is not None
    return registered.data


def test_workflow_schema_has_tenant_composite_foreign_keys() -> None:
    task_table = metadata.tables["kernel.workflow_tasks"]
    receipt_table = metadata.tables["kernel.workflow_signal_receipts"]
    task_keys = {
        tuple(element.parent.name for element in constraint.elements)
        for constraint in task_table.foreign_key_constraints
    }
    receipt_keys = {
        tuple(element.parent.name for element in constraint.elements)
        for constraint in receipt_table.foreign_key_constraints
    }
    assert ("instance_id", "tenant_id") in task_keys
    assert ("instance_id", "tenant_id") in receipt_keys


def test_transactional_workflow_start_and_idempotent_signal() -> None:
    engine = _engine()
    tenant_id, initiator_context, _ = _foundation(engine)
    workflow, permission, definition_id = _definition_and_start_grant(
        engine,
        tenant_id,
        initiator_context,
    )
    started = workflow.start(
        initiator_context,
        definition_id=definition_id,
        payload={"source": "test"},
    )
    assert started.data is not None
    instance_id = started.data["instance_id"]
    assert isinstance(instance_id, UUID)
    assert permission.grant(
        initiator_context,
        principal_subject_id=initiator_context.subject_id,
        resource_type="workflow_instance",
        resource_id=instance_id,
        actions={"signal"},
    ).ok
    first = workflow.signal(
        initiator_context,
        instance_id=instance_id,
        signal_name="complete",
        idempotency_key="complete-1",
        payload={"result": "ok"},
    )
    replay = workflow.signal(
        initiator_context,
        instance_id=instance_id,
        signal_name="complete",
        idempotency_key="complete-1",
        payload={"result": "ok"},
    )
    assert first.data == WorkflowStatus.COMPLETED
    assert replay.data == WorkflowStatus.COMPLETED

    with engine.connect() as connection:
        assert (
            connection.scalar(
                select(func.count()).select_from(WorkflowSignalReceiptRecord)
            )
            == 1
        )
        assert (
            connection.scalar(select(func.count()).select_from(WorkflowHistoryRecord))
            == 2
        )


def test_permission_denial_is_audited_without_workflow_instance() -> None:
    engine = _engine()
    tenant_id, initiator_context, _ = _foundation(engine)
    workflow = TransactionalWorkflowService(
        create_session_factory(engine),
        definition_administrators={initiator_context.subject_id},
    )
    definition = workflow.register_definition(
        initiator_context,
        name="Denied Flow",
        definition_document_ref="workflows/denied-v1",
        version="1.0",
    )
    assert definition.data is not None
    denied = workflow.start(
        initiator_context,
        definition_id=definition.data,
        payload={},
    )
    assert not denied.ok
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    with engine.connect() as connection:
        assert (
            connection.scalar(select(func.count()).select_from(WorkflowInstanceRecord))
            == 0
        )
        assert (
            connection.scalar(
                select(func.count()).select_from(PermissionDecisionRecord)
            )
            == 1
        )


def test_approval_updates_task_and_instance_atomically() -> None:
    engine = _engine()
    tenant_id, initiator_context, approver_context = _foundation(engine)
    workflow, permission, definition_id = _definition_and_start_grant(
        engine,
        tenant_id,
        initiator_context,
    )
    started = workflow.start(
        initiator_context,
        definition_id=definition_id,
        payload={},
        approval_subject_id=approver_context.subject_id,
    )
    assert started.data is not None
    instance_id = started.data["instance_id"]
    task_id = started.data["task_id"]
    assert isinstance(instance_id, UUID)
    assert isinstance(task_id, UUID)
    assert permission.grant(
        initiator_context,
        principal_subject_id=approver_context.subject_id,
        resource_type="workflow_task",
        resource_id=task_id,
        actions={"approve", "reject", "escalate"},
    ).ok
    approved = workflow.approve(
        approver_context,
        instance_id=instance_id,
        task_id=task_id,
        comment="approved",
    )
    assert approved.data == WorkflowStatus.APPROVED

    with engine.connect() as connection:
        assert connection.scalar(
            select(WorkflowInstanceRecord.status).where(
                WorkflowInstanceRecord.id == instance_id
            )
        ) == "approved"
        assert connection.scalar(
            select(WorkflowTaskRecord.status).where(WorkflowTaskRecord.id == task_id)
        ) == "approved"


def test_transactional_ai_commit_requires_bound_completed_approval() -> None:
    engine = _engine()
    tenant_id, initiator_context, approver_context = _foundation(engine)
    ai_subject_id = _register_ai(engine)
    workflow, permission, definition_id = _definition_and_start_grant(
        engine,
        tenant_id,
        initiator_context,
    )
    started = workflow.start(
        initiator_context,
        definition_id=definition_id,
        payload={"action": "high-impact-write"},
        approval_subject_id=approver_context.subject_id,
        approval_principal_subject_id=ai_subject_id,
        approval_action="commit",
        approval_resource_ref="ledger:123",
    )
    assert started.data is not None
    instance_id = started.data["instance_id"]
    task_id = started.data["task_id"]
    ai_context = _context(
        tenant_id,
        subject_id=ai_subject_id,
        subject_type=SubjectType.AI_EMPLOYEE,
        approval_ref=str(instance_id),
    )

    pending = workflow.verify_approved_action(
        ai_context,
        action="commit",
        resource_ref="ledger:123",
    )
    assert pending.error_code == ErrorCode.AI_COMMIT_FORBIDDEN
    assert permission.grant(
        initiator_context,
        principal_subject_id=approver_context.subject_id,
        resource_type="workflow_task",
        resource_id=task_id,
        actions={"approve", "reject", "escalate"},
    ).ok
    assert workflow.approve(
        approver_context,
        instance_id=instance_id,
        task_id=task_id,
    ).ok

    approved = workflow.verify_approved_action(
        ai_context,
        action="commit",
        resource_ref="ledger:123",
    )
    wrong_resource = workflow.verify_approved_action(
        ai_context,
        action="commit",
        resource_ref="ledger:999",
    )
    other_ai = workflow.verify_approved_action(
        _context(
            tenant_id,
            subject_id=uuid4(),
            subject_type=SubjectType.AI_EMPLOYEE,
            approval_ref=str(instance_id),
        ),
        action="commit",
        resource_ref="ledger:123",
    )
    assert approved.data is True
    assert wrong_resource.error_code == ErrorCode.AI_COMMIT_FORBIDDEN
    assert other_ai.error_code == ErrorCode.AI_COMMIT_FORBIDDEN


def test_transactional_rejected_approval_blocks_ai_commit() -> None:
    engine = _engine()
    tenant_id, initiator_context, approver_context = _foundation(engine)
    ai_subject_id = _register_ai(engine)
    workflow, permission, definition_id = _definition_and_start_grant(
        engine,
        tenant_id,
        initiator_context,
    )
    started = workflow.start(
        initiator_context,
        definition_id=definition_id,
        payload={},
        approval_subject_id=approver_context.subject_id,
        approval_principal_subject_id=ai_subject_id,
        approval_action="commit",
        approval_resource_ref="ledger:123",
    )
    assert started.data is not None
    instance_id = started.data["instance_id"]
    task_id = started.data["task_id"]
    assert permission.grant(
        initiator_context,
        principal_subject_id=approver_context.subject_id,
        resource_type="workflow_task",
        resource_id=task_id,
        actions={"approve", "reject", "escalate"},
    ).ok
    rejected = workflow.reject(
        approver_context,
        instance_id=instance_id,
        task_id=task_id,
        reason="risk too high",
    )
    assert rejected.data == WorkflowStatus.REJECTED
    gate = workflow.verify_approved_action(
        _context(
            tenant_id,
            subject_id=ai_subject_id,
            subject_type=SubjectType.AI_EMPLOYEE,
            approval_ref=str(instance_id),
        ),
        action="commit",
        resource_ref="ledger:123",
    )
    assert gate.error_code == ErrorCode.WORKFLOW_APPROVAL_REJECTED
