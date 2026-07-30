"""Tenant-bound SQLAlchemy adapter for Organization Repository."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import overload
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from kernel.infrastructure.persistence.organization_models import (
    EnterpriseRecord,
    MembershipRecord,
    OrganizationUnitRecord,
    TenantRecord,
)
from kernel.organization.models import (
    Enterprise,
    Membership,
    OrganizationStatus,
    OrganizationUnit,
    Tenant,
    UnitType,
)
from kernel.shared.errors import ErrorCode, KernelError


class SQLAlchemyOrganizationRepository:
    def __init__(
        self,
        session: Session,
        *,
        tenant_id: UUID | None,
        platform_scope: bool = False,
    ) -> None:
        if platform_scope == (tenant_id is not None):
            raise ValueError("provide either tenant_id or platform_scope")
        self._session = session
        self._tenant_id = tenant_id
        self._platform_scope = platform_scope

    def add_tenant(self, tenant: Tenant) -> None:
        self._require_platform_scope()
        self._session.add(
            TenantRecord(
                id=tenant.id,
                legal_name=tenant.legal_name,
                status=tenant.status.value,
                region_policy_ref=tenant.region_policy_ref,
                created_at=tenant.created_at,
                updated_at=tenant.updated_at,
                version=tenant.version,
            )
        )

    def get_tenant(self, tenant_id: UUID) -> Tenant | None:
        if not self._platform_scope and tenant_id != self._tenant_id:
            return None
        record = self._session.scalar(
            select(TenantRecord).where(TenantRecord.id == tenant_id)
        )
        return self._to_tenant(record) if record is not None else None

    def save_tenant(self, tenant: Tenant, *, expected_version: int) -> None:
        if not self._platform_scope and tenant.id != self._tenant_id:
            self._raise_cross_tenant()
        result = self._session.execute(
            update(TenantRecord)
            .where(
                TenantRecord.id == tenant.id,
                TenantRecord.version == expected_version,
            )
            .values(
                legal_name=tenant.legal_name,
                status=tenant.status.value,
                region_policy_ref=tenant.region_policy_ref,
                updated_at=tenant.updated_at,
                version=tenant.version,
            )
        )
        if result.rowcount != 1:
            raise KernelError(
                ErrorCode.ORG_VERSION_CONFLICT,
                "tenant version conflict",
            )

    def legal_name_exists(self, legal_name: str) -> bool:
        statement = select(TenantRecord.id).where(
            func.lower(TenantRecord.legal_name) == legal_name.casefold()
        )
        if not self._platform_scope:
            statement = statement.where(TenantRecord.id == self._tenant_id)
        return self._session.scalar(statement) is not None

    def add_enterprise(self, enterprise: Enterprise) -> None:
        self._require_tenant_scope(enterprise.tenant_id)
        self._session.flush()
        self._session.add(
            EnterpriseRecord(
                id=enterprise.id,
                tenant_id=enterprise.tenant_id,
                legal_name=enterprise.legal_name,
                status=enterprise.status.value,
                is_primary=enterprise.is_primary,
                created_at=enterprise.created_at,
                updated_at=enterprise.updated_at,
                version=enterprise.version,
            )
        )

    def get_enterprise(self, enterprise_id: UUID) -> Enterprise | None:
        statement = select(EnterpriseRecord).where(
            EnterpriseRecord.id == enterprise_id
        )
        if not self._platform_scope:
            statement = statement.where(
                EnterpriseRecord.tenant_id == self._tenant_id
            )
        record = self._session.scalar(statement)
        return self._to_enterprise(record) if record is not None else None

    def get_primary_enterprise(self, tenant_id: UUID) -> Enterprise | None:
        self._require_tenant_scope(tenant_id)
        record = self._session.scalar(
            select(EnterpriseRecord).where(
                EnterpriseRecord.tenant_id == tenant_id,
                EnterpriseRecord.is_primary.is_(True),
            )
        )
        return self._to_enterprise(record) if record is not None else None

    def list_enterprises(self, tenant_id: UUID) -> list[Enterprise]:
        self._require_tenant_scope(tenant_id)
        records = self._session.scalars(
            select(EnterpriseRecord).where(
                EnterpriseRecord.tenant_id == tenant_id
            )
        )
        return [self._to_enterprise(record) for record in records]

    def enterprise_legal_name_exists(
        self,
        tenant_id: UUID,
        legal_name: str,
    ) -> bool:
        self._require_tenant_scope(tenant_id)
        return self._session.scalar(
            select(EnterpriseRecord.id).where(
                EnterpriseRecord.tenant_id == tenant_id,
                func.lower(EnterpriseRecord.legal_name) == legal_name.casefold(),
            )
        ) is not None

    def save_enterprise(
        self,
        enterprise: Enterprise,
        *,
        expected_version: int,
    ) -> None:
        self._require_tenant_scope(enterprise.tenant_id)
        result = self._session.execute(
            update(EnterpriseRecord)
            .where(
                EnterpriseRecord.id == enterprise.id,
                EnterpriseRecord.tenant_id == enterprise.tenant_id,
                EnterpriseRecord.version == expected_version,
            )
            .values(
                legal_name=enterprise.legal_name,
                status=enterprise.status.value,
                updated_at=enterprise.updated_at,
                version=enterprise.version,
            )
        )
        if result.rowcount != 1:
            raise KernelError(
                ErrorCode.ORG_VERSION_CONFLICT,
                "enterprise version conflict",
            )

    def lock_enterprise(self, tenant_id: UUID, enterprise_id: UUID) -> None:
        self._require_tenant_scope(tenant_id)
        self._session.scalar(
            select(EnterpriseRecord.id)
            .where(
                EnterpriseRecord.id == enterprise_id,
                EnterpriseRecord.tenant_id == tenant_id,
            )
            .with_for_update()
        )

    def save_unit(
        self,
        unit: OrganizationUnit,
        *,
        expected_version: int | None,
    ) -> None:
        self._require_tenant_scope(unit.tenant_id)
        if expected_version is None:
            self._session.add(
                OrganizationUnitRecord(
                    id=unit.id,
                    tenant_id=unit.tenant_id,
                    enterprise_id=unit.enterprise_id,
                    parent_unit_id=unit.parent_unit_id,
                    unit_type=unit.unit_type.value,
                    name=unit.name,
                    status=unit.status.value,
                    created_at=unit.created_at,
                    updated_at=unit.updated_at,
                    version=unit.version,
                )
            )
            return
        result = self._session.execute(
            update(OrganizationUnitRecord)
            .where(
                OrganizationUnitRecord.id == unit.id,
                OrganizationUnitRecord.tenant_id == unit.tenant_id,
                OrganizationUnitRecord.version == expected_version,
            )
            .values(
                parent_unit_id=unit.parent_unit_id,
                unit_type=unit.unit_type.value,
                name=unit.name,
                status=unit.status.value,
                updated_at=unit.updated_at,
                version=unit.version,
            )
        )
        if result.rowcount != 1:
            raise KernelError(
                ErrorCode.ORG_VERSION_CONFLICT,
                "organization unit version conflict",
            )

    def get_unit(self, unit_id: UUID) -> OrganizationUnit | None:
        record = self._session.scalar(
            self._scoped_units().where(OrganizationUnitRecord.id == unit_id)
        )
        return self._to_unit(record) if record is not None else None

    def list_units(self, tenant_id: UUID) -> list[OrganizationUnit]:
        self._require_tenant_scope(tenant_id)
        statement = select(OrganizationUnitRecord).where(
            OrganizationUnitRecord.tenant_id == tenant_id
        )
        return [self._to_unit(record) for record in self._session.scalars(statement)]

    def lock_unit_hierarchy(self, tenant_id: UUID, enterprise_id: UUID) -> None:
        self._require_tenant_scope(tenant_id)
        list(
            self._session.scalars(
                select(OrganizationUnitRecord.id)
                .where(
                    OrganizationUnitRecord.tenant_id == tenant_id,
                    OrganizationUnitRecord.enterprise_id == enterprise_id,
                )
                .order_by(OrganizationUnitRecord.id)
                .with_for_update()
            )
        )

    def add_membership(self, membership: Membership) -> None:
        self._require_tenant_scope(membership.tenant_id)
        self._session.add(
            MembershipRecord(
                id=membership.id,
                tenant_id=membership.tenant_id,
                enterprise_id=membership.enterprise_id,
                subject_id=membership.subject_id,
                org_unit_id=membership.org_unit_id,
                membership_role_label=membership.membership_role_label,
                status=membership.status.value,
                created_at=membership.created_at,
                updated_at=membership.updated_at,
                ended_at=membership.ended_at,
                version=membership.version,
            )
        )

    def get_membership(self, membership_id: UUID) -> Membership | None:
        record = self._session.scalar(
            self._scoped_memberships().where(MembershipRecord.id == membership_id)
        )
        return self._to_membership(record) if record is not None else None

    def save_membership(
        self,
        membership: Membership,
        *,
        expected_version: int,
    ) -> None:
        self._require_tenant_scope(membership.tenant_id)
        result = self._session.execute(
            update(MembershipRecord)
            .where(
                MembershipRecord.id == membership.id,
                MembershipRecord.tenant_id == membership.tenant_id,
                MembershipRecord.version == expected_version,
            )
            .values(
                org_unit_id=membership.org_unit_id,
                membership_role_label=membership.membership_role_label,
                status=membership.status.value,
                updated_at=membership.updated_at,
                ended_at=membership.ended_at,
                version=membership.version,
            )
        )
        if result.rowcount != 1:
            raise KernelError(
                ErrorCode.ORG_VERSION_CONFLICT,
                "membership version conflict",
            )

    def list_memberships(self, tenant_id: UUID) -> list[Membership]:
        self._require_tenant_scope(tenant_id)
        statement = select(MembershipRecord).where(
            MembershipRecord.tenant_id == tenant_id
        )
        return [
            self._to_membership(record)
            for record in self._session.scalars(statement)
        ]

    def list_active_memberships_for_subject(
        self,
        subject_id: UUID,
    ) -> list[Membership]:
        if not self._platform_scope:
            raise KernelError(
                ErrorCode.ORG_CROSS_TENANT_FORBIDDEN,
                "cross-tenant membership query requires platform scope",
            )
        statement = select(MembershipRecord).where(
            MembershipRecord.subject_id == subject_id,
            MembershipRecord.status == OrganizationStatus.ACTIVE.value,
        )
        return [
            self._to_membership(record)
            for record in self._session.scalars(statement)
        ]

    def _scoped_units(self):
        statement = select(OrganizationUnitRecord)
        if not self._platform_scope:
            statement = statement.where(
                OrganizationUnitRecord.tenant_id == self._tenant_id
            )
        return statement

    def _scoped_memberships(self):
        statement = select(MembershipRecord)
        if not self._platform_scope:
            statement = statement.where(
                MembershipRecord.tenant_id == self._tenant_id
            )
        return statement

    def _require_platform_scope(self) -> None:
        if not self._platform_scope:
            raise KernelError(
                ErrorCode.PERMISSION_DENIED,
                "platform organization scope is required",
            )

    def _require_tenant_scope(self, tenant_id: UUID) -> None:
        if not self._platform_scope and tenant_id != self._tenant_id:
            self._raise_cross_tenant()

    @staticmethod
    def _raise_cross_tenant() -> None:
        raise KernelError(
            ErrorCode.ORG_CROSS_TENANT_FORBIDDEN,
            "organization operation is outside repository tenant scope",
        )

    @classmethod
    def _to_tenant(cls, record: TenantRecord) -> Tenant:
        return Tenant(
            id=record.id,
            legal_name=record.legal_name,
            status=OrganizationStatus(record.status),
            region_policy_ref=record.region_policy_ref,
            created_at=cls._as_utc(record.created_at),
            updated_at=cls._as_utc(record.updated_at),
            version=record.version,
        )

    @classmethod
    def _to_unit(cls, record: OrganizationUnitRecord) -> OrganizationUnit:
        return OrganizationUnit(
            id=record.id,
            tenant_id=record.tenant_id,
            enterprise_id=record.enterprise_id,
            parent_unit_id=record.parent_unit_id,
            unit_type=UnitType(record.unit_type),
            name=record.name,
            status=OrganizationStatus(record.status),
            created_at=cls._as_utc(record.created_at),
            updated_at=cls._as_utc(record.updated_at),
            version=record.version,
        )

    @classmethod
    def _to_membership(cls, record: MembershipRecord) -> Membership:
        return Membership(
            id=record.id,
            tenant_id=record.tenant_id,
            enterprise_id=record.enterprise_id,
            subject_id=record.subject_id,
            org_unit_id=record.org_unit_id,
            membership_role_label=record.membership_role_label,
            status=OrganizationStatus(record.status),
            created_at=cls._as_utc(record.created_at),
            updated_at=cls._as_utc(record.updated_at),
            ended_at=cls._as_utc(record.ended_at),
            version=record.version,
        )

    @classmethod
    def _to_enterprise(cls, record: EnterpriseRecord) -> Enterprise:
        return Enterprise(
            id=record.id,
            tenant_id=record.tenant_id,
            legal_name=record.legal_name,
            status=OrganizationStatus(record.status),
            is_primary=record.is_primary,
            created_at=cls._as_utc(record.created_at),
            updated_at=cls._as_utc(record.updated_at),
            version=record.version,
        )

    @staticmethod
    @overload
    def _as_utc(value: datetime) -> datetime: ...

    @staticmethod
    @overload
    def _as_utc(value: None) -> None: ...

    @staticmethod
    def _as_utc(value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
