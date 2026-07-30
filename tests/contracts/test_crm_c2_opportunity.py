"""PHX-G295 CRM Opportunity C2 package contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import (
    CUSTOMER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    CRMService,
)


class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx(tenant_id: UUID, subject_id: UUID | None = None) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id or uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant_id,
        correlation_id=f"corr-g295-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(
    ctx: ExecutionContext,
    *,
    grant_opportunity: bool,
) -> tuple[CRMService, InMemoryAuditLog]:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    assert permission.grant(
        ctx,
        principal_subject_id=ctx.subject_id,
        resource_type=CUSTOMER_RESOURCE,
        actions={"create", "read"},
        scope_level=ScopeLevel.TENANT,
    ).ok
    if grant_opportunity:
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=OPPORTUNITY_RESOURCE,
            actions={"create", "read", "update", "archive"},
            scope_level=ScopeLevel.TENANT,
        ).ok
    return (
        CRMService(
            permission,
            repository=InMemoryCRMRepository(tenant_id=ctx.tenant_id),
            audit_log=audit,
        ),
        audit,
    )


def test_c2_requires_customer_and_system_assigns_opaque_code() -> None:
    ctx = _ctx(uuid4())
    service, _ = _service(ctx, grant_opportunity=True)
    missing = service.create_opportunity(
        ctx,
        customer_id=uuid4(),
        title="Missing customer",
    )
    assert missing.error_code == ErrorCode.COMMON_NOT_FOUND

    customer = service.create_customer(
        ctx,
        code="C2-CUSTOMER",
        display_name="C2 Customer",
    )
    assert customer.ok and customer.data is not None
    created = service.create_opportunity(
        ctx,
        customer_id=customer.data.id,
        title="System coded opportunity",
    )
    assert created.ok and created.data is not None
    assert created.data.code.startswith("OPP-")
    assert len(created.data.code) == 16


def test_c2_owner_never_bypasses_permission() -> None:
    ctx = _ctx(uuid4())
    service, audit = _service(ctx, grant_opportunity=False)
    customer = service.create_customer(
        ctx,
        code="C2-DENIED",
        display_name="Denied Owner Customer",
    )
    assert customer.ok and customer.data is not None
    denied = service.create_opportunity(
        ctx,
        customer_id=customer.data.id,
        title="Owner is not a grant",
        owner_subject_id=ctx.subject_id,
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    crm_events = [
        event for event in audit.list_events() if event.action.startswith("CRM.Opportunity")
    ]
    assert [event.result for event in crm_events] == ["attempted", "denied"]


def test_c2_update_archive_and_audit_minimization() -> None:
    ctx = _ctx(uuid4())
    service, audit = _service(ctx, grant_opportunity=True)
    customer = service.create_customer(
        ctx,
        code="C2-LIFECYCLE",
        display_name="Lifecycle Customer",
    )
    assert customer.data is not None
    opportunity = service.create_opportunity(
        ctx,
        customer_id=customer.data.id,
        title="Confidential pipeline title",
        owner_subject_id=uuid4(),
    )
    assert opportunity.data is not None
    updated = service.update_opportunity(
        ctx,
        opportunity_id=opportunity.data.id,
        title="Updated title",
        owner_subject_id=None,
        expected_version=1,
    )
    assert updated.ok and updated.data is not None and updated.data.version == 2
    archived = service.archive_opportunity(
        ctx,
        opportunity_id=opportunity.data.id,
        reason="pipeline retired",
        expected_version=2,
    )
    assert archived.ok and archived.data is not None
    assert archived.data.status.value == "archived"
    assert "Confidential pipeline title" not in repr(
        [event.details for event in audit.list_events()]
    )
