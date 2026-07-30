"""PHX-A12 AI Runtime tool governance, memory and approval bridge contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from kernel.workflow.service import WorkflowService
from runtime.ai.models import AgentRunStatus
from runtime.ai.service import AIRuntimeService

ADMIN_ID = uuid4()
AI_ID = uuid4()
APPROVER_ID = uuid4()
HUMAN_ID = uuid4()


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx(
    tenant_id: UUID,
    subject_id: UUID,
    *,
    subject_type: SubjectType = SubjectType.AI_EMPLOYEE,
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


def _services() -> tuple[PermissionService, WorkflowService, AIRuntimeService]:
    permission = PermissionService(
        grant_administrators={ADMIN_ID},
        principal_eligibility=_AllowAll(),
    )
    workflow = WorkflowService(
        permission,
        definition_administrators={ADMIN_ID},
    )
    ai = AIRuntimeService(permission, workflow)
    return permission, workflow, ai


def _bootstrap_run(
    permission: PermissionService,
    ai: AIRuntimeService,
    tenant_id: UUID,
) -> UUID:
    admin = _ctx(tenant_id, ADMIN_ID, subject_type=SubjectType.HUMAN)
    assert permission.grant(
        admin,
        principal_subject_id=AI_ID,
        resource_type="ai_run",
        actions={"create", "read", "request", "commit"},
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=AI_ID,
        resource_type="ai_memory",
        actions={"read", "write"},
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=ADMIN_ID,
        resource_type="tool",
        actions={"register"},
    ).ok
    created = ai.create_agent_run(
        _ctx(tenant_id, AI_ID),
        goal="Draft invoice adjustment",
        plan_summary="read then commit",
    )
    assert created.ok and created.data is not None
    return created.data


def test_tool_invoke_requires_explicit_grant() -> None:
    tenant_id = uuid4()
    permission, _workflow, ai = _services()
    run_id = _bootstrap_run(permission, ai, tenant_id)
    admin = _ctx(tenant_id, ADMIN_ID, subject_type=SubjectType.HUMAN)
    assert ai.register_tool(
        admin,
        name="ledger.read",
        description="Read ledger",
        high_impact=False,
    ).ok
    denied = ai.invoke_tool(
        _ctx(tenant_id, AI_ID),
        run_id=run_id,
        tool_name="ledger.read",
        arguments={"account": "A-1"},
    )
    assert not denied.ok
    assert denied.error_code == ErrorCode.AI_TOOL_DENIED

    assert permission.grant(
        admin,
        principal_subject_id=AI_ID,
        resource_type="tool",
        actions={"invoke_tool"},
    ).ok
    allowed = ai.invoke_tool(
        _ctx(tenant_id, AI_ID),
        run_id=run_id,
        tool_name="ledger.read",
        arguments={"account": "A-1"},
    )
    assert allowed.ok and allowed.data is not None
    assert allowed.data.tool_name == "ledger.read"


def test_high_impact_tool_requires_approval_bridge() -> None:
    tenant_id = uuid4()
    permission, workflow, ai = _services()
    run_id = _bootstrap_run(permission, ai, tenant_id)
    admin = _ctx(tenant_id, ADMIN_ID, subject_type=SubjectType.HUMAN)
    assert ai.register_tool(
        admin,
        name="ledger.commit",
        description="Commit ledger write",
        high_impact=True,
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=AI_ID,
        resource_type="tool",
        actions={"invoke_tool"},
    ).ok
    blocked = ai.invoke_tool(
        _ctx(tenant_id, AI_ID),
        run_id=run_id,
        tool_name="ledger.commit",
        arguments={"amount": 10},
    )
    assert not blocked.ok
    assert blocked.error_code == ErrorCode.AI_APPROVAL_REQUIRED

    definition = workflow.register_definition(
        admin,
        name="ai-approval",
        definition_document_ref="workflows/ai-approval",
        version="1.0",
    )
    assert definition.data is not None
    assert permission.grant(
        admin,
        principal_subject_id=AI_ID,
        resource_type="workflow_definition",
        resource_id=definition.data,
        actions={"start"},
    ).ok
    requested = ai.request_approval(
        _ctx(tenant_id, AI_ID),
        run_id=run_id,
        definition_id=definition.data,
        approval_subject_id=APPROVER_ID,
        action="tool:ledger.commit",
        resource_ref=f"ai_run:{run_id}",
    )
    assert requested.ok and requested.data is not None
    run = ai.get_agent_run(_ctx(tenant_id, AI_ID), run_id=run_id)
    assert run.data is not None
    assert run.data.status == AgentRunStatus.PENDING_APPROVAL

    assert permission.grant(
        admin,
        principal_subject_id=ADMIN_ID,
        resource_type="workflow_instance",
        resource_id=requested.data,
        actions={"read"},
    ).ok
    instance = workflow.get_instance(
        _ctx(tenant_id, ADMIN_ID, subject_type=SubjectType.HUMAN),
        instance_id=requested.data,
    )
    assert instance.data is not None
    task_id = instance.data.current_task_id
    assert task_id is not None
    assert permission.grant(
        admin,
        principal_subject_id=APPROVER_ID,
        resource_type="workflow_task",
        resource_id=task_id,
        actions={"approve", "reject"},
    ).ok
    assert workflow.approve(
        _ctx(tenant_id, APPROVER_ID, subject_type=SubjectType.HUMAN),
        instance_id=requested.data,
        task_id=task_id,
    ).ok

    invoked = ai.invoke_tool(
        _ctx(tenant_id, AI_ID),
        run_id=run_id,
        tool_name="ledger.commit",
        arguments={"amount": 10},
    )
    assert invoked.ok


def test_commit_action_requires_completed_approval() -> None:
    tenant_id = uuid4()
    permission, workflow, ai = _services()
    run_id = _bootstrap_run(permission, ai, tenant_id)
    admin = _ctx(tenant_id, ADMIN_ID, subject_type=SubjectType.HUMAN)
    definition = workflow.register_definition(
        admin,
        name="ai-commit",
        definition_document_ref="workflows/ai-commit",
        version="1.0",
    )
    assert definition.data is not None
    assert permission.grant(
        admin,
        principal_subject_id=AI_ID,
        resource_type="workflow_definition",
        resource_id=definition.data,
        actions={"start"},
    ).ok
    missing = ai.commit_action(
        _ctx(tenant_id, AI_ID),
        run_id=run_id,
        action="commit",
        resource_ref="ledger:1",
    )
    assert missing.error_code == ErrorCode.AI_APPROVAL_REQUIRED

    requested = ai.request_approval(
        _ctx(tenant_id, AI_ID),
        run_id=run_id,
        definition_id=definition.data,
        approval_subject_id=APPROVER_ID,
        action="commit",
        resource_ref="ledger:1",
    )
    assert requested.data is not None
    assert permission.grant(
        admin,
        principal_subject_id=ADMIN_ID,
        resource_type="workflow_instance",
        resource_id=requested.data,
        actions={"read"},
    ).ok
    instance = workflow.get_instance(
        _ctx(tenant_id, ADMIN_ID, subject_type=SubjectType.HUMAN),
        instance_id=requested.data,
    )
    assert instance.data is not None and instance.data.current_task_id is not None
    assert permission.grant(
        admin,
        principal_subject_id=APPROVER_ID,
        resource_type="workflow_task",
        resource_id=instance.data.current_task_id,
        actions={"approve"},
    ).ok
    assert workflow.approve(
        _ctx(tenant_id, APPROVER_ID, subject_type=SubjectType.HUMAN),
        instance_id=requested.data,
        task_id=instance.data.current_task_id,
    ).ok
    committed = ai.commit_action(
        _ctx(tenant_id, AI_ID),
        run_id=run_id,
        action="commit",
        resource_ref="ledger:1",
    )
    assert committed.ok
    run = ai.get_agent_run(_ctx(tenant_id, AI_ID), run_id=run_id)
    assert run.data is not None
    assert run.data.status == AgentRunStatus.COMPLETED


def test_memory_rejects_secrets_and_is_tenant_scoped() -> None:
    tenant_id = uuid4()
    permission, _workflow, ai = _services()
    run_id = _bootstrap_run(permission, ai, tenant_id)
    secret = ai.write_memory(
        _ctx(tenant_id, AI_ID),
        run_id=run_id,
        key="api_token",
        value={"v": "x"},
    )
    assert secret.error_code == ErrorCode.AI_MEMORY_DENIED
    written = ai.write_memory(
        _ctx(tenant_id, AI_ID),
        run_id=run_id,
        key="draft",
        value={"text": "hello"},
    )
    assert written.ok
    foreign = ai.read_memory(
        _ctx(uuid4(), AI_ID),
        run_id=run_id,
        key="draft",
    )
    assert foreign.error_code == ErrorCode.COMMON_NOT_FOUND


def test_human_subject_cannot_create_ai_run() -> None:
    tenant_id = uuid4()
    permission, _workflow, ai = _services()
    admin = _ctx(tenant_id, ADMIN_ID, subject_type=SubjectType.HUMAN)
    assert permission.grant(
        admin,
        principal_subject_id=HUMAN_ID,
        resource_type="ai_run",
        actions={"create"},
    ).ok
    denied = ai.create_agent_run(
        _ctx(tenant_id, HUMAN_ID, subject_type=SubjectType.HUMAN),
        goal="bypass",
    )
    assert denied.error_code == ErrorCode.AI_RUNTIME_REQUIRED
