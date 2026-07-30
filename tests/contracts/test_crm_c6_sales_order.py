"""PHX-G299 CRM Sales Order trace C6 contracts."""

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
        correlation_id=f"corr-g299-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(ctx: ExecutionContext, *, grant_so: bool):
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
        QUOTE_LINE_RESOURCE,
        CONVERSION_RESOURCE,
    ]
    if grant_so:
        resources.append(SALES_ORDER_RESOURCE)
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


def _conversion(service: CRMService, ctx: ExecutionContext):
    customer = service.create_customer(ctx, code="C6-C", display_name="C6 Customer").data
    assert customer is not None
    opportunity = service.create_opportunity(
        ctx, customer_id=customer.id, title="C6 Opportunity"
    ).data
    assert opportunity is not None
    requirement = service.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C6 Requirement"
    ).data
    assert requirement is not None
    quote = service.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert service.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="C13 commercial line",
        quantity=Decimal("1"),
        unit_price=Decimal("10.00"),
    ).ok
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
    return quote, conversion


def test_c6_create_is_idempotent_and_consumes_conversion() -> None:
    ctx = _ctx()
    service, _ = _service(ctx, grant_so=True)
    _, conversion = _conversion(service, ctx)
    key = uuid4()
    first = service.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=key
    )
    retry = service.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=key
    )
    assert first.ok and first.data is not None
    assert retry.ok and retry.data is not None and retry.data.id == first.data.id
    consumed = service.get_conversion(ctx, conversion_id=conversion.id)
    assert consumed.data is not None and consumed.data.status.value == "consumed"


def test_c6_rejects_stale_quote_snapshot() -> None:
    ctx = _ctx()
    service, _ = _service(ctx, grant_so=True)
    quote, conversion = _conversion(service, ctx)
    # C13 freezes issued quotes; commercial header mutation is blocked (replaces
    # the former draft-mutate-after-convert stale-snapshot path).
    issued = service.get_quote(ctx, quote_id=quote.id).data
    assert issued is not None and issued.status.value == "issued"
    blocked = service.update_quote(
        ctx,
        quote_id=issued.id,
        currency="EUR",
        notes=None,
        expected_version=issued.version,
    )
    assert blocked.error_code == ErrorCode.COMMON_CONFLICT
    assert blocked.error_message == "quote is issued"
    result = service.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=uuid4()
    )
    assert result.ok and result.data is not None


def test_c6_permission_default_deny_is_audited() -> None:
    ctx = _ctx()
    service, audit = _service(ctx, grant_so=False)
    _, conversion = _conversion(service, ctx)
    denied = service.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=uuid4()
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event for event in audit.list_events()
        if event.action.startswith("CRM.SalesOrder")
    ]
    assert [event.result for event in events] == ["attempted", "denied"]
