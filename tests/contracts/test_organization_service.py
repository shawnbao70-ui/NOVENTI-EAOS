"""Organization Kernel contract tests — O-01..O-05."""

from __future__ import annotations

from uuid import UUID, uuid4

from kernel.organization.models import OrganizationStatus, UnitType
from kernel.organization.service import OrganizationService
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode

GOVERNOR_ID = uuid4()


class _AllowAllMembershipEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _service() -> OrganizationService:
    return OrganizationService(
        platform_governors={GOVERNOR_ID},
        membership_eligibility=_AllowAllMembershipEligibility(),
    )


def _platform_ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=GOVERNOR_ID,
        subject_type=SubjectType.SERVICE,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        platform_scope=True,
    )


def _tenant_ctx(tenant_id: UUID) -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
        correlation_id=str(uuid4()),
        request_time=ExecutionContext.utc_now(),
        tenant_id=tenant_id,
    )


def _create_tenant(service: OrganizationService, name: str = "Acme") -> UUID:
    result = service.create_tenant(_platform_ctx(), legal_name=name)
    assert result.ok and result.data is not None
    return result.data


def test_o01_create_tenant_is_audited() -> None:
    service = OrganizationService(platform_governors={GOVERNOR_ID})
    result = service.create_tenant(_platform_ctx(), legal_name="Acme")
    assert result.ok
    assert result.audit_id is not None
    assert len(service.audit_log.list_events()) == 1


def test_create_tenant_creates_one_primary_enterprise() -> None:
    service = OrganizationService(platform_governors={GOVERNOR_ID})
    tenant_id = _create_tenant(service, "Acme Holdings")

    enterprises = service.list_enterprises(_tenant_ctx(tenant_id))

    assert enterprises.ok and enterprises.data is not None
    assert len(enterprises.data) == 1
    assert enterprises.data[0].tenant_id == tenant_id
    assert enterprises.data[0].legal_name == "Acme Holdings"
    assert enterprises.data[0].is_primary


def test_duplicate_tenant_name_is_rejected() -> None:
    service = OrganizationService(platform_governors={GOVERNOR_ID})
    assert service.create_tenant(_platform_ctx(), legal_name="Acme").ok
    duplicate = service.create_tenant(_platform_ctx(), legal_name="acme")
    assert not duplicate.ok
    assert duplicate.error_code == ErrorCode.ORG_TENANT_DUPLICATE_NAME


def test_o02_upsert_unit_parent_must_share_tenant() -> None:
    service = OrganizationService(platform_governors={GOVERNOR_ID})
    tenant_a = _create_tenant(service, "A")
    tenant_b = _create_tenant(service, "B")
    parent = service.upsert_unit(
        _tenant_ctx(tenant_a),
        unit_type=UnitType.HEADQUARTERS,
        name="A HQ",
    )
    assert parent.ok and parent.data is not None
    child = service.upsert_unit(
        _tenant_ctx(tenant_a),
        unit_type=UnitType.DEPARTMENT,
        name="Sales",
        parent_unit_id=parent.data,
    )
    assert child.ok

    cross_tenant = service.upsert_unit(
        _tenant_ctx(tenant_b),
        unit_type=UnitType.DEPARTMENT,
        name="Invalid",
        parent_unit_id=parent.data,
    )
    assert not cross_tenant.ok
    assert cross_tenant.error_code == ErrorCode.ORG_UNIT_CROSS_TENANT


def test_o03_cross_tenant_membership_is_forbidden() -> None:
    service = _service()
    tenant_a = _create_tenant(service, "A")
    tenant_b = _create_tenant(service, "B")
    unit_a = service.upsert_unit(
        _tenant_ctx(tenant_a),
        unit_type=UnitType.DEPARTMENT,
        name="A Unit",
    )
    assert unit_a.data is not None
    result = service.add_membership(
        _tenant_ctx(tenant_b),
        subject_id=uuid4(),
        org_unit_id=unit_a.data,
    )
    assert not result.ok
    assert result.error_code == ErrorCode.ORG_CROSS_TENANT_FORBIDDEN


def test_o04_membership_lifecycle() -> None:
    service = _service()
    tenant = _create_tenant(service)
    ctx = _tenant_ctx(tenant)
    unit = service.upsert_unit(
        ctx,
        unit_type=UnitType.DEPARTMENT,
        name="Engineering",
    )
    assert unit.data is not None
    subject_id = uuid4()
    added = service.add_membership(
        ctx,
        subject_id=subject_id,
        org_unit_id=unit.data,
        membership_role_label="manager",
    )
    assert added.ok and added.data is not None

    listed = service.list_memberships(ctx, subject_id=subject_id)
    assert listed.ok and listed.data is not None
    assert len(listed.data) == 1

    removed = service.remove_membership(
        ctx,
        membership_id=added.data,
        reason="left organization",
        expected_version=1,
    )
    assert removed.ok
    ended = service.list_memberships(ctx, status=OrganizationStatus.ENDED)
    assert ended.data is not None and len(ended.data) == 1


def test_o05_role_label_does_not_create_permission_state() -> None:
    service = _service()
    tenant = _create_tenant(service)
    result = service.add_membership(
        _tenant_ctx(tenant),
        subject_id=uuid4(),
        membership_role_label="administrator",
    )
    assert result.ok
    # Organization owns membership only; no permission service or grant is produced.
    assert not hasattr(service, "_permission")


def test_platform_scope_without_governor_authority_is_denied() -> None:
    service = OrganizationService()
    result = service.create_tenant(_platform_ctx(), legal_name="Unauthorized")
    assert not result.ok
    assert result.error_code == ErrorCode.PERMISSION_DENIED


def test_suspended_tenant_blocks_membership_mutation() -> None:
    service = _service()
    tenant = _create_tenant(service)
    assert service.suspend_tenant(
        _platform_ctx(),
        tenant_id=tenant,
        reason="compliance hold",
        expected_version=1,
    ).ok

    added = service.add_membership(
        _tenant_ctx(tenant),
        subject_id=uuid4(),
    )

    assert not added.ok
    assert added.error_code == ErrorCode.ORG_TENANT_SUSPENDED


def test_unit_hierarchy_rejects_self_and_descendant_parent() -> None:
    service = _service()
    tenant = _create_tenant(service)
    ctx = _tenant_ctx(tenant)
    root = service.upsert_unit(
        ctx,
        unit_type=UnitType.HEADQUARTERS,
        name="HQ",
    )
    assert root.data is not None
    child = service.upsert_unit(
        ctx,
        unit_type=UnitType.DEPARTMENT,
        name="Engineering",
        parent_unit_id=root.data,
    )
    assert child.data is not None

    self_parent = service.upsert_unit(
        ctx,
        unit_id=root.data,
        unit_type=UnitType.HEADQUARTERS,
        name="HQ",
        parent_unit_id=root.data,
    )
    assert self_parent.error_code == ErrorCode.ORG_UNIT_CYCLE_DETECTED

    descendant_parent = service.upsert_unit(
        ctx,
        unit_id=root.data,
        unit_type=UnitType.HEADQUARTERS,
        name="HQ",
        parent_unit_id=child.data,
    )
    assert descendant_parent.error_code == ErrorCode.ORG_UNIT_CYCLE_DETECTED


def test_ended_membership_is_immutable() -> None:
    service = _service()
    tenant = _create_tenant(service)
    ctx = _tenant_ctx(tenant)
    unit = service.upsert_unit(
        ctx,
        unit_type=UnitType.DEPARTMENT,
        name="Engineering",
    )
    target = service.upsert_unit(
        ctx,
        unit_type=UnitType.DEPARTMENT,
        name="Operations",
    )
    assert unit.data is not None and target.data is not None
    membership = service.add_membership(
        ctx,
        subject_id=uuid4(),
        org_unit_id=unit.data,
    )
    assert membership.data is not None
    assert service.remove_membership(
        ctx,
        membership_id=membership.data,
        reason="left",
        expected_version=1,
    ).ok

    repeated = service.remove_membership(
        ctx,
        membership_id=membership.data,
        reason="again",
    )
    transferred = service.transfer_membership_unit(
        ctx,
        membership_id=membership.data,
        to_org_unit_id=target.data,
    )

    assert repeated.error_code == ErrorCode.ORG_MEMBERSHIP_NOT_ACTIVE
    assert transferred.error_code == ErrorCode.ORG_MEMBERSHIP_NOT_ACTIVE


def test_unit_update_rejects_stale_version() -> None:
    service = _service()
    tenant = _create_tenant(service)
    ctx = _tenant_ctx(tenant)
    created = service.upsert_unit(
        ctx,
        unit_type=UnitType.DEPARTMENT,
        name="Engineering",
    )
    assert created.data is not None
    updated = service.upsert_unit(
        ctx,
        unit_id=created.data,
        unit_type=UnitType.DEPARTMENT,
        name="Product Engineering",
        expected_version=1,
    )
    assert updated.ok

    stale = service.upsert_unit(
        ctx,
        unit_id=created.data,
        unit_type=UnitType.DEPARTMENT,
        name="Stale Update",
        expected_version=1,
    )

    assert stale.error_code == ErrorCode.ORG_VERSION_CONFLICT
    units = service.get_unit_tree(ctx)
    assert units.data is not None
    unit = next(item for item in units.data if item.id == created.data)
    assert unit.name == "Product Engineering"
    assert unit.version == 2


def test_membership_suspend_and_reactivate_state_machine() -> None:
    service = _service()
    tenant = _create_tenant(service)
    ctx = _tenant_ctx(tenant)
    subject_id = uuid4()
    membership = service.add_membership(ctx, subject_id=subject_id)
    assert membership.data is not None

    assert service.suspend_membership(
        ctx,
        membership_id=membership.data,
        reason="temporary leave",
        expected_version=1,
    ).ok
    transferred_while_suspended = service.transfer_membership_unit(
        ctx,
        membership_id=membership.data,
        to_org_unit_id=uuid4(),
        expected_version=2,
    )
    assert transferred_while_suspended.error_code == ErrorCode.ORG_MEMBERSHIP_NOT_ACTIVE
    assert service.reactivate_membership(
        ctx,
        membership_id=membership.data,
        reason="returned",
        expected_version=2,
    ).ok

    listed = service.list_memberships(ctx, subject_id=subject_id)
    assert listed.data is not None
    assert listed.data[0].status == OrganizationStatus.ACTIVE
    assert listed.data[0].version == 3


def test_multiple_enterprises_have_independent_lifecycle() -> None:
    service = _service()
    tenant = _create_tenant(service)
    ctx = _tenant_ctx(tenant)
    created = service.create_enterprise(ctx, legal_name="Acme Europe")
    assert created.data is not None
    assert len(service.list_enterprises(ctx).data or []) == 2

    assert service.suspend_enterprise(
        ctx,
        enterprise_id=created.data,
        reason="regional hold",
        expected_version=1,
    ).ok
    blocked = service.upsert_unit(
        ctx,
        enterprise_id=created.data,
        unit_type=UnitType.BRANCH,
        name="Berlin",
    )
    assert blocked.error_code == ErrorCode.ORG_INVALID_STATE_TRANSITION
    assert service.reactivate_enterprise(
        ctx,
        enterprise_id=created.data,
        reason="hold released",
        expected_version=2,
    ).ok
    assert service.upsert_unit(
        ctx,
        enterprise_id=created.data,
        unit_type=UnitType.BRANCH,
        name="Berlin",
    ).ok


def test_enterprise_close_and_primary_guard() -> None:
    service = _service()
    tenant = _create_tenant(service)
    ctx = _tenant_ctx(tenant)
    primary = (service.list_enterprises(ctx).data or [])[0]
    secondary = service.create_enterprise(ctx, legal_name="Acme Closure")
    assert secondary.data is not None

    assert service.close_enterprise(
        ctx,
        enterprise_id=secondary.data,
        reason="entity dissolved",
        expected_version=1,
    ).ok
    closed = service.get_enterprise(ctx, enterprise_id=secondary.data)
    assert closed.data is not None
    assert closed.data.status == OrganizationStatus.CLOSED
    denied = service.close_enterprise(
        ctx,
        enterprise_id=primary.id,
        reason="invalid direct close",
        expected_version=1,
    )
    assert denied.error_code == ErrorCode.ORG_ACTIVE_DEPENDENCIES


def test_suspended_enterprise_blocks_all_member_and_unit_writes() -> None:
    service = _service()
    tenant = _create_tenant(service)
    ctx = _tenant_ctx(tenant)
    enterprise = service.create_enterprise(ctx, legal_name="Acme Suspended")
    assert enterprise.data is not None
    unit = service.upsert_unit(
        ctx,
        enterprise_id=enterprise.data,
        unit_type=UnitType.DEPARTMENT,
        name="Operations",
    )
    assert unit.data is not None
    membership = service.add_membership(
        ctx,
        enterprise_id=enterprise.data,
        subject_id=uuid4(),
        org_unit_id=unit.data,
    )
    assert membership.data is not None
    assert service.suspend_enterprise(
        ctx,
        enterprise_id=enterprise.data,
        reason="compliance hold",
        expected_version=1,
    ).ok

    operations = (
        service.set_unit_status(
            ctx,
            unit_id=unit.data,
            status=OrganizationStatus.INACTIVE,
            reason="blocked",
            expected_version=1,
        ),
        service.remove_membership(
            ctx,
            membership_id=membership.data,
            reason="blocked",
            expected_version=1,
        ),
        service.suspend_membership(
            ctx,
            membership_id=membership.data,
            reason="blocked",
            expected_version=1,
        ),
        service.transfer_membership_unit(
            ctx,
            membership_id=membership.data,
            to_org_unit_id=unit.data,
            expected_version=1,
        ),
    )
    assert all(
        result.error_code == ErrorCode.ORG_INVALID_STATE_TRANSITION
        for result in operations
    )


def test_subject_can_join_two_enterprises_but_not_duplicate_one() -> None:
    service = _service()
    tenant = _create_tenant(service)
    ctx = _tenant_ctx(tenant)
    primary = (service.list_enterprises(ctx).data or [])[0]
    secondary = service.create_enterprise(ctx, legal_name="Acme Asia")
    assert secondary.data is not None
    subject_id = uuid4()

    assert service.add_membership(
        ctx,
        enterprise_id=primary.id,
        subject_id=subject_id,
    ).ok
    assert service.add_membership(
        ctx,
        enterprise_id=secondary.data,
        subject_id=subject_id,
    ).ok
    duplicate = service.add_membership(
        ctx,
        enterprise_id=secondary.data,
        subject_id=subject_id,
    )
    assert duplicate.error_code == ErrorCode.ORG_MEMBERSHIP_DUPLICATE


def test_unit_lifecycle_requires_dependencies_to_end() -> None:
    service = _service()
    tenant = _create_tenant(service)
    ctx = _tenant_ctx(tenant)
    unit = service.upsert_unit(
        ctx,
        unit_type=UnitType.DEPARTMENT,
        name="Engineering",
    )
    assert unit.data is not None
    membership = service.add_membership(
        ctx,
        subject_id=uuid4(),
        org_unit_id=unit.data,
    )
    assert membership.data is not None

    blocked = service.set_unit_status(
        ctx,
        unit_id=unit.data,
        status=OrganizationStatus.INACTIVE,
        reason="reorganization",
        expected_version=1,
    )
    assert blocked.error_code == ErrorCode.ORG_ACTIVE_DEPENDENCIES
    assert service.remove_membership(
        ctx,
        membership_id=membership.data,
        reason="reassigned",
        expected_version=1,
    ).ok
    assert service.set_unit_status(
        ctx,
        unit_id=unit.data,
        status=OrganizationStatus.INACTIVE,
        reason="reorganization",
        expected_version=1,
    ).ok
    denied = service.add_membership(
        ctx,
        subject_id=uuid4(),
        org_unit_id=unit.data,
    )
    assert denied.error_code == ErrorCode.ORG_INVALID_STATE_TRANSITION
