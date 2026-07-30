"""Transactional SQLAlchemy composition for Enterprise Brain commands."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from eaos_platform.brain.models import BrainInsight
from eaos_platform.brain.service import BrainService
from eaos_platform.twin.service import TwinService
from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
from kernel.infrastructure.persistence.brain_repository import SQLAlchemyBrainRepository
from kernel.infrastructure.persistence.identity_permission import (
    SQLAlchemyPrincipalEligibility,
)
from kernel.infrastructure.persistence.permission_repository import (
    SQLAlchemyPermissionRepository,
)
from kernel.infrastructure.persistence.twin_repository import SQLAlchemyTwinRepository
from kernel.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext
from kernel.shared.errors import ErrorCode
from kernel.shared.results import KernelResult

T = TypeVar("T")


class TransactionalBrainService:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def publish_insight(
        self,
        ctx: ExecutionContext,
        *,
        kind: str,
        summary: str,
        confidence: float,
        source_ref: str,
        reason: str,
        bias_notes: str = "",
        twin_ref: UUID | None = None,
        knowledge_refs: list[str] | None = None,
        details: Mapping[str, Any] | None = None,
        advisory: bool = True,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.publish_insight(
                ctx,
                kind=kind,
                summary=summary,
                confidence=confidence,
                source_ref=source_ref,
                reason=reason,
                bias_notes=bias_notes,
                twin_ref=twin_ref,
                knowledge_refs=knowledge_refs,
                details=details,
                advisory=advisory,
            ),
        )

    def get_insight(
        self,
        ctx: ExecutionContext,
        *,
        insight_id: UUID,
    ) -> KernelResult[BrainInsight]:
        return self._execute(
            ctx,
            lambda service: service.get_insight(ctx, insight_id=insight_id),
        )

    def request_execution(
        self,
        ctx: ExecutionContext,
        *,
        insight_id: UUID,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.request_execution(ctx, insight_id=insight_id),
        )

    def _execute(
        self,
        ctx: ExecutionContext,
        operation: Callable[[BrainService], KernelResult[T]],
    ) -> KernelResult[T]:
        if ctx.tenant_id is None or ctx.platform_scope:
            return KernelResult.failure(
                ErrorCode.CTX_INVALID,
                "Enterprise Brain requires tenant data-plane context",
            )
        try:
            with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
                audit_log = SQLAlchemyAuditLog(
                    unit_of_work.session,
                    tenant_id=ctx.tenant_id,
                )
                permission = PermissionService(
                    repository=SQLAlchemyPermissionRepository(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                    ),
                    audit_log=audit_log,
                    principal_eligibility=SQLAlchemyPrincipalEligibility(
                        unit_of_work.session
                    ),
                )
                twin = TwinService(
                    permission,
                    repository=SQLAlchemyTwinRepository(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                    ),
                    audit_log=audit_log,
                )
                result = operation(
                    BrainService(
                        permission,
                        repository=SQLAlchemyBrainRepository(
                            unit_of_work.session,
                            tenant_id=ctx.tenant_id,
                        ),
                        audit_log=audit_log,
                        twin_reader=twin,
                    )
                )
                if not result.ok:
                    if result.error_code in {
                        ErrorCode.PERMISSION_DENIED,
                        ErrorCode.BRAIN_NOT_FOUND,
                        ErrorCode.BRAIN_PROVENANCE_REQUIRED,
                        ErrorCode.BRAIN_CONFIDENCE_INVALID,
                        ErrorCode.BRAIN_SECRET_DENIED,
                        ErrorCode.BRAIN_EXECUTION_FORBIDDEN,
                        ErrorCode.BRAIN_ADVISORY_REQUIRED,
                        ErrorCode.TWIN_NOT_FOUND,
                    }:
                        unit_of_work.commit()
                    return result
                unit_of_work.commit()
                return result
        except IntegrityError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "Enterprise Brain persistence conflict",
            )
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL,
                "Enterprise Brain persistence operation failed",
            )
