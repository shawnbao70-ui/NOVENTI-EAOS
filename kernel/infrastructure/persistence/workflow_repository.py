"""Tenant-bound SQLAlchemy adapter for Workflow Repository."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import overload
from uuid import UUID

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from kernel.infrastructure.persistence.workflow_models import (
    WorkflowDefinitionRecord,
    WorkflowHistoryRecord,
    WorkflowInstanceRecord,
    WorkflowSignalReceiptRecord,
    WorkflowTaskRecord,
)
from kernel.shared.errors import ErrorCode, KernelError
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


class SQLAlchemyWorkflowRepository:
    def __init__(
        self,
        session: Session,
        *,
        tenant_id: UUID | None,
        platform_scope: bool = False,
    ) -> None:
        if platform_scope == (tenant_id is not None):
            raise ValueError("provide either tenant_id or platform_scope")
        self._session = session
        self._tenant_id = tenant_id
        self._platform_scope = platform_scope

    def add_definition(self, definition: WorkflowDefinition) -> None:
        self._require_scope(definition.tenant_id)
        self._session.add(
            WorkflowDefinitionRecord(
                id=definition.id,
                tenant_id=definition.tenant_id,
                name=definition.name,
                document_ref=definition.document_ref,
                version=definition.version,
                status=definition.status.value,
                created_at=definition.created_at,
            )
        )

    def get_definition(self, definition_id: UUID) -> WorkflowDefinition | None:
        statement = select(WorkflowDefinitionRecord).where(
            WorkflowDefinitionRecord.id == definition_id
        )
        if not self._platform_scope:
            statement = statement.where(
                or_(
                    WorkflowDefinitionRecord.tenant_id == self._tenant_id,
                    WorkflowDefinitionRecord.tenant_id.is_(None),
                )
            )
        record = self._session.scalar(statement)
        return self._to_definition(record) if record is not None else None

    def find_definition(
        self,
        *,
        tenant_id: UUID | None,
        name: str,
        version: str,
    ) -> WorkflowDefinition | None:
        self._require_scope(tenant_id)
        record = self._session.scalar(
            select(WorkflowDefinitionRecord).where(
                WorkflowDefinitionRecord.tenant_id == tenant_id
                if tenant_id is not None
                else WorkflowDefinitionRecord.tenant_id.is_(None),
                func.lower(WorkflowDefinitionRecord.name) == name.casefold(),
                WorkflowDefinitionRecord.version == version,
            )
        )
        return self._to_definition(record) if record is not None else None

    def save_definition(self, definition: WorkflowDefinition) -> None:
        self._require_scope(definition.tenant_id)
        record = self._session.scalar(
            select(WorkflowDefinitionRecord).where(
                WorkflowDefinitionRecord.id == definition.id
            )
        )
        if record is None:
            raise KernelError(
                ErrorCode.WORKFLOW_DEFINITION_NOT_FOUND,
                "workflow definition not found",
            )
        record.status = definition.status.value

    def add_instance(self, instance: WorkflowInstance) -> None:
        self._require_scope(instance.tenant_id)
        self._session.add(self._instance_record(instance))
        # No ORM relationships are declared between independent persistence
        # records, so establish the parent row before task/history children.
        self._session.flush()

    def get_instance(self, instance_id: UUID) -> WorkflowInstance | None:
        record = self._session.scalar(
            self._scoped_instances().where(WorkflowInstanceRecord.id == instance_id)
        )
        return self._to_instance(record) if record is not None else None

    def find_active_by_business_key(
        self,
        *,
        tenant_id: UUID,
        business_key: str,
    ) -> WorkflowInstance | None:
        self._require_scope(tenant_id)
        record = self._session.scalar(
            select(WorkflowInstanceRecord).where(
                WorkflowInstanceRecord.tenant_id == tenant_id,
                WorkflowInstanceRecord.business_key == business_key,
                WorkflowInstanceRecord.status.in_(
                    (
                        WorkflowStatus.RUNNING.value,
                        WorkflowStatus.PENDING_APPROVAL.value,
                        WorkflowStatus.APPROVED.value,
                        WorkflowStatus.COMPENSATING.value,
                    )
                ),
            )
        )
        return self._to_instance(record) if record is not None else None

    def save_instance(
        self,
        instance: WorkflowInstance,
        *,
        expected_version: int,
    ) -> None:
        self._require_scope(instance.tenant_id)
        result = self._session.execute(
            update(WorkflowInstanceRecord)
            .where(
                WorkflowInstanceRecord.id == instance.id,
                WorkflowInstanceRecord.tenant_id == instance.tenant_id,
                WorkflowInstanceRecord.version == expected_version,
            )
            .values(
                status=instance.status.value,
                payload=instance.payload,
                business_key=instance.business_key,
                current_task_id=instance.current_task_id,
                approval_principal_subject_id=instance.approval_principal_subject_id,
                approval_action=instance.approval_action,
                approval_resource_ref=instance.approval_resource_ref,
                approval_plan_version=instance.approval_plan_version,
                approval_scope=instance.approval_scope,
                approval_expires_at=instance.approval_expires_at,
                updated_at=instance.updated_at,
                version=instance.version,
            )
        )
        if result.rowcount != 1:
            raise KernelError(
                ErrorCode.WORKFLOW_VERSION_CONFLICT,
                "workflow instance version conflict",
            )

    def add_task(self, task: WorkflowTask) -> None:
        self._require_scope(task.tenant_id)
        self._session.add(
            WorkflowTaskRecord(
                id=task.id,
                instance_id=task.instance_id,
                tenant_id=task.tenant_id,
                assignee_subject_id=task.assignee_subject_id,
                status=task.status.value,
                decision_comment=task.decision_comment,
                escalated_from_subject_id=task.escalated_from_subject_id,
                due_at=task.due_at,
                created_at=task.created_at,
                updated_at=task.updated_at,
                version=task.version,
            )
        )

    def get_task(self, task_id: UUID) -> WorkflowTask | None:
        record = self._session.scalar(
            self._scoped_tasks().where(WorkflowTaskRecord.id == task_id)
        )
        return self._to_task(record) if record is not None else None

    def save_task(self, task: WorkflowTask, *, expected_version: int) -> None:
        self._require_scope(task.tenant_id)
        result = self._session.execute(
            update(WorkflowTaskRecord)
            .where(
                WorkflowTaskRecord.id == task.id,
                WorkflowTaskRecord.tenant_id == task.tenant_id,
                WorkflowTaskRecord.version == expected_version,
            )
            .values(
                assignee_subject_id=task.assignee_subject_id,
                status=task.status.value,
                decision_comment=task.decision_comment,
                escalated_from_subject_id=task.escalated_from_subject_id,
                due_at=task.due_at,
                updated_at=task.updated_at,
                version=task.version,
            )
        )
        if result.rowcount != 1:
            raise KernelError(
                ErrorCode.WORKFLOW_VERSION_CONFLICT,
                "workflow task version conflict",
            )

    def list_tasks(self, tenant_id: UUID) -> list[WorkflowTask]:
        self._require_scope(tenant_id)
        return [
            self._to_task(record)
            for record in self._session.scalars(
                select(WorkflowTaskRecord).where(
                    WorkflowTaskRecord.tenant_id == tenant_id
                )
            )
        ]

    def add_history(self, entry: WorkflowHistoryEntry) -> None:
        self._require_scope(entry.tenant_id)
        self._session.add(
            WorkflowHistoryRecord(
                id=entry.id,
                instance_id=entry.instance_id,
                tenant_id=entry.tenant_id,
                action=entry.action,
                subject_id=entry.subject_id,
                correlation_id=entry.correlation_id,
                timestamp=entry.timestamp,
                details=entry.details,
            )
        )

    def list_history(self, instance_id: UUID) -> list[WorkflowHistoryEntry]:
        statement = select(WorkflowHistoryRecord).where(
            WorkflowHistoryRecord.instance_id == instance_id
        )
        if not self._platform_scope:
            statement = statement.where(
                WorkflowHistoryRecord.tenant_id == self._tenant_id
            )
        return [
            self._to_history(record)
            for record in self._session.scalars(statement)
        ]

    def get_signal_receipt(
        self,
        instance_id: UUID,
        idempotency_key: str,
    ) -> SignalReceipt | None:
        statement = select(WorkflowSignalReceiptRecord).where(
            WorkflowSignalReceiptRecord.instance_id == instance_id,
            WorkflowSignalReceiptRecord.idempotency_key == idempotency_key,
        )
        if not self._platform_scope:
            statement = statement.where(
                WorkflowSignalReceiptRecord.tenant_id == self._tenant_id
            )
        record = self._session.scalar(statement)
        return self._to_receipt(record) if record is not None else None

    def add_signal_receipt(self, receipt: SignalReceipt) -> None:
        self._require_scope(receipt.tenant_id)
        self._session.add(
            WorkflowSignalReceiptRecord(
                instance_id=receipt.instance_id,
                tenant_id=receipt.tenant_id,
                idempotency_key=receipt.idempotency_key,
                request_fingerprint=receipt.request_fingerprint,
                resulting_status=receipt.resulting_status.value,
                processed_at=receipt.processed_at,
            )
        )

    def _scoped_instances(self):
        statement = select(WorkflowInstanceRecord)
        if not self._platform_scope:
            statement = statement.where(
                WorkflowInstanceRecord.tenant_id == self._tenant_id
            )
        return statement

    def _scoped_tasks(self):
        statement = select(WorkflowTaskRecord)
        if not self._platform_scope:
            statement = statement.where(
                WorkflowTaskRecord.tenant_id == self._tenant_id
            )
        return statement

    def _require_scope(self, tenant_id: UUID | None) -> None:
        if self._platform_scope:
            return
        if tenant_id != self._tenant_id:
            raise KernelError(
                ErrorCode.WORKFLOW_CROSS_TENANT_FORBIDDEN,
                "workflow operation is outside repository tenant scope",
            )

    @staticmethod
    def _instance_record(instance: WorkflowInstance) -> WorkflowInstanceRecord:
        return WorkflowInstanceRecord(
            id=instance.id,
            definition_id=instance.definition_id,
            tenant_id=instance.tenant_id,
            initiator_subject_id=instance.initiator_subject_id,
            status=instance.status.value,
            payload=instance.payload,
            business_key=instance.business_key,
            current_task_id=instance.current_task_id,
            approval_principal_subject_id=instance.approval_principal_subject_id,
            approval_action=instance.approval_action,
            approval_resource_ref=instance.approval_resource_ref,
            approval_plan_version=instance.approval_plan_version,
            approval_scope=instance.approval_scope,
            approval_expires_at=instance.approval_expires_at,
            created_at=instance.created_at,
            updated_at=instance.updated_at,
            version=instance.version,
        )

    @classmethod
    def _to_definition(cls, record: WorkflowDefinitionRecord) -> WorkflowDefinition:
        return WorkflowDefinition(
            id=record.id,
            tenant_id=record.tenant_id,
            name=record.name,
            document_ref=record.document_ref,
            version=record.version,
            status=WorkflowDefinitionStatus(record.status),
            created_at=cls._as_utc(record.created_at),
        )

    @classmethod
    def _to_instance(cls, record: WorkflowInstanceRecord) -> WorkflowInstance:
        return WorkflowInstance(
            id=record.id,
            definition_id=record.definition_id,
            tenant_id=record.tenant_id,
            initiator_subject_id=record.initiator_subject_id,
            status=WorkflowStatus(record.status),
            payload=dict(record.payload),
            business_key=record.business_key,
            current_task_id=record.current_task_id,
            approval_principal_subject_id=record.approval_principal_subject_id,
            approval_action=record.approval_action,
            approval_resource_ref=record.approval_resource_ref,
            approval_plan_version=record.approval_plan_version,
            approval_scope=record.approval_scope,
            approval_expires_at=cls._as_utc(record.approval_expires_at),
            created_at=cls._as_utc(record.created_at),
            updated_at=cls._as_utc(record.updated_at),
            version=record.version,
        )

    @classmethod
    def _to_task(cls, record: WorkflowTaskRecord) -> WorkflowTask:
        return WorkflowTask(
            id=record.id,
            instance_id=record.instance_id,
            tenant_id=record.tenant_id,
            assignee_subject_id=record.assignee_subject_id,
            status=TaskStatus(record.status),
            decision_comment=record.decision_comment,
            escalated_from_subject_id=record.escalated_from_subject_id,
            due_at=cls._as_utc(record.due_at),
            created_at=cls._as_utc(record.created_at),
            updated_at=cls._as_utc(record.updated_at),
            version=record.version,
        )

    @classmethod
    def _to_history(cls, record: WorkflowHistoryRecord) -> WorkflowHistoryEntry:
        return WorkflowHistoryEntry(
            id=record.id,
            instance_id=record.instance_id,
            tenant_id=record.tenant_id,
            action=record.action,
            subject_id=record.subject_id,
            correlation_id=record.correlation_id,
            timestamp=cls._as_utc(record.timestamp),
            details=dict(record.details),
        )

    @classmethod
    def _to_receipt(cls, record: WorkflowSignalReceiptRecord) -> SignalReceipt:
        return SignalReceipt(
            instance_id=record.instance_id,
            tenant_id=record.tenant_id,
            idempotency_key=record.idempotency_key,
            request_fingerprint=record.request_fingerprint,
            resulting_status=WorkflowStatus(record.resulting_status),
            processed_at=cls._as_utc(record.processed_at),
        )

    @staticmethod
    @overload
    def _as_utc(value: datetime) -> datetime: ...

    @staticmethod
    @overload
    def _as_utc(value: None) -> None: ...

    @staticmethod
    def _as_utc(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
