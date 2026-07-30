"""Transactional SQLAlchemy composition for Knowledge commands."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from eaos_platform.knowledge.models import (
    KnowledgeEntity,
    KnowledgeLayer,
    ProvenanceRecord,
)
from eaos_platform.knowledge.service import KnowledgeService
from kernel.event_bus.domain_emit import DomainEventEmitter
from kernel.infrastructure.persistence.event_repository import SQLAlchemyOutboxWriter
from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
from kernel.infrastructure.persistence.identity_permission import (
    SQLAlchemyPrincipalEligibility,
)
from kernel.infrastructure.persistence.knowledge_repository import (
    SQLAlchemyKnowledgeRepository,
)
from kernel.infrastructure.persistence.permission_repository import (
    SQLAlchemyPermissionRepository,
)
from kernel.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext
from kernel.shared.errors import ErrorCode
from kernel.shared.results import KernelResult

T = TypeVar("T")


class TransactionalKnowledgeService:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def upsert_entity(
        self,
        ctx: ExecutionContext,
        *,
        entity_type: str,
        name: str,
        layer: KnowledgeLayer,
        source_ref: str,
        reason: str,
        attributes: dict[str, Any] | None = None,
        labels: set[str] | frozenset[str] | None = None,
        retain_until: datetime | None = None,
        entity_id: UUID | None = None,
        expected_version: int | None = None,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.upsert_entity(
                ctx,
                entity_type=entity_type,
                name=name,
                layer=layer,
                attributes=attributes,
                labels=labels,
                source_ref=source_ref,
                reason=reason,
                retain_until=retain_until,
                entity_id=entity_id,
                expected_version=expected_version,
            ),
            conflict_code=ErrorCode.KNOWLEDGE_ENTITY_CONFLICT,
        )

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
        return self._execute(
            ctx,
            lambda service: service.link(
                ctx,
                from_entity_id=from_entity_id,
                to_entity_id=to_entity_id,
                relation_type=relation_type,
                source_ref=source_ref,
                reason=reason,
                attributes=attributes,
            ),
            conflict_code=ErrorCode.KNOWLEDGE_LINK_INVALID,
        )

    def get_entity(
        self,
        ctx: ExecutionContext,
        *,
        entity_id: UUID,
    ) -> KernelResult[KnowledgeEntity]:
        return self._execute(
            ctx,
            lambda service: service.get_entity(ctx, entity_id=entity_id),
        )

    def query(
        self,
        ctx: ExecutionContext,
        *,
        entity_type: str | None = None,
        layer: KnowledgeLayer | None = None,
        include_archived: bool = False,
    ) -> KernelResult[list[KnowledgeEntity]]:
        return self._execute(
            ctx,
            lambda service: service.query(
                ctx,
                entity_type=entity_type,
                layer=layer,
                include_archived=include_archived,
            ),
        )

    def search(
        self,
        ctx: ExecutionContext,
        *,
        text: str,
    ) -> KernelResult[list[KnowledgeEntity]]:
        return self._execute(
            ctx,
            lambda service: service.search(ctx, text=text),
        )

    def get_provenance(
        self,
        ctx: ExecutionContext,
        *,
        subject_kind: str,
        subject_id: UUID,
    ) -> KernelResult[list[ProvenanceRecord]]:
        return self._execute(
            ctx,
            lambda service: service.get_provenance(
                ctx,
                subject_kind=subject_kind,
                subject_id=subject_id,
            ),
        )

    def archive_entity(
        self,
        ctx: ExecutionContext,
        *,
        entity_id: UUID,
        reason: str,
        source_ref: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.archive_entity(
                ctx,
                entity_id=entity_id,
                reason=reason,
                source_ref=source_ref,
                expected_version=expected_version,
            ),
        )

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
        return self._execute(
            ctx,
            lambda service: service.share(
                ctx,
                entity_id=entity_id,
                share_with_subject_id=share_with_subject_id,
                source_ref=source_ref,
                reason=reason,
                expected_version=expected_version,
            ),
        )

    def _execute(
        self,
        ctx: ExecutionContext,
        operation: Callable[[KnowledgeService], KernelResult[T]],
        *,
        conflict_code: ErrorCode = ErrorCode.COMMON_CONFLICT,
    ) -> KernelResult[T]:
        try:
            with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
                try:
                    knowledge_repository = SQLAlchemyKnowledgeRepository(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                        platform_scope=ctx.platform_scope,
                    )
                    permission_repository = SQLAlchemyPermissionRepository(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                        platform_scope=ctx.platform_scope,
                    )
                    audit_log = SQLAlchemyAuditLog(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                        platform_scope=ctx.platform_scope,
                    )
                except ValueError:
                    return KernelResult.failure(
                        ErrorCode.CTX_INVALID,
                        "execution context has an invalid persistence scope",
                    )
                permission = PermissionService(
                    repository=permission_repository,
                    audit_log=audit_log,
                    principal_eligibility=SQLAlchemyPrincipalEligibility(
                        unit_of_work.session
                    ),
                    domain_events=DomainEventEmitter(
                        SQLAlchemyOutboxWriter(unit_of_work.session)
                    ),
                )
                result = operation(
                    KnowledgeService(
                        permission,
                        repository=knowledge_repository,
                        audit_log=audit_log,
                        domain_events=DomainEventEmitter(
                            SQLAlchemyOutboxWriter(unit_of_work.session)
                        ),
                    )
                )
                if not result.ok:
                    if result.error_code == ErrorCode.PERMISSION_DENIED:
                        unit_of_work.commit()
                    return result
                unit_of_work.commit()
                return result
        except IntegrityError:
            return KernelResult.failure(conflict_code, "knowledge persistence conflict")
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL,
                "knowledge persistence operation failed",
            )
