"""Knowledge Shared Capability service — PHX-K10."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from eaos_platform.knowledge.models import (
    KnowledgeEntity,
    KnowledgeLayer,
    KnowledgeLink,
    KnowledgeStatus,
    ProvenanceRecord,
)
from eaos_platform.knowledge.repository import (
    InMemoryKnowledgeRepository,
    KnowledgeRepository,
)
from kernel.permission.models import PermissionEffect, Resource
from kernel.permission.service import PermissionService
from kernel.event_bus.domain_emit import DomainEventEmitter
from kernel.shared.audit import AuditLog, InMemoryAuditLog
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult

_SECRET_KEYS = {
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
    "private_key",
    "credential",
}


class KnowledgeService:
    """Tenant-safe knowledge graph with provenance and governed retrieval."""

    def __init__(
        self,
        permission_service: PermissionService,
        repository: KnowledgeRepository | None = None,
        audit_log: AuditLog | None = None,
        domain_events: DomainEventEmitter | None = None,
    ) -> None:
        self._permission = permission_service
        self._repo = repository or InMemoryKnowledgeRepository()
        self._audit = audit_log or InMemoryAuditLog()
        self._domain_events = domain_events

    @property
    def audit_log(self) -> AuditLog:
        return self._audit

    def upsert_entity(
        self,
        ctx: ExecutionContext,
        *,
        entity_type: str,
        name: str,
        layer: KnowledgeLayer,
        attributes: dict[str, Any] | None = None,
        labels: set[str] | frozenset[str] | None = None,
        source_ref: str,
        reason: str,
        retain_until: datetime | None = None,
        entity_id: UUID | None = None,
        expected_version: int | None = None,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            cleaned_type = entity_type.strip()
            cleaned_name = name.strip()
            if not cleaned_type or not cleaned_name:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "entity_type and name are required",
                )
            self._require_provenance(source_ref, reason)
            attrs = dict(attributes or {})
            self._reject_secrets(attrs)
            label_set = frozenset(item.strip() for item in (labels or ()) if item.strip())
            if retain_until is not None and retain_until <= datetime.now(timezone.utc):
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "retain_until must be in the future",
                )

            existing = None
            if entity_id is not None:
                existing = self._require_readable_entity(ctx, entity_id, for_write=True)
            else:
                existing = self._repo.find_entity_by_type_name(
                    tenant_id=ctx.tenant_id,
                    entity_type=cleaned_type,
                    name=cleaned_name,
                )

            self._require_permission(
                ctx,
                action="upsert",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="knowledge_entity",
                    resource_id=existing.id if existing is not None else None,
                ),
            )

            now = datetime.now(timezone.utc)
            if existing is None:
                entity = KnowledgeEntity(
                    id=uuid4(),
                    tenant_id=ctx.tenant_id,
                    entity_type=cleaned_type,
                    name=cleaned_name,
                    layer=layer,
                    status=KnowledgeStatus.ACTIVE,
                    attributes=attrs,
                    labels=label_set,
                    retain_until=retain_until,
                    created_at=now,
                    updated_at=now,
                )
                self._repo.add_entity(entity)
            else:
                if existing.layer == KnowledgeLayer.DERIVED and layer != KnowledgeLayer.DERIVED:
                    raise KernelError(
                        ErrorCode.KNOWLEDGE_DERIVED_MISLABELLED,
                        "derived knowledge cannot be relabelled as non-derived in place",
                    )
                if layer == KnowledgeLayer.CANONICAL and existing.layer == KnowledgeLayer.DERIVED:
                    raise KernelError(
                        ErrorCode.KNOWLEDGE_DERIVED_MISLABELLED,
                        "derived knowledge cannot be disguised as canonical",
                    )
                expected = self._require_expected_version(
                    expected_version if expected_version is not None else existing.version
                )
                existing.entity_type = cleaned_type
                existing.name = cleaned_name
                existing.layer = layer
                existing.attributes = attrs
                existing.labels = label_set
                existing.retain_until = retain_until
                existing.updated_at = now
                existing.version = expected + 1
                self._repo.save_entity(existing, expected_version=expected)
                entity = existing

            self._record_provenance(
                ctx,
                subject_kind="entity",
                subject_id=entity.id,
                source_ref=source_ref,
                reason=reason,
                derived=layer == KnowledgeLayer.DERIVED,
                details={"entity_type": cleaned_type, "name": cleaned_name},
            )
            audit = self._audit.record(
                ctx,
                action="Knowledge.UpsertEntity",
                resource=f"knowledge_entity:{entity.id}",
                result="ok",
            )
            self._emit(
                ctx,
                event_name="knowledge.entity.upserted",
                payload={
                    "entity_id": str(entity.id),
                    "entity_type": entity.entity_type,
                    "layer": entity.layer.value,
                    "version": entity.version,
                },
            )
            return KernelResult.success(entity.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def link(
        self,
        ctx: ExecutionContext,
        *,
        from_entity_id: UUID,
        to_entity_id: UUID,
        relation_type: str,
        source_ref: str,
        reason: str,
        attributes: dict[str, Any] | None = None,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            relation = relation_type.strip()
            if not relation:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "relation_type is required",
                )
            if from_entity_id == to_entity_id:
                raise KernelError(
                    ErrorCode.KNOWLEDGE_LINK_INVALID,
                    "self-links are forbidden",
                )
            self._require_provenance(source_ref, reason)
            attrs = dict(attributes or {})
            self._reject_secrets(attrs)
            source = self._require_readable_entity(ctx, from_entity_id, for_write=True)
            target = self._require_readable_entity(ctx, to_entity_id, for_write=True)
            self._require_permission(
                ctx,
                action="create",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="knowledge_link",
                ),
            )
            now = datetime.now(timezone.utc)
            edge = KnowledgeLink(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                from_entity_id=source.id,
                to_entity_id=target.id,
                relation_type=relation,
                status=KnowledgeStatus.ACTIVE,
                attributes=attrs,
                created_at=now,
                updated_at=now,
            )
            self._repo.add_link(edge)
            self._record_provenance(
                ctx,
                subject_kind="link",
                subject_id=edge.id,
                source_ref=source_ref,
                reason=reason,
                derived=False,
                details={
                    "from_entity_id": str(source.id),
                    "to_entity_id": str(target.id),
                    "relation_type": relation,
                },
            )
            audit = self._audit.record(
                ctx,
                action="Knowledge.Link",
                resource=f"knowledge_link:{edge.id}",
                result="ok",
            )
            self._emit(
                ctx,
                event_name="knowledge.link.created",
                payload={
                    "link_id": str(edge.id),
                    "from_entity_id": str(edge.from_entity_id),
                    "to_entity_id": str(edge.to_entity_id),
                    "relation_type": edge.relation_type,
                },
            )
            return KernelResult.success(edge.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_entity(
        self,
        ctx: ExecutionContext,
        *,
        entity_id: UUID,
    ) -> KernelResult[KnowledgeEntity]:
        try:
            entity = self._require_readable_entity(ctx, entity_id, for_write=False)
            self._require_permission(
                ctx,
                action="read",
                resource=Resource(
                    tenant_id=entity.tenant_id,
                    resource_type="knowledge_entity",
                    resource_id=entity.id,
                ),
            )
            return KernelResult.success(entity)
        except KernelError as err:
            return KernelResult.from_error(err)

    def query(
        self,
        ctx: ExecutionContext,
        *,
        entity_type: str | None = None,
        layer: KnowledgeLayer | None = None,
        include_archived: bool = False,
    ) -> KernelResult[list[KnowledgeEntity]]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_permission(
                ctx,
                action="query",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="knowledge_graph",
                    resource_id=ctx.tenant_id,
                ),
            )
            now = datetime.now(timezone.utc)
            results: list[KnowledgeEntity] = []
            for entity in self._repo.list_entities(tenant_id=ctx.tenant_id):
                if not self._is_visible(ctx, entity):
                    continue
                if not include_archived and entity.status != KnowledgeStatus.ACTIVE:
                    continue
                if entity.retain_until is not None and entity.retain_until <= now:
                    continue
                if entity_type and entity.entity_type.casefold() != entity_type.casefold():
                    continue
                if layer is not None and entity.layer != layer:
                    continue
                results.append(entity)
            return KernelResult.success(results)
        except KernelError as err:
            return KernelResult.from_error(err)

    def search(
        self,
        ctx: ExecutionContext,
        *,
        text: str,
    ) -> KernelResult[list[KnowledgeEntity]]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            needle = text.strip().casefold()
            if not needle:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "search text is required",
                )
            self._require_permission(
                ctx,
                action="search",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="knowledge_graph",
                    resource_id=ctx.tenant_id,
                ),
            )
            now = datetime.now(timezone.utc)
            hits: list[KnowledgeEntity] = []
            for entity in self._repo.list_entities(tenant_id=ctx.tenant_id):
                if not self._is_visible(ctx, entity):
                    continue
                if entity.status != KnowledgeStatus.ACTIVE:
                    continue
                if entity.retain_until is not None and entity.retain_until <= now:
                    continue
                haystack = " ".join(
                    [
                        entity.name.casefold(),
                        entity.entity_type.casefold(),
                        " ".join(label.casefold() for label in entity.labels),
                    ]
                )
                if needle in haystack:
                    hits.append(entity)
            return KernelResult.success(hits)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_provenance(
        self,
        ctx: ExecutionContext,
        *,
        subject_kind: str,
        subject_id: UUID,
    ) -> KernelResult[list[ProvenanceRecord]]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            kind = subject_kind.strip().lower()
            if kind not in {"entity", "link"}:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "subject_kind must be entity or link",
                )
            if kind == "entity":
                self._require_readable_entity(ctx, subject_id, for_write=False)
            else:
                link = self._repo.get_link(subject_id)
                if link is None or link.tenant_id != ctx.tenant_id:
                    raise KernelError(
                        ErrorCode.KNOWLEDGE_LINK_NOT_FOUND,
                        "knowledge link not found",
                    )
            self._require_permission(
                ctx,
                action="read",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type="knowledge_provenance",
                    resource_id=subject_id,
                ),
            )
            records = self._repo.list_provenance(
                tenant_id=ctx.tenant_id,
                subject_kind=kind,
                subject_id=subject_id,
            )
            return KernelResult.success(records)
        except KernelError as err:
            return KernelResult.from_error(err)

    def archive_entity(
        self,
        ctx: ExecutionContext,
        *,
        entity_id: UUID,
        reason: str,
        source_ref: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        try:
            self._require_provenance(source_ref, reason)
            entity = self._require_readable_entity(ctx, entity_id, for_write=True)
            self._require_permission(
                ctx,
                action="archive",
                resource=Resource(
                    tenant_id=entity.tenant_id,
                    resource_type="knowledge_entity",
                    resource_id=entity.id,
                ),
            )
            if entity.status == KnowledgeStatus.ARCHIVED:
                return KernelResult.success(True)
            expected = self._require_expected_version(
                expected_version if expected_version is not None else entity.version
            )
            entity.status = KnowledgeStatus.ARCHIVED
            entity.updated_at = datetime.now(timezone.utc)
            entity.version = expected + 1
            self._repo.save_entity(entity, expected_version=expected)
            self._record_provenance(
                ctx,
                subject_kind="entity",
                subject_id=entity.id,
                source_ref=source_ref,
                reason=reason,
                derived=entity.layer == KnowledgeLayer.DERIVED,
                details={"status": "archived"},
            )
            audit = self._audit.record(
                ctx,
                action="Knowledge.ArchiveEntity",
                resource=f"knowledge_entity:{entity.id}",
                result="ok",
            )
            self._emit(
                ctx,
                event_name="knowledge.entity.archived",
                payload={
                    "entity_id": str(entity.id),
                    "version": entity.version,
                    "status": entity.status.value,
                },
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def share(
        self,
        ctx: ExecutionContext,
        *,
        entity_id: UUID,
        share_with_subject_id: UUID,
        source_ref: str,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        try:
            self._require_provenance(source_ref, reason)
            entity = self._require_readable_entity(ctx, entity_id, for_write=True)
            self._require_permission(
                ctx,
                action="share",
                resource=Resource(
                    tenant_id=entity.tenant_id,
                    resource_type="knowledge_entity",
                    resource_id=entity.id,
                ),
            )
            expected = self._require_expected_version(
                expected_version if expected_version is not None else entity.version
            )
            shared = set(entity.shared_with_subject_ids)
            shared.add(share_with_subject_id)
            entity.shared_with_subject_ids = frozenset(shared)
            entity.updated_at = datetime.now(timezone.utc)
            entity.version = expected + 1
            self._repo.save_entity(entity, expected_version=expected)
            self._record_provenance(
                ctx,
                subject_kind="entity",
                subject_id=entity.id,
                source_ref=source_ref,
                reason=reason,
                derived=False,
                details={"shared_with": str(share_with_subject_id)},
            )
            audit = self._audit.record(
                ctx,
                action="Knowledge.Share",
                resource=f"knowledge_entity:{entity.id}",
                result="ok",
            )
            self._emit(
                ctx,
                event_name="knowledge.entity.shared",
                payload={
                    "entity_id": str(entity.id),
                    "share_with_subject_id": str(share_with_subject_id),
                    "version": entity.version,
                },
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def _require_readable_entity(
        self,
        ctx: ExecutionContext,
        entity_id: UUID,
        *,
        for_write: bool,
    ) -> KnowledgeEntity:
        require_context(ctx, tenant_data_plane=True)
        entity = self._repo.get_entity(entity_id)
        if entity is None or entity.tenant_id != ctx.tenant_id:
            raise KernelError(
                ErrorCode.KNOWLEDGE_ENTITY_NOT_FOUND,
                "knowledge entity not found",
            )
        if for_write and entity.status != KnowledgeStatus.ACTIVE:
            raise KernelError(
                ErrorCode.KNOWLEDGE_ARCHIVED,
                "archived knowledge cannot be modified",
            )
        if not for_write:
            if entity.status == KnowledgeStatus.ARCHIVED:
                raise KernelError(
                    ErrorCode.KNOWLEDGE_ARCHIVED,
                    "knowledge entity is archived",
                )
            if (
                entity.retain_until is not None
                and entity.retain_until <= datetime.now(timezone.utc)
            ):
                raise KernelError(
                    ErrorCode.KNOWLEDGE_RETENTION_EXPIRED,
                    "knowledge retention window has expired",
                )
            if not self._is_visible(ctx, entity):
                raise KernelError(
                    ErrorCode.KNOWLEDGE_ENTITY_NOT_FOUND,
                    "knowledge entity not found",
                )
        return entity

    def _is_visible(self, ctx: ExecutionContext, entity: KnowledgeEntity) -> bool:
        if ctx.subject_id in entity.shared_with_subject_ids:
            return True
        # Owners with graph-level grants see active tenant knowledge; share is additive.
        return True

    def _require_permission(
        self,
        ctx: ExecutionContext,
        *,
        action: str,
        resource: Resource,
    ) -> None:
        result = self._permission.evaluate(
            ctx,
            principal_subject_id=ctx.subject_id,
            action=action,
            resource=resource,
        )
        if not result.ok:
            raise KernelError(
                result.error_code or ErrorCode.PERMISSION_DENIED,
                result.error_message or "permission evaluation failed",
            )
        if result.data is None or result.data.effect != PermissionEffect.ALLOW:
            raise KernelError(ErrorCode.PERMISSION_DENIED, "permission denied")

    def _record_provenance(
        self,
        ctx: ExecutionContext,
        *,
        subject_kind: str,
        subject_id: UUID,
        source_ref: str,
        reason: str,
        derived: bool,
        details: dict[str, Any],
    ) -> None:
        assert ctx.tenant_id is not None
        self._repo.add_provenance(
            ProvenanceRecord(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                subject_kind=subject_kind,
                subject_id=subject_id,
                actor_subject_id=ctx.subject_id,
                source_ref=source_ref.strip(),
                reason=reason.strip(),
                derived=derived,
                recorded_at=datetime.now(timezone.utc),
                details=details,
            )
        )
        self._emit(
            ctx,
            event_name="knowledge.provenance.recorded",
            payload={
                "subject_kind": subject_kind,
                "subject_id": str(subject_id),
                "derived": derived,
            },
        )

    def _emit(
        self,
        ctx: ExecutionContext,
        *,
        event_name: str,
        payload: dict[str, object],
        tenant_id: UUID | None = None,
    ) -> None:
        if self._domain_events is None:
            return
        self._domain_events.enqueue_fact(
            ctx,
            event_name=event_name,
            producer="knowledge.platform",
            payload=payload,
            tenant_id=tenant_id,
        )

    @staticmethod
    def _require_provenance(source_ref: str, reason: str) -> None:
        if not source_ref.strip() or not reason.strip():
            raise KernelError(
                ErrorCode.KNOWLEDGE_PROVENANCE_REQUIRED,
                "source_ref and reason are required",
            )

    @staticmethod
    def _reject_secrets(attributes: dict[str, Any]) -> None:
        for key in attributes:
            normalized = key.strip().casefold().replace("-", "_")
            if normalized in _SECRET_KEYS or any(
                token in normalized for token in ("password", "secret", "token", "api_key")
            ):
                raise KernelError(
                    ErrorCode.KNOWLEDGE_SECRET_FORBIDDEN,
                    "secrets must not be stored in knowledge attributes",
                )

    @staticmethod
    def _require_expected_version(expected_version: int | None) -> int:
        if expected_version is None or expected_version < 1:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "expected_version must be a positive integer",
            )
        return expected_version
