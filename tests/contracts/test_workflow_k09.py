"""PHX-K09 Workflow concurrency, SLA, binding and compensation contracts."""

from __future__ import annotations

from datetime import timedelta
from uuid import UUID, uuid4

from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from kernel.workflow.models import WorkflowDefinitionStatus, WorkflowStatus
from kernel.workflow.service import WorkflowService

ADMIN_ID = uuid4()
INITIATOR_ID = uuid4()
APPROVER_ID = uuid4()
ESCALATEE_ID = uuid4()


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx(tenant_id: UUID, subject_id: UUID) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id,
        subject_type=SubjectType.HUMAN,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        tenant_id=tenant_id,
    )


def _services() -> tuple[PermissionService, WorkflowService]:
    permission = PermissionService(
        grant_administrators={ADMIN_ID},
        principal_eligibility=_AllowAll(),
    )
    workflow = WorkflowService(
        permission,
        definition_administrators={ADMIN_ID},
    )
    return permission, workflow


def _start_pending(
    permission: PermissionService,
    workflow: WorkflowService,
    tenant_id: UUID,
    *,
    due_at=None,
    plan_version: str | None = None,
) -> tuple[UUID, UUID]:
    admin = _ctx(tenant_id, ADMIN_ID)
    definition = workflow.register_definition(
        admin,
        name=f"flow-{uuid4()}",
        definition_document_ref="docs/workflows/k09",
        version="1.0",
    )
    assert definition.data is not None
    assert permission.grant(
        admin,
        principal_subject_id=INITIATOR_ID,
        resource_type="workflow_definition",
        resource_id=definition.data,
        actions={"start"},
    ).ok
    started = workflow.start(
        _ctx(tenant_id, INITIATOR_ID),
        definition_id=definition.data,
        payload={},
        approval_subject_id=APPROVER_ID,
        approval_principal_subject_id=INITIATOR_ID,
        approval_action="commit",
        approval_resource_ref="resource:1",
        approval_plan_version=plan_version,
        due_at=due_at,
    )
    assert started.data is not None
    task_id = started.data["task_id"]
    assert task_id is not None
    assert permission.grant(
        admin,
        principal_subject_id=APPROVER_ID,
        resource_type="workflow_task",
        resource_id=task_id,
        actions={"approve", "reject", "escalate"},
    ).ok
    return started.data["instance_id"], task_id


def test_reject_requires_reject_permission_not_approve() -> None:
    tenant_id = uuid4()
    permission, workflow = _services()
    instance_id, task_id = _start_pending(permission, workflow, tenant_id)
    # Revoke escalate/approve by granting only escalate to a different principal path:
    # Approver currently has approve+reject; create a fresh approver with only approve.
    only_approve = uuid4()
    admin = _ctx(tenant_id, ADMIN_ID)
    definition = workflow.register_definition(
        admin,
        name="reject-perm",
        definition_document_ref="docs/workflows/reject",
        version="1.0",
    )
    assert definition.data is not None
    assert permission.grant(
        admin,
        principal_subject_id=INITIATOR_ID,
        resource_type="workflow_definition",
        resource_id=definition.data,
        actions={"start"},
    ).ok
    started = workflow.start(
        _ctx(tenant_id, INITIATOR_ID),
        definition_id=definition.data,
        payload={},
        approval_subject_id=only_approve,
    )
    assert started.data is not None
    task_id = started.data["task_id"]
    assert permission.grant(
        admin,
        principal_subject_id=only_approve,
        resource_type="workflow_task",
        resource_id=task_id,
        actions={"approve"},
    ).ok
    denied = workflow.reject(
        _ctx(tenant_id, only_approve),
        instance_id=started.data["instance_id"],
        task_id=task_id,
        reason="no",
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED


def test_stale_approve_version_conflicts() -> None:
    tenant_id = uuid4()
    permission, workflow = _services()
    instance_id, task_id = _start_pending(permission, workflow, tenant_id)
    stale = workflow.approve(
        _ctx(tenant_id, APPROVER_ID),
        instance_id=instance_id,
        task_id=task_id,
        expected_version=99,
    )
    assert stale.error_code == ErrorCode.WORKFLOW_VERSION_CONFLICT


def test_escalate_and_cancel_contracts() -> None:
    tenant_id = uuid4()
    permission, workflow = _services()
    instance_id, task_id = _start_pending(permission, workflow, tenant_id)
    admin = _ctx(tenant_id, ADMIN_ID)
    escalated = workflow.escalate(
        _ctx(tenant_id, APPROVER_ID),
        instance_id=instance_id,
        task_id=task_id,
        to_subject_id=ESCALATEE_ID,
        reason="need senior review",
    )
    assert escalated.ok
    assert permission.grant(
        admin,
        principal_subject_id=INITIATOR_ID,
        resource_type="workflow_instance",
        resource_id=instance_id,
        actions={"cancel"},
    ).ok
    cancelled = workflow.cancel(
        _ctx(tenant_id, INITIATOR_ID),
        instance_id=instance_id,
        reason="withdrawn",
    )
    assert cancelled.data == WorkflowStatus.CANCELLED


def test_deprecated_definition_cannot_start() -> None:
    tenant_id = uuid4()
    permission, workflow = _services()
    admin = _ctx(tenant_id, ADMIN_ID)
    definition = workflow.register_definition(
        admin,
        name="to-deprecate",
        definition_document_ref="docs/workflows/old",
        version="1.0",
    )
    assert definition.data is not None
    assert workflow.deprecate_definition(admin, definition_id=definition.data).ok
    assert permission.grant(
        admin,
        principal_subject_id=INITIATOR_ID,
        resource_type="workflow_definition",
        resource_id=definition.data,
        actions={"start"},
    ).ok
    started = workflow.start(
        _ctx(tenant_id, INITIATOR_ID),
        definition_id=definition.data,
        payload={},
    )
    assert started.error_code == ErrorCode.WORKFLOW_DEFINITION_INVALID
    stored = workflow._repo.get_definition(definition.data)
    assert stored is not None
    assert stored.status == WorkflowDefinitionStatus.DEPRECATED


def test_overdue_task_cannot_approve() -> None:
    tenant_id = uuid4()
    permission, workflow = _services()
    instance_id, task_id = _start_pending(
        permission,
        workflow,
        tenant_id,
        due_at=ExecutionContext.utc_now() + timedelta(hours=1),
    )
    task = workflow._repo.get_task(task_id)
    assert task is not None
    expected = task.version
    task.due_at = ExecutionContext.utc_now() - timedelta(seconds=1)
    task.version = expected + 1
    workflow._repo.save_task(task, expected_version=expected)
    denied = workflow.approve(
        _ctx(tenant_id, APPROVER_ID),
        instance_id=instance_id,
        task_id=task_id,
    )
    assert denied.error_code == ErrorCode.WORKFLOW_APPROVAL_EXPIRED


def test_compensation_path() -> None:
    tenant_id = uuid4()
    permission, workflow = _services()
    admin = _ctx(tenant_id, ADMIN_ID)
    definition = workflow.register_definition(
        admin,
        name="compensate-flow",
        definition_document_ref="docs/workflows/comp",
        version="1.0",
    )
    assert definition.data is not None
    assert permission.grant(
        admin,
        principal_subject_id=INITIATOR_ID,
        resource_type="workflow_definition",
        resource_id=definition.data,
        actions={"start"},
    ).ok
    started = workflow.start(
        _ctx(tenant_id, INITIATOR_ID),
        definition_id=definition.data,
        payload={},
    )
    assert started.data is not None
    instance_id = started.data["instance_id"]
    assert permission.grant(
        admin,
        principal_subject_id=INITIATOR_ID,
        resource_type="workflow_instance",
        resource_id=instance_id,
        actions={"signal", "compensate"},
    ).ok
    assert workflow.signal(
        _ctx(tenant_id, INITIATOR_ID),
        instance_id=instance_id,
        signal_name="complete",
        idempotency_key="done-1",
    ).ok
    compensating = workflow.compensate(
        _ctx(tenant_id, INITIATOR_ID),
        instance_id=instance_id,
        reason="rollback side effects",
    )
    assert compensating.data == WorkflowStatus.COMPENSATING
    compensated = workflow.signal(
        _ctx(tenant_id, INITIATOR_ID),
        instance_id=instance_id,
        signal_name="compensation_complete",
        idempotency_key="comp-1",
    )
    assert compensated.data == WorkflowStatus.COMPENSATED


def test_plan_version_binding_enforced() -> None:
    tenant_id = uuid4()
    permission, workflow = _services()
    instance_id, task_id = _start_pending(
        permission,
        workflow,
        tenant_id,
        plan_version="plan-v2",
    )
    assert workflow.approve(
        _ctx(tenant_id, APPROVER_ID),
        instance_id=instance_id,
        task_id=task_id,
    ).ok
    ctx = ExecutionContext(
        subject_id=INITIATOR_ID,
        subject_type=SubjectType.HUMAN,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        tenant_id=tenant_id,
        approval_ref=str(instance_id),
    )
    mismatched = workflow.verify_approved_action(
        ctx,
        action="commit",
        resource_ref="resource:1",
        plan_version="plan-v1",
    )
    matched = workflow.verify_approved_action(
        ctx,
        action="commit",
        resource_ref="resource:1",
        plan_version="plan-v2",
    )
    assert mismatched.error_code == ErrorCode.AI_COMMIT_FORBIDDEN
    assert matched.data is True
