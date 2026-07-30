"""Transactional SQLAlchemy composition for Workflow commands."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from kernel.event_bus.domain_emit import DomainEventEmitter
from kernel.infrastructure.persistence.event_repository import SQLAlchemyOutboxWriter
from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
from kernel.infrastructure.persistence.identity_permission import (
    SQLAlchemyPrincipalEligibility,
)
from kernel.infrastructure.persistence.permission_repository import (
    SQLAlchemyPermissionRepository,
)
from kernel.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from kernel.infrastructure.persistence.workflow_repository import (
    SQLAlchemyWorkflowRepository,
)
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext
from kernel.shared.errors import ErrorCode
from kernel.shared.results import KernelResult
from kernel.workflow.models import (
    TaskStatus,
    WorkflowInstance,
    WorkflowStatus,
    WorkflowTask,
)
from kernel.workflow.service import WorkflowService

T = TypeVar("T")


class TransactionalWorkflowService:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        *,
        definition_administrators: set[UUID] | frozenset[UUID] | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._definition_administrators = frozenset(definition_administrators or ())

    def register_definition(
        self,
        ctx: ExecutionContext,
        *,
        name: str,
        definition_document_ref: str,
        version: str,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.register_definition(
                ctx,
                name=name,
                definition_document_ref=definition_document_ref,
                version=version,
            ),
            conflict_code=ErrorCode.WORKFLOW_DEFINITION_CONFLICT,
        )

    def deprecate_definition(
        self,
        ctx: ExecutionContext,
        *,
        definition_id: UUID,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.deprecate_definition(
                ctx,
                definition_id=definition_id,
            ),
        )

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
        return self._execute(
            ctx,
            lambda service: service.start(
                ctx,
                definition_id=definition_id,
                payload=payload,
                business_key=business_key,
                initiator_subject_id=initiator_subject_id,
                approval_subject_id=approval_subject_id,
                approval_principal_subject_id=approval_principal_subject_id,
                approval_action=approval_action,
                approval_resource_ref=approval_resource_ref,
                approval_plan_version=approval_plan_version,
                approval_scope=approval_scope,
                approval_expires_at=approval_expires_at,
                due_at=due_at,
            ),
            conflict_code=ErrorCode.WORKFLOW_BUSINESS_KEY_CONFLICT,
        )

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
        result = self._execute(
            ctx,
            lambda service: service.signal(
                ctx,
                instance_id=instance_id,
                signal_name=signal_name,
                idempotency_key=idempotency_key,
                payload=payload,
                expected_version=expected_version,
            ),
            conflict_code=ErrorCode.WORKFLOW_SIGNAL_CONFLICT,
        )
        if result.error_code != ErrorCode.WORKFLOW_SIGNAL_CONFLICT:
            return result
        # Concurrent same-key inserts may surface as IntegrityError; converge
        # to an idempotent replay when the stored fingerprint matches.
        return self._execute(
            ctx,
            lambda service: service.signal(
                ctx,
                instance_id=instance_id,
                signal_name=signal_name,
                idempotency_key=idempotency_key,
                payload=payload,
                expected_version=expected_version,
            ),
            conflict_code=ErrorCode.WORKFLOW_SIGNAL_CONFLICT,
        )

    def approve(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
        task_id: UUID,
        comment: str | None = None,
        expected_version: int | None = None,
    ) -> KernelResult[WorkflowStatus]:
        return self._execute(
            ctx,
            lambda service: service.approve(
                ctx,
                instance_id=instance_id,
                task_id=task_id,
                comment=comment,
                expected_version=expected_version,
            ),
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
        return self._execute(
            ctx,
            lambda service: service.reject(
                ctx,
                instance_id=instance_id,
                task_id=task_id,
                reason=reason,
                expected_version=expected_version,
            ),
        )

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
        return self._execute(
            ctx,
            lambda service: service.escalate(
                ctx,
                instance_id=instance_id,
                task_id=task_id,
                to_subject_id=to_subject_id,
                reason=reason,
                expected_version=expected_version,
            ),
        )

    def cancel(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[WorkflowStatus]:
        return self._execute(
            ctx,
            lambda service: service.cancel(
                ctx,
                instance_id=instance_id,
                reason=reason,
                expected_version=expected_version,
            ),
        )

    def compensate(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[WorkflowStatus]:
        return self._execute(
            ctx,
            lambda service: service.compensate(
                ctx,
                instance_id=instance_id,
                reason=reason,
                expected_version=expected_version,
            ),
        )

    def get_instance(
        self,
        ctx: ExecutionContext,
        *,
        instance_id: UUID,
    ) -> KernelResult[WorkflowInstance]:
        return self._execute(
            ctx,
            lambda service: service.get_instance(ctx, instance_id=instance_id),
        )

    def list_tasks(
        self,
        ctx: ExecutionContext,
        *,
        assignee_subject_id: UUID | None = None,
        status: TaskStatus | None = None,
        overdue_only: bool = False,
    ) -> KernelResult[list[WorkflowTask]]:
        return self._execute(
            ctx,
            lambda service: service.list_tasks(
                ctx,
                assignee_subject_id=assignee_subject_id,
                status=status,
                overdue_only=overdue_only,
            ),
        )

    def verify_approved_action(
        self,
        ctx: ExecutionContext,
        *,
        action: str,
        resource_ref: str,
        plan_version: str | None = None,
        scope: str | None = None,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.verify_approved_action(
                ctx,
                action=action,
                resource_ref=resource_ref,
                plan_version=plan_version,
                scope=scope,
            ),
        )

    def _execute(
        self,
        ctx: ExecutionContext,
        operation: Callable[[WorkflowService], KernelResult[T]],
        *,
        conflict_code: ErrorCode = ErrorCode.COMMON_CONFLICT,
    ) -> KernelResult[T]:
        try:
            with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
                try:
                    workflow_repository = SQLAlchemyWorkflowRepository(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                        platform_scope=ctx.platform_scope,
                    )
                    permission_repository = SQLAlchemyPermissionRepository(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                        platform_scope=ctx.platform_scope,
                    )
                    audit_log = SQLAlchemyAuditLog(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                        platform_scope=ctx.platform_scope,
                    )
                except ValueError:
                    return KernelResult.failure(
                        ErrorCode.CTX_INVALID,
                        "execution context has an invalid persistence scope",
                    )
                permission = PermissionService(
                    repository=permission_repository,
                    audit_log=audit_log,
                    principal_eligibility=SQLAlchemyPrincipalEligibility(
                        unit_of_work.session
                    ),
                    domain_events=DomainEventEmitter(
                        SQLAlchemyOutboxWriter(unit_of_work.session)
                    ),
                )
                result = operation(
                    WorkflowService(
                        permission,
                        repository=workflow_repository,
                        audit_log=audit_log,
                        definition_administrators=self._definition_administrators,
                        domain_events=DomainEventEmitter(
                            SQLAlchemyOutboxWriter(unit_of_work.session)
                        ),
                    )
                )
                if not result.ok:
                    if result.error_code == ErrorCode.PERMISSION_DENIED:
                        unit_of_work.commit()
                    return result
                unit_of_work.commit()
                return result
        except IntegrityError:
            return KernelResult.failure(
                conflict_code,
                "workflow persistence conflict",
            )
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL,
                "workflow persistence operation failed",
            )
