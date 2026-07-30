"""Workflow Kernel service — PHX-K09 approval truth source."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from kernel.permission.models import PermissionEffect, Resource
from kernel.permission.service import PermissionService
from kernel.event_bus.domain_emit import DomainEventEmitter
from kernel.shared.audit import AuditLog, InMemoryAuditLog
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult
from kernel.workflow.models import (
    SignalReceipt,
    TaskStatus,
    WorkflowDefinition,
    WorkflowDefinitionStatus,
    WorkflowHistoryEntry,
    WorkflowInstance,
    WorkflowStatus,
    WorkflowTask,
)
from kernel.workflow.repository import InMemoryWorkflowRepository, WorkflowRepository


class WorkflowService:
    """Tenant-safe workflow state machine with permission and approval gates."""

    def __init__(
        self,
        permission_service: PermissionService,
        repository: WorkflowRepository | None = None,
        audit_log: AuditLog | None = None,
        definition_administrators: set[UUID] | frozenset[UUID] | None = None,
        domain_events: DomainEventEmitter | None = None,
    ) -> None:
        self._permission = permission_service
        self._repo = repository or InMemoryWorkflowRepository()
        self._audit = audit_log or InMemoryAuditLog()
        self._definition_administrators = frozenset(definition_administrators or ())
        self._domain_events = domain_events

    @property
    def audit_log(self) -> AuditLog:
        return self._audit

    def register_definition(
        self,
        ctx: ExecutionContext,
        *,
        name: str,
        definition_document_ref: str,
        version: str,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=not ctx.platform_scope)
            if ctx.subject_id not in self._definition_administrators:
                raise KernelError(
                    ErrorCode.PERMISSION_DENIED,
                    "workflow definition administration authority is required",
                )
            if not name.strip() or not definition_document_ref.strip() or not version.strip():
                raise KernelError(
                    ErrorCode.WORKFLOW_DEFINITION_INVALID,
                    "name, definition_document_ref, and version are required",
                )
            if self._repo.find_definition(
                tenant_id=ctx.tenant_id,
                name=name.strip(),
                version=version.strip(),
            ) is not None:
                raise KernelError(
                    ErrorCode.WORKFLOW_DEFINITION_CONFLICT,
                    "workflow definition name and version already exist in this scope",
                )
            definition = WorkflowDefinition(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                name=name.strip(),
                document_ref=definition_document_ref.strip(),
                version=version.strip(),
                status=WorkflowDefinitionStatus.ACTIVE,
                created_at=datetime.now(timezone.utc),
            )
            self._repo.add_definition(definition)
            audit = self._audit.record(
                ctx,
                action="Workflow.RegisterDefinition",
                resource=f"workflow_definition:{definition.id}",
                result="ok",
            )
            return KernelResult.success(definition.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def deprecate_definition(
        self,
        ctx: ExecutionContext,
        *,
        definition_id: UUID,
    ) -> KernelResult[bool]:
        try:
            require_context(ctx, tenant_data_plane=not ctx.platform_scope)
            if ctx.subject_id not in self._definition_administrators:
                raise KernelError(
                    ErrorCode.PERMISSION_DENIED,
                    "workflow definition administration authority is required",
                )
            definition = self._repo.get_definition(definition_id)
            if definition is None or (
                definition.tenant_id is not None and definition.tenant_id != ctx.tenant_id
            ):
                raise KernelError(
                    ErrorCode.WORKFLOW_DEFINITION_NOT_FOUND,
                    "workflow definition not found",
                )
            if definition.status == WorkflowDefinitionStatus.DEPRECATED:
                return KernelResult.success(True)
            definition.status = WorkflowDefinitionStatus.DEPRECATED
            self._repo.save_definition(definition)
            audit = self._audit.record(
                ctx,
                action="Workflow.DeprecateDefinition",
                resource=f"workflow_definition:{definition.id}",
                result="ok",
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def start(
        self,
        ctx: ExecutionContext,
        *,
        definition_id: UUID,
        payload: dict[str, Any],
        business_key: str | None = None,
        initiator_subject_id: UUID | None = None,
        approval_subject_id: UUID | None = None,
        approval_principal_subject_id: UUID | None = None,
        approval_action: str | None = None,
        approval_resource_ref: str | None = None,
        approval_plan_version: str | None = None,
        approval_scope: str | None = None,
        approval_expires_at: datetime | None = None,
        due_at: datetime | None = None,
    ) -> KernelResult[dict[str, Any]]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            definition = self._repo.get_definition(definition_id)
            if definition is None or (
                definition.tenant_id is not None and definition.tenant_id != ctx.tenant_id
            ):
                raise KernelError(
                    ErrorCode.WORKFLOW_DEFINITION_NOT_FOUND,
                    "workflow definition not found",
                )
            if definition.status != WorkflowDefinitionStatus.ACTIVE:
                raise KernelError(
                    ErrorCode.WORKFLOW_DEFINITION_INVALID,
                    "workflow definition is not active",
                )
            initiator = initiator_subject_id or ctx.subject_id
            if initiator != ctx.subject_id:
                raise KernelError(
                    ErrorCode.PERMISSION_DENIED,
                    "delegated workflow initiation is not supported",
                )
            approval_binding = (
                approval_principal_subject_id,
                approval_action,
                approval_resource_ref,
            )
            if any(value is not None for value in approval_binding) and not all(
                value is not None and (not isinstance(value, str) or value.strip())
                for value in approval_binding
            ):
                raise KernelError(
                    ErrorCode.WORKFLOW_DEFINITION_INVALID,
                    "approval principal, action, and resource must be supplied together",
                )
            if approval_expires_at is not None and approval_expires_at <= datetime.now(
                timezone.utc
            ):
                raise KernelError(
                    ErrorCode.WORKFLOW_APPROVAL_EXPIRED,
                    "approval_expires_at must be in the future",
                )
            if due_at is not None and due_at <= datetime.now(timezone.utc):
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "due_at must be in the future",
                )
            cleaned_key = business_key.strip() if business_key else None
            if cleaned_key:
                existing = self._repo.find_active_by_business_key(
                    tenant_id=ctx.tenant_id,
                    business_key=cleaned_key,
                )
                if existing is not None:
                    raise KernelError(
                        ErrorCode.WORKFLOW_BUSINESS_KEY_CONFLICT,
                        "active workflow already exists for business_key",
                    )
            self._require_permission(
                ctx,
                principal_subject_id=initiator,
                action="start",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="workflow_definition",
                    resource_id=definition_id,
                ),
            )

            now = datetime.now(timezone.utc)
            status = (
                WorkflowStatus.PENDING_APPROVAL
                if approval_subject_id is not None
                else WorkflowStatus.RUNNING
            )
            instance = WorkflowInstance(
                id=uuid4(),
                definition_id=definition_id,
                tenant_id=ctx.tenant_id,
                initiator_subject_id=initiator,
                status=status,
                payload=dict(payload),
                business_key=cleaned_key,
                created_at=now,
                updated_at=now,
                approval_principal_subject_id=approval_principal_subject_id,
                approval_action=approval_action.strip() if approval_action else None,
                approval_resource_ref=(
                    approval_resource_ref.strip() if approval_resource_ref else None
                ),
                approval_plan_version=(
                    approval_plan_version.strip() if approval_plan_version else None
                ),
                approval_scope=approval_scope.strip() if approval_scope else None,
                approval_expires_at=approval_expires_at,
            )
            task: WorkflowTask | None = None
            if approval_subject_id is not None:
                task = WorkflowTask(
                    id=uuid4(),
                    instance_id=instance.id,
                    tenant_id=ctx.tenant_id,
                    assignee_subject_id=approval_subject_id,
                    status=TaskStatus.PENDING,
                    created_at=now,
                    updated_at=now,
                    due_at=due_at,
                )
                instance.current_task_id = task.id
            self._repo.add_instance(instance)
            if task is not None:
                self._repo.add_task(task)
            self._record_history(ctx, instance.id, "started")
            audit = self._audit.record(
                ctx,
                action="Workflow.Start",
                resource=f"workflow_instance:{instance.id}",
                result="ok",
            )
            self._emit(
                ctx,
                event_name="workflow.instance.started",
                payload={
                    "instance_id": str(instance.id),
                    "definition_id": str(instance.definition_id),
                    "version": instance.version,
                    "status": instance.status.value,
                },
            )
            return KernelResult.success(
                {
                    "instance_id": instance.id,
                    "status": instance.status,
                    "task_id": instance.current_task_id,
                },
                audit_id=audit.id,
            )
        except KernelError as err:
            return KernelResult.from_error(err)

    def signal(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
        signal_name: str,
        idempotency_key: str,
        payload: dict[str, Any] | None = None,
        expected_version: int | None = None,
    ) -> KernelResult[WorkflowStatus]:
        try:
            instance = self._require_instance(ctx, instance_id)
            self._require_permission(
                ctx,
                principal_subject_id=ctx.subject_id,
                action="signal",
                resource=self._instance_resource(instance),
            )
            normalized_key = idempotency_key.strip()
            if not normalized_key:
                raise KernelError(
                    ErrorCode.WORKFLOW_IDEMPOTENCY_REQUIRED,
                    "idempotency_key is required",
                )
            fingerprint = self._signal_fingerprint(signal_name, payload or {})
            prior = self._repo.get_signal_receipt(instance.id, normalized_key)
            if prior is not None:
                if prior.request_fingerprint != fingerprint:
                    raise KernelError(
                        ErrorCode.WORKFLOW_SIGNAL_CONFLICT,
                        "idempotency key was already used with a different signal request",
                    )
                audit = self._audit.record(
                    ctx,
                    action="Workflow.Signal",
                    resource=f"workflow_instance:{instance.id}",
                    result="idempotent_replay",
                    details={
                        "signal_name": signal_name,
                        "idempotency_key": normalized_key,
                    },
                )
                return KernelResult.success(prior.resulting_status, audit_id=audit.id)
            if signal_name == "complete":
                if instance.status != WorkflowStatus.RUNNING:
                    raise KernelError(
                        ErrorCode.WORKFLOW_INVALID_STATE,
                        "only a running workflow can be completed",
                    )
                next_status = WorkflowStatus.COMPLETED
                history_action = "completed"
            elif signal_name == "compensation_complete":
                if instance.status != WorkflowStatus.COMPENSATING:
                    raise KernelError(
                        ErrorCode.WORKFLOW_INVALID_STATE,
                        "only a compensating workflow can complete compensation",
                    )
                next_status = WorkflowStatus.COMPENSATED
                history_action = "compensated"
            else:
                raise KernelError(
                    ErrorCode.WORKFLOW_SIGNAL_UNKNOWN,
                    "unsupported workflow signal",
                )
            expected = self._require_expected_version(
                expected_version if expected_version is not None else instance.version
            )
            instance.status = next_status
            self._touch(instance)
            self._repo.save_instance(instance, expected_version=expected)
            self._record_history(ctx, instance.id, history_action, payload or {})
            self._repo.add_signal_receipt(
                SignalReceipt(
                    instance_id=instance.id,
                    tenant_id=instance.tenant_id,
                    idempotency_key=normalized_key,
                    request_fingerprint=fingerprint,
                    resulting_status=instance.status,
                    processed_at=datetime.now(timezone.utc),
                )
            )
            audit = self._audit.record(
                ctx,
                action="Workflow.Signal",
                resource=f"workflow_instance:{instance.id}",
                result="ok",
                details={
                    "signal_name": signal_name,
                    "idempotency_key": normalized_key,
                },
            )
            if history_action == "completed":
                self._emit(
                    ctx,
                    event_name="workflow.instance.completed",
                    payload={
                        "instance_id": str(instance.id),
                        "version": instance.version,
                        "status": instance.status.value,
                    },
                )
            elif history_action == "compensated":
                self._emit(
                    ctx,
                    event_name="workflow.instance.compensated",
                    payload={
                        "instance_id": str(instance.id),
                        "version": instance.version,
                        "status": instance.status.value,
                    },
                )
            return KernelResult.success(instance.status, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def approve(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
        task_id: UUID,
        comment: str | None = None,
        expected_version: int | None = None,
    ) -> KernelResult[WorkflowStatus]:
        return self._decide(
            ctx,
            instance_id=instance_id,
            task_id=task_id,
            approved=True,
            comment=comment,
            expected_version=expected_version,
        )

    def reject(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
        task_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[WorkflowStatus]:
        if not reason or not reason.strip():
            return KernelResult.failure(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "reason is required",
            )
        return self._decide(
            ctx,
            instance_id=instance_id,
            task_id=task_id,
            approved=False,
            comment=reason,
            expected_version=expected_version,
        )

    def _decide(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
        task_id: UUID,
        approved: bool,
        comment: str | None,
        expected_version: int | None,
    ) -> KernelResult[WorkflowStatus]:
        try:
            instance = self._require_instance(ctx, instance_id)
            task = self._require_task(ctx, task_id, instance_id=instance.id)
            if instance.status != WorkflowStatus.PENDING_APPROVAL:
                raise KernelError(
                    ErrorCode.WORKFLOW_INVALID_STATE,
                    "workflow is not awaiting approval",
                )
            if instance.current_task_id != task.id:
                raise KernelError(
                    ErrorCode.WORKFLOW_INVALID_STATE,
                    "task is not the current approval task",
                )
            if task.status != TaskStatus.PENDING:
                raise KernelError(
                    ErrorCode.WORKFLOW_INVALID_STATE,
                    "approval task is already decided",
                )
            if task.assignee_subject_id != ctx.subject_id:
                raise KernelError(
                    ErrorCode.WORKFLOW_TASK_NOT_ASSIGNEE,
                    "subject is not the approval task assignee",
                )
            if task.due_at is not None and task.due_at <= datetime.now(timezone.utc):
                raise KernelError(
                    ErrorCode.WORKFLOW_APPROVAL_EXPIRED,
                    "approval task is overdue",
                )
            permission_action = "approve" if approved else "reject"
            self._require_permission(
                ctx,
                principal_subject_id=ctx.subject_id,
                action=permission_action,
                resource=Resource(
                    tenant_id=instance.tenant_id,
                    resource_type="workflow_task",
                    resource_id=task.id,
                ),
            )

            now = datetime.now(timezone.utc)
            task_expected = self._require_expected_version(
                expected_version if expected_version is not None else task.version
            )
            instance_expected = instance.version
            task.status = TaskStatus.APPROVED if approved else TaskStatus.REJECTED
            task.decision_comment = comment
            task.updated_at = now
            task.version = task_expected + 1
            instance.status = (
                WorkflowStatus.APPROVED if approved else WorkflowStatus.REJECTED
            )
            self._touch(instance, at=now)
            self._repo.save_task(task, expected_version=task_expected)
            self._repo.save_instance(instance, expected_version=instance_expected)
            action = "approved" if approved else "rejected"
            self._record_history(ctx, instance.id, action, {"task_id": str(task.id)})
            audit = self._audit.record(
                ctx,
                action=f"Workflow.{action.title()}",
                resource=f"workflow_task:{task.id}",
                result="ok",
            )
            self._emit(
                ctx,
                event_name=(
                    "workflow.task.approved" if approved else "workflow.task.rejected"
                ),
                payload={
                    "instance_id": str(instance.id),
                    "task_id": str(task.id),
                    "instance_version": instance.version,
                    "task_version": task.version,
                    "instance_status": instance.status.value,
                    "task_status": task.status.value,
                },
            )
            return KernelResult.success(instance.status, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def escalate(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
        task_id: UUID,
        to_subject_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[WorkflowStatus]:
        try:
            if not reason or not reason.strip():
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "reason is required",
                )
            instance = self._require_instance(ctx, instance_id)
            task = self._require_task(ctx, task_id, instance_id=instance.id)
            if instance.status != WorkflowStatus.PENDING_APPROVAL:
                raise KernelError(
                    ErrorCode.WORKFLOW_INVALID_STATE,
                    "only pending-approval workflows can escalate tasks",
                )
            if instance.current_task_id != task.id:
                raise KernelError(
                    ErrorCode.WORKFLOW_INVALID_STATE,
                    "task is not the current approval task",
                )
            if task.status != TaskStatus.PENDING:
                raise KernelError(
                    ErrorCode.WORKFLOW_INVALID_STATE,
                    "only pending tasks can be escalated",
                )
            self._require_permission(
                ctx,
                principal_subject_id=ctx.subject_id,
                action="escalate",
                resource=Resource(
                    tenant_id=instance.tenant_id,
                    resource_type="workflow_task",
                    resource_id=task.id,
                ),
            )
            task_expected = self._require_expected_version(
                expected_version if expected_version is not None else task.version
            )
            task.escalated_from_subject_id = task.assignee_subject_id
            task.assignee_subject_id = to_subject_id
            task.updated_at = datetime.now(timezone.utc)
            task.version = task_expected + 1
            self._repo.save_task(task, expected_version=task_expected)
            self._record_history(
                ctx,
                instance.id,
                "escalated",
                {"to_subject_id": str(to_subject_id), "reason": reason.strip()},
            )
            audit = self._audit.record(
                ctx,
                action="Workflow.Escalate",
                resource=f"workflow_task:{task.id}",
                result="ok",
            )
            self._emit(
                ctx,
                event_name="workflow.task.escalated",
                payload={
                    "instance_id": str(instance.id),
                    "task_id": str(task.id),
                    "to_subject_id": str(to_subject_id),
                    "task_version": task.version,
                },
            )
            return KernelResult.success(instance.status, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def cancel(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[WorkflowStatus]:
        try:
            if not reason or not reason.strip():
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "reason is required",
                )
            instance = self._require_instance(ctx, instance_id)
            if instance.status in {
                WorkflowStatus.COMPLETED,
                WorkflowStatus.CANCELLED,
                WorkflowStatus.REJECTED,
                WorkflowStatus.COMPENSATED,
            }:
                raise KernelError(
                    ErrorCode.WORKFLOW_INVALID_STATE,
                    "workflow cannot be cancelled from its current state",
                )
            try:
                self._require_permission(
                    ctx,
                    principal_subject_id=ctx.subject_id,
                    action="cancel",
                    resource=self._instance_resource(instance),
                )
            except KernelError as err:
                if err.code == ErrorCode.PERMISSION_DENIED:
                    raise KernelError(
                        ErrorCode.WORKFLOW_CANCEL_FORBIDDEN,
                        "cancel is forbidden for this subject",
                    ) from err
                raise
            expected = self._require_expected_version(
                expected_version if expected_version is not None else instance.version
            )
            instance.status = WorkflowStatus.CANCELLED
            self._touch(instance)
            self._repo.save_instance(instance, expected_version=expected)
            if instance.current_task_id is not None:
                task = self._repo.get_task(instance.current_task_id)
                if task is not None and task.status == TaskStatus.PENDING:
                    task_expected = task.version
                    task.status = TaskStatus.CANCELLED
                    task.updated_at = instance.updated_at
                    task.version = task_expected + 1
                    self._repo.save_task(task, expected_version=task_expected)
            self._record_history(
                ctx, instance.id, "cancelled", {"reason": reason.strip()}
            )
            audit = self._audit.record(
                ctx,
                action="Workflow.Cancel",
                resource=f"workflow_instance:{instance.id}",
                result="ok",
            )
            self._emit(
                ctx,
                event_name="workflow.instance.cancelled",
                payload={
                    "instance_id": str(instance.id),
                    "version": instance.version,
                    "status": instance.status.value,
                },
            )
            return KernelResult.success(instance.status, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def compensate(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[WorkflowStatus]:
        try:
            if not reason or not reason.strip():
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "reason is required",
                )
            instance = self._require_instance(ctx, instance_id)
            if instance.status not in {
                WorkflowStatus.COMPLETED,
                WorkflowStatus.APPROVED,
                WorkflowStatus.CANCELLED,
            }:
                raise KernelError(
                    ErrorCode.WORKFLOW_INVALID_STATE,
                    "workflow cannot enter compensation from its current state",
                )
            self._require_permission(
                ctx,
                principal_subject_id=ctx.subject_id,
                action="compensate",
                resource=self._instance_resource(instance),
            )
            expected = self._require_expected_version(
                expected_version if expected_version is not None else instance.version
            )
            instance.status = WorkflowStatus.COMPENSATING
            self._touch(instance)
            self._repo.save_instance(instance, expected_version=expected)
            self._record_history(
                ctx, instance.id, "compensation_started", {"reason": reason.strip()}
            )
            audit = self._audit.record(
                ctx,
                action="Workflow.Compensate",
                resource=f"workflow_instance:{instance.id}",
                result="ok",
            )
            return KernelResult.success(instance.status, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_instance(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
    ) -> KernelResult[WorkflowInstance]:
        try:
            instance = self._require_instance(ctx, instance_id)
            self._require_permission(
                ctx,
                principal_subject_id=ctx.subject_id,
                action="read",
                resource=self._instance_resource(instance),
            )
            return KernelResult.success(instance)
        except KernelError as err:
            return KernelResult.from_error(err)

    def list_tasks(
        self,
        ctx: ExecutionContext,
        *,
        assignee_subject_id: UUID | None = None,
        status: TaskStatus | None = None,
        overdue_only: bool = False,
    ) -> KernelResult[list[WorkflowTask]]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            assignee = assignee_subject_id or ctx.subject_id
            if assignee != ctx.subject_id:
                self._require_permission(
                    ctx,
                    principal_subject_id=ctx.subject_id,
                    action="read_all",
                    resource=Resource(
                        tenant_id=ctx.tenant_id,
                        resource_type="workflow_task",
                    ),
                )
            now = datetime.now(timezone.utc)
            tasks = [
                task
                for task in self._repo.list_tasks(ctx.tenant_id)
                if task.assignee_subject_id == assignee
            ]
            if status is not None:
                tasks = [task for task in tasks if task.status == status]
            if overdue_only:
                tasks = [
                    task
                    for task in tasks
                    if task.status == TaskStatus.PENDING
                    and task.due_at is not None
                    and task.due_at <= now
                ]
            return KernelResult.success(tasks)
        except KernelError as err:
            return KernelResult.from_error(err)

    def verify_approved_action(
        self,
        ctx: ExecutionContext,
        *,
        action: str,
        resource_ref: str,
        plan_version: str | None = None,
        scope: str | None = None,
    ) -> KernelResult[bool]:
        """Enforce ADR-0008 / ADR-0024 before an AI high-impact commit."""

        try:
            require_context(ctx, tenant_data_plane=True)
            if not ctx.approval_ref:
                raise KernelError(
                    ErrorCode.AI_APPROVAL_REQUIRED,
                    "approval_ref is required for a high-impact AI action",
                )
            try:
                instance_id = UUID(ctx.approval_ref)
            except ValueError as exc:
                raise KernelError(
                    ErrorCode.AI_COMMIT_FORBIDDEN,
                    "approval_ref is invalid",
                ) from exc
            instance = self._require_instance(ctx, instance_id)
            if (
                instance.approval_principal_subject_id != ctx.subject_id
                or instance.approval_action != action.strip()
                or instance.approval_resource_ref != resource_ref.strip()
            ):
                raise KernelError(
                    ErrorCode.AI_COMMIT_FORBIDDEN,
                    "approval does not authorize this subject, action, and resource",
                )
            if instance.approval_plan_version is not None:
                if plan_version is None or plan_version.strip() != instance.approval_plan_version:
                    raise KernelError(
                        ErrorCode.AI_COMMIT_FORBIDDEN,
                        "approval plan_version does not match",
                    )
            if instance.approval_scope is not None:
                if scope is None or scope.strip() != instance.approval_scope:
                    raise KernelError(
                        ErrorCode.AI_COMMIT_FORBIDDEN,
                        "approval scope does not match",
                    )
            if (
                instance.approval_expires_at is not None
                and instance.approval_expires_at <= datetime.now(timezone.utc)
            ):
                raise KernelError(
                    ErrorCode.WORKFLOW_APPROVAL_EXPIRED,
                    "approval has expired",
                )
            if instance.status == WorkflowStatus.REJECTED:
                raise KernelError(
                    ErrorCode.WORKFLOW_APPROVAL_REJECTED,
                    "approval was rejected",
                )
            if instance.status != WorkflowStatus.APPROVED:
                raise KernelError(
                    ErrorCode.AI_COMMIT_FORBIDDEN,
                    "approval is not complete",
                )
            return KernelResult.success(True)
        except KernelError as err:
            return KernelResult.from_error(err)

    def _require_instance(
        self,
        ctx: ExecutionContext,
        instance_id: UUID,
    ) -> WorkflowInstance:
        require_context(ctx, tenant_data_plane=True)
        instance = self._repo.get_instance(instance_id)
        if instance is None or instance.tenant_id != ctx.tenant_id:
            raise KernelError(
                ErrorCode.WORKFLOW_INSTANCE_NOT_FOUND,
                "workflow instance not found",
            )
        return instance

    def _require_task(
        self,
        ctx: ExecutionContext,
        task_id: UUID,
        *,
        instance_id: UUID,
    ) -> WorkflowTask:
        task = self._repo.get_task(task_id)
        if (
            task is None
            or task.tenant_id != ctx.tenant_id
            or task.instance_id != instance_id
        ):
            raise KernelError(ErrorCode.WORKFLOW_TASK_NOT_FOUND, "workflow task not found")
        return task

    def _require_permission(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        action: str,
        resource: Resource,
    ) -> None:
        result = self._permission.evaluate(
            ctx,
            principal_subject_id=principal_subject_id,
            action=action,
            resource=resource,
        )
        if not result.ok:
            raise KernelError(
                result.error_code or ErrorCode.PERMISSION_DENIED,
                result.error_message or "permission evaluation failed",
            )
        if result.data is None or result.data.effect != PermissionEffect.ALLOW:
            raise KernelError(ErrorCode.PERMISSION_DENIED, "permission denied")

    def _record_history(
        self,
        ctx: ExecutionContext,
        instance_id: UUID,
        action: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        assert ctx.tenant_id is not None
        self._repo.add_history(
            WorkflowHistoryEntry(
                id=uuid4(),
                instance_id=instance_id,
                tenant_id=ctx.tenant_id,
                action=action,
                subject_id=ctx.subject_id,
                correlation_id=ctx.correlation_id,
                timestamp=datetime.now(timezone.utc),
                details=details or {},
            )
        )

    @staticmethod
    def _signal_fingerprint(signal_name: str, payload: dict[str, Any]) -> str:
        try:
            canonical = json.dumps(
                {"signal_name": signal_name, "payload": payload},
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
        except (TypeError, ValueError) as exc:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "signal payload must be JSON serializable",
            ) from exc
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _instance_resource(instance: WorkflowInstance) -> Resource:
        return Resource(
            tenant_id=instance.tenant_id,
            resource_type="workflow_instance",
            resource_id=instance.id,
        )

    @staticmethod
    def _touch(
        instance: WorkflowInstance,
        *,
        at: datetime | None = None,
    ) -> None:
        instance.updated_at = at or datetime.now(timezone.utc)
        instance.version += 1

    def _emit(
        self,
        ctx: ExecutionContext,
        *,
        event_name: str,
        payload: dict[str, object],
        tenant_id: UUID | None = None,
    ) -> None:
        if self._domain_events is None:
            return
        self._domain_events.enqueue_fact(
            ctx,
            event_name=event_name,
            producer="workflow.kernel",
            payload=payload,
            tenant_id=tenant_id,
        )

    @staticmethod
    def _require_expected_version(expected_version: int | None) -> int:
        if expected_version is None or expected_version < 1:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "expected_version must be a positive integer",
            )
        return expected_version
