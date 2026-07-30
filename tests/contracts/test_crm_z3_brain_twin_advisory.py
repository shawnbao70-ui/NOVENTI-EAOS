"""PHX-G327 Brain/Twin CRM advisory projection contracts (hermetic)."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from eaos_platform.brain.models import InsightKind
from eaos_platform.twin.models import TwinSnapshotStatus
from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from noventi.crm.customer360 import CUSTOMER360_RESOURCE
from noventi.crm.customer_advisory import (
    BrainAdvisoryRef,
    CustomerAdvisoryProjection,
    CustomerAdvisoryService,
    InMemoryCustomerAdvisoryRepository,
    TwinAdvisoryRef,
)


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=uuid4(),
        correlation_id=f"corr-g327-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _stack(
    ctx: ExecutionContext,
    *,
    grant_360: bool = True,
    projections: tuple[CustomerAdvisoryProjection, ...] = (),
) -> CustomerAdvisoryService:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_Eligibility(),
    )
    if grant_360:
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=CUSTOMER360_RESOURCE,
            actions={"read"},
            scope_level=ScopeLevel.TENANT,
        ).ok
    return CustomerAdvisoryService(
        permission,
        repository=InMemoryCustomerAdvisoryRepository(projections),
    )


def test_g327_advisory_read_returns_closed_refs_only() -> None:
    ctx = _ctx()
    assert ctx.tenant_id is not None
    customer_id = uuid4()
    now = datetime.now(timezone.utc)
    twin_id = uuid4()
    brain_id = uuid4()
    projection = CustomerAdvisoryProjection(
        customer_id=customer_id,
        twin_snapshot_refs=(
            TwinAdvisoryRef(
                id=twin_id,
                entity_ref=f"pkg.crm.customer:{customer_id}",
                status=TwinSnapshotStatus.ACTIVE,
                source_ref="crm:sync",
                updated_at=now,
            ),
        ),
        brain_insight_refs=(
            BrainAdvisoryRef(
                id=brain_id,
                kind=InsightKind.RECOMMENDATION,
                summary="Review commercial hold risk",
                advisory=True,
                twin_ref=twin_id,
                updated_at=now,
            ),
        ),
    )
    advisory = _stack(ctx, projections=(projection,))
    result = advisory.get_customer_advisory(ctx, customer_id)
    assert result.ok
    assert result.data is not None
    assert result.data.customer_id == customer_id
    assert result.data.execution_authority == "none"
    assert len(result.data.twin_snapshot_refs) == 1
    assert result.data.twin_snapshot_refs[0].id == twin_id
    assert len(result.data.brain_insight_refs) == 1
    assert result.data.brain_insight_refs[0].advisory is True
    assert result.data.brain_insight_refs[0].summary.startswith("Review")


def test_g327_default_deny_without_customer360_read() -> None:
    ctx = _ctx()
    customer_id = uuid4()
    advisory = _stack(
        ctx,
        grant_360=False,
        projections=(
            CustomerAdvisoryProjection(
                customer_id=customer_id,
                twin_snapshot_refs=(),
                brain_insight_refs=(),
            ),
        ),
    )
    result = advisory.get_customer_advisory(ctx, customer_id)
    assert not result.ok
    assert result.error_code == ErrorCode.PERMISSION_DENIED


def test_g327_advisory_has_no_execute_or_authorize_surface() -> None:
    assert not hasattr(CustomerAdvisoryService, "execute")
    assert not hasattr(CustomerAdvisoryService, "authorize")
    assert not hasattr(CustomerAdvisoryService, "request_execution")
    assert not hasattr(CustomerAdvisoryService, "authorize_from_twin")
    assert not hasattr(CustomerAdvisoryService, "create_customer_advisory")
    assert not hasattr(CustomerAdvisoryService, "update_customer_advisory")
