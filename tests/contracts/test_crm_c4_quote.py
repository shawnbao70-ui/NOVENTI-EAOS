"""PHX-G297 CRM Quote C4 package contracts."""

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
    QUOTE_RESOURCE,
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
        correlation_id=f"corr-g297-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(ctx: ExecutionContext, *, grant_quote: bool):
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    resources = [CUSTOMER_RESOURCE, OPPORTUNITY_RESOURCE, REQUIREMENT_RESOURCE]
    if grant_quote:
        resources.append(QUOTE_RESOURCE)
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


def _requirement(service: CRMService, ctx: ExecutionContext):
    customer = service.create_customer(
        ctx, code="C4-CUSTOMER", display_name="C4 Customer"
    )
    assert customer.data is not None
    opportunity = service.create_opportunity(
        ctx, customer_id=customer.data.id, title="C4 Opportunity"
    )
    assert opportunity.data is not None
    requirement = service.create_requirement(
        ctx, opportunity_id=opportunity.data.id, title="C4 Requirement"
    )
    assert requirement.data is not None
    return requirement.data


def test_c4_requires_active_requirement_and_assigns_code() -> None:
    ctx = _ctx()
    service, _ = _service(ctx, grant_quote=True)
    missing = service.create_quote(ctx, requirement_id=uuid4())
    assert missing.error_code == ErrorCode.COMMON_NOT_FOUND
    requirement = _requirement(service, ctx)
    created = service.create_quote(ctx, requirement_id=requirement.id)
    assert created.ok and created.data is not None
    assert created.data.code.startswith("QTE-")
    assert created.data.currency == "USD"
    assert created.data.status.value == "draft"


def test_c4_permission_is_default_deny() -> None:
    ctx = _ctx()
    service, audit = _service(ctx, grant_quote=False)
    requirement = _requirement(service, ctx)
    denied = service.create_quote(ctx, requirement_id=requirement.id)
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event for event in audit.list_events() if event.action.startswith("CRM.Quote")
    ]
    assert [event.result for event in events] == ["attempted", "denied"]


def test_c4_update_archive_and_audit_minimization() -> None:
    ctx = _ctx()
    service, audit = _service(ctx, grant_quote=True)
    requirement = _requirement(service, ctx)
    created = service.create_quote(
        ctx,
        requirement_id=requirement.id,
        currency="eur",
        notes="Confidential commercial draft notes",
    )
    assert created.data is not None and created.data.currency == "EUR"
    updated = service.update_quote(
        ctx,
        quote_id=created.data.id,
        currency="USD",
        notes=None,
        expected_version=1,
    )
    assert updated.ok and updated.data is not None and updated.data.version == 2
    archived = service.archive_quote(
        ctx,
        quote_id=created.data.id,
        reason="Draft withdrawn",
        expected_version=2,
    )
    assert archived.ok and archived.data is not None
    assert archived.data.status.value == "archived"
    assert "Confidential commercial draft notes" not in repr(
        [event.details for event in audit.list_events()]
    )
