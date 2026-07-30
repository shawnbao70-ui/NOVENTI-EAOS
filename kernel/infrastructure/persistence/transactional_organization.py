"""Transactional SQLAlchemy composition for Organization commands."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar
from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from kernel.event_bus.domain_emit import DomainEventEmitter
from kernel.infrastructure.persistence.event_repository import SQLAlchemyOutboxWriter
from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
from kernel.infrastructure.persistence.organization_repository import (
    SQLAlchemyOrganizationRepository,
)
from kernel.infrastructure.persistence.identity_organization import (
    SQLAlchemyMembershipEligibility,
)
from kernel.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from kernel.organization.models import (
    Enterprise,
    Membership,
    OrganizationStatus,
    OrganizationUnit,
    Tenant,
    UnitType,
)
from kernel.organization.service import OrganizationService
from kernel.shared.context import ExecutionContext
from kernel.shared.errors import ErrorCode
from kernel.shared.results import KernelResult

T = TypeVar("T")


class TransactionalOrganizationService:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        *,
        platform_governors: set[UUID] | frozenset[UUID] | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._platform_governors = frozenset(platform_governors or ())

    def create_tenant(
        self,
        ctx: ExecutionContext,
        *,
        legal_name: str,
        region_policy_ref: str | None = None,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.create_tenant(
                ctx,
                legal_name=legal_name,
                region_policy_ref=region_policy_ref,
            ),
            conflict_code=ErrorCode.ORG_TENANT_DUPLICATE_NAME,
        )

    def get_tenant(self, ctx: ExecutionContext, *, tenant_id: UUID) -> KernelResult[Tenant]:
        return self._execute(
            ctx,
            lambda service: service.get_tenant(ctx, tenant_id=tenant_id),
        )

    def suspend_tenant(
        self,
        ctx: ExecutionContext,
        *,
        tenant_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.suspend_tenant(
                ctx,
                tenant_id=tenant_id,
                reason=reason,
                expected_version=expected_version,
            ),
        )

    def get_enterprise(
        self,
        ctx: ExecutionContext,
        *,
        enterprise_id: UUID,
    ) -> KernelResult[Enterprise]:
        return self._execute(
            ctx,
            lambda service: service.get_enterprise(
                ctx,
                enterprise_id=enterprise_id,
            ),
        )

    def list_enterprises(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[list[Enterprise]]:
        return self._execute(ctx, lambda service: service.list_enterprises(ctx))

    def create_enterprise(
        self,
        ctx: ExecutionContext,
        *,
        legal_name: str,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.create_enterprise(
                ctx,
                legal_name=legal_name,
            ),
            conflict_code=ErrorCode.ORG_ENTERPRISE_DUPLICATE_NAME,
        )

    def suspend_enterprise(
        self,
        ctx: ExecutionContext,
        *,
        enterprise_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.suspend_enterprise(
                ctx,
                enterprise_id=enterprise_id,
                reason=reason,
                expected_version=expected_version,
            ),
        )

    def reactivate_enterprise(
        self,
        ctx: ExecutionContext,
        *,
        enterprise_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.reactivate_enterprise(
                ctx,
                enterprise_id=enterprise_id,
                reason=reason,
                expected_version=expected_version,
            ),
        )

    def close_enterprise(
        self,
        ctx: ExecutionContext,
        *,
        enterprise_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.close_enterprise(
                ctx,
                enterprise_id=enterprise_id,
                reason=reason,
                expected_version=expected_version,
            ),
        )

    def reactivate_tenant(
        self,
        ctx: ExecutionContext,
        *,
        tenant_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.reactivate_tenant(
                ctx,
                tenant_id=tenant_id,
                reason=reason,
                expected_version=expected_version,
            ),
        )

    def upsert_unit(
        self,
        ctx: ExecutionContext,
        *,
        unit_type: UnitType | str,
        name: str,
        unit_id: UUID | None = None,
        enterprise_id: UUID | None = None,
        parent_unit_id: UUID | None = None,
        status: OrganizationStatus = OrganizationStatus.ACTIVE,
        expected_version: int | None = None,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.upsert_unit(
                ctx,
                unit_type=unit_type,
                name=name,
                unit_id=unit_id,
                enterprise_id=enterprise_id,
                parent_unit_id=parent_unit_id,
                status=status,
                expected_version=expected_version,
            ),
        )

    def get_unit_tree(
        self,
        ctx: ExecutionContext,
        *,
        root_unit_id: UUID | None = None,
    ) -> KernelResult[list[OrganizationUnit]]:
        return self._execute(
            ctx,
            lambda service: service.get_unit_tree(
                ctx,
                root_unit_id=root_unit_id,
            ),
        )

    def set_unit_status(
        self,
        ctx: ExecutionContext,
        *,
        unit_id: UUID,
        status: OrganizationStatus | str,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.set_unit_status(
                ctx,
                unit_id=unit_id,
                status=status,
                reason=reason,
                expected_version=expected_version,
            ),
        )

    def add_membership(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID,
        enterprise_id: UUID | None = None,
        org_unit_id: UUID | None = None,
        membership_role_label: str | None = None,
    ) -> KernelResult[UUID]:
        return self._execute(
            ctx,
            lambda service: service.add_membership(
                ctx,
                subject_id=subject_id,
                enterprise_id=enterprise_id,
                org_unit_id=org_unit_id,
                membership_role_label=membership_role_label,
            ),
            conflict_code=ErrorCode.ORG_MEMBERSHIP_DUPLICATE,
        )

    def remove_membership(
        self,
        ctx: ExecutionContext,
        *,
        membership_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.remove_membership(
                ctx,
                membership_id=membership_id,
                reason=reason,
                expected_version=expected_version,
            ),
        )

    def list_memberships(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID | None = None,
        org_unit_id: UUID | None = None,
        status: OrganizationStatus | None = None,
    ) -> KernelResult[list[Membership]]:
        return self._execute(
            ctx,
            lambda service: service.list_memberships(
                ctx,
                subject_id=subject_id,
                org_unit_id=org_unit_id,
                status=status,
            ),
        )

    def suspend_membership(
        self,
        ctx: ExecutionContext,
        *,
        membership_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.suspend_membership(
                ctx,
                membership_id=membership_id,
                reason=reason,
                expected_version=expected_version,
            ),
        )

    def reactivate_membership(
        self,
        ctx: ExecutionContext,
        *,
        membership_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.reactivate_membership(
                ctx,
                membership_id=membership_id,
                reason=reason,
                expected_version=expected_version,
            ),
        )

    def transfer_membership_unit(
        self,
        ctx: ExecutionContext,
        *,
        membership_id: UUID,
        to_org_unit_id: UUID,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._execute(
            ctx,
            lambda service: service.transfer_membership_unit(
                ctx,
                membership_id=membership_id,
                to_org_unit_id=to_org_unit_id,
                expected_version=expected_version,
            ),
        )

    def _execute(
        self,
        ctx: ExecutionContext,
        operation: Callable[[OrganizationService], KernelResult[T]],
        *,
        conflict_code: ErrorCode = ErrorCode.COMMON_CONFLICT,
    ) -> KernelResult[T]:
        try:
            with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
                try:
                    repository = SQLAlchemyOrganizationRepository(
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
                    OrganizationService(
                        repository=repository,
                        audit_log=audit_log,
                        platform_governors=self._platform_governors,
                        membership_eligibility=SQLAlchemyMembershipEligibility(
                            unit_of_work.session
                        ),
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
                "organization persistence conflict",
            )
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL,
                "organization persistence operation failed",
            )
