"""Tenant-bound SQLAlchemy adapter for Brain Repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from eaos_platform.brain.models import BrainInsight, InsightKind
from kernel.infrastructure.persistence.brain_models import BrainInsightRecord
from kernel.shared.errors import ErrorCode, KernelError


class SQLAlchemyBrainRepository:
    def __init__(self, session: Session, *, tenant_id: UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def add_insight(self, insight: BrainInsight) -> None:
        self._require_tenant(insight.tenant_id)
        self._session.add(
            BrainInsightRecord(
                id=insight.id,
                tenant_id=insight.tenant_id,
                kind=insight.kind.value,
                summary=insight.summary,
                confidence=insight.confidence,
                source_ref=insight.source_ref,
                reason=insight.reason,
                advisory=True,
                bias_notes=insight.bias_notes,
                twin_ref=insight.twin_ref,
                knowledge_refs_json=list(insight.knowledge_refs),
                details_json=dict(insight.details),
                created_at=insight.created_at,
                updated_at=insight.updated_at,
                version=insight.version,
            )
        )

    def get_insight(self, insight_id: UUID) -> BrainInsight | None:
        record = self._session.scalar(
            select(BrainInsightRecord).where(
                BrainInsightRecord.id == insight_id,
                BrainInsightRecord.tenant_id == self._tenant_id,
            )
        )
        return self._to_insight(record) if record is not None else None

    def _require_tenant(self, tenant_id: UUID) -> None:
        if tenant_id != self._tenant_id:
            raise KernelError(ErrorCode.COMMON_INTERNAL, "tenant boundary violation")

    @staticmethod
    def _to_insight(record: BrainInsightRecord) -> BrainInsight:
        return BrainInsight(
            id=record.id,
            tenant_id=record.tenant_id,
            kind=InsightKind(record.kind),
            summary=record.summary,
            confidence=float(record.confidence),
            source_ref=record.source_ref,
            reason=record.reason,
            advisory=bool(record.advisory),
            created_at=record.created_at,
            updated_at=record.updated_at,
            bias_notes=record.bias_notes,
            twin_ref=record.twin_ref,
            knowledge_refs=list(record.knowledge_refs_json),
            details=dict(record.details_json),
            version=record.version,
        )
