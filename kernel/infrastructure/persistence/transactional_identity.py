"""Transactional SQLAlchemy composition for Identity commands."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from datetime import datetime
from typing import TypeVar
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from kernel.identity.models import (
    AIEmployeeProfile,
    AssignmentMode,
    CredentialValidationView,
    ExternalRef,
    SessionValidationView,
    Subject,
    SubjectKind,
)
from kernel.identity.service import IdentityService
from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
from kernel.infrastructure.persistence.identity_repository import (
    SQLAlchemyIdentityRepository,
)
from kernel.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from kernel.shared.context import ExecutionContext
from kernel.shared.errors import ErrorCode
from kernel.shared.results import KernelResult

T = TypeVar("T")


class TransactionalIdentityService:
    """Run each Identity call in one atomic SQLAlchemy Unit of Work."""

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        *,
        platform_governors: set[UUID] | frozenset[UUID] | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._platform_governors = frozenset(platform_governors or ())

    def register_subject(
        self,
        ctx: ExecutionContext,
        *,
        subject_type: SubjectKind | str,
        display_name: str,
        external_refs: Sequence[ExternalRef] | None = None,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.register_subject(
                ctx,
                subject_type=subject_type,
                display_name=display_name,
                external_refs=external_refs,
            ),
            conflict_code=ErrorCode.IDENTITY_DUPLICATE,
        )

    def grant_platform_governor(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.grant_platform_governor(
                ctx,
                subject_id=subject_id,
            ),
            conflict_code=ErrorCode.IDENTITY_GOVERNOR_CONFLICT,
        )

    def revoke_platform_governor(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID,
        reason: str,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.revoke_platform_governor(
                ctx,
                subject_id=subject_id,
                reason=reason,
            ),
        )

    def register_ai_employee(
        self,
        ctx: ExecutionContext,
        *,
        display_name: str,
        capabilities_profile: str = "default",
        owner_policy: str = "platform",
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.register_ai_employee(
                ctx,
                display_name=display_name,
                capabilities_profile=capabilities_profile,
                owner_policy=owner_policy,
            ),
            conflict_code=ErrorCode.IDENTITY_DUPLICATE,
        )

    def get_ai_profile(
        self,
        ctx: ExecutionContext,
        *,
        ai_subject_id: UUID,
    ) -> KernelResult[AIEmployeeProfile]:
        return self._execute(
            ctx,
            lambda service: service.get_ai_profile(
                ctx,
                ai_subject_id=ai_subject_id,
            ),
        )

    def update_ai_profile(
        self,
        ctx: ExecutionContext,
        *,
        ai_subject_id: UUID,
        expected_version: int,
        capabilities_profile: str,
        owner_policy: str,
    ) -> KernelResult[AIEmployeeProfile]:
        return self._execute(
            ctx,
            lambda service: service.update_ai_profile(
                ctx,
                ai_subject_id=ai_subject_id,
                expected_version=expected_version,
                capabilities_profile=capabilities_profile,
                owner_policy=owner_policy,
            ),
            conflict_code=ErrorCode.IDENTITY_AI_PROFILE_CONFLICT,
        )

    def resolve_subject(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID | None = None,
        external_ref: ExternalRef | None = None,
    ) -> KernelResult[Subject]:
        return self._execute(
            ctx,
            lambda service: service.resolve_subject(
                ctx,
                subject_id=subject_id,
                external_ref=external_ref,
            ),
        )

    def bind_credential(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID,
        credential_kind: str,
        secret_handle: str,
        expires_at: datetime | None = None,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.bind_credential(
                ctx,
                subject_id=subject_id,
                credential_kind=credential_kind,
                secret_handle=secret_handle,
                expires_at=expires_at,
            ),
        )

    def validate_credential(
        self,
        ctx: ExecutionContext,
        *,
        credential_id: UUID,
    ) -> KernelResult[CredentialValidationView]:
        return self._execute(
            ctx,
            lambda service: service.validate_credential(
                ctx,
                credential_id=credential_id,
            ),
        )

    def revoke_credential(
        self,
        ctx: ExecutionContext,
        *,
        credential_id: UUID,
        reason: str,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.revoke_credential(
                ctx,
                credential_id=credential_id,
                reason=reason,
            ),
        )

    def create_session(
        self,
        ctx: ExecutionContext,
        *,
        credential_id: UUID,
        ttl_seconds: int = 3600,
    ) -> KernelResult[dict]:
        return self._execute(
            ctx,
            lambda service: service.create_session(
                ctx,
                credential_id=credential_id,
                ttl_seconds=ttl_seconds,
            ),
        )

    def validate_session(
        self,
        ctx: ExecutionContext,
        *,
        session_id: UUID,
    ) -> KernelResult[SessionValidationView]:
        return self._execute(
            ctx,
            lambda service: service.validate_session(
                ctx,
                session_id=session_id,
            ),
        )

    def revoke_session(
        self,
        ctx: ExecutionContext,
        *,
        session_id: UUID,
        reason: str,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.revoke_session(
                ctx,
                session_id=session_id,
                reason=reason,
            ),
        )

    def assign_ai_to_tenant(
        self,
        ctx: ExecutionContext,
        *,
        ai_subject_id: UUID,
        management_policy: str = "tenant_managed",
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.assign_ai_to_tenant(
                ctx,
                ai_subject_id=ai_subject_id,
                management_policy=management_policy,
            ),
            conflict_code=ErrorCode.IDENTITY_AI_ASSIGNMENT_CONFLICT,
        )

    def reassign_ai(
        self,
        ctx: ExecutionContext,
        *,
        ai_subject_id: UUID,
        to_tenant_id: UUID | None = None,
        mode: AssignmentMode | str = AssignmentMode.REASSIGN,
        management_policy: str = "tenant_managed",
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.reassign_ai(
                ctx,
                ai_subject_id=ai_subject_id,
                to_tenant_id=to_tenant_id,
                mode=mode,
                management_policy=management_policy,
            ),
            conflict_code=ErrorCode.IDENTITY_AI_ASSIGNMENT_CONFLICT,
        )

    def _execute(
        self,
        ctx: ExecutionContext,
        operation: Callable[[IdentityService], KernelResult[T]],
        *,
        conflict_code: ErrorCode = ErrorCode.COMMON_CONFLICT,
    ) -> KernelResult[T]:
        try:
            with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
                try:
                    repository = SQLAlchemyIdentityRepository(
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

                result = operation(
                    IdentityService(
                        repository=repository,
                        audit_log=audit_log,
                        platform_governors=self._platform_governors,
                    )
                )
                if not result.ok:
                    return result
                unit_of_work.commit()
                return result
        except IntegrityError:
            return KernelResult.failure(
                conflict_code,
                "identity persistence conflict",
            )
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL,
                "identity persistence operation failed",
            )
