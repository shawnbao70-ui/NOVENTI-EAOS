"""AI Runtime service — PHX-A12 Agent / Tool / Memory / Approval bridge."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping, Protocol
from uuid import UUID, uuid4

from eaos_platform.knowledge.models import KnowledgeEntity
from kernel.permission.models import PermissionEffect, Resource
from kernel.permission.service import PermissionService
from kernel.shared.audit import AuditLog, InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult
from kernel.workflow.service import WorkflowService
from runtime.ai.models import (
    AgentRun,
    AgentRunStatus,
    MemoryEntry,
    ToolDeclaration,
    ToolInvocationResult,
)
from runtime.ai.repository import AIRuntimeRepository, InMemoryAIRuntimeRepository

_SECRET_TOKENS = ("password", "secret", "token", "api_key", "private_key", "credential")
_AI_SUBJECTS = {SubjectType.AI, SubjectType.AI_EMPLOYEE}


class KnowledgeReader(Protocol):
    def get_entity(
        self,
        ctx: ExecutionContext,
        *,
        entity_id: UUID,
    ) -> KernelResult[KnowledgeEntity]: ...


class AIRuntimeService:
    """Governed AI execution surface: runs, tools, memory, approval bridge."""

    def __init__(
        self,
        permission_service: PermissionService,
        workflow_service: WorkflowService,
        repository: AIRuntimeRepository | None = None,
        audit_log: AuditLog | None = None,
        knowledge_reader: KnowledgeReader | None = None,
    ) -> None:
        self._permission = permission_service
        self._workflow = workflow_service
        self._repo = repository or InMemoryAIRuntimeRepository()
        self._audit = audit_log or InMemoryAuditLog()
        self._knowledge = knowledge_reader

    @property
    def audit_log(self) -> AuditLog:
        return self._audit

    def create_agent_run(
        self,
        ctx: ExecutionContext,
        *,
        goal: str,
        plan_summary: str = "",
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_ai_subject(ctx)
            cleaned_goal = goal.strip()
            if not cleaned_goal:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "goal is required",
                )
            self._require_permission(
                ctx,
                action="create",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="ai_run",
                ),
            )
            now = datetime.now(timezone.utc)
            run = AgentRun(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                subject_id=ctx.subject_id,
                goal=cleaned_goal,
                plan_summary=plan_summary.strip(),
                status=AgentRunStatus.PLANNED,
                created_at=now,
                updated_at=now,
            )
            self._repo.add_run(run)
            audit = self._audit.record(
                ctx,
                action="AI.CreateAgentRun",
                resource=f"ai_run:{run.id}",
                result="ok",
                details={"goal": cleaned_goal},
            )
            return KernelResult.success(run.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_agent_run(
        self,
        ctx: ExecutionContext,
        *,
        run_id: UUID,
    ) -> KernelResult[AgentRun]:
        try:
            run = self._require_run(ctx, run_id)
            self._require_permission(
                ctx,
                action="read",
                resource=Resource(
                    tenant_id=run.tenant_id,
                    resource_type="ai_run",
                    resource_id=run.id,
                ),
            )
            return KernelResult.success(run)
        except KernelError as err:
            return KernelResult.from_error(err)

    def register_tool(
        self,
        ctx: ExecutionContext,
        *,
        name: str,
        description: str,
        high_impact: bool = False,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            cleaned = name.strip()
            if not cleaned:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "tool name is required",
                )
            self._require_permission(
                ctx,
                action="register",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="tool",
                ),
            )
            tool = ToolDeclaration(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                name=cleaned,
                description=description.strip(),
                high_impact=high_impact,
                created_at=datetime.now(timezone.utc),
            )
            self._repo.add_tool(tool)
            audit = self._audit.record(
                ctx,
                action="AI.RegisterTool",
                resource=f"tool:{tool.name}",
                result="ok",
                details={"high_impact": high_impact},
            )
            return KernelResult.success(tool.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

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
        try:
            self._require_ai_subject(ctx)
            run = self._require_run(ctx, run_id, writable=True)
            tool = self._repo.get_tool_by_name(
                tenant_id=run.tenant_id,
                name=tool_name,
            )
            if tool is None:
                raise KernelError(
                    ErrorCode.AI_TOOL_DENIED,
                    "tool is not registered",
                )
            self._require_permission(
                ctx,
                action="invoke_tool",
                resource=Resource(
                    tenant_id=run.tenant_id,
                    resource_type="tool",
                    resource_id=tool.id,
                ),
                deny_code=ErrorCode.AI_TOOL_DENIED,
            )
            args = dict(arguments or {})
            self._reject_secrets(args)
            if tool.high_impact:
                self._require_approved(
                    ctx,
                    run=run,
                    action=f"tool:{tool.name}",
                    resource_ref=f"ai_run:{run.id}",
                    plan_version=plan_version,
                    scope=scope,
                )
            expected = run.version
            run.status = AgentRunStatus.RUNNING
            run.updated_at = datetime.now(timezone.utc)
            run.version = expected + 1
            self._repo.save_run(run, expected_version=expected)
            output = {
                "echo": args,
                "tool": tool.name,
                "run_id": str(run.id),
            }
            audit = self._audit.record(
                ctx,
                action="AI.InvokeTool",
                resource=f"tool:{tool.name}",
                result="ok",
                details={
                    "run_id": str(run.id),
                    "high_impact": tool.high_impact,
                    "argument_keys": sorted(args),
                },
            )
            return KernelResult.success(
                ToolInvocationResult(
                    tool_name=tool.name,
                    high_impact=tool.high_impact,
                    output=output,
                ),
                audit_id=audit.id,
            )
        except KernelError as err:
            return KernelResult.from_error(err)

    def write_memory(
        self,
        ctx: ExecutionContext,
        *,
        run_id: UUID,
        key: str,
        value: Mapping[str, Any],
    ) -> KernelResult[UUID]:
        try:
            self._require_ai_subject(ctx)
            run = self._require_run(ctx, run_id, writable=True)
            cleaned_key = key.strip()
            if not cleaned_key:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "memory key is required",
                )
            payload = dict(value)
            self._reject_secrets(payload, key_name=cleaned_key)
            self._require_permission(
                ctx,
                action="write",
                resource=Resource(
                    tenant_id=run.tenant_id,
                    resource_type="ai_memory",
                    resource_id=run.id,
                ),
                deny_code=ErrorCode.AI_MEMORY_DENIED,
            )
            now = datetime.now(timezone.utc)
            existing = self._repo.get_memory(
                tenant_id=run.tenant_id,
                run_id=run.id,
                key=cleaned_key,
            )
            if existing is None:
                entry = MemoryEntry(
                    id=uuid4(),
                    tenant_id=run.tenant_id,
                    run_id=run.id,
                    key=cleaned_key,
                    value=payload,
                    created_at=now,
                    updated_at=now,
                )
                self._repo.upsert_memory(entry, expected_version=None)
            else:
                entry = existing
                entry.value = payload
                entry.updated_at = now
                entry.version = existing.version + 1
                self._repo.upsert_memory(entry, expected_version=existing.version)
            audit = self._audit.record(
                ctx,
                action="AI.WriteMemory",
                resource=f"ai_memory:{run.id}",
                result="ok",
                details={"key": cleaned_key},
            )
            return KernelResult.success(entry.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def read_memory(
        self,
        ctx: ExecutionContext,
        *,
        run_id: UUID,
        key: str,
    ) -> KernelResult[MemoryEntry]:
        try:
            run = self._require_run(ctx, run_id)
            self._require_permission(
                ctx,
                action="read",
                resource=Resource(
                    tenant_id=run.tenant_id,
                    resource_type="ai_memory",
                    resource_id=run.id,
                ),
                deny_code=ErrorCode.AI_MEMORY_DENIED,
            )
            entry = self._repo.get_memory(
                tenant_id=run.tenant_id,
                run_id=run.id,
                key=key,
            )
            if entry is None:
                raise KernelError(
                    ErrorCode.AI_MEMORY_DENIED,
                    "memory entry not found",
                )
            return KernelResult.success(entry)
        except KernelError as err:
            return KernelResult.from_error(err)

    def access_knowledge(
        self,
        ctx: ExecutionContext,
        *,
        run_id: UUID,
        entity_id: UUID,
    ) -> KernelResult[KnowledgeEntity]:
        try:
            self._require_ai_subject(ctx)
            run = self._require_run(ctx, run_id)
            self._require_permission(
                ctx,
                action="read",
                resource=Resource(
                    tenant_id=run.tenant_id,
                    resource_type="knowledge_entity",
                    resource_id=entity_id,
                ),
                deny_code=ErrorCode.AI_KNOWLEDGE_DENIED,
            )
            if self._knowledge is None:
                raise KernelError(
                    ErrorCode.AI_KNOWLEDGE_DENIED,
                    "knowledge capability is not configured",
                )
            result = self._knowledge.get_entity(ctx, entity_id=entity_id)
            if not result.ok:
                raise KernelError(
                    ErrorCode.AI_KNOWLEDGE_DENIED,
                    result.error_message or "knowledge access denied",
                )
            assert result.data is not None
            audit = self._audit.record(
                ctx,
                action="AI.AccessKnowledge",
                resource=f"knowledge_entity:{entity_id}",
                result="ok",
                details={"run_id": str(run.id)},
            )
            return KernelResult.success(result.data, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

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
        try:
            self._require_ai_subject(ctx)
            run = self._require_run(ctx, run_id, writable=True)
            self._require_permission(
                ctx,
                action="request",
                resource=Resource(
                    tenant_id=run.tenant_id,
                    resource_type="ai_run",
                    resource_id=run.id,
                ),
            )
            started = self._workflow.start(
                ctx,
                definition_id=definition_id,
                payload={
                    "run_id": str(run.id),
                    "goal": run.goal,
                },
                approval_subject_id=approval_subject_id,
                approval_principal_subject_id=ctx.subject_id,
                approval_action=action.strip(),
                approval_resource_ref=resource_ref.strip(),
                approval_plan_version=plan_version,
                approval_scope=scope,
            )
            if not started.ok or started.data is None:
                raise KernelError(
                    started.error_code or ErrorCode.COMMON_INTERNAL,
                    started.error_message or "failed to start approval workflow",
                )
            instance_id = started.data["instance_id"]
            expected = run.version
            run.approval_ref = str(instance_id)
            run.status = AgentRunStatus.PENDING_APPROVAL
            run.updated_at = datetime.now(timezone.utc)
            run.version = expected + 1
            self._repo.save_run(run, expected_version=expected)
            audit = self._audit.record(
                ctx,
                action="AI.RequestApproval",
                resource=f"ai_run:{run.id}",
                result="ok",
                details={
                    "approval_ref": str(instance_id),
                    "action": action.strip(),
                    "resource_ref": resource_ref.strip(),
                },
            )
            return KernelResult.success(instance_id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

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
        try:
            self._require_ai_subject(ctx)
            run = self._require_run(ctx, run_id, writable=True)
            self._require_permission(
                ctx,
                action="commit",
                resource=Resource(
                    tenant_id=run.tenant_id,
                    resource_type="ai_run",
                    resource_id=run.id,
                ),
            )
            self._require_approved(
                ctx,
                run=run,
                action=action,
                resource_ref=resource_ref,
                plan_version=plan_version,
                scope=scope,
            )
            expected = run.version
            run.status = AgentRunStatus.COMPLETED
            run.updated_at = datetime.now(timezone.utc)
            run.version = expected + 1
            self._repo.save_run(run, expected_version=expected)
            audit = self._audit.record(
                ctx,
                action="AI.CommitAction",
                resource=f"ai_run:{run.id}",
                result="ok",
                details={
                    "action": action.strip(),
                    "resource_ref": resource_ref.strip(),
                    "approval_ref": run.approval_ref,
                },
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def _require_approved(
        self,
        ctx: ExecutionContext,
        *,
        run: AgentRun,
        action: str,
        resource_ref: str,
        plan_version: str | None,
        scope: str | None,
    ) -> None:
        approval_ref = ctx.approval_ref or run.approval_ref
        if not approval_ref:
            raise KernelError(
                ErrorCode.AI_APPROVAL_REQUIRED,
                "approval is required for this high-impact AI action",
            )
        from dataclasses import replace

        approved_ctx = replace(ctx, approval_ref=approval_ref)
        verified = self._workflow.verify_approved_action(
            approved_ctx,
            action=action,
            resource_ref=resource_ref,
            plan_version=plan_version,
            scope=scope,
        )
        if not verified.ok:
            raise KernelError(
                verified.error_code or ErrorCode.AI_COMMIT_FORBIDDEN,
                verified.error_message or "approval verification failed",
            )

    def _require_run(
        self,
        ctx: ExecutionContext,
        run_id: UUID,
        *,
        writable: bool = False,
    ) -> AgentRun:
        require_context(ctx, tenant_data_plane=True)
        run = self._repo.get_run(run_id)
        if run is None or run.tenant_id != ctx.tenant_id:
            raise KernelError(
                ErrorCode.COMMON_NOT_FOUND,
                "agent run not found",
            )
        if run.subject_id != ctx.subject_id and ctx.subject_type in _AI_SUBJECTS:
            raise KernelError(
                ErrorCode.PERMISSION_DENIED,
                "agent run belongs to a different AI subject",
            )
        if writable and run.status in {
            AgentRunStatus.COMPLETED,
            AgentRunStatus.FAILED,
            AgentRunStatus.CANCELLED,
        }:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "agent run is terminal",
            )
        return run

    def _require_permission(
        self,
        ctx: ExecutionContext,
        *,
        action: str,
        resource: Resource,
        deny_code: ErrorCode = ErrorCode.PERMISSION_DENIED,
    ) -> None:
        result = self._permission.evaluate(
            ctx,
            principal_subject_id=ctx.subject_id,
            action=action,
            resource=resource,
        )
        if not result.ok:
            raise KernelError(
                result.error_code or deny_code,
                result.error_message or "permission evaluation failed",
            )
        if result.data is None or result.data.effect != PermissionEffect.ALLOW:
            raise KernelError(deny_code, "permission denied")

    @staticmethod
    def _require_ai_subject(ctx: ExecutionContext) -> None:
        if ctx.subject_type not in _AI_SUBJECTS:
            raise KernelError(
                ErrorCode.AI_RUNTIME_REQUIRED,
                "AI Runtime operations require an AI subject",
            )

    @staticmethod
    def _reject_secrets(
        payload: Mapping[str, Any],
        *,
        key_name: str | None = None,
    ) -> None:
        candidates = list(payload.keys())
        if key_name is not None:
            candidates.append(key_name)
        for key in candidates:
            normalized = str(key).strip().casefold().replace("-", "_")
            if any(token in normalized for token in _SECRET_TOKENS):
                raise KernelError(
                    ErrorCode.AI_MEMORY_DENIED,
                    "secrets must not be stored in AI Runtime payloads",
                )
