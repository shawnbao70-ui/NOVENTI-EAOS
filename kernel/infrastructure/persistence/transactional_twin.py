"""Transactional SQLAlchemy composition for Digital Twin commands."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime
from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from eaos_platform.twin.models import TwinSnapshot
from eaos_platform.twin.service import TwinService
from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
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


class TransactionalTwinService:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def upsert_snapshot(
        self,
        ctx: ExecutionContext,
        *,
        entity_ref: str,
        state: Mapping[str, Any],
        source_ref: str,
        reason: str,
        confidence: float,
        valid_from: datetime | None = None,
        valid_until: datetime | None = None,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.upsert_snapshot(
                ctx,
                entity_ref=entity_ref,
                state=state,
                source_ref=source_ref,
                reason=reason,
                confidence=confidence,
                valid_from=valid_from,
                valid_until=valid_until,
            ),
        )

    def get_snapshot(
        self,
        ctx: ExecutionContext,
        *,
        snapshot_id: UUID,
    ) -> KernelResult[TwinSnapshot]:
        return self._execute(
            ctx,
            lambda service: service.get_snapshot(ctx, snapshot_id=snapshot_id),
        )

    def authorize_from_twin(
        self,
        ctx: ExecutionContext,
        *,
        snapshot_id: UUID,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.authorize_from_twin(ctx, snapshot_id=snapshot_id),
        )

    def _execute(
        self,
        ctx: ExecutionContext,
        operation: Callable[[TwinService], KernelResult[T]],
    ) -> KernelResult[T]:
        if ctx.tenant_id is None or ctx.platform_scope:
            return KernelResult.failure(
                ErrorCode.CTX_INVALID,
                "Digital Twin requires tenant data-plane context",
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
                result = operation(
                    TwinService(
                        permission,
                        repository=SQLAlchemyTwinRepository(
                            unit_of_work.session,
                            tenant_id=ctx.tenant_id,
                        ),
                        audit_log=audit_log,
                    )
                )
                if not result.ok:
                    if result.error_code in {
                        ErrorCode.PERMISSION_DENIED,
                        ErrorCode.TWIN_NOT_FOUND,
                        ErrorCode.TWIN_PROVENANCE_REQUIRED,
                        ErrorCode.TWIN_CONFIDENCE_INVALID,
                        ErrorCode.TWIN_SECRET_DENIED,
                        ErrorCode.TWIN_EXECUTION_FORBIDDEN,
                    }:
                        unit_of_work.commit()
                    return result
                unit_of_work.commit()
                return result
        except IntegrityError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "Digital Twin persistence conflict",
            )
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL,
                "Digital Twin persistence operation failed",
            )
