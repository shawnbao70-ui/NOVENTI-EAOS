"""Tenant-bound SQLAlchemy adapter for Knowledge Repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from eaos_platform.knowledge.models import (
    KnowledgeEntity,
    KnowledgeLayer,
    KnowledgeLink,
    KnowledgeStatus,
    ProvenanceRecord,
)
from kernel.infrastructure.persistence.knowledge_models import (
    KnowledgeEntityRecord,
    KnowledgeLinkRecord,
    KnowledgeProvenanceRecord,
)
from kernel.shared.errors import ErrorCode, KernelError


class SQLAlchemyKnowledgeRepository:
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

    def add_entity(self, entity: KnowledgeEntity) -> None:
        self._require_tenant_scope(entity.tenant_id)
        self._session.add(self._entity_record(entity))

    def get_entity(self, entity_id: UUID) -> KnowledgeEntity | None:
        record = self._session.scalar(
            self._scoped_entities().where(KnowledgeEntityRecord.id == entity_id)
        )
        return self._to_entity(record) if record is not None else None

    def find_entity_by_type_name(
        self,
        *,
        tenant_id: UUID,
        entity_type: str,
        name: str,
    ) -> KnowledgeEntity | None:
        self._require_tenant_scope(tenant_id)
        record = self._session.scalar(
            select(KnowledgeEntityRecord).where(
                KnowledgeEntityRecord.tenant_id == tenant_id,
                KnowledgeEntityRecord.entity_type == entity_type,
                KnowledgeEntityRecord.name == name,
                KnowledgeEntityRecord.status == KnowledgeStatus.ACTIVE.value,
            )
        )
        if record is None:
            # Case-insensitive fallback for SQLite / mixed case callers.
            for candidate in self._session.scalars(
                select(KnowledgeEntityRecord).where(
                    KnowledgeEntityRecord.tenant_id == tenant_id,
                    KnowledgeEntityRecord.status == KnowledgeStatus.ACTIVE.value,
                )
            ):
                if (
                    candidate.entity_type.casefold() == entity_type.casefold()
                    and candidate.name.casefold() == name.casefold()
                ):
                    return self._to_entity(candidate)
            return None
        return self._to_entity(record)

    def save_entity(
        self,
        entity: KnowledgeEntity,
        *,
        expected_version: int,
    ) -> None:
        self._require_tenant_scope(entity.tenant_id)
        result = self._session.execute(
            update(KnowledgeEntityRecord)
            .where(
                KnowledgeEntityRecord.id == entity.id,
                KnowledgeEntityRecord.tenant_id == entity.tenant_id,
                KnowledgeEntityRecord.version == expected_version,
            )
            .values(
                entity_type=entity.entity_type,
                name=entity.name,
                layer=entity.layer.value,
                status=entity.status.value,
                attributes=dict(entity.attributes),
                labels=sorted(entity.labels),
                shared_with_subject_ids=[
                    str(subject_id) for subject_id in sorted(entity.shared_with_subject_ids)
                ],
                retain_until=entity.retain_until,
                updated_at=entity.updated_at,
                version=entity.version,
            )
        )
        if result.rowcount != 1:
            raise KernelError(
                ErrorCode.KNOWLEDGE_VERSION_CONFLICT,
                "knowledge entity version conflict",
            )

    def list_entities(self, *, tenant_id: UUID) -> list[KnowledgeEntity]:
        self._require_tenant_scope(tenant_id)
        records = self._session.scalars(
            select(KnowledgeEntityRecord).where(
                KnowledgeEntityRecord.tenant_id == tenant_id
            )
        )
        return [self._to_entity(record) for record in records]

    def add_link(self, link: KnowledgeLink) -> None:
        self._require_tenant_scope(link.tenant_id)
        self._session.add(
            KnowledgeLinkRecord(
                id=link.id,
                tenant_id=link.tenant_id,
                from_entity_id=link.from_entity_id,
                to_entity_id=link.to_entity_id,
                relation_type=link.relation_type,
                status=link.status.value,
                attributes=dict(link.attributes),
                created_at=link.created_at,
                updated_at=link.updated_at,
                version=link.version,
            )
        )

    def get_link(self, link_id: UUID) -> KnowledgeLink | None:
        record = self._session.scalar(
            self._scoped_links().where(KnowledgeLinkRecord.id == link_id)
        )
        return self._to_link(record) if record is not None else None

    def list_links(self, *, tenant_id: UUID) -> list[KnowledgeLink]:
        self._require_tenant_scope(tenant_id)
        records = self._session.scalars(
            select(KnowledgeLinkRecord).where(KnowledgeLinkRecord.tenant_id == tenant_id)
        )
        return [self._to_link(record) for record in records]

    def add_provenance(self, record: ProvenanceRecord) -> None:
        self._require_tenant_scope(record.tenant_id)
        self._session.add(
            KnowledgeProvenanceRecord(
                id=record.id,
                tenant_id=record.tenant_id,
                subject_kind=record.subject_kind,
                subject_id=record.subject_id,
                actor_subject_id=record.actor_subject_id,
                source_ref=record.source_ref,
                reason=record.reason,
                derived=record.derived,
                recorded_at=record.recorded_at,
                details=dict(record.details),
            )
        )

    def list_provenance(
        self,
        *,
        tenant_id: UUID,
        subject_kind: str,
        subject_id: UUID,
    ) -> list[ProvenanceRecord]:
        self._require_tenant_scope(tenant_id)
        records = self._session.scalars(
            select(KnowledgeProvenanceRecord)
            .where(
                KnowledgeProvenanceRecord.tenant_id == tenant_id,
                KnowledgeProvenanceRecord.subject_kind == subject_kind,
                KnowledgeProvenanceRecord.subject_id == subject_id,
            )
            .order_by(KnowledgeProvenanceRecord.recorded_at.asc())
        )
        return [self._to_provenance(item) for item in records]

    def _scoped_entities(self):
        statement = select(KnowledgeEntityRecord)
        if not self._platform_scope:
            statement = statement.where(
                KnowledgeEntityRecord.tenant_id == self._tenant_id
            )
        return statement

    def _scoped_links(self):
        statement = select(KnowledgeLinkRecord)
        if not self._platform_scope:
            statement = statement.where(KnowledgeLinkRecord.tenant_id == self._tenant_id)
        return statement

    def _require_tenant_scope(self, tenant_id: UUID | None) -> None:
        if self._platform_scope:
            raise KernelError(
                ErrorCode.KNOWLEDGE_CROSS_TENANT_FORBIDDEN,
                "knowledge requires a tenant scope",
            )
        if tenant_id != self._tenant_id:
            raise KernelError(
                ErrorCode.KNOWLEDGE_CROSS_TENANT_FORBIDDEN,
                "cross-tenant knowledge access is forbidden",
            )

    @staticmethod
    def _entity_record(entity: KnowledgeEntity) -> KnowledgeEntityRecord:
        return KnowledgeEntityRecord(
            id=entity.id,
            tenant_id=entity.tenant_id,
            entity_type=entity.entity_type,
            name=entity.name,
            layer=entity.layer.value,
            status=entity.status.value,
            attributes=dict(entity.attributes),
            labels=sorted(entity.labels),
            shared_with_subject_ids=[
                str(subject_id) for subject_id in sorted(entity.shared_with_subject_ids)
            ],
            retain_until=entity.retain_until,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            version=entity.version,
        )

    @staticmethod
    def _to_entity(record: KnowledgeEntityRecord) -> KnowledgeEntity:
        return KnowledgeEntity(
            id=record.id,
            tenant_id=record.tenant_id,
            entity_type=record.entity_type,
            name=record.name,
            layer=KnowledgeLayer(record.layer),
            status=KnowledgeStatus(record.status),
            attributes=dict(record.attributes or {}),
            labels=frozenset(record.labels or ()),
            shared_with_subject_ids=frozenset(
                UUID(value) for value in (record.shared_with_subject_ids or ())
            ),
            retain_until=record.retain_until,
            created_at=record.created_at,
            updated_at=record.updated_at,
            version=record.version,
        )

    @staticmethod
    def _to_link(record: KnowledgeLinkRecord) -> KnowledgeLink:
        return KnowledgeLink(
            id=record.id,
            tenant_id=record.tenant_id,
            from_entity_id=record.from_entity_id,
            to_entity_id=record.to_entity_id,
            relation_type=record.relation_type,
            status=KnowledgeStatus(record.status),
            attributes=dict(record.attributes or {}),
            created_at=record.created_at,
            updated_at=record.updated_at,
            version=record.version,
        )

    @staticmethod
    def _to_provenance(record: KnowledgeProvenanceRecord) -> ProvenanceRecord:
        return ProvenanceRecord(
            id=record.id,
            tenant_id=record.tenant_id,
            subject_kind=record.subject_kind,
            subject_id=record.subject_id,
            actor_subject_id=record.actor_subject_id,
            source_ref=record.source_ref,
            reason=record.reason,
            derived=record.derived,
            recorded_at=record.recorded_at,
            details=dict(record.details or {}),
        )
