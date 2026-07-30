"""Tenant-bound SQLAlchemy adapter for Smart Terminal Repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from kernel.infrastructure.persistence.smart_terminal_models import (
    TerminalExtensionRecord,
    TerminalIntentRecord,
    TerminalPreviewRecord,
    TerminalSessionRecord,
)
from kernel.shared.errors import ErrorCode, KernelError
from smart_terminal.models import (
    DeviceTrust,
    ExtensionStatus,
    IntentStatus,
    PlanPreview,
    PreviewStatus,
    TerminalExtension,
    TerminalIntent,
    TerminalSession,
    TerminalSessionStatus,
)


class SQLAlchemySmartTerminalRepository:
    def __init__(self, session: Session, *, tenant_id: UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def add_session(self, session: TerminalSession) -> None:
        self._require_tenant(session.tenant_id)
        self._session.add(
            TerminalSessionRecord(
                id=session.id,
                tenant_id=session.tenant_id,
                subject_id=session.subject_id,
                identity_session_id=session.identity_session_id,
                correlation_id=session.correlation_id,
                device_trust=session.device_trust.value,
                status=session.status.value,
                created_at=session.created_at,
                updated_at=session.updated_at,
                version=session.version,
            )
        )

    def get_session(self, session_id: UUID) -> TerminalSession | None:
        record = self._session.scalar(
            select(TerminalSessionRecord).where(
                TerminalSessionRecord.id == session_id,
                TerminalSessionRecord.tenant_id == self._tenant_id,
            )
        )
        return self._to_session(record) if record is not None else None

    def save_session(
        self,
        session: TerminalSession,
        *,
        expected_version: int,
    ) -> None:
        self._require_tenant(session.tenant_id)
        result = self._session.execute(
            update(TerminalSessionRecord)
            .where(
                TerminalSessionRecord.id == session.id,
                TerminalSessionRecord.tenant_id == session.tenant_id,
                TerminalSessionRecord.version == expected_version,
            )
            .values(
                status=session.status.value,
                device_trust=session.device_trust.value,
                updated_at=session.updated_at,
                version=session.version,
            )
        )
        if result.rowcount != 1:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "terminal session version conflict")

    def add_intent(self, intent: TerminalIntent) -> None:
        self._require_tenant(intent.tenant_id)
        self._session.add(
            TerminalIntentRecord(
                id=intent.id,
                tenant_id=intent.tenant_id,
                subject_id=intent.subject_id,
                terminal_session_id=intent.terminal_session_id,
                text=intent.text,
                status=intent.status.value,
                created_at=intent.created_at,
                updated_at=intent.updated_at,
                version=intent.version,
            )
        )

    def get_intent(self, intent_id: UUID) -> TerminalIntent | None:
        record = self._session.scalar(
            select(TerminalIntentRecord).where(
                TerminalIntentRecord.id == intent_id,
                TerminalIntentRecord.tenant_id == self._tenant_id,
            )
        )
        return self._to_intent(record) if record is not None else None

    def save_intent(
        self,
        intent: TerminalIntent,
        *,
        expected_version: int,
    ) -> None:
        self._require_tenant(intent.tenant_id)
        result = self._session.execute(
            update(TerminalIntentRecord)
            .where(
                TerminalIntentRecord.id == intent.id,
                TerminalIntentRecord.tenant_id == intent.tenant_id,
                TerminalIntentRecord.version == expected_version,
            )
            .values(
                status=intent.status.value,
                text=intent.text,
                updated_at=intent.updated_at,
                version=intent.version,
            )
        )
        if result.rowcount != 1:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "terminal intent version conflict")

    def add_preview(self, preview: PlanPreview) -> None:
        self._require_tenant(preview.tenant_id)
        self._session.add(
            TerminalPreviewRecord(
                id=preview.id,
                tenant_id=preview.tenant_id,
                subject_id=preview.subject_id,
                intent_id=preview.intent_id,
                terminal_session_id=preview.terminal_session_id,
                action=preview.action,
                resource_ref=preview.resource_ref,
                plan_version=preview.plan_version,
                scope=preview.scope,
                impact_summary=preview.impact_summary,
                high_impact=preview.high_impact,
                status=preview.status.value,
                approval_ref=preview.approval_ref,
                created_at=preview.created_at,
                updated_at=preview.updated_at,
                version=preview.version,
            )
        )

    def get_preview(self, preview_id: UUID) -> PlanPreview | None:
        record = self._session.scalar(
            select(TerminalPreviewRecord).where(
                TerminalPreviewRecord.id == preview_id,
                TerminalPreviewRecord.tenant_id == self._tenant_id,
            )
        )
        return self._to_preview(record) if record is not None else None

    def save_preview(
        self,
        preview: PlanPreview,
        *,
        expected_version: int,
    ) -> None:
        self._require_tenant(preview.tenant_id)
        result = self._session.execute(
            update(TerminalPreviewRecord)
            .where(
                TerminalPreviewRecord.id == preview.id,
                TerminalPreviewRecord.tenant_id == preview.tenant_id,
                TerminalPreviewRecord.version == expected_version,
            )
            .values(
                status=preview.status.value,
                approval_ref=preview.approval_ref,
                updated_at=preview.updated_at,
                version=preview.version,
            )
        )
        if result.rowcount != 1:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "plan preview version conflict")

    def list_previews_for_intent(self, intent_id: UUID) -> list[PlanPreview]:
        records = self._session.scalars(
            select(TerminalPreviewRecord).where(
                TerminalPreviewRecord.intent_id == intent_id,
                TerminalPreviewRecord.tenant_id == self._tenant_id,
            )
        ).all()
        return [self._to_preview(record) for record in records]

    def _require_tenant(self, tenant_id: UUID) -> None:
        if tenant_id != self._tenant_id:
            raise KernelError(ErrorCode.COMMON_INTERNAL, "tenant boundary violation")

    @staticmethod
    def _to_session(record: TerminalSessionRecord) -> TerminalSession:
        return TerminalSession(
            id=record.id,
            tenant_id=record.tenant_id,
            subject_id=record.subject_id,
            correlation_id=record.correlation_id,
            device_trust=DeviceTrust(record.device_trust),
            status=TerminalSessionStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            identity_session_id=record.identity_session_id,
            version=record.version,
        )

    @staticmethod
    def _to_intent(record: TerminalIntentRecord) -> TerminalIntent:
        return TerminalIntent(
            id=record.id,
            tenant_id=record.tenant_id,
            subject_id=record.subject_id,
            terminal_session_id=record.terminal_session_id,
            text=record.text,
            status=IntentStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            version=record.version,
        )

    @staticmethod
    def _to_preview(record: TerminalPreviewRecord) -> PlanPreview:
        return PlanPreview(
            id=record.id,
            tenant_id=record.tenant_id,
            subject_id=record.subject_id,
            intent_id=record.intent_id,
            terminal_session_id=record.terminal_session_id,
            action=record.action,
            resource_ref=record.resource_ref,
            plan_version=record.plan_version,
            scope=record.scope,
            impact_summary=record.impact_summary,
            high_impact=record.high_impact,
            status=PreviewStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            approval_ref=record.approval_ref,
            version=record.version,
        )

    def add_extension(self, extension: TerminalExtension) -> None:
        self._require_tenant(extension.tenant_id)
        self._session.add(
            TerminalExtensionRecord(
                id=extension.id,
                tenant_id=extension.tenant_id,
                extension_key=extension.extension_key,
                extension_version=extension.version,
                signature_ref=extension.signature_ref,
                status=extension.status.value,
                declared_capabilities_json=sorted(extension.declared_capabilities),
                declared_actions_json=sorted(extension.declared_actions),
                allowed_surfaces_json=sorted(extension.allowed_surfaces),
                data_scope=extension.data_scope,
                created_at=extension.created_at,
                updated_at=extension.updated_at,
                version=extension.version_num,
            )
        )

    def get_extension(self, extension_id: UUID) -> TerminalExtension | None:
        record = self._session.scalar(
            select(TerminalExtensionRecord).where(
                TerminalExtensionRecord.id == extension_id,
                TerminalExtensionRecord.tenant_id == self._tenant_id,
            )
        )
        return self._to_extension(record) if record is not None else None

    def save_extension(
        self,
        extension: TerminalExtension,
        *,
        expected_version: int,
    ) -> None:
        self._require_tenant(extension.tenant_id)
        result = self._session.execute(
            update(TerminalExtensionRecord)
            .where(
                TerminalExtensionRecord.id == extension.id,
                TerminalExtensionRecord.tenant_id == extension.tenant_id,
                TerminalExtensionRecord.version == expected_version,
            )
            .values(
                signature_ref=extension.signature_ref,
                status=extension.status.value,
                declared_capabilities_json=sorted(extension.declared_capabilities),
                declared_actions_json=sorted(extension.declared_actions),
                allowed_surfaces_json=sorted(extension.allowed_surfaces),
                data_scope=extension.data_scope,
                updated_at=extension.updated_at,
                version=extension.version_num,
            )
        )
        if result.rowcount != 1:
            raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                "terminal extension version conflict",
            )

    def list_extensions(self, *, tenant_id: UUID) -> list[TerminalExtension]:
        self._require_tenant(tenant_id)
        records = self._session.scalars(
            select(TerminalExtensionRecord).where(
                TerminalExtensionRecord.tenant_id == self._tenant_id,
            )
        ).all()
        return [self._to_extension(record) for record in records]

    @staticmethod
    def _to_extension(record: TerminalExtensionRecord) -> TerminalExtension:
        return TerminalExtension(
            id=record.id,
            tenant_id=record.tenant_id,
            extension_key=record.extension_key,
            version=record.extension_version,
            signature_ref=record.signature_ref,
            status=ExtensionStatus(record.status),
            declared_capabilities=frozenset(record.declared_capabilities_json or ()),
            declared_actions=frozenset(record.declared_actions_json or ()),
            allowed_surfaces=frozenset(record.allowed_surfaces_json or ()),
            data_scope=record.data_scope,
            created_at=record.created_at,
            updated_at=record.updated_at,
            version_num=record.version,
        )
