"""Organization-owned scope resolver for Permission evaluation."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from kernel.infrastructure.persistence.organization_models import (
    EnterpriseRecord,
    OrganizationUnitRecord,
)
from kernel.permission.models import Resource, ScopeLevel


class SQLAlchemyScopeResolver:
    def __init__(self, session: Session) -> None:
        self._session = session

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
        if scope_level == ScopeLevel.ENTERPRISE:
            if enterprise_id is None:
                return False
            enterprise = self._session.scalar(
                select(EnterpriseRecord).where(
                    EnterpriseRecord.id == enterprise_id,
                    EnterpriseRecord.tenant_id == tenant_id,
                    EnterpriseRecord.status == "active",
                )
            )
            if enterprise is None:
                return False
            return resource.enterprise_id == enterprise_id
        if scope_level == ScopeLevel.ORG_UNIT:
            if enterprise_id is None or org_unit_id is None:
                return False
            if resource.org_unit_id is None:
                return False
            if resource.enterprise_id not in {None, enterprise_id}:
                return False
            return self._unit_in_subtree(
                tenant_id=tenant_id,
                enterprise_id=enterprise_id,
                root_unit_id=org_unit_id,
                candidate_unit_id=resource.org_unit_id,
            )
        if scope_level == ScopeLevel.RESOURCE:
            return True
        return False

    def _unit_in_subtree(
        self,
        *,
        tenant_id: UUID,
        enterprise_id: UUID,
        root_unit_id: UUID,
        candidate_unit_id: UUID,
    ) -> bool:
        units = {
            unit.id: unit
            for unit in self._session.scalars(
                select(OrganizationUnitRecord).where(
                    OrganizationUnitRecord.tenant_id == tenant_id,
                    OrganizationUnitRecord.enterprise_id == enterprise_id,
                    OrganizationUnitRecord.status == "active",
                )
            )
        }
        if root_unit_id not in units or candidate_unit_id not in units:
            return False
        current_id: UUID | None = candidate_unit_id
        seen: set[UUID] = set()
        while current_id is not None:
            if current_id == root_unit_id:
                return True
            if current_id in seen:
                return False
            seen.add(current_id)
            current = units.get(current_id)
            if current is None:
                return False
            current_id = current.parent_unit_id
        return False
