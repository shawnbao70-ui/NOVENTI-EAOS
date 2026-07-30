"""Transactional SQLAlchemy composition for AI Runtime commands."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from eaos_platform.knowledge.models import KnowledgeEntity
from eaos_platform.knowledge.service import KnowledgeService
from kernel.infrastructure.persistence.ai_runtime_repository import (
    SQLAlchemyAIRuntimeRepository,
)
from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
from kernel.infrastructure.persistence.identity_permission import (
    SQLAlchemyPrincipalEligibility,
)
from kernel.infrastructure.persistence.knowledge_repository import (
    SQLAlchemyKnowledgeRepository,
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
from kernel.workflow.service import WorkflowService
from runtime.ai.models import AgentRun, MemoryEntry, ToolInvocationResult
from runtime.ai.service import AIRuntimeService

T = TypeVar("T")


class TransactionalAIRuntimeService:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        *,
        definition_administrators: set[UUID] | frozenset[UUID] | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._definition_administrators = frozenset(definition_administrators or ())

    def create_agent_run(
        self,
        ctx: ExecutionContext,
        *,
        goal: str,
        plan_summary: str = "",
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.create_agent_run(
                ctx,
                goal=goal,
                plan_summary=plan_summary,
            ),
        )

    def get_agent_run(
        self,
        ctx: ExecutionContext,
        *,
        run_id: UUID,
    ) -> KernelResult[AgentRun]:
        return self._execute(
            ctx,
            lambda service: service.get_agent_run(ctx, run_id=run_id),
        )

    def register_tool(
        self,
        ctx: ExecutionContext,
        *,
        name: str,
        description: str,
        high_impact: bool = False,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.register_tool(
                ctx,
                name=name,
                description=description,
                high_impact=high_impact,
            ),
            conflict_code=ErrorCode.COMMON_CONFLICT,
        )

    def invoke_tool(
        self,
        ctx: ExecutionContext,
        *,
        run_id: UUID,
        tool_name: str,
        arguments: Mapping[str, Any] | None = None,
        plan_version: str | None = None,
        scope: str | None = None,
    ) -> KernelResult[ToolInvocationResult]:
        return self._execute(
            ctx,
            lambda service: service.invoke_tool(
                ctx,
                run_id=run_id,
                tool_name=tool_name,
                arguments=arguments,
                plan_version=plan_version,
                scope=scope,
            ),
        )

    def write_memory(
        self,
        ctx: ExecutionContext,
        *,
        run_id: UUID,
        key: str,
        value: Mapping[str, Any],
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.write_memory(
                ctx,
                run_id=run_id,
                key=key,
                value=value,
            ),
        )

    def read_memory(
        self,
        ctx: ExecutionContext,
        *,
        run_id: UUID,
        key: str,
    ) -> KernelResult[MemoryEntry]:
        return self._execute(
            ctx,
            lambda service: service.read_memory(ctx, run_id=run_id, key=key),
        )

    def access_knowledge(
        self,
        ctx: ExecutionContext,
        *,
        run_id: UUID,
        entity_id: UUID,
    ) -> KernelResult[KnowledgeEntity]:
        return self._execute(
            ctx,
            lambda service: service.access_knowledge(
                ctx,
                run_id=run_id,
                entity_id=entity_id,
            ),
        )

    def request_approval(
        self,
        ctx: ExecutionContext,
        *,
        run_id: UUID,
        definition_id: UUID,
        approval_subject_id: UUID,
        action: str,
        resource_ref: str,
        plan_version: str | None = None,
        scope: str | None = None,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.request_approval(
                ctx,
                run_id=run_id,
                definition_id=definition_id,
                approval_subject_id=approval_subject_id,
                action=action,
                resource_ref=resource_ref,
                plan_version=plan_version,
                scope=scope,
            ),
        )

    def commit_action(
        self,
        ctx: ExecutionContext,
        *,
        run_id: UUID,
        action: str,
        resource_ref: str,
        plan_version: str | None = None,
        scope: str | None = None,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.commit_action(
                ctx,
                run_id=run_id,
                action=action,
                resource_ref=resource_ref,
                plan_version=plan_version,
                scope=scope,
            ),
        )

    def _execute(
        self,
        ctx: ExecutionContext,
        operation: Callable[[AIRuntimeService], KernelResult[T]],
        *,
        conflict_code: ErrorCode = ErrorCode.COMMON_CONFLICT,
    ) -> KernelResult[T]:
        if ctx.tenant_id is None or ctx.platform_scope:
            return KernelResult.failure(
                ErrorCode.CTX_INVALID,
                "AI Runtime requires tenant data-plane context",
            )
        try:
            with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
                audit_log = SQLAlchemyAuditLog(
                    unit_of_work.session,
                    tenant_id=ctx.tenant_id,
                )
                permission_repository = SQLAlchemyPermissionRepository(
                    unit_of_work.session,
                    tenant_id=ctx.tenant_id,
                )
                permission = PermissionService(
                    repository=permission_repository,
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
                knowledge = KnowledgeService(
                    permission,
                    repository=SQLAlchemyKnowledgeRepository(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                    ),
                    audit_log=audit_log,
                )
                result = operation(
                    AIRuntimeService(
                        permission,
                        workflow,
                        repository=SQLAlchemyAIRuntimeRepository(
                            unit_of_work.session,
                            tenant_id=ctx.tenant_id,
                        ),
                        audit_log=audit_log,
                        knowledge_reader=knowledge,
                    )
                )
                if not result.ok:
                    if result.error_code in {
                        ErrorCode.PERMISSION_DENIED,
                        ErrorCode.AI_TOOL_DENIED,
                        ErrorCode.AI_MEMORY_DENIED,
                        ErrorCode.AI_KNOWLEDGE_DENIED,
                        ErrorCode.AI_APPROVAL_REQUIRED,
                        ErrorCode.AI_COMMIT_FORBIDDEN,
                    }:
                        unit_of_work.commit()
                    return result
                unit_of_work.commit()
                return result
        except IntegrityError:
            return KernelResult.failure(conflict_code, "AI Runtime persistence conflict")
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL,
                "AI Runtime persistence operation failed",
            )
