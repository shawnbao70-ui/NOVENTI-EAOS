"""PHX-T13 Smart Terminal session, preview, approval and commit contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from kernel.workflow.service import WorkflowService
from smart_terminal.models import PreviewStatus
from smart_terminal.service import SmartTerminalService

ADMIN_ID = uuid4()
OPERATOR_ID = uuid4()
APPROVER_ID = uuid4()


class _AllowAll:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx(
    tenant_id: UUID,
    subject_id: UUID,
    *,
    subject_type: SubjectType = SubjectType.HUMAN,
) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id,
        subject_type=subject_type,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        tenant_id=tenant_id,
    )


def _services() -> tuple[PermissionService, WorkflowService, SmartTerminalService]:
    permission = PermissionService(
        grant_administrators={ADMIN_ID},
        principal_eligibility=_AllowAll(),
    )
    workflow = WorkflowService(
        permission,
        definition_administrators={ADMIN_ID},
    )
    terminal = SmartTerminalService(permission, workflow)
    return permission, workflow, terminal


def _grant_terminal(
    permission: PermissionService,
    tenant_id: UUID,
    subject_id: UUID,
) -> None:
    admin = _ctx(tenant_id, ADMIN_ID)
    assert permission.grant(
        admin,
        principal_subject_id=subject_id,
        resource_type="terminal_session",
        actions={"open", "read", "close"},
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=subject_id,
        resource_type="terminal_intent",
        actions={"compose", "read"},
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=subject_id,
        resource_type="terminal_preview",
        actions={"build", "read"},
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=subject_id,
        resource_type="terminal_approval",
        actions={"present", "request"},
    ).ok
    assert permission.grant(
        admin,
        principal_subject_id=subject_id,
        resource_type="terminal_commit",
        actions={"execute"},
    ).ok


def test_client_cannot_elevate_tenant_or_subject() -> None:
    tenant_id = uuid4()
    permission, _workflow, terminal = _services()
    _grant_terminal(permission, tenant_id, OPERATOR_ID)
    denied_tenant = terminal.open_session(
        _ctx(tenant_id, OPERATOR_ID),
        claimed_tenant_id=uuid4(),
    )
    assert denied_tenant.error_code == ErrorCode.TERMINAL_CONTEXT_ELEVATION_DENIED
    denied_subject = terminal.open_session(
        _ctx(tenant_id, OPERATOR_ID),
        claimed_subject_id=uuid4(),
    )
    assert denied_subject.error_code == ErrorCode.TERMINAL_CONTEXT_ELEVATION_DENIED


def test_intent_preview_commit_low_impact() -> None:
    tenant_id = uuid4()
    permission, _workflow, terminal = _services()
    _grant_terminal(permission, tenant_id, OPERATOR_ID)
    operator = _ctx(tenant_id, OPERATOR_ID)
    opened = terminal.open_session(operator)
    assert opened.ok and opened.data is not None
    intent = terminal.compose_intent(
        operator,
        terminal_session_id=opened.data,
        text="Prepare monthly report",
    )
    assert intent.ok and intent.data is not None
    preview = terminal.build_preview(
        operator,
        intent_id=intent.data,
        action="report.generate",
        resource_ref="report:monthly",
        plan_version="v1",
        scope="tenant",
        impact_summary="Generate read-only monthly report",
        high_impact=False,
    )
    assert preview.ok and preview.data is not None
    committed = terminal.commit(operator, preview_id=preview.data)
    assert committed.ok and committed.data is not None
    assert committed.data.verified_against == "permission"
    assert committed.data.approved is False


def test_high_impact_commit_requires_workflow_approval() -> None:
    tenant_id = uuid4()
    permission, workflow, terminal = _services()
    _grant_terminal(permission, tenant_id, OPERATOR_ID)
    admin = _ctx(tenant_id, ADMIN_ID)
    operator = _ctx(tenant_id, OPERATOR_ID)
    opened = terminal.open_session(operator)
    assert opened.data is not None
    intent = terminal.compose_intent(
        operator,
        terminal_session_id=opened.data,
        text="Adjust ledger balance",
    )
    assert intent.data is not None
    preview = terminal.build_preview(
        operator,
        intent_id=intent.data,
        action="ledger.adjust",
        resource_ref="ledger:42",
        plan_version="v1",
        scope="tenant",
        impact_summary="Adjust ledger balance by 100",
        high_impact=True,
    )
    assert preview.data is not None
    blocked = terminal.commit(operator, preview_id=preview.data)
    assert blocked.error_code == ErrorCode.TERMINAL_APPROVAL_INVALID

    definition = workflow.register_definition(
        admin,
        name="terminal-approval",
        definition_document_ref="workflows/terminal-approval",
        version="1.0",
    )
    assert definition.data is not None
    assert permission.grant(
        admin,
        principal_subject_id=OPERATOR_ID,
        resource_type="workflow_definition",
        resource_id=definition.data,
        actions={"start"},
    ).ok
    requested = terminal.request_approval(
        operator,
        preview_id=preview.data,
        definition_id=definition.data,
        approval_subject_id=APPROVER_ID,
    )
    assert requested.ok and requested.data is not None
    assert permission.grant(
        admin,
        principal_subject_id=OPERATOR_ID,
        resource_type="workflow_instance",
        resource_id=requested.data,
        actions={"read"},
    ).ok
    presented = terminal.present_approval(operator, preview_id=preview.data)
    assert presented.ok and presented.data is not None
    assert presented.data.source == "workflow"
    assert presented.data.workflow_status is not None

    assert permission.grant(
        admin,
        principal_subject_id=ADMIN_ID,
        resource_type="workflow_instance",
        resource_id=requested.data,
        actions={"read"},
    ).ok
    instance = workflow.get_instance(admin, instance_id=requested.data)
    assert instance.data is not None and instance.data.current_task_id is not None
    assert permission.grant(
        admin,
        principal_subject_id=APPROVER_ID,
        resource_type="workflow_task",
        resource_id=instance.data.current_task_id,
        actions={"approve"},
    ).ok
    assert workflow.approve(
        _ctx(tenant_id, APPROVER_ID),
        instance_id=requested.data,
        task_id=instance.data.current_task_id,
    ).ok

    committed = terminal.commit(operator, preview_id=preview.data)
    assert committed.ok and committed.data is not None
    assert committed.data.approved is True
    assert committed.data.verified_against == "workflow+permission"


def test_rebuilding_preview_invalidates_prior_active() -> None:
    tenant_id = uuid4()
    permission, _workflow, terminal = _services()
    _grant_terminal(permission, tenant_id, OPERATOR_ID)
    operator = _ctx(tenant_id, OPERATOR_ID)
    opened = terminal.open_session(operator)
    assert opened.data is not None
    intent = terminal.compose_intent(
        operator,
        terminal_session_id=opened.data,
        text="Update customer",
    )
    assert intent.data is not None
    first = terminal.build_preview(
        operator,
        intent_id=intent.data,
        action="customer.update",
        resource_ref="customer:1",
        plan_version="v1",
        scope="tenant",
        impact_summary="Update name",
        high_impact=False,
    )
    assert first.data is not None
    second = terminal.build_preview(
        operator,
        intent_id=intent.data,
        action="customer.update",
        resource_ref="customer:1",
        plan_version="v2",
        scope="tenant",
        impact_summary="Update name and address",
        high_impact=False,
    )
    assert second.data is not None
    stale = terminal.commit(operator, preview_id=first.data)
    assert stale.error_code == ErrorCode.TERMINAL_STALE_PREVIEW
    prior = terminal.get_preview(operator, preview_id=first.data)
    assert prior.data is not None
    assert prior.data.status == PreviewStatus.INVALIDATED


def test_untrusted_device_blocks_high_impact_commit() -> None:
    tenant_id = uuid4()
    permission, _workflow, terminal = _services()
    _grant_terminal(permission, tenant_id, OPERATOR_ID)
    operator = _ctx(tenant_id, OPERATOR_ID)
    opened = terminal.open_session(operator, device_trust="untrusted")
    assert opened.data is not None
    intent = terminal.compose_intent(
        operator,
        terminal_session_id=opened.data,
        text="Delete archive",
    )
    assert intent.data is not None
    preview = terminal.build_preview(
        operator,
        intent_id=intent.data,
        action="archive.delete",
        resource_ref="archive:9",
        plan_version="v1",
        scope="tenant",
        impact_summary="Delete archive permanently",
        high_impact=True,
    )
    assert preview.data is not None
    denied = terminal.commit(operator, preview_id=preview.data)
    assert denied.error_code == ErrorCode.TERMINAL_DEVICE_UNTRUSTED


def test_secrets_rejected_in_intent_text() -> None:
    tenant_id = uuid4()
    permission, _workflow, terminal = _services()
    _grant_terminal(permission, tenant_id, OPERATOR_ID)
    operator = _ctx(tenant_id, OPERATOR_ID)
    opened = terminal.open_session(operator)
    assert opened.data is not None
    denied = terminal.compose_intent(
        operator,
        terminal_session_id=opened.data,
        text="store api_key for vendor",
    )
    assert denied.error_code == ErrorCode.TERMINAL_SECRET_DENIED


def test_cross_tenant_session_not_visible() -> None:
    tenant_a = uuid4()
    tenant_b = uuid4()
    permission, _workflow, terminal = _services()
    _grant_terminal(permission, tenant_a, OPERATOR_ID)
    _grant_terminal(permission, tenant_b, OPERATOR_ID)
    opened = terminal.open_session(_ctx(tenant_a, OPERATOR_ID))
    assert opened.data is not None
    missing = terminal.get_session(
        _ctx(tenant_b, OPERATOR_ID),
        terminal_session_id=opened.data,
    )
    assert missing.error_code == ErrorCode.COMMON_NOT_FOUND
