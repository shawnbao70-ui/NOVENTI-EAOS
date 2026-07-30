"""SQL composition for the read-only customer advisory projection (PHX-G327)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from kernel.infrastructure.persistence.audit_log import SQLAlchemyAuditLog
from kernel.infrastructure.persistence.brain_models import BrainInsightRecord
from kernel.infrastructure.persistence.identity_permission import (
    SQLAlchemyPrincipalEligibility,
)
from kernel.infrastructure.persistence.permission_repository import (
    SQLAlchemyPermissionRepository,
)
from kernel.infrastructure.persistence.twin_models import TwinSnapshotRecord
from kernel.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult
from noventi.crm.customer_advisory import (
    BrainAdvisoryRef,
    CustomerAdvisoryProjection,
    CustomerAdvisoryService,
    TwinAdvisoryRef,
)
from noventi.crm.persistence import CustomerRecord
from eaos_platform.brain.models import InsightKind
from eaos_platform.twin.models import TwinSnapshotStatus


class SQLAlchemyCustomerAdvisoryRepository:
    """Tenant-scoped live composition over CRM, Twin, and Brain records."""

    def __init__(self, session: Session, *, tenant_id: UUID) -> None:
        self._session = session
        self._tenant_id = tenant_id

    def get_customer_advisory(
        self, customer_id: UUID
    ) -> CustomerAdvisoryProjection | None:
        customer = self._session.scalar(
            select(CustomerRecord).where(
                CustomerRecord.id == customer_id,
                CustomerRecord.tenant_id == self._tenant_id,
            )
        )
        if customer is None:
            return None

        entity_ref = f"pkg.crm.customer:{customer_id}"
        snapshots = self._session.scalars(
            select(TwinSnapshotRecord)
            .where(
                TwinSnapshotRecord.tenant_id == self._tenant_id,
                TwinSnapshotRecord.entity_ref == entity_ref,
            )
            .order_by(
                TwinSnapshotRecord.updated_at.desc(),
                TwinSnapshotRecord.id.desc(),
            )
            .limit(10)
        ).all()
        snapshot_ids = tuple(snapshot.id for snapshot in snapshots)

        advisory_links = [
            BrainInsightRecord.source_ref == entity_ref,
            BrainInsightRecord.details_json["customer_id"].as_string()
            == str(customer_id),
        ]
        if snapshot_ids:
            advisory_links.append(
                BrainInsightRecord.twin_ref.in_(snapshot_ids)
            )

        insights = self._session.scalars(
            select(BrainInsightRecord)
            .where(
                BrainInsightRecord.tenant_id == self._tenant_id,
                BrainInsightRecord.advisory.is_(True),
                or_(*advisory_links),
            )
            .order_by(
                BrainInsightRecord.updated_at.desc(),
                BrainInsightRecord.id.desc(),
            )
            .limit(20)
        ).all()

        return CustomerAdvisoryProjection(
            customer_id=customer.id,
            twin_snapshot_refs=tuple(
                TwinAdvisoryRef(
                    id=snapshot.id,
                    entity_ref=snapshot.entity_ref,
                    status=TwinSnapshotStatus(snapshot.status),
                    source_ref=snapshot.source_ref,
                    updated_at=snapshot.updated_at,
                )
                for snapshot in snapshots
            ),
            brain_insight_refs=tuple(
                BrainAdvisoryRef(
                    id=insight.id,
                    kind=InsightKind(insight.kind),
                    summary=insight.summary,
                    advisory=insight.advisory,
                    twin_ref=insight.twin_ref,
                    updated_at=insight.updated_at,
                )
                for insight in insights
            ),
        )


class TransactionalCustomerAdvisoryService:
    """Read-only UoW composition; incidental permission state is rolled back."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def get_customer_advisory(
        self, ctx: ExecutionContext, customer_id: UUID
    ) -> KernelResult[CustomerAdvisoryProjection]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            with SQLAlchemyUnitOfWork(self._session_factory) as unit_of_work:
                session = unit_of_work.session
                permission = PermissionService(
                    repository=SQLAlchemyPermissionRepository(
                        session,
                        tenant_id=ctx.tenant_id,
                    ),
                    audit_log=SQLAlchemyAuditLog(
                        session,
                        tenant_id=ctx.tenant_id,
                    ),
                    principal_eligibility=SQLAlchemyPrincipalEligibility(
                        session
                    ),
                )
                service = CustomerAdvisoryService(
                    permission,
                    repository=SQLAlchemyCustomerAdvisoryRepository(
                        session,
                        tenant_id=ctx.tenant_id,
                    ),
                )
                with session.no_autoflush:
                    return service.get_customer_advisory(ctx, customer_id)
        except KernelError as error:
            return KernelResult.from_error(error)
        except SQLAlchemyError:
            return KernelResult.failure(
                ErrorCode.COMMON_INTERNAL,
                "Customer advisory persistence unavailable",
            )
