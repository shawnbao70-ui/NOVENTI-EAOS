"""In-memory Knowledge repository."""

from __future__ import annotations

from copy import deepcopy
from typing import Optional, Protocol, runtime_checkable
from uuid import UUID

from eaos_platform.knowledge.models import (
    KnowledgeEntity,
    KnowledgeLink,
    KnowledgeStatus,
    ProvenanceRecord,
)
from kernel.shared.errors import ErrorCode, KernelError


@runtime_checkable
class KnowledgeRepository(Protocol):
    def add_entity(self, entity: KnowledgeEntity) -> None: ...

    def get_entity(self, entity_id: UUID) -> Optional[KnowledgeEntity]: ...

    def find_entity_by_type_name(
        self,
        *,
        tenant_id: UUID,
        entity_type: str,
        name: str,
    ) -> Optional[KnowledgeEntity]: ...

    def save_entity(
        self,
        entity: KnowledgeEntity,
        *,
        expected_version: int,
    ) -> None: ...

    def list_entities(self, *, tenant_id: UUID) -> list[KnowledgeEntity]: ...

    def add_link(self, link: KnowledgeLink) -> None: ...

    def get_link(self, link_id: UUID) -> Optional[KnowledgeLink]: ...

    def list_links(self, *, tenant_id: UUID) -> list[KnowledgeLink]: ...

    def add_provenance(self, record: ProvenanceRecord) -> None: ...

    def list_provenance(
        self,
        *,
        tenant_id: UUID,
        subject_kind: str,
        subject_id: UUID,
    ) -> list[ProvenanceRecord]: ...


class InMemoryKnowledgeRepository:
    def __init__(self) -> None:
        self.entities: dict[UUID, KnowledgeEntity] = {}
        self.links: dict[UUID, KnowledgeLink] = {}
        self.provenance: list[ProvenanceRecord] = []

    def add_entity(self, entity: KnowledgeEntity) -> None:
        self.entities[entity.id] = deepcopy(entity)

    def get_entity(self, entity_id: UUID) -> Optional[KnowledgeEntity]:
        entity = self.entities.get(entity_id)
        return deepcopy(entity) if entity is not None else None

    def find_entity_by_type_name(
        self,
        *,
        tenant_id: UUID,
        entity_type: str,
        name: str,
    ) -> Optional[KnowledgeEntity]:
        for entity in self.entities.values():
            if (
                entity.tenant_id == tenant_id
                and entity.entity_type.casefold() == entity_type.casefold()
                and entity.name.casefold() == name.casefold()
                and entity.status == KnowledgeStatus.ACTIVE
            ):
                return deepcopy(entity)
        return None

    def save_entity(
        self,
        entity: KnowledgeEntity,
        *,
        expected_version: int,
    ) -> None:
        current = self.entities.get(entity.id)
        if current is None or current.version != expected_version:
            raise KernelError(
                ErrorCode.KNOWLEDGE_VERSION_CONFLICT,
                "knowledge entity version conflict",
            )
        self.entities[entity.id] = deepcopy(entity)

    def list_entities(self, *, tenant_id: UUID) -> list[KnowledgeEntity]:
        return [
            deepcopy(entity)
            for entity in self.entities.values()
            if entity.tenant_id == tenant_id
        ]

    def add_link(self, link: KnowledgeLink) -> None:
        self.links[link.id] = deepcopy(link)

    def get_link(self, link_id: UUID) -> Optional[KnowledgeLink]:
        link = self.links.get(link_id)
        return deepcopy(link) if link is not None else None

    def list_links(self, *, tenant_id: UUID) -> list[KnowledgeLink]:
        return [
            deepcopy(link) for link in self.links.values() if link.tenant_id == tenant_id
        ]

    def add_provenance(self, record: ProvenanceRecord) -> None:
        self.provenance.append(deepcopy(record))

    def list_provenance(
        self,
        *,
        tenant_id: UUID,
        subject_kind: str,
        subject_id: UUID,
    ) -> list[ProvenanceRecord]:
        return [
            deepcopy(record)
            for record in self.provenance
            if record.tenant_id == tenant_id
            and record.subject_kind == subject_kind
            and record.subject_id == subject_id
        ]
