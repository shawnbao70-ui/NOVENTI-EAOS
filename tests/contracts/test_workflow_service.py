"""Workflow Kernel contract tests — W-01..W-05 and ADR-0008."""

from __future__ import annotations

from uuid import UUID, uuid4

from kernel.permission.models import Resource
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from kernel.workflow.models import WorkflowStatus
from kernel.workflow.service import WorkflowService

ADMIN_ID = uuid4()
INITIATOR_ID = uuid4()
APPROVER_ID = uuid4()
AI_ID = uuid4()


class _AllowAllPrincipalEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx(
    tenant_id: UUID,
    subject_id: UUID,
    *,
    subject_type: SubjectType = SubjectType.HUMAN,
    approval_ref: str | None = None,
) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id,
        subject_type=subject_type,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        tenant_id=tenant_id,
        approval_ref=approval_ref,
    )


def _services() -> tuple[PermissionService, WorkflowService]:
    permission = PermissionService(
        grant_administrators={ADMIN_ID},
        principal_eligibility=_AllowAllPrincipalEligibility(),
    )
    workflow = WorkflowService(
        permission,
        definition_administrators={ADMIN_ID},
    )
    return permission, workflow


def _definition_and_start_grant(
    permission: PermissionService,
    workflow: WorkflowService,
    tenant_id: UUID,
    initiator_id: UUID = INITIATOR_ID,
) -> UUID:
    admin_ctx = _ctx(tenant_id, ADMIN_ID)
    definition = workflow.register_definition(
        admin_ctx,
        name="Approval Flow",
        definition_document_ref="docs/workflows/approval-v1",
        version="1.0",
    )
    assert definition.ok and definition.data is not None
    grant = permission.grant(
        admin_ctx,
        principal_subject_id=initiator_id,
        resource_type="workflow_definition",
        resource_id=definition.data,
        actions={"start"},
    )
    assert grant.ok
    return definition.data


def _start_approval(
    permission: PermissionService,
    workflow: WorkflowService,
    tenant_id: UUID,
) -> tuple[UUID, UUID]:
    definition_id = _definition_and_start_grant(permission, workflow, tenant_id)
    started = workflow.start(
        _ctx(tenant_id, INITIATOR_ID),
        definition_id=definition_id,
        payload={"action": "high-impact-write"},
        approval_subject_id=APPROVER_ID,
        approval_principal_subject_id=AI_ID,
        approval_action="commit",
        approval_resource_ref="ledger:123",
    )
    assert started.ok and started.data is not None
    instance_id = started.data["instance_id"]
    task_id = started.data["task_id"]
    assert isinstance(instance_id, UUID)
    assert isinstance(task_id, UUID)
    return instance_id, task_id


def _grant_task_approval(
    permission: PermissionService,
    tenant_id: UUID,
    task_id: UUID,
) -> None:
    grant = permission.grant(
        _ctx(tenant_id, ADMIN_ID),
        principal_subject_id=APPROVER_ID,
        resource_type="workflow_task",
        resource_id=task_id,
        actions={"approve", "reject", "escalate"},
    )
    assert grant.ok


def test_w01_start_creates_queryable_pending_instance() -> None:
    tenant_id = uuid4()
    permission, workflow = _services()
    instance_id, task_id = _start_approval(permission, workflow, tenant_id)
    instance = workflow._repo.get_instance(instance_id)
    assert instance is not None
    assert instance.status == WorkflowStatus.PENDING_APPROVAL
    assert instance.current_task_id == task_id


def test_start_without_permission_is_denied() -> None:
    tenant_id = uuid4()
    _, workflow = _services()
    definition = workflow.register_definition(
        _ctx(tenant_id, ADMIN_ID),
        name="Protected Flow",
        definition_document_ref="docs/workflows/protected",
        version="1.0",
    )
    assert definition.data is not None
    started = workflow.start(
        _ctx(tenant_id, INITIATOR_ID),
        definition_id=definition.data,
        payload={},
    )
    assert not started.ok
    assert started.error_code == ErrorCode.PERMISSION_DENIED


def test_definition_name_and_version_are_unique_per_tenant() -> None:
    tenant_id = uuid4()
    _, workflow = _services()
    ctx = _ctx(tenant_id, ADMIN_ID)
    first = workflow.register_definition(
        ctx,
        name="Versioned Flow",
        definition_document_ref="docs/workflows/v1",
        version="1.0",
    )
    assert first.ok
    duplicate = workflow.register_definition(
        ctx,
        name="versioned flow",
        definition_document_ref="docs/workflows/other",
        version="1.0",
    )
    assert not duplicate.ok
    assert duplicate.error_code == ErrorCode.WORKFLOW_DEFINITION_CONFLICT


def test_w02_approve_is_audited_and_transitions_state() -> None:
    tenant_id = uuid4()
    permission, workflow = _services()
    instance_id, task_id = _start_approval(permission, workflow, tenant_id)
    _grant_task_approval(permission, tenant_id, task_id)
    approved = workflow.approve(
        _ctx(tenant_id, APPROVER_ID),
        instance_id=instance_id,
        task_id=task_id,
        comment="approved",
    )
    assert approved.ok
    assert approved.data == WorkflowStatus.APPROVED
    assert approved.audit_id is not None


def test_non_assignee_cannot_approve_even_with_no_grant() -> None:
    tenant_id = uuid4()
    permission, workflow = _services()
    instance_id, task_id = _start_approval(permission, workflow, tenant_id)
    result = workflow.approve(
        _ctx(tenant_id, uuid4()),
        instance_id=instance_id,
        task_id=task_id,
    )
    assert not result.ok
    assert result.error_code == ErrorCode.WORKFLOW_TASK_NOT_ASSIGNEE


def test_w04_ai_commit_requires_completed_approval() -> None:
    tenant_id = uuid4()
    permission, workflow = _services()
    instance_id, task_id = _start_approval(permission, workflow, tenant_id)
    pending_gate = workflow.verify_approved_action(
        _ctx(
            tenant_id,
            AI_ID,
            subject_type=SubjectType.AI_EMPLOYEE,
            approval_ref=str(instance_id),
        ),
        action="commit",
        resource_ref="ledger:123",
    )
    assert not pending_gate.ok
    assert pending_gate.error_code == ErrorCode.AI_COMMIT_FORBIDDEN

    _grant_task_approval(permission, tenant_id, task_id)
    assert workflow.approve(
        _ctx(tenant_id, APPROVER_ID),
        instance_id=instance_id,
        task_id=task_id,
    ).ok
    approved_gate = workflow.verify_approved_action(
        _ctx(
            tenant_id,
            AI_ID,
            subject_type=SubjectType.AI_EMPLOYEE,
            approval_ref=str(instance_id),
        ),
        action="commit",
        resource_ref="ledger:123",
    )
    assert approved_gate.ok


def test_missing_approval_ref_is_denied() -> None:
    tenant_id = uuid4()
    _, workflow = _services()
    gate = workflow.verify_approved_action(
        _ctx(tenant_id, AI_ID, subject_type=SubjectType.AI_EMPLOYEE),
        action="commit",
        resource_ref="ledger:123",
    )
    assert not gate.ok
    assert gate.error_code == ErrorCode.AI_APPROVAL_REQUIRED


def test_w05_rejected_approval_blocks_ai_commit() -> None:
    tenant_id = uuid4()
    permission, workflow = _services()
    instance_id, task_id = _start_approval(permission, workflow, tenant_id)
    _grant_task_approval(permission, tenant_id, task_id)
    rejected = workflow.reject(
        _ctx(tenant_id, APPROVER_ID),
        instance_id=instance_id,
        task_id=task_id,
        reason="risk too high",
    )
    assert rejected.data == WorkflowStatus.REJECTED
    gate = workflow.verify_approved_action(
        _ctx(
            tenant_id,
            AI_ID,
            subject_type=SubjectType.AI_EMPLOYEE,
            approval_ref=str(instance_id),
        ),
        action="commit",
        resource_ref="ledger:123",
    )
    assert not gate.ok
    assert gate.error_code == ErrorCode.WORKFLOW_APPROVAL_REJECTED


def test_approval_cannot_be_reused_by_another_ai_or_resource() -> None:
    tenant_id = uuid4()
    permission, workflow = _services()
    instance_id, task_id = _start_approval(permission, workflow, tenant_id)
    _grant_task_approval(permission, tenant_id, task_id)
    assert workflow.approve(
        _ctx(tenant_id, APPROVER_ID),
        instance_id=instance_id,
        task_id=task_id,
    ).ok

    other_ai = workflow.verify_approved_action(
        _ctx(
            tenant_id,
            uuid4(),
            subject_type=SubjectType.AI_EMPLOYEE,
            approval_ref=str(instance_id),
        ),
        action="commit",
        resource_ref="ledger:123",
    )
    assert not other_ai.ok
    assert other_ai.error_code == ErrorCode.AI_COMMIT_FORBIDDEN

    other_resource = workflow.verify_approved_action(
        _ctx(
            tenant_id,
            AI_ID,
            subject_type=SubjectType.AI_EMPLOYEE,
            approval_ref=str(instance_id),
        ),
        action="commit",
        resource_ref="ledger:999",
    )
    assert not other_resource.ok
    assert other_resource.error_code == ErrorCode.AI_COMMIT_FORBIDDEN


def test_cross_tenant_instance_is_hidden() -> None:
    tenant_id = uuid4()
    permission, workflow = _services()
    instance_id, _ = _start_approval(permission, workflow, tenant_id)
    result = workflow.get_instance(
        _ctx(uuid4(), INITIATOR_ID),
        instance_id=instance_id,
    )
    assert not result.ok
    assert result.error_code == ErrorCode.WORKFLOW_INSTANCE_NOT_FOUND


def test_running_workflow_can_complete_with_signal_permission() -> None:
    tenant_id = uuid4()
    permission, workflow = _services()
    definition_id = _definition_and_start_grant(permission, workflow, tenant_id)
    started = workflow.start(
        _ctx(tenant_id, INITIATOR_ID),
        definition_id=definition_id,
        payload={},
    )
    assert started.data is not None
    instance_id = started.data["instance_id"]
    assert isinstance(instance_id, UUID)
    assert permission.grant(
        _ctx(tenant_id, ADMIN_ID),
        principal_subject_id=INITIATOR_ID,
        resource_type="workflow_instance",
        resource_id=instance_id,
        actions={"signal"},
    ).ok
    completed = workflow.signal(
        _ctx(tenant_id, INITIATOR_ID),
        instance_id=instance_id,
        signal_name="complete",
        idempotency_key="complete-001",
    )
    assert completed.data == WorkflowStatus.COMPLETED


def test_signal_retry_with_same_key_is_idempotent() -> None:
    tenant_id = uuid4()
    permission, workflow = _services()
    definition_id = _definition_and_start_grant(permission, workflow, tenant_id)
    started = workflow.start(
        _ctx(tenant_id, INITIATOR_ID),
        definition_id=definition_id,
        payload={},
    )
    assert started.data is not None
    instance_id = started.data["instance_id"]
    assert isinstance(instance_id, UUID)
    assert permission.grant(
        _ctx(tenant_id, ADMIN_ID),
        principal_subject_id=INITIATOR_ID,
        resource_type="workflow_instance",
        resource_id=instance_id,
        actions={"signal"},
    ).ok
    first = workflow.signal(
        _ctx(tenant_id, INITIATOR_ID),
        instance_id=instance_id,
        signal_name="complete",
        idempotency_key="request-42",
        payload={"source": "test"},
    )
    second = workflow.signal(
        _ctx(tenant_id, INITIATOR_ID),
        instance_id=instance_id,
        signal_name="complete",
        idempotency_key="request-42",
        payload={"source": "test"},
    )
    assert first.data == WorkflowStatus.COMPLETED
    assert second.data == WorkflowStatus.COMPLETED
    assert len(workflow._repo.list_history(instance_id)) == 2  # start + complete


def test_signal_key_reuse_with_different_payload_conflicts() -> None:
    tenant_id = uuid4()
    permission, workflow = _services()
    definition_id = _definition_and_start_grant(permission, workflow, tenant_id)
    started = workflow.start(
        _ctx(tenant_id, INITIATOR_ID),
        definition_id=definition_id,
        payload={},
    )
    assert started.data is not None
    instance_id = started.data["instance_id"]
    assert isinstance(instance_id, UUID)
    assert permission.grant(
        _ctx(tenant_id, ADMIN_ID),
        principal_subject_id=INITIATOR_ID,
        resource_type="workflow_instance",
        resource_id=instance_id,
        actions={"signal"},
    ).ok
    assert workflow.signal(
        _ctx(tenant_id, INITIATOR_ID),
        instance_id=instance_id,
        signal_name="complete",
        idempotency_key="request-42",
        payload={"version": 1},
    ).ok
    conflict = workflow.signal(
        _ctx(tenant_id, INITIATOR_ID),
        instance_id=instance_id,
        signal_name="complete",
        idempotency_key="request-42",
        payload={"version": 2},
    )
    assert not conflict.ok
    assert conflict.error_code == ErrorCode.WORKFLOW_SIGNAL_CONFLICT
