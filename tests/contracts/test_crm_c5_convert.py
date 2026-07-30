"""PHX-G298 CRM Quote Convert C5 contracts."""

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
        correlation_id=f"corr-g298-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(ctx: ExecutionContext, *, grant_convert: bool):
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
    ]
    if grant_convert:
        resources.append(CONVERSION_RESOURCE)
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
    customer = service.create_customer(ctx, code="C5-C", display_name="C5 Customer").data
    assert customer is not None
    opportunity = service.create_opportunity(
        ctx, customer_id=customer.id, title="C5 Opportunity"
    ).data
    assert opportunity is not None
    requirement = service.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C5 Requirement"
    ).data
    assert requirement is not None
    quote = service.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    return quote


def test_c5_convert_is_idempotent_and_does_not_mutate_quote() -> None:
    ctx = _ctx()
    service, _ = _service(ctx, grant_convert=True)
    quote = _quote(service, ctx)
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
    key = uuid4()
    first = service.convert_quote(ctx, quote_id=quote.id, idempotency_key=key)
    retry = service.convert_quote(ctx, quote_id=quote.id, idempotency_key=key)
    assert first.ok and first.data is not None
    assert retry.ok and retry.data is not None and retry.data.id == first.data.id
    fetched = service.get_quote(ctx, quote_id=quote.id)
    assert fetched.data is not None and fetched.data.status.value == "issued"


def test_c5_different_idempotency_key_conflicts() -> None:
    ctx = _ctx()
    service, _ = _service(ctx, grant_convert=True)
    quote = _quote(service, ctx)
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
    assert service.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    ).ok
    conflict = service.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    )
    assert conflict.error_code == ErrorCode.COMMON_CONFLICT


def test_c5_permission_default_deny_is_audited() -> None:
    ctx = _ctx()
    service, audit = _service(ctx, grant_convert=False)
    quote = _quote(service, ctx)
    denied = service.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event
        for event in audit.list_events()
        if event.action.startswith("CRM.QuoteConversion")
    ]
    assert [event.result for event in events] == ["attempted", "denied"]
