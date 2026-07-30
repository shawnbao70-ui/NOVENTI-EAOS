"""SQLAlchemy Identity ↔ Organization L2 composition."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from kernel.identity.models import AssignmentMode, EntityStatus, SubjectKind
from kernel.identity.service import IdentityService
from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
from kernel.infrastructure.persistence.identity_models import (
    AIAssignmentRecord,
    SubjectRecord,
)
from kernel.infrastructure.persistence.identity_repository import (
    SQLAlchemyIdentityRepository,
)
from kernel.infrastructure.persistence.organization_repository import (
    SQLAlchemyOrganizationRepository,
)
from kernel.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from kernel.organization.models import OrganizationStatus
from kernel.organization.service import OrganizationService
from kernel.shared.context import ExecutionContext
from kernel.shared.errors import ErrorCode
from kernel.shared.results import KernelResult


class SQLAlchemyMembershipEligibility:
    def __init__(self, session: Session) -> None:
        self._session = session

    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        subject = self._session.get(SubjectRecord, subject_id)
        if subject is None or subject.status != EntityStatus.ACTIVE.value:
            return False
        if subject.subject_type == SubjectKind.AI_EMPLOYEE.value:
            assignment_id = self._session.scalar(
                select(AIAssignmentRecord.id).where(
                    AIAssignmentRecord.ai_subject_id == subject_id,
                    AIAssignmentRecord.tenant_id == tenant_id,
                    AIAssignmentRecord.status == EntityStatus.ACTIVE.value,
                )
            )
            return assignment_id is not None
        return subject.tenant_id == tenant_id


class TransactionalIdentityOrganizationCoordinator:
    """Coordinate cross-domain membership and AI reassignment atomically."""

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        *,
        platform_governors: set[UUID] | frozenset[UUID] | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._platform_governors = frozenset(platform_governors or ())

    def add_membership(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID,
        org_unit_id: UUID | None = None,
        membership_role_label: str | None = None,
    ) -> KernelResult[UUID]:
        try:
            with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
                repository = SQLAlchemyOrganizationRepository(
                    unit_of_work.session,
                    tenant_id=ctx.tenant_id,
                    platform_scope=ctx.platform_scope,
                )
                service = OrganizationService(
                    repository=repository,
                    audit_log=SQLAlchemyAuditLog(
                        unit_of_work.session,
                        tenant_id=ctx.tenant_id,
                        platform_scope=ctx.platform_scope,
                    ),
                    platform_governors=self._platform_governors,
                    membership_eligibility=SQLAlchemyMembershipEligibility(
                        unit_of_work.session
                    ),
                )
                result = service.add_membership(
                    ctx,
                    subject_id=subject_id,
                    org_unit_id=org_unit_id,
                    membership_role_label=membership_role_label,
                )
                if not result.ok:
                    return result
                unit_of_work.commit()
                return result
        except ValueError:
            return KernelResult.failure(
                ErrorCode.CTX_INVALID,
                "execution context has an invalid persistence scope",
            )
        except IntegrityError:
            return KernelResult.failure(
                ErrorCode.ORG_MEMBERSHIP_DUPLICATE,
                "identity organization persistence conflict",
            )
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL,
                "identity organization persistence operation failed",
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
        try:
            with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
                identity_repository = SQLAlchemyIdentityRepository(
                    unit_of_work.session,
                    tenant_id=None,
                    platform_scope=True,
                )
                organization_repository = SQLAlchemyOrganizationRepository(
                    unit_of_work.session,
                    tenant_id=None,
                    platform_scope=True,
                )
                audit_log = SQLAlchemyAuditLog(
                    unit_of_work.session,
                    tenant_id=None,
                    platform_scope=True,
                )
                now = datetime.now(timezone.utc)
                memberships = organization_repository.list_active_memberships_for_subject(
                    ai_subject_id
                )
                for membership in memberships:
                    expected_version = membership.version
                    membership.status = OrganizationStatus.ENDED
                    membership.ended_at = now
                    membership.updated_at = now
                    membership.version = expected_version + 1
                    organization_repository.save_membership(
                        membership,
                        expected_version=expected_version,
                    )
                if memberships:
                    audit_log.record(
                        ctx,
                        action="Org.EndMembershipsForAIReassignment",
                        resource=f"subject:{ai_subject_id}",
                        result="ok",
                        details={"membership_count": len(memberships)},
                    )
                result = IdentityService(
                    repository=identity_repository,
                    audit_log=audit_log,
                    platform_governors=self._platform_governors,
                ).reassign_ai(
                    ctx,
                    ai_subject_id=ai_subject_id,
                    to_tenant_id=to_tenant_id,
                    mode=mode,
                    management_policy=management_policy,
                )
                if not result.ok:
                    return result
                unit_of_work.commit()
                return result
        except ValueError:
            return KernelResult.failure(
                ErrorCode.CTX_INVALID,
                "execution context has an invalid persistence scope",
            )
        except IntegrityError:
            return KernelResult.failure(
                ErrorCode.IDENTITY_AI_ASSIGNMENT_CONFLICT,
                "identity organization persistence conflict",
            )
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL,
                "identity organization persistence operation failed",
            )
