"""Tenant-bound SQLAlchemy adapter for Twin Repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from eaos_platform.twin.models import TwinSnapshot, TwinSnapshotStatus
from kernel.infrastructure.persistence.twin_models import TwinSnapshotRecord
from kernel.shared.errors import ErrorCode, KernelError


class SQLAlchemyTwinRepository:
    def __init__(self, session: Session, *, tenant_id: UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def add_snapshot(self, snapshot: TwinSnapshot) -> None:
        self._require_tenant(snapshot.tenant_id)
        self._session.add(
            TwinSnapshotRecord(
                id=snapshot.id,
                tenant_id=snapshot.tenant_id,
                entity_ref=snapshot.entity_ref,
                state_json=dict(snapshot.state),
                source_ref=snapshot.source_ref,
                reason=snapshot.reason,
                confidence=snapshot.confidence,
                status=snapshot.status.value,
                valid_from=snapshot.valid_from,
                valid_until=snapshot.valid_until,
                created_at=snapshot.created_at,
                updated_at=snapshot.updated_at,
                version=snapshot.version,
            )
        )

    def get_snapshot(self, snapshot_id: UUID) -> TwinSnapshot | None:
        record = self._session.scalar(
            select(TwinSnapshotRecord).where(
                TwinSnapshotRecord.id == snapshot_id,
                TwinSnapshotRecord.tenant_id == self._tenant_id,
            )
        )
        return self._to_snapshot(record) if record is not None else None

    def get_active_by_entity_ref(
        self,
        *,
        tenant_id: UUID,
        entity_ref: str,
    ) -> TwinSnapshot | None:
        self._require_tenant(tenant_id)
        record = self._session.scalar(
            select(TwinSnapshotRecord).where(
                TwinSnapshotRecord.tenant_id == tenant_id,
                TwinSnapshotRecord.entity_ref == entity_ref,
                TwinSnapshotRecord.status == TwinSnapshotStatus.ACTIVE.value,
            )
        )
        return self._to_snapshot(record) if record is not None else None

    def save_snapshot(
        self,
        snapshot: TwinSnapshot,
        *,
        expected_version: int,
    ) -> None:
        self._require_tenant(snapshot.tenant_id)
        result = self._session.execute(
            update(TwinSnapshotRecord)
            .where(
                TwinSnapshotRecord.id == snapshot.id,
                TwinSnapshotRecord.tenant_id == snapshot.tenant_id,
                TwinSnapshotRecord.version == expected_version,
            )
            .values(
                status=snapshot.status.value,
                updated_at=snapshot.updated_at,
                version=snapshot.version,
            )
        )
        if result.rowcount != 1:
            raise KernelError(ErrorCode.COMMON_CONFLICT, "twin snapshot version conflict")

    def _require_tenant(self, tenant_id: UUID) -> None:
        if tenant_id != self._tenant_id:
            raise KernelError(ErrorCode.COMMON_INTERNAL, "tenant boundary violation")

    @staticmethod
    def _to_snapshot(record: TwinSnapshotRecord) -> TwinSnapshot:
        return TwinSnapshot(
            id=record.id,
            tenant_id=record.tenant_id,
            entity_ref=record.entity_ref,
            state=dict(record.state_json),
            source_ref=record.source_ref,
            reason=record.reason,
            confidence=float(record.confidence),
            status=TwinSnapshotStatus(record.status),
            created_at=record.created_at,
            updated_at=record.updated_at,
            valid_from=record.valid_from,
            valid_until=record.valid_until,
            version=record.version,
        )
