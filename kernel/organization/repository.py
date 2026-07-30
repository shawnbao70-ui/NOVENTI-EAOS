"""In-memory Organization repository for the PHX-004 slice."""

from __future__ import annotations

from dataclasses import replace
from typing import Optional, Protocol, runtime_checkable
from uuid import UUID

from kernel.organization.models import Enterprise, Membership, OrganizationUnit, Tenant


@runtime_checkable
class OrganizationRepository(Protocol):
    def add_tenant(self, tenant: Tenant) -> None: ...

    def get_tenant(self, tenant_id: UUID) -> Optional[Tenant]: ...

    def save_tenant(self, tenant: Tenant, *, expected_version: int) -> None: ...

    def legal_name_exists(self, legal_name: str) -> bool: ...

    def add_enterprise(self, enterprise: Enterprise) -> None: ...

    def get_enterprise(self, enterprise_id: UUID) -> Optional[Enterprise]: ...

    def get_primary_enterprise(self, tenant_id: UUID) -> Optional[Enterprise]: ...

    def list_enterprises(self, tenant_id: UUID) -> list[Enterprise]: ...

    def enterprise_legal_name_exists(
        self,
        tenant_id: UUID,
        legal_name: str,
    ) -> bool: ...

    def save_enterprise(
        self,
        enterprise: Enterprise,
        *,
        expected_version: int,
    ) -> None: ...

    def lock_enterprise(self, tenant_id: UUID, enterprise_id: UUID) -> None: ...

    def save_unit(
        self,
        unit: OrganizationUnit,
        *,
        expected_version: int | None,
    ) -> None: ...

    def get_unit(self, unit_id: UUID) -> Optional[OrganizationUnit]: ...

    def list_units(self, tenant_id: UUID) -> list[OrganizationUnit]: ...

    def lock_unit_hierarchy(self, tenant_id: UUID, enterprise_id: UUID) -> None: ...

    def add_membership(self, membership: Membership) -> None: ...

    def get_membership(self, membership_id: UUID) -> Optional[Membership]: ...

    def save_membership(
        self,
        membership: Membership,
        *,
        expected_version: int,
    ) -> None: ...

    def list_memberships(self, tenant_id: UUID) -> list[Membership]: ...

    def list_active_memberships_for_subject(
        self,
        subject_id: UUID,
    ) -> list[Membership]: ...


class InMemoryOrganizationRepository:
    def __init__(self) -> None:
        self.tenants: dict[UUID, Tenant] = {}
        self.enterprises: dict[UUID, Enterprise] = {}
        self.units: dict[UUID, OrganizationUnit] = {}
        self.memberships: dict[UUID, Membership] = {}

    def add_tenant(self, tenant: Tenant) -> None:
        self.tenants[tenant.id] = replace(tenant)

    def get_tenant(self, tenant_id: UUID) -> Optional[Tenant]:
        tenant = self.tenants.get(tenant_id)
        return replace(tenant) if tenant is not None else None

    def save_tenant(self, tenant: Tenant, *, expected_version: int) -> None:
        current = self.tenants.get(tenant.id)
        if current is None or current.version != expected_version:
            from kernel.shared.errors import ErrorCode, KernelError

            raise KernelError(
                ErrorCode.ORG_VERSION_CONFLICT,
                "tenant version conflict",
            )
        self.tenants[tenant.id] = replace(tenant)

    def legal_name_exists(self, legal_name: str) -> bool:
        normalized = legal_name.casefold()
        return any(tenant.legal_name.casefold() == normalized for tenant in self.tenants.values())

    def add_enterprise(self, enterprise: Enterprise) -> None:
        self.enterprises[enterprise.id] = replace(enterprise)

    def get_enterprise(self, enterprise_id: UUID) -> Optional[Enterprise]:
        enterprise = self.enterprises.get(enterprise_id)
        return replace(enterprise) if enterprise is not None else None

    def get_primary_enterprise(self, tenant_id: UUID) -> Optional[Enterprise]:
        enterprise = next(
            (
                enterprise
                for enterprise in self.enterprises.values()
                if enterprise.tenant_id == tenant_id and enterprise.is_primary
            ),
            None,
        )
        return replace(enterprise) if enterprise is not None else None

    def list_enterprises(self, tenant_id: UUID) -> list[Enterprise]:
        return [
            replace(enterprise)
            for enterprise in self.enterprises.values()
            if enterprise.tenant_id == tenant_id
        ]

    def enterprise_legal_name_exists(
        self,
        tenant_id: UUID,
        legal_name: str,
    ) -> bool:
        normalized = legal_name.casefold()
        return any(
            enterprise.tenant_id == tenant_id
            and enterprise.legal_name.casefold() == normalized
            for enterprise in self.enterprises.values()
        )

    def save_enterprise(
        self,
        enterprise: Enterprise,
        *,
        expected_version: int,
    ) -> None:
        current = self.enterprises.get(enterprise.id)
        if current is None or current.version != expected_version:
            from kernel.shared.errors import ErrorCode, KernelError

            raise KernelError(
                ErrorCode.ORG_VERSION_CONFLICT,
                "enterprise version conflict",
            )
        self.enterprises[enterprise.id] = replace(enterprise)

    def lock_enterprise(self, tenant_id: UUID, enterprise_id: UUID) -> None:
        del tenant_id, enterprise_id

    def save_unit(
        self,
        unit: OrganizationUnit,
        *,
        expected_version: int | None,
    ) -> None:
        current = self.units.get(unit.id)
        if expected_version is None:
            if current is not None:
                from kernel.shared.errors import ErrorCode, KernelError

                raise KernelError(ErrorCode.ORG_VERSION_CONFLICT, "unit already exists")
        elif current is None or current.version != expected_version:
            from kernel.shared.errors import ErrorCode, KernelError

            raise KernelError(ErrorCode.ORG_VERSION_CONFLICT, "unit version conflict")
        self.units[unit.id] = replace(unit)

    def get_unit(self, unit_id: UUID) -> Optional[OrganizationUnit]:
        unit = self.units.get(unit_id)
        return replace(unit) if unit is not None else None

    def list_units(self, tenant_id: UUID) -> list[OrganizationUnit]:
        return [
            replace(unit)
            for unit in self.units.values()
            if unit.tenant_id == tenant_id
        ]

    def lock_unit_hierarchy(self, tenant_id: UUID, enterprise_id: UUID) -> None:
        del tenant_id, enterprise_id

    def add_membership(self, membership: Membership) -> None:
        self.memberships[membership.id] = replace(membership)

    def get_membership(self, membership_id: UUID) -> Optional[Membership]:
        membership = self.memberships.get(membership_id)
        return replace(membership) if membership is not None else None

    def save_membership(
        self,
        membership: Membership,
        *,
        expected_version: int,
    ) -> None:
        current = self.memberships.get(membership.id)
        if current is None or current.version != expected_version:
            from kernel.shared.errors import ErrorCode, KernelError

            raise KernelError(
                ErrorCode.ORG_VERSION_CONFLICT,
                "membership version conflict",
            )
        self.memberships[membership.id] = replace(membership)

    def list_memberships(self, tenant_id: UUID) -> list[Membership]:
        return [
            replace(membership)
            for membership in self.memberships.values()
            if membership.tenant_id == tenant_id
        ]

    def list_active_memberships_for_subject(
        self,
        subject_id: UUID,
    ) -> list[Membership]:
        from kernel.organization.models import OrganizationStatus

        return [
            replace(membership)
            for membership in self.memberships.values()
            if membership.subject_id == subject_id
            and membership.status == OrganizationStatus.ACTIVE
        ]
