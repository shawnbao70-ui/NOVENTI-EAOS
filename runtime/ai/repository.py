"""In-memory AI Runtime repository."""

from __future__ import annotations

from copy import deepcopy
from typing import Optional, Protocol, runtime_checkable
from uuid import UUID

from runtime.ai.models import AgentRun, MemoryEntry, ToolDeclaration
from kernel.shared.errors import ErrorCode, KernelError


@runtime_checkable
class AIRuntimeRepository(Protocol):
    def add_run(self, run: AgentRun) -> None: ...

    def get_run(self, run_id: UUID) -> Optional[AgentRun]: ...

    def save_run(self, run: AgentRun, *, expected_version: int) -> None: ...

    def add_tool(self, tool: ToolDeclaration) -> None: ...

    def get_tool_by_name(
        self,
        *,
        tenant_id: UUID,
        name: str,
    ) -> Optional[ToolDeclaration]: ...

    def list_tools(self, *, tenant_id: UUID) -> list[ToolDeclaration]: ...

    def upsert_memory(self, entry: MemoryEntry, *, expected_version: int | None) -> None: ...

    def get_memory(
        self,
        *,
        tenant_id: UUID,
        run_id: UUID,
        key: str,
    ) -> Optional[MemoryEntry]: ...

    def list_memory(self, *, tenant_id: UUID, run_id: UUID) -> list[MemoryEntry]: ...


class InMemoryAIRuntimeRepository:
    def __init__(self) -> None:
        self.runs: dict[UUID, AgentRun] = {}
        self.tools: dict[UUID, ToolDeclaration] = {}
        self.memory: dict[tuple[UUID, UUID, str], MemoryEntry] = {}

    def add_run(self, run: AgentRun) -> None:
        self.runs[run.id] = deepcopy(run)

    def get_run(self, run_id: UUID) -> Optional[AgentRun]:
        run = self.runs.get(run_id)
        return deepcopy(run) if run is not None else None

    def save_run(self, run: AgentRun, *, expected_version: int) -> None:
        current = self.runs.get(run.id)
        if current is None or current.version != expected_version:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "agent run version conflict",
            )
        self.runs[run.id] = deepcopy(run)

    def add_tool(self, tool: ToolDeclaration) -> None:
        for existing in self.tools.values():
            if (
                existing.tenant_id == tool.tenant_id
                and existing.name.casefold() == tool.name.casefold()
            ):
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "tool already registered",
                )
        self.tools[tool.id] = deepcopy(tool)

    def get_tool_by_name(
        self,
        *,
        tenant_id: UUID,
        name: str,
    ) -> Optional[ToolDeclaration]:
        for tool in self.tools.values():
            if tool.tenant_id == tenant_id and tool.name.casefold() == name.casefold():
                return deepcopy(tool)
        return None

    def list_tools(self, *, tenant_id: UUID) -> list[ToolDeclaration]:
        return [
            deepcopy(tool)
            for tool in self.tools.values()
            if tool.tenant_id == tenant_id
        ]

    def upsert_memory(
        self,
        entry: MemoryEntry,
        *,
        expected_version: int | None,
    ) -> None:
        key = (entry.tenant_id, entry.run_id, entry.key.casefold())
        current = self.memory.get(key)
        if current is None:
            self.memory[key] = deepcopy(entry)
            return
        if expected_version is None or current.version != expected_version:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "memory version conflict",
            )
        self.memory[key] = deepcopy(entry)

    def get_memory(
        self,
        *,
        tenant_id: UUID,
        run_id: UUID,
        key: str,
    ) -> Optional[MemoryEntry]:
        entry = self.memory.get((tenant_id, run_id, key.casefold()))
        return deepcopy(entry) if entry is not None else None

    def list_memory(self, *, tenant_id: UUID, run_id: UUID) -> list[MemoryEntry]:
        return [
            deepcopy(entry)
            for (tenant, run, _), entry in self.memory.items()
            if tenant == tenant_id and run == run_id
        ]
