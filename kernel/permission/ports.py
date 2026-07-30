"""Fail-closed cross-domain ports for Permission evaluation."""

from __future__ import annotations

from typing import Protocol, runtime_checkable
from uuid import UUID

from kernel.permission.models import Resource, ScopeLevel
from kernel.shared.context import ExecutionContext


@runtime_checkable
class PrincipalEligibility(Protocol):
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool: ...


class RejectAllPrincipalEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return False


@runtime_checkable
class ConditionEvaluator(Protocol):
    def evaluate(
        self,
        *,
        condition_ref: str,
        ctx: ExecutionContext,
        principal_subject_id: UUID,
        action: str,
        resource: Resource,
    ) -> bool: ...


class RejectAllConditionEvaluator:
    """Unknown, missing or unavailable conditions never produce allow."""

    def evaluate(
        self,
        *,
        condition_ref: str,
        ctx: ExecutionContext,
        principal_subject_id: UUID,
        action: str,
        resource: Resource,
    ) -> bool:
        del condition_ref, ctx, principal_subject_id, action, resource
        return False


@runtime_checkable
class ScopeResolver(Protocol):
    def covers(
        self,
        *,
        tenant_id: UUID,
        scope_level: ScopeLevel,
        enterprise_id: UUID | None,
        org_unit_id: UUID | None,
        resource: Resource,
    ) -> bool: ...


class TenantOnlyScopeResolver:
    """Fail-closed default: only TENANT scope without enterprise/unit ids covers."""

    def covers(
        self,
        *,
        tenant_id: UUID,
        scope_level: ScopeLevel,
        enterprise_id: UUID | None,
        org_unit_id: UUID | None,
        resource: Resource,
    ) -> bool:
        if resource.tenant_id != tenant_id:
            return False
        if scope_level == ScopeLevel.TENANT:
            return enterprise_id is None and org_unit_id is None
        if scope_level == ScopeLevel.RESOURCE:
            return True
        return False
