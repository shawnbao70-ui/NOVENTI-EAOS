"""PHX-G306 CRM Quote Issue C13 contracts."""

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
        correlation_id=f"corr-g306-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(ctx: ExecutionContext, *, grant_issue: bool = True):
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_Eligibility(),
    )
    quote_actions = {
        "create",
        "read",
        "update",
        "archive",
        "convert",
    }
    if grant_issue:
        quote_actions.add("issue")
    for resource, actions in (
        (
            CUSTOMER_RESOURCE,
            {"create", "read", "update", "archive"},
        ),
        (
            OPPORTUNITY_RESOURCE,
            {"create", "read", "update", "archive"},
        ),
        (
            REQUIREMENT_RESOURCE,
            {"create", "read", "update", "archive"},
        ),
        (QUOTE_RESOURCE, quote_actions),
        (
            QUOTE_LINE_RESOURCE,
            {"create", "read", "update", "archive"},
        ),
        (
            CONVERSION_RESOURCE,
            {"create", "read", "convert"},
        ),
    ):
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=resource,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok
    return CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=ctx.tenant_id),
        audit_log=audit,
    ), audit


def _quote_with_line(service: CRMService, ctx: ExecutionContext):
    customer = service.create_customer(
        ctx, code=f"C13-{uuid4().hex[:8]}", display_name="C13 Customer"
    ).data
    assert customer is not None
    opportunity = service.create_opportunity(
        ctx, customer_id=customer.id, title="C13 Opportunity"
    ).data
    assert opportunity is not None
    requirement = service.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C13 Requirement"
    ).data
    assert requirement is not None
    quote = service.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert service.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="C13 line",
        quantity=Decimal("2"),
        unit_price=Decimal("10"),
    ).ok
    return service.get_quote(ctx, quote_id=quote.id).data


def test_c13_issue_default_deny_is_audited() -> None:
    ctx = _ctx()
    service, audit = _service(ctx, grant_issue=False)
    quote = _quote_with_line(service, ctx)
    assert quote is not None
    denied = service.issue_quote(
        ctx,
        quote_id=quote.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event
        for event in audit.list_events()
        if event.action.startswith("CRM.Quote.Issue")
    ]
    assert [event.result for event in events] == ["attempted", "denied"]


def test_c13_issue_requires_human_confirm_and_active_line() -> None:
    ctx = _ctx()
    service, _ = _service(ctx)
    quote = _quote_with_line(service, ctx)
    assert quote is not None
    missing_confirm = service.issue_quote(
        ctx,
        quote_id=quote.id,
        idempotency_key=uuid4(),
        human_confirm=False,
    )
    assert missing_confirm.error_code == ErrorCode.COMMON_VALIDATION_FAILED
    empty = service.create_quote(
        ctx,
        requirement_id=quote.requirement_id,
    ).data
    assert empty is not None
    no_lines = service.issue_quote(
        ctx,
        quote_id=empty.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert no_lines.error_code == ErrorCode.COMMON_VALIDATION_FAILED


def test_c13_issue_is_idempotent_and_wrong_key_conflicts() -> None:
    ctx = _ctx()
    service, _ = _service(ctx)
    quote = _quote_with_line(service, ctx)
    assert quote is not None
    key = uuid4()
    first = service.issue_quote(
        ctx, quote_id=quote.id, idempotency_key=key, human_confirm=True
    )
    retry = service.issue_quote(
        ctx, quote_id=quote.id, idempotency_key=key, human_confirm=True
    )
    assert first.ok and first.data is not None
    assert first.data.status.value == "issued"
    assert retry.data is not None and retry.data.id == first.data.id
    conflict = service.issue_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4(), human_confirm=True
    )
    assert conflict.error_code == ErrorCode.COMMON_CONFLICT


def test_c13_convert_requires_issued() -> None:
    ctx = _ctx()
    service, _ = _service(ctx)
    quote = _quote_with_line(service, ctx)
    assert quote is not None
    draft_convert = service.convert_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4()
    )
    assert draft_convert.error_code == ErrorCode.COMMON_CONFLICT
    assert draft_convert.error_message == "quote must be issued"
    issued = service.issue_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4(), human_confirm=True
    ).data
    assert issued is not None
    converted = service.convert_quote(
        ctx, quote_id=issued.id, idempotency_key=uuid4()
    )
    assert converted.ok and converted.data is not None


def test_c13_line_and_header_update_blocked_after_issue() -> None:
    ctx = _ctx()
    service, _ = _service(ctx)
    quote = _quote_with_line(service, ctx)
    assert quote is not None
    line = service.list_quote_lines(ctx, quote_id=quote.id).data
    assert line is not None and line
    issued = service.issue_quote(
        ctx, quote_id=quote.id, idempotency_key=uuid4(), human_confirm=True
    ).data
    assert issued is not None
    header = service.update_quote(
        ctx,
        quote_id=issued.id,
        currency="USD",
        notes="blocked",
        expected_version=issued.version,
    )
    assert header.error_code == ErrorCode.COMMON_CONFLICT
    assert header.error_message == "quote is issued"
    line_update = service.update_quote_line(
        ctx,
        quote_id=issued.id,
        quote_line_id=line[0].id,
        description="blocked",
        quantity=Decimal("1"),
        unit_price=Decimal("1"),
        expected_version=line[0].version,
    )
    assert line_update.error_message == "quote is issued"
    line_create = service.create_quote_line(
        ctx,
        quote_id=issued.id,
        description="blocked",
        quantity=Decimal("1"),
        unit_price=Decimal("1"),
    )
    assert line_create.error_message == "quote is issued"
