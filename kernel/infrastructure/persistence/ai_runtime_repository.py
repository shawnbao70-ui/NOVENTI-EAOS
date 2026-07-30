"""Tenant-bound SQLAlchemy adapter for AI Runtime Repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from kernel.infrastructure.persistence.ai_runtime_models import (
    AIAgentRunRecord,
    AIMemoryEntryRecord,
    AIToolDeclarationRecord,
)
from kernel.shared.errors import ErrorCode, KernelError
from runtime.ai.models import AgentRun, AgentRunStatus, MemoryEntry, ToolDeclaration


class SQLAlchemyAIRuntimeRepository:
    def __init__(self, session: Session, *, tenant_id: UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def add_run(self, run: AgentRun) -> None:
        self._require_tenant(run.tenant_id)
        self._session.add(
            AIAgentRunRecord(
                id=run.id,
                tenant_id=run.tenant_id,
                subject_id=run.subject_id,
                goal=run.goal,
                plan_summary=run.plan_summary,
                status=run.status.value,
                approval_ref=run.approval_ref,
                last_error_code=run.last_error_code,
                created_at=run.created_at,
                updated_at=run.updated_at,
                version=run.version,
            )
        )

    def get_run(self, run_id: UUID) -> AgentRun | None:
        record = self._session.scalar(
            select(AIAgentRunRecord).where(
                AIAgentRunRecord.id == run_id,
                AIAgentRunRecord.tenant_id == self._tenant_id,
            )
        )
        return self._to_run(record) if record is not None else None

    def save_run(self, run: AgentRun, *, expected_version: int) -> None:
        self._require_tenant(run.tenant_id)
        result = self._session.execute(
            update(AIAgentRunRecord)
            .where(
                AIAgentRunRecord.id == run.id,
                AIAgentRunRecord.tenant_id == run.tenant_id,
                AIAgentRunRecord.version == expected_version,
            )
            .values(
                status=run.status.value,
                approval_ref=run.approval_ref,
                last_error_code=run.last_error_code,
                plan_summary=run.plan_summary,
                updated_at=run.updated_at,
                version=run.version,
            )
        )
        if result.rowcount != 1:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "agent run version conflict",
            )

    def add_tool(self, tool: ToolDeclaration) -> None:
        self._require_tenant(tool.tenant_id)
        self._session.add(
            AIToolDeclarationRecord(
                id=tool.id,
                tenant_id=tool.tenant_id,
                name=tool.name,
                description=tool.description,
                high_impact=tool.high_impact,
                created_at=tool.created_at,
            )
        )

    def get_tool_by_name(
        self,
        *,
        tenant_id: UUID,
        name: str,
    ) -> ToolDeclaration | None:
        self._require_tenant(tenant_id)
        record = self._session.scalar(
            select(AIToolDeclarationRecord).where(
                AIToolDeclarationRecord.tenant_id == tenant_id,
                func.lower(AIToolDeclarationRecord.name) == name.casefold(),
            )
        )
        return self._to_tool(record) if record is not None else None

    def list_tools(self, *, tenant_id: UUID) -> list[ToolDeclaration]:
        self._require_tenant(tenant_id)
        records = self._session.scalars(
            select(AIToolDeclarationRecord).where(
                AIToolDeclarationRecord.tenant_id == tenant_id
            )
        )
        return [self._to_tool(record) for record in records]

    def upsert_memory(
        self,
        entry: MemoryEntry,
        *,
        expected_version: int | None,
    ) -> None:
        self._require_tenant(entry.tenant_id)
        existing = self._session.scalar(
            select(AIMemoryEntryRecord).where(
                AIMemoryEntryRecord.tenant_id == entry.tenant_id,
                AIMemoryEntryRecord.run_id == entry.run_id,
                func.lower(AIMemoryEntryRecord.key) == entry.key.casefold(),
            )
        )
        if existing is None:
            self._session.add(
                AIMemoryEntryRecord(
                    id=entry.id,
                    tenant_id=entry.tenant_id,
                    run_id=entry.run_id,
                    key=entry.key,
                    value=dict(entry.value),
                    created_at=entry.created_at,
                    updated_at=entry.updated_at,
                    version=entry.version,
                )
            )
            return
        if expected_version is None or existing.version != expected_version:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "memory version conflict",
            )
        existing.value = dict(entry.value)
        existing.updated_at = entry.updated_at
        existing.version = entry.version

    def get_memory(
        self,
        *,
        tenant_id: UUID,
        run_id: UUID,
        key: str,
    ) -> MemoryEntry | None:
        self._require_tenant(tenant_id)
        record = self._session.scalar(
            select(AIMemoryEntryRecord).where(
                AIMemoryEntryRecord.tenant_id == tenant_id,
                AIMemoryEntryRecord.run_id == run_id,
                func.lower(AIMemoryEntryRecord.key) == key.casefold(),
            )
        )
        return self._to_memory(record) if record is not None else None

    def list_memory(self, *, tenant_id: UUID, run_id: UUID) -> list[MemoryEntry]:
        self._require_tenant(tenant_id)
        records = self._session.scalars(
            select(AIMemoryEntryRecord).where(
                AIMemoryEntryRecord.tenant_id == tenant_id,
                AIMemoryEntryRecord.run_id == run_id,
            )
        )
        return [self._to_memory(record) for record in records]

    def _require_tenant(self, tenant_id: UUID) -> None:
        if tenant_id != self._tenant_id:
            raise KernelError(
                ErrorCode.PERMISSION_DENIED,
                "cross-tenant AI Runtime access is forbidden",
            )

    @staticmethod
    def _to_run(record: AIAgentRunRecord) -> AgentRun:
        return AgentRun(
            id=record.id,
            tenant_id=record.tenant_id,
            subject_id=record.subject_id,
            goal=record.goal,
            plan_summary=record.plan_summary or "",
            status=AgentRunStatus(record.status),
            approval_ref=record.approval_ref,
            last_error_code=record.last_error_code,
            created_at=record.created_at,
            updated_at=record.updated_at,
            version=record.version,
        )

    @staticmethod
    def _to_tool(record: AIToolDeclarationRecord) -> ToolDeclaration:
        return ToolDeclaration(
            id=record.id,
            tenant_id=record.tenant_id,
            name=record.name,
            description=record.description,
            high_impact=record.high_impact,
            created_at=record.created_at,
        )

    @staticmethod
    def _to_memory(record: AIMemoryEntryRecord) -> MemoryEntry:
        return MemoryEntry(
            id=record.id,
            tenant_id=record.tenant_id,
            run_id=record.run_id,
            key=record.key,
            value=dict(record.value or {}),
            created_at=record.created_at,
            updated_at=record.updated_at,
            version=record.version,
        )
