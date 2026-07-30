"""PHX-G300 CRM Quote Line C7 contracts."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import (
    CONVERSION_RESOURCE,
    CUSTOMER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    QUOTE_LINE_RESOURCE,
    QUOTE_RESOURCE,
    REQUIREMENT_RESOURCE,
    SALES_ORDER_RESOURCE,
    CRMService,
)


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=uuid4(),
        correlation_id=f"corr-g300-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(ctx: ExecutionContext, *, grant_lines: bool):
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_Eligibility(),
    )
    resources = [
        CUSTOMER_RESOURCE,
        OPPORTUNITY_RESOURCE,
        REQUIREMENT_RESOURCE,
        QUOTE_RESOURCE,
        CONVERSION_RESOURCE,
        SALES_ORDER_RESOURCE,
    ]
    if grant_lines:
        resources.append(QUOTE_LINE_RESOURCE)
    for resource in resources:
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=resource,
            actions={"create", "read", "update", "archive", "convert", "issue"},
            scope_level=ScopeLevel.TENANT,
        ).ok
    return CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=ctx.tenant_id),
        audit_log=audit,
    ), audit


def _quote(service: CRMService, ctx: ExecutionContext):
    customer = service.create_customer(
        ctx, code="C7-C", display_name="C7 Customer"
    ).data
    assert customer is not None
    opportunity = service.create_opportunity(
        ctx, customer_id=customer.id, title="C7 Opportunity"
    ).data
    assert opportunity is not None
    requirement = service.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C7 Requirement"
    ).data
    assert requirement is not None
    quote = service.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    return quote


def test_c7_line_amount_lifecycle_and_quote_version() -> None:
    ctx = _ctx()
    service, _ = _service(ctx, grant_lines=True)
    quote = _quote(service, ctx)
    created = service.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="Manual commercial line",
        quantity=Decimal("2.500"),
        unit_price=Decimal("12.34"),
    )
    assert created.ok and created.data is not None
    assert created.data.amount == Decimal("30.85")
    touched = service.get_quote(ctx, quote_id=quote.id)
    assert touched.data is not None and touched.data.version == 2
    updated = service.update_quote_line(
        ctx,
        quote_id=quote.id,
        quote_line_id=created.data.id,
        description="Revised line",
        quantity=Decimal("3"),
        unit_price=Decimal("10.00"),
        expected_version=1,
    )
    assert updated.data is not None and updated.data.amount == Decimal("30.00")
    archived = service.archive_quote_line(
        ctx,
        quote_id=quote.id,
        quote_line_id=created.data.id,
        reason="Removed from draft",
        expected_version=2,
    )
    assert archived.ok and archived.data is not None
    assert archived.data.status.value == "archived"


def test_c7_line_change_invalidates_conversion_snapshot() -> None:
    ctx = _ctx()
    service, _ = _service(ctx, grant_lines=True)
    quote = _quote(service, ctx)
    line = service.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="Initial line",
        quantity=Decimal("1"),
        unit_price=Decimal("5"),
    ).data
    assert line is not None
    assert service.issue_quote(
        ctx,
        quote_id=quote.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok
    conversion = service.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    ).data
    assert conversion is not None
    blocked = service.update_quote_line(
        ctx,
        quote_id=quote.id,
        quote_line_id=line.id,
        description="Changed after issue",
        quantity=Decimal("2"),
        unit_price=Decimal("5"),
        expected_version=1,
    )
    assert blocked.error_code == ErrorCode.COMMON_CONFLICT
    created = service.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=uuid4()
    )
    assert created.ok and created.data is not None


def test_c7_permission_default_deny_and_audit_minimization() -> None:
    ctx = _ctx()
    service, audit = _service(ctx, grant_lines=False)
    quote = _quote(service, ctx)
    denied = service.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="Confidential price description",
        quantity=Decimal("1"),
        unit_price=Decimal("99.99"),
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event for event in audit.list_events()
        if event.action.startswith("CRM.QuoteLine")
    ]
    assert [event.result for event in events] == ["attempted", "denied"]
    assert "Confidential price description" not in repr(
        [event.details for event in audit.list_events()]
    )
