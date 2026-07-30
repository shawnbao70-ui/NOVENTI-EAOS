"""PHX-G296 CRM Requirement C3 package contracts."""

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
    REQUIREMENT_RESOURCE,
    CRMService,
)


class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=uuid4(),
        correlation_id=f"corr-g296-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(
    ctx: ExecutionContext, *, grant_requirement: bool
) -> tuple[CRMService, InMemoryAuditLog]:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    resources = [CUSTOMER_RESOURCE, OPPORTUNITY_RESOURCE]
    if grant_requirement:
        resources.append(REQUIREMENT_RESOURCE)
    for resource_type in resources:
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=resource_type,
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


def _opportunity(service: CRMService, ctx: ExecutionContext):
    customer = service.create_customer(
        ctx, code="C3-CUSTOMER", display_name="C3 Customer"
    )
    assert customer.data is not None
    opportunity = service.create_opportunity(
        ctx, customer_id=customer.data.id, title="C3 Opportunity"
    )
    assert opportunity.data is not None
    return opportunity.data


def test_c3_requires_active_opportunity_and_assigns_code() -> None:
    ctx = _ctx()
    service, _ = _service(ctx, grant_requirement=True)
    missing = service.create_requirement(
        ctx, opportunity_id=uuid4(), title="Missing"
    )
    assert missing.error_code == ErrorCode.COMMON_NOT_FOUND
    opportunity = _opportunity(service, ctx)
    created = service.create_requirement(
        ctx, opportunity_id=opportunity.id, title="Required product"
    )
    assert created.ok and created.data is not None
    assert created.data.code.startswith("REQ-")
    assert len(created.data.code) == 16


def test_c3_permission_is_default_deny() -> None:
    ctx = _ctx()
    service, audit = _service(ctx, grant_requirement=False)
    opportunity = _opportunity(service, ctx)
    denied = service.create_requirement(
        ctx,
        opportunity_id=opportunity.id,
        title="Permission denied requirement",
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event for event in audit.list_events()
        if event.action.startswith("CRM.Requirement")
    ]
    assert [event.result for event in events] == ["attempted", "denied"]


def test_c3_update_archive_and_audit_minimization() -> None:
    ctx = _ctx()
    service, audit = _service(ctx, grant_requirement=True)
    opportunity = _opportunity(service, ctx)
    created = service.create_requirement(
        ctx,
        opportunity_id=opportunity.id,
        title="Confidential requirement",
        description="Secret application parameters",
    )
    assert created.data is not None
    updated = service.update_requirement(
        ctx,
        requirement_id=created.data.id,
        title="Updated requirement",
        description=None,
        expected_version=1,
    )
    assert updated.ok and updated.data is not None and updated.data.version == 2
    archived = service.archive_requirement(
        ctx,
        requirement_id=created.data.id,
        reason="No longer needed",
        expected_version=2,
    )
    assert archived.ok and archived.data is not None
    assert archived.data.status.value == "archived"
    audit_text = repr([event.details for event in audit.list_events()])
    assert "Confidential requirement" not in audit_text
    assert "Secret application parameters" not in audit_text
