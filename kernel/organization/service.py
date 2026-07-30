"""Organization Kernel service — IF-ORG-001 vertical slice."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from kernel.organization.models import (
    Enterprise,
    Membership,
    OrganizationStatus,
    OrganizationUnit,
    Tenant,
    UnitType,
)
from kernel.organization.eligibility import (
    MembershipEligibility,
    RejectAllMembershipEligibility,
)
from kernel.event_bus.domain_emit import DomainEventEmitter
from kernel.organization.repository import InMemoryOrganizationRepository, OrganizationRepository
from kernel.shared.audit import AuditLog, InMemoryAuditLog
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult


class OrganizationService:
    """Tenant-safe Organization operations with auditable side effects."""

    def __init__(
        self,
        repository: OrganizationRepository | None = None,
        audit_log: AuditLog | None = None,
        platform_governors: set[UUID] | frozenset[UUID] | None = None,
        membership_eligibility: MembershipEligibility | None = None,
        domain_events: DomainEventEmitter | None = None,
    ) -> None:
        self._repo = repository or InMemoryOrganizationRepository()
        self._audit = audit_log or InMemoryAuditLog()
        self._platform_governors = frozenset(platform_governors or ())
        self._membership_eligibility = (
            membership_eligibility or RejectAllMembershipEligibility()
        )
        self._domain_events = domain_events

    @property
    def audit_log(self) -> AuditLog:
        return self._audit

    def create_tenant(
        self,
        ctx: ExecutionContext,
        *,
        legal_name: str,
        region_policy_ref: str | None = None,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=False)
            self._require_platform_governor(ctx)
            if not legal_name or not legal_name.strip():
                raise KernelError(ErrorCode.ORG_TENANT_INVALID, "legal_name is required")
            if self._repo.legal_name_exists(legal_name.strip()):
                raise KernelError(
                    ErrorCode.ORG_TENANT_DUPLICATE_NAME,
                    "tenant legal name already exists",
                )

            now = datetime.now(timezone.utc)
            tenant = Tenant(
                id=uuid4(),
                legal_name=legal_name.strip(),
                status=OrganizationStatus.ACTIVE,
                created_at=now,
                updated_at=now,
                region_policy_ref=region_policy_ref,
            )
            enterprise = Enterprise(
                id=uuid4(),
                tenant_id=tenant.id,
                legal_name=tenant.legal_name,
                status=OrganizationStatus.ACTIVE,
                is_primary=True,
                created_at=now,
                updated_at=now,
            )
            self._repo.add_tenant(tenant)
            self._repo.add_enterprise(enterprise)
            audit = self._audit.record(
                ctx,
                action="Org.CreateTenant",
                resource=f"tenant:{tenant.id}",
                result="ok",
                details={"primary_enterprise_id": str(enterprise.id)},
            )
            self._emit(
                ctx,
                event_name="organization.tenant.created",
                payload={
                    "tenant_id": str(tenant.id),
                    "version": tenant.version,
                    "status": tenant.status.value,
                },
                tenant_id=tenant.id,
            )
            self._emit(
                ctx,
                event_name="organization.enterprise.created",
                payload={
                    "enterprise_id": str(enterprise.id),
                    "tenant_id": str(tenant.id),
                    "version": enterprise.version,
                    "status": enterprise.status.value,
                    "is_primary": enterprise.is_primary,
                },
                tenant_id=tenant.id,
            )
            return KernelResult.success(tenant.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_tenant(
        self,
        ctx: ExecutionContext,
        *,
        tenant_id: UUID,
    ) -> KernelResult[Tenant]:
        try:
            require_context(ctx, tenant_data_plane=not ctx.platform_scope)
            if not ctx.platform_scope and ctx.tenant_id != tenant_id:
                raise KernelError(
                    ErrorCode.ORG_TENANT_NOT_FOUND,
                    "tenant not found",
                )
            tenant = self._repo.get_tenant(tenant_id)
            if tenant is None:
                raise KernelError(ErrorCode.ORG_TENANT_NOT_FOUND, "tenant not found")
            return KernelResult.success(tenant)
        except KernelError as err:
            return KernelResult.from_error(err)

    def suspend_tenant(
        self,
        ctx: ExecutionContext,
        *,
        tenant_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._set_tenant_status(
            ctx,
            tenant_id=tenant_id,
            status=OrganizationStatus.SUSPENDED,
            reason=reason,
            expected_version=expected_version,
            action="Org.SuspendTenant",
        )

    def get_enterprise(
        self,
        ctx: ExecutionContext,
        *,
        enterprise_id: UUID,
    ) -> KernelResult[Enterprise]:
        try:
            require_context(ctx, tenant_data_plane=True)
            enterprise = self._repo.get_enterprise(enterprise_id)
            if enterprise is None or enterprise.tenant_id != ctx.tenant_id:
                raise KernelError(
                    ErrorCode.ORG_ENTERPRISE_NOT_FOUND,
                    "enterprise not found",
                )
            return KernelResult.success(enterprise)
        except KernelError as err:
            return KernelResult.from_error(err)

    def list_enterprises(
        self,
        ctx: ExecutionContext,
    ) -> KernelResult[list[Enterprise]]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            return KernelResult.success(self._repo.list_enterprises(ctx.tenant_id))
        except KernelError as err:
            return KernelResult.from_error(err)

    def create_enterprise(
        self,
        ctx: ExecutionContext,
        *,
        legal_name: str,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_tenant_for_mutation(ctx.tenant_id)
            normalized_name = legal_name.strip()
            if not normalized_name:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "enterprise legal_name is required",
                )
            if self._repo.enterprise_legal_name_exists(
                ctx.tenant_id,
                normalized_name,
            ):
                raise KernelError(
                    ErrorCode.ORG_ENTERPRISE_DUPLICATE_NAME,
                    "enterprise legal name already exists in tenant",
                )
            now = datetime.now(timezone.utc)
            enterprise = Enterprise(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                legal_name=normalized_name,
                status=OrganizationStatus.ACTIVE,
                is_primary=False,
                created_at=now,
                updated_at=now,
            )
            self._repo.add_enterprise(enterprise)
            audit = self._audit.record(
                ctx,
                action="Org.CreateEnterprise",
                resource=f"enterprise:{enterprise.id}",
                result="ok",
            )
            self._emit(
                ctx,
                event_name="organization.enterprise.created",
                payload={
                    "enterprise_id": str(enterprise.id),
                    "tenant_id": str(enterprise.tenant_id),
                    "version": enterprise.version,
                    "status": enterprise.status.value,
                    "is_primary": enterprise.is_primary,
                },
            )
            return KernelResult.success(enterprise.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def suspend_enterprise(
        self,
        ctx: ExecutionContext,
        *,
        enterprise_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._set_enterprise_status(
            ctx,
            enterprise_id=enterprise_id,
            status=OrganizationStatus.SUSPENDED,
            reason=reason,
            expected_version=expected_version,
            action="Org.SuspendEnterprise",
        )

    def reactivate_enterprise(
        self,
        ctx: ExecutionContext,
        *,
        enterprise_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._set_enterprise_status(
            ctx,
            enterprise_id=enterprise_id,
            status=OrganizationStatus.ACTIVE,
            reason=reason,
            expected_version=expected_version,
            action="Org.ReactivateEnterprise",
        )

    def close_enterprise(
        self,
        ctx: ExecutionContext,
        *,
        enterprise_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._set_enterprise_status(
            ctx,
            enterprise_id=enterprise_id,
            status=OrganizationStatus.CLOSED,
            reason=reason,
            expected_version=expected_version,
            action="Org.CloseEnterprise",
        )

    def _set_enterprise_status(
        self,
        ctx: ExecutionContext,
        *,
        enterprise_id: UUID,
        status: OrganizationStatus,
        reason: str,
        expected_version: int | None,
        action: str,
    ) -> KernelResult[bool]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_tenant_for_mutation(ctx.tenant_id)
            self._require_reason(reason)
            self._repo.lock_enterprise(ctx.tenant_id, enterprise_id)
            enterprise = self._repo.get_enterprise(enterprise_id)
            if enterprise is None or enterprise.tenant_id != ctx.tenant_id:
                raise KernelError(
                    ErrorCode.ORG_ENTERPRISE_NOT_FOUND,
                    "enterprise not found",
                )
            current_version = self._require_expected_version(expected_version)
            if enterprise.version != current_version:
                raise KernelError(
                    ErrorCode.ORG_VERSION_CONFLICT,
                    "enterprise version conflict",
                )
            allowed_transitions = {
                (OrganizationStatus.ACTIVE, OrganizationStatus.SUSPENDED),
                (OrganizationStatus.SUSPENDED, OrganizationStatus.ACTIVE),
                (OrganizationStatus.ACTIVE, OrganizationStatus.CLOSED),
                (OrganizationStatus.SUSPENDED, OrganizationStatus.CLOSED),
            }
            if (enterprise.status, status) not in allowed_transitions:
                raise KernelError(
                    ErrorCode.ORG_INVALID_STATE_TRANSITION,
                    f"enterprise cannot transition from {enterprise.status} to {status}",
                )
            if status == OrganizationStatus.CLOSED:
                if enterprise.is_primary:
                    raise KernelError(
                        ErrorCode.ORG_ACTIVE_DEPENDENCIES,
                        "primary enterprise closes with the tenant lifecycle",
                    )
                self._ensure_enterprise_has_no_active_dependencies(enterprise)
            enterprise.status = status
            enterprise.updated_at = datetime.now(timezone.utc)
            enterprise.version = current_version + 1
            self._repo.save_enterprise(
                enterprise,
                expected_version=current_version,
            )
            audit = self._audit.record(
                ctx,
                action=action,
                resource=f"enterprise:{enterprise.id}",
                result="ok",
                details={"reason": reason},
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def reactivate_tenant(
        self,
        ctx: ExecutionContext,
        *,
        tenant_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._set_tenant_status(
            ctx,
            tenant_id=tenant_id,
            status=OrganizationStatus.ACTIVE,
            reason=reason,
            expected_version=expected_version,
            action="Org.ReactivateTenant",
        )

    def _set_tenant_status(
        self,
        ctx: ExecutionContext,
        *,
        tenant_id: UUID,
        status: OrganizationStatus,
        reason: str,
        expected_version: int | None,
        action: str,
    ) -> KernelResult[bool]:
        try:
            require_context(ctx, tenant_data_plane=False)
            self._require_platform_governor(ctx)
            self._require_reason(reason)
            tenant = self._repo.get_tenant(tenant_id)
            if tenant is None:
                raise KernelError(ErrorCode.ORG_TENANT_NOT_FOUND, "tenant not found")
            current_version = self._require_expected_version(expected_version)
            if tenant.version != current_version:
                raise KernelError(
                    ErrorCode.ORG_VERSION_CONFLICT,
                    "tenant version conflict",
                )
            if (tenant.status, status) not in {
                (OrganizationStatus.ACTIVE, OrganizationStatus.SUSPENDED),
                (OrganizationStatus.SUSPENDED, OrganizationStatus.ACTIVE),
            }:
                raise KernelError(
                    ErrorCode.ORG_INVALID_STATE_TRANSITION,
                    f"tenant cannot transition from {tenant.status} to {status}",
                )
            tenant.status = status
            tenant.updated_at = datetime.now(timezone.utc)
            tenant.version = current_version + 1
            self._repo.save_tenant(tenant, expected_version=current_version)
            audit = self._audit.record(
                ctx,
                action=action,
                resource=f"tenant:{tenant.id}",
                result="ok",
                details={"reason": reason},
            )
            if status == OrganizationStatus.SUSPENDED:
                self._emit(
                    ctx,
                    event_name="organization.tenant.suspended",
                    payload={
                        "tenant_id": str(tenant.id),
                        "version": tenant.version,
                        "status": tenant.status.value,
                    },
                    tenant_id=tenant.id,
                )
            elif status == OrganizationStatus.ACTIVE:
                self._emit(
                    ctx,
                    event_name="organization.tenant.reactivated",
                    payload={
                        "tenant_id": str(tenant.id),
                        "version": tenant.version,
                        "status": tenant.status.value,
                    },
                    tenant_id=tenant.id,
                )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

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
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_tenant_for_mutation(ctx.tenant_id)
            enterprise = self._resolve_enterprise(
                tenant_id=ctx.tenant_id,
                enterprise_id=enterprise_id,
            )
            if parent_unit_id is not None:
                self._repo.lock_unit_hierarchy(ctx.tenant_id, enterprise.id)
            if not name or not name.strip():
                raise KernelError(ErrorCode.COMMON_VALIDATION_FAILED, "unit name is required")
            try:
                kind = UnitType(unit_type)
            except ValueError as exc:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "invalid unit_type",
                ) from exc
            try:
                unit_status = OrganizationStatus(status)
            except ValueError as exc:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "invalid unit status",
                ) from exc
            if unit_status not in (
                OrganizationStatus.ACTIVE,
                OrganizationStatus.INACTIVE,
            ):
                raise KernelError(
                    ErrorCode.ORG_INVALID_STATE_TRANSITION,
                    "unit upsert only supports active or inactive status",
                )

            if parent_unit_id is not None:
                parent = self._repo.get_unit(parent_unit_id)
                if parent is None:
                    raise KernelError(
                        ErrorCode.ORG_UNIT_PARENT_INVALID,
                        "parent unit not found",
                    )
                if parent.tenant_id != ctx.tenant_id:
                    raise KernelError(
                        ErrorCode.ORG_UNIT_CROSS_TENANT,
                        "parent unit belongs to another tenant",
                    )
                if parent.enterprise_id != enterprise.id:
                    raise KernelError(
                        ErrorCode.ORG_UNIT_ENTERPRISE_MISMATCH,
                        "parent unit belongs to another enterprise",
                    )
                if parent.status != OrganizationStatus.ACTIVE:
                    raise KernelError(
                        ErrorCode.ORG_INVALID_STATE_TRANSITION,
                        "parent unit must be active",
                    )
                self._ensure_acyclic_parent(
                    unit_id=unit_id,
                    parent_unit_id=parent_unit_id,
                )

            now = datetime.now(timezone.utc)
            is_create = unit_id is None
            if unit_id is None:
                if expected_version is not None:
                    raise KernelError(
                        ErrorCode.COMMON_VALIDATION_FAILED,
                        "expected_version is only valid for unit updates",
                    )
                unit = OrganizationUnit(
                    id=uuid4(),
                    tenant_id=ctx.tenant_id,
                    enterprise_id=enterprise.id,
                    unit_type=kind,
                    name=name.strip(),
                    status=unit_status,
                    created_at=now,
                    updated_at=now,
                    parent_unit_id=parent_unit_id,
                )
            else:
                current_version = self._require_expected_version(expected_version)
                unit = self._repo.get_unit(unit_id)
                if unit is None or unit.tenant_id != ctx.tenant_id:
                    raise KernelError(ErrorCode.ORG_UNIT_NOT_FOUND, "unit not found")
                if unit.version != current_version:
                    raise KernelError(
                        ErrorCode.ORG_VERSION_CONFLICT,
                        "organization unit version conflict",
                    )
                if unit.enterprise_id != enterprise.id:
                    raise KernelError(
                        ErrorCode.ORG_UNIT_ENTERPRISE_MISMATCH,
                        "organization unit cannot move across enterprises",
                    )
                if unit.status == OrganizationStatus.CLOSED:
                    raise KernelError(
                        ErrorCode.ORG_INVALID_STATE_TRANSITION,
                        "closed organization unit is immutable",
                    )
                if unit.status != unit_status:
                    raise KernelError(
                        ErrorCode.ORG_INVALID_STATE_TRANSITION,
                        "use SetUnitStatus for unit lifecycle transitions",
                    )
                unit.unit_type = kind
                unit.name = name.strip()
                unit.status = unit_status
                unit.parent_unit_id = parent_unit_id
                unit.updated_at = now
                unit.version = current_version + 1

            self._repo.save_unit(
                unit,
                expected_version=expected_version,
            )
            audit = self._audit.record(
                ctx,
                action="Org.UpsertUnit",
                resource=f"org_unit:{unit.id}",
                result="ok",
            )
            self._emit(
                ctx,
                event_name=(
                    "organization.unit.created"
                    if is_create
                    else "organization.unit.updated"
                ),
                payload={
                    "unit_id": str(unit.id),
                    "enterprise_id": str(unit.enterprise_id),
                    "version": unit.version,
                    "status": unit.status.value,
                },
            )
            return KernelResult.success(unit.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def set_unit_status(
        self,
        ctx: ExecutionContext,
        *,
        unit_id: UUID,
        status: OrganizationStatus | str,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_tenant_for_mutation(ctx.tenant_id)
            self._require_reason(reason)
            unit = self._repo.get_unit(unit_id)
            if unit is None or unit.tenant_id != ctx.tenant_id:
                raise KernelError(ErrorCode.ORG_UNIT_NOT_FOUND, "unit not found")
            self._resolve_enterprise(
                tenant_id=ctx.tenant_id,
                enterprise_id=unit.enterprise_id,
            )
            unit = self._repo.get_unit(unit_id)
            if unit is None:
                raise KernelError(ErrorCode.ORG_UNIT_NOT_FOUND, "unit not found")
            self._repo.lock_unit_hierarchy(ctx.tenant_id, unit.enterprise_id)
            unit = self._repo.get_unit(unit_id)
            if unit is None:
                raise KernelError(ErrorCode.ORG_UNIT_NOT_FOUND, "unit not found")
            try:
                target_status = OrganizationStatus(status)
            except ValueError as exc:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "invalid unit status",
                ) from exc
            if target_status not in (
                OrganizationStatus.ACTIVE,
                OrganizationStatus.INACTIVE,
                OrganizationStatus.CLOSED,
            ):
                raise KernelError(
                    ErrorCode.ORG_INVALID_STATE_TRANSITION,
                    "unsupported unit status",
                )
            if (unit.status, target_status) not in {
                (OrganizationStatus.ACTIVE, OrganizationStatus.INACTIVE),
                (OrganizationStatus.INACTIVE, OrganizationStatus.ACTIVE),
                (OrganizationStatus.ACTIVE, OrganizationStatus.CLOSED),
                (OrganizationStatus.INACTIVE, OrganizationStatus.CLOSED),
            }:
                raise KernelError(
                    ErrorCode.ORG_INVALID_STATE_TRANSITION,
                    f"unit cannot transition from {unit.status} to {target_status}",
                )
            if target_status in (
                OrganizationStatus.INACTIVE,
                OrganizationStatus.CLOSED,
            ):
                self._ensure_unit_has_no_active_dependencies(unit)
            current_version = self._require_expected_version(expected_version)
            if unit.version != current_version:
                raise KernelError(
                    ErrorCode.ORG_VERSION_CONFLICT,
                    "organization unit version conflict",
                )
            unit.status = target_status
            unit.updated_at = datetime.now(timezone.utc)
            unit.version = current_version + 1
            self._repo.save_unit(unit, expected_version=current_version)
            audit = self._audit.record(
                ctx,
                action="Org.SetUnitStatus",
                resource=f"org_unit:{unit.id}",
                result="ok",
                details={"reason": reason, "status": target_status.value},
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_unit_tree(
        self,
        ctx: ExecutionContext,
        *,
        root_unit_id: UUID | None = None,
    ) -> KernelResult[list[OrganizationUnit]]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            units = self._repo.list_units(ctx.tenant_id)
            if root_unit_id is None:
                return KernelResult.success(units)
            root = next((unit for unit in units if unit.id == root_unit_id), None)
            if root is None:
                raise KernelError(ErrorCode.ORG_UNIT_NOT_FOUND, "unit not found")
            descendants = [root]
            pending = [root.id]
            while pending:
                parent_id = pending.pop()
                children = [unit for unit in units if unit.parent_unit_id == parent_id]
                descendants.extend(children)
                pending.extend(child.id for child in children)
            return KernelResult.success(descendants)
        except KernelError as err:
            return KernelResult.from_error(err)

    def add_membership(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID,
        enterprise_id: UUID | None = None,
        org_unit_id: UUID | None = None,
        membership_role_label: str | None = None,
    ) -> KernelResult[UUID]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_tenant_for_mutation(ctx.tenant_id)
            enterprise = self._resolve_enterprise(
                tenant_id=ctx.tenant_id,
                enterprise_id=enterprise_id,
            )
            if not self._membership_eligibility.is_eligible(
                subject_id=subject_id,
                tenant_id=ctx.tenant_id,
            ):
                raise KernelError(
                    ErrorCode.ORG_SUBJECT_INELIGIBLE,
                    "subject is not eligible for tenant membership",
                )
            if org_unit_id is not None:
                unit = self._repo.get_unit(org_unit_id)
                if unit is None:
                    raise KernelError(ErrorCode.ORG_UNIT_NOT_FOUND, "unit not found")
                if unit.tenant_id != ctx.tenant_id:
                    raise KernelError(
                        ErrorCode.ORG_CROSS_TENANT_FORBIDDEN,
                        "cross-tenant membership is forbidden",
                    )
                if unit.enterprise_id != enterprise.id:
                    raise KernelError(
                        ErrorCode.ORG_UNIT_ENTERPRISE_MISMATCH,
                        "membership unit belongs to another enterprise",
                    )
                if unit.status != OrganizationStatus.ACTIVE:
                    raise KernelError(
                        ErrorCode.ORG_INVALID_STATE_TRANSITION,
                        "membership unit must be active",
                    )

            for existing in self._repo.list_memberships(ctx.tenant_id):
                if (
                    existing.subject_id == subject_id
                    and existing.enterprise_id == enterprise.id
                    and existing.org_unit_id == org_unit_id
                    and existing.status == OrganizationStatus.ACTIVE
                ):
                    raise KernelError(
                        ErrorCode.ORG_MEMBERSHIP_DUPLICATE,
                        "active membership already exists",
                    )

            now = datetime.now(timezone.utc)
            membership = Membership(
                id=uuid4(),
                tenant_id=ctx.tenant_id,
                enterprise_id=enterprise.id,
                subject_id=subject_id,
                status=OrganizationStatus.ACTIVE,
                created_at=now,
                updated_at=now,
                org_unit_id=org_unit_id,
                membership_role_label=membership_role_label,
            )
            self._repo.add_membership(membership)
            audit = self._audit.record(
                ctx,
                action="Org.AddMembership",
                resource=f"membership:{membership.id}",
                result="ok",
            )
            self._emit(
                ctx,
                event_name="organization.membership.added",
                payload={
                    "membership_id": str(membership.id),
                    "subject_id": str(membership.subject_id),
                    "enterprise_id": str(membership.enterprise_id),
                    "version": membership.version,
                    "status": membership.status.value,
                },
            )
            return KernelResult.success(membership.id, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def remove_membership(
        self,
        ctx: ExecutionContext,
        *,
        membership_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_tenant_for_mutation(ctx.tenant_id)
            self._require_reason(reason)
            membership = self._repo.get_membership(membership_id)
            if membership is None or membership.tenant_id != ctx.tenant_id:
                raise KernelError(
                    ErrorCode.ORG_MEMBERSHIP_NOT_FOUND,
                    "membership not found",
                )
            self._resolve_enterprise(
                tenant_id=ctx.tenant_id,
                enterprise_id=membership.enterprise_id,
            )
            membership = self._repo.get_membership(membership_id)
            if membership is None:
                raise KernelError(
                    ErrorCode.ORG_MEMBERSHIP_NOT_FOUND,
                    "membership not found",
                )
            if membership.status not in (
                OrganizationStatus.ACTIVE,
                OrganizationStatus.SUSPENDED,
            ):
                raise KernelError(
                    ErrorCode.ORG_MEMBERSHIP_NOT_ACTIVE,
                    "membership is not active or suspended",
                )
            current_version = self._require_expected_version(expected_version)
            if membership.version != current_version:
                raise KernelError(
                    ErrorCode.ORG_VERSION_CONFLICT,
                    "membership version conflict",
                )
            now = datetime.now(timezone.utc)
            membership.status = OrganizationStatus.ENDED
            membership.ended_at = now
            membership.updated_at = now
            membership.version = current_version + 1
            self._repo.save_membership(
                membership,
                expected_version=current_version,
            )
            audit = self._audit.record(
                ctx,
                action="Org.RemoveMembership",
                resource=f"membership:{membership.id}",
                result="ok",
                details={"reason": reason},
            )
            self._emit(
                ctx,
                event_name="organization.membership.ended",
                payload={
                    "membership_id": str(membership.id),
                    "version": membership.version,
                    "status": membership.status.value,
                },
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def list_memberships(
        self,
        ctx: ExecutionContext,
        *,
        subject_id: UUID | None = None,
        org_unit_id: UUID | None = None,
        status: OrganizationStatus | None = None,
    ) -> KernelResult[list[Membership]]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            memberships = self._repo.list_memberships(ctx.tenant_id)
            if subject_id is not None:
                memberships = [m for m in memberships if m.subject_id == subject_id]
            if org_unit_id is not None:
                memberships = [m for m in memberships if m.org_unit_id == org_unit_id]
            if status is not None:
                memberships = [m for m in memberships if m.status == status]
            return KernelResult.success(memberships)
        except KernelError as err:
            return KernelResult.from_error(err)

    def suspend_membership(
        self,
        ctx: ExecutionContext,
        *,
        membership_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._set_membership_status(
            ctx,
            membership_id=membership_id,
            status=OrganizationStatus.SUSPENDED,
            reason=reason,
            expected_version=expected_version,
            action="Org.SuspendMembership",
        )

    def reactivate_membership(
        self,
        ctx: ExecutionContext,
        *,
        membership_id: UUID,
        reason: str,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        return self._set_membership_status(
            ctx,
            membership_id=membership_id,
            status=OrganizationStatus.ACTIVE,
            reason=reason,
            expected_version=expected_version,
            action="Org.ReactivateMembership",
        )

    def _set_membership_status(
        self,
        ctx: ExecutionContext,
        *,
        membership_id: UUID,
        status: OrganizationStatus,
        reason: str,
        expected_version: int | None,
        action: str,
    ) -> KernelResult[bool]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_tenant_for_mutation(ctx.tenant_id)
            self._require_reason(reason)
            membership = self._repo.get_membership(membership_id)
            if membership is None or membership.tenant_id != ctx.tenant_id:
                raise KernelError(
                    ErrorCode.ORG_MEMBERSHIP_NOT_FOUND,
                    "membership not found",
                )
            self._resolve_enterprise(
                tenant_id=ctx.tenant_id,
                enterprise_id=membership.enterprise_id,
            )
            membership = self._repo.get_membership(membership_id)
            if membership is None:
                raise KernelError(
                    ErrorCode.ORG_MEMBERSHIP_NOT_FOUND,
                    "membership not found",
                )
            current_version = self._require_expected_version(expected_version)
            if membership.version != current_version:
                raise KernelError(
                    ErrorCode.ORG_VERSION_CONFLICT,
                    "membership version conflict",
                )
            if (membership.status, status) not in {
                (OrganizationStatus.ACTIVE, OrganizationStatus.SUSPENDED),
                (OrganizationStatus.SUSPENDED, OrganizationStatus.ACTIVE),
            }:
                raise KernelError(
                    ErrorCode.ORG_INVALID_STATE_TRANSITION,
                    f"membership cannot transition from {membership.status} to {status}",
                )
            if (
                status == OrganizationStatus.ACTIVE
                and membership.org_unit_id is not None
            ):
                target = self._repo.get_unit(membership.org_unit_id)
                if target is None or target.status != OrganizationStatus.ACTIVE:
                    raise KernelError(
                        ErrorCode.ORG_INVALID_STATE_TRANSITION,
                        "membership unit must be active",
                    )
            membership.status = status
            membership.updated_at = datetime.now(timezone.utc)
            membership.version = current_version + 1
            self._repo.save_membership(
                membership,
                expected_version=current_version,
            )
            audit = self._audit.record(
                ctx,
                action=action,
                resource=f"membership:{membership.id}",
                result="ok",
                details={"reason": reason},
            )
            if status == OrganizationStatus.SUSPENDED:
                self._emit(
                    ctx,
                    event_name="organization.membership.suspended",
                    payload={
                        "membership_id": str(membership.id),
                        "version": membership.version,
                        "status": membership.status.value,
                    },
                )
            elif status == OrganizationStatus.ACTIVE:
                self._emit(
                    ctx,
                    event_name="organization.membership.reactivated",
                    payload={
                        "membership_id": str(membership.id),
                        "version": membership.version,
                        "status": membership.status.value,
                    },
                )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def transfer_membership_unit(
        self,
        ctx: ExecutionContext,
        *,
        membership_id: UUID,
        to_org_unit_id: UUID,
        expected_version: int | None = None,
    ) -> KernelResult[bool]:
        try:
            require_context(ctx, tenant_data_plane=True)
            assert ctx.tenant_id is not None
            self._require_tenant_for_mutation(ctx.tenant_id)
            membership = self._repo.get_membership(membership_id)
            if membership is None or membership.tenant_id != ctx.tenant_id:
                raise KernelError(
                    ErrorCode.ORG_MEMBERSHIP_NOT_FOUND,
                    "membership not found",
                )
            self._resolve_enterprise(
                tenant_id=ctx.tenant_id,
                enterprise_id=membership.enterprise_id,
            )
            membership = self._repo.get_membership(membership_id)
            if membership is None:
                raise KernelError(
                    ErrorCode.ORG_MEMBERSHIP_NOT_FOUND,
                    "membership not found",
                )
            if membership.status != OrganizationStatus.ACTIVE:
                raise KernelError(
                    ErrorCode.ORG_MEMBERSHIP_NOT_ACTIVE,
                    "only active membership can be transferred",
                )
            current_version = self._require_expected_version(expected_version)
            if membership.version != current_version:
                raise KernelError(
                    ErrorCode.ORG_VERSION_CONFLICT,
                    "membership version conflict",
                )
            target = self._repo.get_unit(to_org_unit_id)
            if target is None:
                raise KernelError(ErrorCode.ORG_UNIT_NOT_FOUND, "target unit not found")
            if target.tenant_id != ctx.tenant_id:
                raise KernelError(
                    ErrorCode.ORG_CROSS_TENANT_FORBIDDEN,
                    "cross-tenant transfer is forbidden",
                )
            if target.enterprise_id != membership.enterprise_id:
                raise KernelError(
                    ErrorCode.ORG_UNIT_ENTERPRISE_MISMATCH,
                    "membership cannot transfer across enterprises",
                )
            if target.status != OrganizationStatus.ACTIVE:
                raise KernelError(
                    ErrorCode.ORG_INVALID_STATE_TRANSITION,
                    "target unit must be active",
                )
            membership.org_unit_id = to_org_unit_id
            membership.updated_at = datetime.now(timezone.utc)
            membership.version = current_version + 1
            self._repo.save_membership(
                membership,
                expected_version=current_version,
            )
            audit = self._audit.record(
                ctx,
                action="Org.TransferMembershipUnit",
                resource=f"membership:{membership.id}",
                result="ok",
            )
            self._emit(
                ctx,
                event_name="organization.membership.transferred",
                payload={
                    "membership_id": str(membership.id),
                    "to_org_unit_id": str(to_org_unit_id),
                    "version": membership.version,
                },
            )
            return KernelResult.success(True, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)

    def _require_tenant_for_mutation(self, tenant_id: UUID) -> Tenant:
        tenant = self._repo.get_tenant(tenant_id)
        if tenant is None:
            raise KernelError(ErrorCode.ORG_TENANT_NOT_FOUND, "tenant not found")
        if tenant.status == OrganizationStatus.SUSPENDED:
            raise KernelError(ErrorCode.ORG_TENANT_SUSPENDED, "tenant is suspended")
        if tenant.status == OrganizationStatus.CLOSED:
            raise KernelError(ErrorCode.ORG_TENANT_CLOSED, "tenant is closed")
        if tenant.status != OrganizationStatus.ACTIVE:
            raise KernelError(
                ErrorCode.ORG_INVALID_STATE_TRANSITION,
                "tenant is not active",
            )
        return tenant

    def _resolve_enterprise(
        self,
        *,
        tenant_id: UUID,
        enterprise_id: UUID | None,
    ) -> Enterprise:
        enterprise = (
            self._repo.get_enterprise(enterprise_id)
            if enterprise_id is not None
            else self._repo.get_primary_enterprise(tenant_id)
        )
        if enterprise is None or enterprise.tenant_id != tenant_id:
            raise KernelError(
                ErrorCode.ORG_ENTERPRISE_NOT_FOUND,
                "enterprise not found",
            )
        self._repo.lock_enterprise(tenant_id, enterprise.id)
        enterprise = self._repo.get_enterprise(enterprise.id)
        if enterprise is None:
            raise KernelError(
                ErrorCode.ORG_ENTERPRISE_NOT_FOUND,
                "enterprise not found",
            )
        if enterprise.status != OrganizationStatus.ACTIVE:
            raise KernelError(
                ErrorCode.ORG_INVALID_STATE_TRANSITION,
                "enterprise is not active",
            )
        return enterprise

    def _ensure_enterprise_has_no_active_dependencies(
        self,
        enterprise: Enterprise,
    ) -> None:
        if any(
            unit.enterprise_id == enterprise.id
            and unit.status != OrganizationStatus.CLOSED
            for unit in self._repo.list_units(enterprise.tenant_id)
        ):
            raise KernelError(
                ErrorCode.ORG_ACTIVE_DEPENDENCIES,
                "organization units block enterprise close",
            )
        if any(
            membership.enterprise_id == enterprise.id
            and membership.status in (
                OrganizationStatus.ACTIVE,
                OrganizationStatus.SUSPENDED,
            )
            for membership in self._repo.list_memberships(enterprise.tenant_id)
        ):
            raise KernelError(
                ErrorCode.ORG_ACTIVE_DEPENDENCIES,
                "memberships block enterprise close",
            )

    def _ensure_acyclic_parent(
        self,
        *,
        unit_id: UUID | None,
        parent_unit_id: UUID,
    ) -> None:
        if unit_id is None:
            return
        if parent_unit_id == unit_id:
            raise KernelError(
                ErrorCode.ORG_UNIT_CYCLE_DETECTED,
                "organization unit cannot be its own parent",
            )
        visited: set[UUID] = set()
        current_id: UUID | None = parent_unit_id
        while current_id is not None:
            if current_id == unit_id or current_id in visited:
                raise KernelError(
                    ErrorCode.ORG_UNIT_CYCLE_DETECTED,
                    "organization unit hierarchy must be acyclic",
                )
            visited.add(current_id)
            current = self._repo.get_unit(current_id)
            if current is None:
                break
            current_id = current.parent_unit_id

    def _ensure_unit_has_no_active_dependencies(
        self,
        unit: OrganizationUnit,
    ) -> None:
        units = self._repo.list_units(unit.tenant_id)
        subtree_ids = {unit.id}
        pending = [unit.id]
        while pending:
            parent_id = pending.pop()
            for candidate in units:
                if (
                    candidate.parent_unit_id == parent_id
                    and candidate.id not in subtree_ids
                ):
                    subtree_ids.add(candidate.id)
                    pending.append(candidate.id)
                    if candidate.status == OrganizationStatus.ACTIVE:
                        raise KernelError(
                            ErrorCode.ORG_ACTIVE_DEPENDENCIES,
                            "active descendant blocks unit lifecycle transition",
                        )
        if any(
            membership.org_unit_id in subtree_ids
            and membership.status in (
                OrganizationStatus.ACTIVE,
                OrganizationStatus.SUSPENDED,
            )
            for membership in self._repo.list_memberships(unit.tenant_id)
        ):
            raise KernelError(
                ErrorCode.ORG_ACTIVE_DEPENDENCIES,
                "active membership blocks unit lifecycle transition",
            )

    @staticmethod
    def _require_expected_version(expected_version: int | None) -> int:
        if expected_version is None or expected_version < 1:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "expected_version must be a positive integer",
            )
        return expected_version

    @staticmethod
    def _require_reason(reason: str) -> None:
        if not reason or not reason.strip():
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "reason is required",
            )

    def _require_platform_governor(self, ctx: ExecutionContext) -> None:
        if not ctx.platform_scope or ctx.subject_id not in self._platform_governors:
            raise KernelError(
                ErrorCode.PERMISSION_DENIED,
                "platform governance authority is required",
            )

    def _emit(
        self,
        ctx: ExecutionContext,
        *,
        event_name: str,
        payload: dict[str, object],
        tenant_id: UUID | None = None,
    ) -> None:
        if self._domain_events is None:
            return
        self._domain_events.enqueue_fact(
            ctx,
            event_name=event_name,
            producer="organization.kernel",
            payload=payload,
            tenant_id=tenant_id,
        )
