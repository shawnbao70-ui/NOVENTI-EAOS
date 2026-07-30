"""Organization ↔ Permission boundary contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from kernel.organization.service import OrganizationService
from kernel.permission.models import PermissionEffect, Resource
from kernel.permission.service import PermissionService
from kernel.shared.context import ExecutionContext, SubjectType

GOVERNOR_ID = uuid4()
GRANT_ADMIN_ID = uuid4()


class _AllowAllMembershipEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


class _AllowAllPrincipalEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx(tenant_id: UUID | None, subject_id: UUID, *, platform: bool = False) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id,
        subject_type=SubjectType.HUMAN,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        tenant_id=tenant_id,
        platform_scope=platform,
    )


def test_membership_role_label_never_grants_permission_implicitly() -> None:
    organization = OrganizationService(
        platform_governors={GOVERNOR_ID},
        membership_eligibility=_AllowAllMembershipEligibility(),
    )
    permission = PermissionService(
        grant_administrators={GRANT_ADMIN_ID},
        principal_eligibility=_AllowAllPrincipalEligibility(),
    )
    tenant_result = organization.create_tenant(
        _ctx(None, GOVERNOR_ID, platform=True),
        legal_name="Boundary Test Tenant",
    )
    assert tenant_result.data is not None
    tenant_id = tenant_result.data
    subject_id = uuid4()
    tenant_ctx = _ctx(tenant_id, GRANT_ADMIN_ID)

    membership = organization.add_membership(
        tenant_ctx,
        subject_id=subject_id,
        membership_role_label="administrator",
    )
    assert membership.ok

    before_grant = permission.evaluate(
        tenant_ctx,
        principal_subject_id=subject_id,
        action="write",
        resource=Resource(tenant_id=tenant_id, resource_type="tenant_settings"),
    )
    assert before_grant.data is not None
    assert before_grant.data.effect == PermissionEffect.DENY

    explicit = permission.grant(
        tenant_ctx,
        principal_subject_id=subject_id,
        resource_type="tenant_settings",
        actions={"write"},
    )
    assert explicit.ok
    after_grant = permission.evaluate(
        tenant_ctx,
        principal_subject_id=subject_id,
        action="write",
        resource=Resource(tenant_id=tenant_id, resource_type="tenant_settings"),
    )
    assert after_grant.data is not None
    assert after_grant.data.effect == PermissionEffect.ALLOW
