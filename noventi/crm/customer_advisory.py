"""Read-only customer Twin and Brain advisory projection (PHX-G327)."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Protocol
from uuid import UUID

from eaos_platform.brain.models import InsightKind
from eaos_platform.twin.models import TwinSnapshotStatus
from kernel.permission.models import PermissionEffect, Resource
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult
from noventi.crm.customer360 import CUSTOMER360_RESOURCE


@dataclass(frozen=True, slots=True)
class TwinAdvisoryRef:
    id: UUID
    entity_ref: str
    status: TwinSnapshotStatus
    source_ref: str
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class BrainAdvisoryRef:
    id: UUID
    kind: InsightKind
    summary: str
    advisory: bool
    twin_ref: UUID | None
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class CustomerAdvisoryProjection:
    customer_id: UUID
    twin_snapshot_refs: tuple[TwinAdvisoryRef, ...]
    brain_insight_refs: tuple[BrainAdvisoryRef, ...]
    execution_authority: Literal["none"] = "none"


class CustomerAdvisoryRepository(Protocol):
    def get_customer_advisory(
        self, customer_id: UUID
    ) -> CustomerAdvisoryProjection | None: ...


class CustomerAdvisoryPermissionEvaluator(Protocol):
    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        action: str,
        resource: Resource,
    ) -> KernelResult: ...


class InMemoryCustomerAdvisoryRepository:
    """Constructor-populated read repository intended for service tests."""

    def __init__(
        self, projections: Iterable[CustomerAdvisoryProjection] = ()
    ) -> None:
        self._projections = {
            projection.customer_id: projection for projection in projections
        }

    def get_customer_advisory(
        self, customer_id: UUID
    ) -> CustomerAdvisoryProjection | None:
        return self._projections.get(customer_id)


class CustomerAdvisoryService:
    def __init__(
        self,
        permission: CustomerAdvisoryPermissionEvaluator,
        *,
        repository: CustomerAdvisoryRepository,
    ) -> None:
        self._permission = permission
        self._repository = repository

    def get_customer_advisory(
        self, ctx: ExecutionContext, customer_id: UUID
    ) -> KernelResult[CustomerAdvisoryProjection]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            permission = self._permission.evaluate(
                ctx,
                principal_subject_id=ctx.subject_id,
                action="read",
                resource=Resource(
                    tenant_id=ctx.tenant_id,
                    resource_type=CUSTOMER360_RESOURCE,
                    resource_id=customer_id,
                ),
            )
            if not permission.ok:
                return permission
            decision = permission.data
            if decision is None or decision.effect != PermissionEffect.ALLOW:
                return KernelResult.failure(
                    ErrorCode.PERMISSION_DENIED,
                    "Customer advisory read is denied by Permission",
                    details={
                        "reason_code": (
                            decision.reason_code
                            if decision is not None
                            else ErrorCode.PERMISSION_DENIED.value
                        )
                    },
                )
            projection = self._repository.get_customer_advisory(customer_id)
            if projection is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND,
                    "customer not found",
                )
            return KernelResult.success(projection)
        except KernelError as error:
            return KernelResult.from_error(error)
