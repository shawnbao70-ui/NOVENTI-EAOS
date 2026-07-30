"""Transactional SQLAlchemy composition for Smart Terminal commands."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
from kernel.infrastructure.persistence.identity_permission import (
    SQLAlchemyPrincipalEligibility,
)
from kernel.infrastructure.persistence.permission_repository import (
    SQLAlchemyPermissionRepository,
)
from kernel.infrastructure.persistence.smart_terminal_repository import (
    SQLAlchemySmartTerminalRepository,
)
from kernel.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from kernel.infrastructure.persistence.workflow_repository import (
    SQLAlchemyWorkflowRepository,
)
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext
from kernel.shared.errors import ErrorCode
from kernel.shared.results import KernelResult
from kernel.workflow.service import WorkflowService
from smart_terminal.models import (
    ApprovalPresentation,
    CommitReceipt,
    PlanPreview,
    TerminalExtension,
    TerminalIntent,
    TerminalSession,
)
from smart_terminal.service import SmartTerminalService

T = TypeVar("T")


class TransactionalSmartTerminalService:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        *,
        definition_administrators: set[UUID] | frozenset[UUID] | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._definition_administrators = frozenset(definition_administrators or ())

    def open_session(
        self,
        ctx: ExecutionContext,
        *,
        device_trust: str = "trusted",
        claimed_tenant_id: UUID | None = None,
        claimed_subject_id: UUID | None = None,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.open_session(
                ctx,
                device_trust=device_trust,
                claimed_tenant_id=claimed_tenant_id,
                claimed_subject_id=claimed_subject_id,
            ),
        )

    def get_session(
        self,
        ctx: ExecutionContext,
        *,
        terminal_session_id: UUID,
    ) -> KernelResult[TerminalSession]:
        return self._execute(
            ctx,
            lambda service: service.get_session(
                ctx,
                terminal_session_id=terminal_session_id,
            ),
        )

    def close_session(
        self,
        ctx: ExecutionContext,
        *,
        terminal_session_id: UUID,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.close_session(
                ctx,
                terminal_session_id=terminal_session_id,
            ),
        )

    def compose_intent(
        self,
        ctx: ExecutionContext,
        *,
        terminal_session_id: UUID,
        text: str,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.compose_intent(
                ctx,
                terminal_session_id=terminal_session_id,
                text=text,
            ),
        )

    def get_intent(
        self,
        ctx: ExecutionContext,
        *,
        intent_id: UUID,
    ) -> KernelResult[TerminalIntent]:
        return self._execute(
            ctx,
            lambda service: service.get_intent(ctx, intent_id=intent_id),
        )

    def build_preview(
        self,
        ctx: ExecutionContext,
        *,
        intent_id: UUID,
        action: str,
        resource_ref: str,
        plan_version: str,
        scope: str,
        impact_summary: str,
        high_impact: bool = False,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.build_preview(
                ctx,
                intent_id=intent_id,
                action=action,
                resource_ref=resource_ref,
                plan_version=plan_version,
                scope=scope,
                impact_summary=impact_summary,
                high_impact=high_impact,
            ),
        )

    def get_preview(
        self,
        ctx: ExecutionContext,
        *,
        preview_id: UUID,
    ) -> KernelResult[PlanPreview]:
        return self._execute(
            ctx,
            lambda service: service.get_preview(ctx, preview_id=preview_id),
        )

    def request_approval(
        self,
        ctx: ExecutionContext,
        *,
        preview_id: UUID,
        definition_id: UUID,
        approval_subject_id: UUID,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.request_approval(
                ctx,
                preview_id=preview_id,
                definition_id=definition_id,
                approval_subject_id=approval_subject_id,
            ),
        )

    def present_approval(
        self,
        ctx: ExecutionContext,
        *,
        preview_id: UUID,
    ) -> KernelResult[ApprovalPresentation]:
        return self._execute(
            ctx,
            lambda service: service.present_approval(ctx, preview_id=preview_id),
        )

    def commit(
        self,
        ctx: ExecutionContext,
        *,
        preview_id: UUID,
    ) -> KernelResult[CommitReceipt]:
        return self._execute(
            ctx,
            lambda service: service.commit(ctx, preview_id=preview_id),
        )

    def register_extension(
        self,
        ctx: ExecutionContext,
        *,
        extension_key: str,
        version: str,
        signature_ref: str | None = None,
        declared_capabilities: list[str] | None = None,
        declared_actions: list[str] | None = None,
        allowed_surfaces: list[str] | None = None,
        data_scope: str = "",
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.register_extension(
                ctx,
                extension_key=extension_key,
                version=version,
                signature_ref=signature_ref,
                declared_capabilities=declared_capabilities,
                declared_actions=declared_actions,
                allowed_surfaces=allowed_surfaces,
                data_scope=data_scope,
            ),
        )

    def activate_extension(
        self,
        ctx: ExecutionContext,
        *,
        extension_id: UUID,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.activate_extension(
                ctx,
                extension_id=extension_id,
            ),
        )

    def revoke_extension(
        self,
        ctx: ExecutionContext,
        *,
        extension_id: UUID,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.revoke_extension(
                ctx,
                extension_id=extension_id,
            ),
        )

    def list_extensions(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[list[TerminalExtension]]:
        return self._execute(
            ctx,
            lambda service: service.list_extensions(ctx),
        )

    def invoke_extension_action(
        self,
        ctx: ExecutionContext,
        *,
        extension_id: UUID,
        action: str,
        surface: str,
    ) -> KernelResult[dict[str, object]]:
        return self._execute(
            ctx,
            lambda service: service.invoke_extension_action(
                ctx,
                extension_id=extension_id,
                action=action,
                surface=surface,
            ),
        )

    def _execute(
        self,
        ctx: ExecutionContext,
        operation: Callable[[SmartTerminalService], KernelResult[T]],
        *,
        conflict_code: ErrorCode = ErrorCode.COMMON_CONFLICT,
    ) -> KernelResult[T]:
        if ctx.tenant_id is None or ctx.platform_scope:
            return KernelResult.failure(
                ErrorCode.CTX_INVALID,
                "Smart Terminal requires tenant data-plane context",
            )
        try:
            with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
                audit_log = SQLAlchemyAuditLog(
                    unit_of_work.session,
                    tenant_id=ctx.tenant_id,
                )
                permission = PermissionService(
                    repository=SQLAlchemyPermissionRepository(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                    ),
                    audit_log=audit_log,
                    principal_eligibility=SQLAlchemyPrincipalEligibility(
                        unit_of_work.session
                    ),
                )
                workflow = WorkflowService(
                    permission,
                    repository=SQLAlchemyWorkflowRepository(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                    ),
                    audit_log=audit_log,
                    definition_administrators=self._definition_administrators,
                )
                result = operation(
                    SmartTerminalService(
                        permission,
                        workflow,
                        repository=SQLAlchemySmartTerminalRepository(
                            unit_of_work.session,
                            tenant_id=ctx.tenant_id,
                        ),
                        audit_log=audit_log,
                    )
                )
                if not result.ok:
                    if result.error_code in {
                        ErrorCode.PERMISSION_DENIED,
                        ErrorCode.TERMINAL_CONTEXT_ELEVATION_DENIED,
                        ErrorCode.TERMINAL_DEVICE_UNTRUSTED,
                        ErrorCode.TERMINAL_STALE_PREVIEW,
                        ErrorCode.TERMINAL_APPROVAL_INVALID,
                        ErrorCode.TERMINAL_COMMIT_FORBIDDEN,
                        ErrorCode.TERMINAL_SECRET_DENIED,
                    }:
                        unit_of_work.commit()
                    return result
                unit_of_work.commit()
                return result
        except IntegrityError:
            return KernelResult.failure(
                conflict_code,
                "Smart Terminal persistence conflict",
            )
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL,
                "Smart Terminal persistence operation failed",
            )
