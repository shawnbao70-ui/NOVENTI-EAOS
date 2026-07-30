"""In-memory Workflow repository for PHX-K09."""

from __future__ import annotations

from copy import deepcopy
from typing import Optional, Protocol, runtime_checkable
from uuid import UUID

from kernel.shared.errors import ErrorCode, KernelError
from kernel.workflow.models import (
    SignalReceipt,
    WorkflowDefinition,
    WorkflowHistoryEntry,
    WorkflowInstance,
    WorkflowStatus,
    WorkflowTask,
)


@runtime_checkable
class WorkflowRepository(Protocol):
    def add_definition(self, definition: WorkflowDefinition) -> None: ...

    def get_definition(self, definition_id: UUID) -> Optional[WorkflowDefinition]: ...

    def find_definition(
        self,
        *,
        tenant_id: Optional[UUID],
        name: str,
        version: str,
    ) -> Optional[WorkflowDefinition]: ...

    def save_definition(self, definition: WorkflowDefinition) -> None: ...

    def add_instance(self, instance: WorkflowInstance) -> None: ...

    def get_instance(self, instance_id: UUID) -> Optional[WorkflowInstance]: ...

    def find_active_by_business_key(
        self,
        *,
        tenant_id: UUID,
        business_key: str,
    ) -> Optional[WorkflowInstance]: ...

    def save_instance(
        self,
        instance: WorkflowInstance,
        *,
        expected_version: int,
    ) -> None: ...

    def add_task(self, task: WorkflowTask) -> None: ...

    def get_task(self, task_id: UUID) -> Optional[WorkflowTask]: ...

    def save_task(self, task: WorkflowTask, *, expected_version: int) -> None: ...

    def list_tasks(self, tenant_id: UUID) -> list[WorkflowTask]: ...

    def add_history(self, entry: WorkflowHistoryEntry) -> None: ...

    def list_history(self, instance_id: UUID) -> list[WorkflowHistoryEntry]: ...

    def get_signal_receipt(
        self,
        instance_id: UUID,
        idempotency_key: str,
    ) -> Optional[SignalReceipt]: ...

    def add_signal_receipt(self, receipt: SignalReceipt) -> None: ...


_ACTIVE_STATUSES = {
    WorkflowStatus.RUNNING,
    WorkflowStatus.PENDING_APPROVAL,
    WorkflowStatus.APPROVED,
    WorkflowStatus.COMPENSATING,
}


class InMemoryWorkflowRepository:
    def __init__(self) -> None:
        self.definitions: dict[UUID, WorkflowDefinition] = {}
        self.instances: dict[UUID, WorkflowInstance] = {}
        self.tasks: dict[UUID, WorkflowTask] = {}
        self.history: list[WorkflowHistoryEntry] = []
        self.signal_receipts: dict[tuple[UUID, str], SignalReceipt] = {}

    def add_definition(self, definition: WorkflowDefinition) -> None:
        self.definitions[definition.id] = deepcopy(definition)

    def get_definition(self, definition_id: UUID) -> Optional[WorkflowDefinition]:
        definition = self.definitions.get(definition_id)
        return deepcopy(definition) if definition is not None else None

    def find_definition(
        self,
        *,
        tenant_id: Optional[UUID],
        name: str,
        version: str,
    ) -> Optional[WorkflowDefinition]:
        for definition in self.definitions.values():
            if (
                definition.tenant_id == tenant_id
                and definition.name.casefold() == name.casefold()
                and definition.version == version
            ):
                return deepcopy(definition)
        return None

    def save_definition(self, definition: WorkflowDefinition) -> None:
        if definition.id not in self.definitions:
            raise KernelError(
                ErrorCode.WORKFLOW_DEFINITION_NOT_FOUND,
                "workflow definition not found",
            )
        self.definitions[definition.id] = deepcopy(definition)

    def add_instance(self, instance: WorkflowInstance) -> None:
        self.instances[instance.id] = deepcopy(instance)

    def get_instance(self, instance_id: UUID) -> Optional[WorkflowInstance]:
        instance = self.instances.get(instance_id)
        return deepcopy(instance) if instance is not None else None

    def find_active_by_business_key(
        self,
        *,
        tenant_id: UUID,
        business_key: str,
    ) -> Optional[WorkflowInstance]:
        for instance in self.instances.values():
            if (
                instance.tenant_id == tenant_id
                and instance.business_key == business_key
                and instance.status in _ACTIVE_STATUSES
            ):
                return deepcopy(instance)
        return None

    def save_instance(
        self,
        instance: WorkflowInstance,
        *,
        expected_version: int,
    ) -> None:
        current = self.instances.get(instance.id)
        if current is None or current.version != expected_version:
            raise KernelError(
                ErrorCode.WORKFLOW_VERSION_CONFLICT,
                "workflow instance version conflict",
            )
        self.instances[instance.id] = deepcopy(instance)

    def add_task(self, task: WorkflowTask) -> None:
        self.tasks[task.id] = deepcopy(task)

    def get_task(self, task_id: UUID) -> Optional[WorkflowTask]:
        task = self.tasks.get(task_id)
        return deepcopy(task) if task is not None else None

    def save_task(self, task: WorkflowTask, *, expected_version: int) -> None:
        current = self.tasks.get(task.id)
        if current is None or current.version != expected_version:
            raise KernelError(
                ErrorCode.WORKFLOW_VERSION_CONFLICT,
                "workflow task version conflict",
            )
        self.tasks[task.id] = deepcopy(task)

    def list_tasks(self, tenant_id: UUID) -> list[WorkflowTask]:
        return [
            deepcopy(task)
            for task in self.tasks.values()
            if task.tenant_id == tenant_id
        ]

    def add_history(self, entry: WorkflowHistoryEntry) -> None:
        self.history.append(deepcopy(entry))

    def list_history(self, instance_id: UUID) -> list[WorkflowHistoryEntry]:
        return [
            deepcopy(entry)
            for entry in self.history
            if entry.instance_id == instance_id
        ]

    def get_signal_receipt(
        self,
        instance_id: UUID,
        idempotency_key: str,
    ) -> Optional[SignalReceipt]:
        return self.signal_receipts.get((instance_id, idempotency_key))

    def add_signal_receipt(self, receipt: SignalReceipt) -> None:
        key = (receipt.instance_id, receipt.idempotency_key)
        existing = self.signal_receipts.get(key)
        if existing is not None:
            if existing.request_fingerprint != receipt.request_fingerprint:
                raise KernelError(
                    ErrorCode.WORKFLOW_SIGNAL_CONFLICT,
                    "idempotency key was already used with a different signal request",
                )
            return
        self.signal_receipts[key] = receipt
