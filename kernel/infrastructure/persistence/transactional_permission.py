"""Transactional SQLAlchemy composition for Permission commands."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import TypeVar
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from kernel.event_bus.domain_emit import DomainEventEmitter
from kernel.infrastructure.persistence.event_repository import SQLAlchemyOutboxWriter
from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
from kernel.infrastructure.persistence.identity_permission import (
    SQLAlchemyPrincipalEligibility,
)
from kernel.infrastructure.persistence.organization_permission import (
    SQLAlchemyScopeResolver,
)
from kernel.infrastructure.persistence.permission_repository import (
    SQLAlchemyPermissionRepository,
)
from kernel.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from kernel.permission.models import Grant, PermissionDecision, PolicyRule, Resource, ScopeLevel
from kernel.permission.ports import ConditionEvaluator
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext
from kernel.shared.errors import ErrorCode
from kernel.shared.results import KernelResult

T = TypeVar("T")


class TransactionalPermissionService:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        *,
        grant_administrators: set[UUID] | frozenset[UUID] | None = None,
        decision_auditors: set[UUID] | frozenset[UUID] | None = None,
        condition_evaluator: ConditionEvaluator | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._grant_administrators = frozenset(grant_administrators or ())
        self._decision_auditors = frozenset(decision_auditors or ())
        self._condition_evaluator = condition_evaluator

    def grant(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        resource_type: str,
        actions: set[str] | frozenset[str],
        resource_id: UUID | None = None,
        scope_level: ScopeLevel = ScopeLevel.RESOURCE,
        enterprise_id: UUID | None = None,
        org_unit_id: UUID | None = None,
        conditions_ref: str | None = None,
        expires_at: datetime | None = None,
        delegable: bool = False,
        remaining_depth: int = 0,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.grant(
                ctx,
                principal_subject_id=principal_subject_id,
                resource_type=resource_type,
                actions=actions,
                resource_id=resource_id,
                scope_level=scope_level,
                enterprise_id=enterprise_id,
                org_unit_id=org_unit_id,
                conditions_ref=conditions_ref,
                expires_at=expires_at,
                delegable=delegable,
                remaining_depth=remaining_depth,
            ),
            conflict_code=ErrorCode.PERMISSION_GRANT_CONFLICT,
        )

    def revoke(
        self,
        ctx: ExecutionContext,
        *,
        grant_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.revoke(
                ctx,
                grant_id=grant_id,
                reason=reason,
                expected_version=expected_version,
            ),
        )

    def create_policy(
        self,
        ctx: ExecutionContext,
        *,
        name: str,
        policy_version: str,
        rules: list[PolicyRule],
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.create_policy(
                ctx,
                name=name,
                policy_version=policy_version,
                rules=rules,
            ),
            conflict_code=ErrorCode.PERMISSION_POLICY_CONFLICT,
        )

    def activate_policy(
        self,
        ctx: ExecutionContext,
        *,
        policy_id: UUID,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.activate_policy(
                ctx,
                policy_id=policy_id,
                expected_version=expected_version,
            ),
        )

    def deprecate_policy(
        self,
        ctx: ExecutionContext,
        *,
        policy_id: UUID,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.deprecate_policy(
                ctx,
                policy_id=policy_id,
                expected_version=expected_version,
            ),
        )

    def delegate(
        self,
        ctx: ExecutionContext,
        *,
        parent_grant_id: UUID,
        to_principal_subject_id: UUID,
        actions: set[str] | frozenset[str] | None = None,
        scope_level: ScopeLevel | None = None,
        enterprise_id: UUID | None = None,
        org_unit_id: UUID | None = None,
        resource_id: UUID | None = None,
        expires_at: datetime | None = None,
        conditions_ref: str | None = None,
        remaining_depth: int | None = None,
        delegable: bool = False,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.delegate(
                ctx,
                parent_grant_id=parent_grant_id,
                to_principal_subject_id=to_principal_subject_id,
                actions=actions,
                scope_level=scope_level,
                enterprise_id=enterprise_id,
                org_unit_id=org_unit_id,
                resource_id=resource_id,
                expires_at=expires_at,
                conditions_ref=conditions_ref,
                remaining_depth=remaining_depth,
                delegable=delegable,
            ),
            conflict_code=ErrorCode.PERMISSION_GRANT_CONFLICT,
        )

    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        action: str,
        resource: Resource,
    ) -> KernelResult[PermissionDecision]:
        return self._execute(
            ctx,
            lambda service: service.evaluate(
                ctx,
                principal_subject_id=principal_subject_id,
                action=action,
                resource=resource,
            ),
        )

    def explain(
        self,
        ctx: ExecutionContext,
        *,
        decision_id: UUID,
    ) -> KernelResult[dict[str, str]]:
        return self._execute(
            ctx,
            lambda service: service.explain(ctx, decision_id=decision_id),
        )

    def list_effective(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        resource_type: str | None = None,
    ) -> KernelResult[list[Grant]]:
        return self._execute(
            ctx,
            lambda service: service.list_effective(
                ctx,
                principal_subject_id=principal_subject_id,
                resource_type=resource_type,
            ),
        )

    def _execute(
        self,
        ctx: ExecutionContext,
        operation: Callable[[PermissionService], KernelResult[T]],
        *,
        conflict_code: ErrorCode = ErrorCode.COMMON_CONFLICT,
    ) -> KernelResult[T]:
        try:
            with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
                try:
                    repository = SQLAlchemyPermissionRepository(
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
                    PermissionService(
                        repository=repository,
                        audit_log=audit_log,
                        grant_administrators=self._grant_administrators,
                        decision_auditors=self._decision_auditors,
                        principal_eligibility=SQLAlchemyPrincipalEligibility(
                            unit_of_work.session
                        ),
                        condition_evaluator=self._condition_evaluator,
                        scope_resolver=SQLAlchemyScopeResolver(unit_of_work.session),
                        domain_events=DomainEventEmitter(
                            SQLAlchemyOutboxWriter(unit_of_work.session)
                        ),
                    )
                )
                if not result.ok:
                    return result
                unit_of_work.commit()
                return result
        except IntegrityError:
            return KernelResult.failure(
                conflict_code,
                "permission persistence conflict",
            )
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL,
                "permission persistence operation failed",
            )
