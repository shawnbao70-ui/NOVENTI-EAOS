"""PHX-G308 CRM AR Invoice Issue C15 contracts."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from uuid import UUID, uuid4

from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from noventi.crm.models import DeliveryOrderStatus
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import (
    AR_INVOICE_RESOURCE,
    CONVERSION_RESOURCE,
    CUSTOMER_RESOURCE,
    DELIVERY_ORDER_RESOURCE,
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
        correlation_id=f"corr-g308-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(ctx: ExecutionContext, *, grant_issue: bool = True):
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_Eligibility(),
    )
    for resource in (
        CUSTOMER_RESOURCE,
        OPPORTUNITY_RESOURCE,
        REQUIREMENT_RESOURCE,
        QUOTE_RESOURCE,
        QUOTE_LINE_RESOURCE,
        CONVERSION_RESOURCE,
        SALES_ORDER_RESOURCE,
        DELIVERY_ORDER_RESOURCE,
        AR_INVOICE_RESOURCE,
    ):
        actions = {
            "create",
            "read",
            "update",
            "archive",
            "convert",
            "issue",
            "confirm",
            "release",
        }
        if not grant_issue and resource == AR_INVOICE_RESOURCE:
            actions.discard("issue")
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


def _draft_invoice(service: CRMService, ctx: ExecutionContext, *, release_do: bool = True):
    customer = service.create_customer(
        ctx, code=f"C15-{uuid4().hex[:8]}", display_name="C15 Customer"
    ).data
    assert customer is not None
    opportunity = service.create_opportunity(
        ctx, customer_id=customer.id, title="C15 Opportunity"
    ).data
    assert opportunity is not None
    requirement = service.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C15 Requirement"
    ).data
    assert requirement is not None
    quote = service.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert service.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="C15 line",
        quantity=Decimal("2"),
        unit_price=Decimal("10"),
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
    sales_order = service.create_sales_order(
        ctx, conversion_id=conversion.id, idempotency_key=uuid4()
    ).data
    assert sales_order is not None
    sales_order = service.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).data
    assert sales_order is not None
    delivery_order = service.create_delivery_order(
        ctx, sales_order_id=sales_order.id, idempotency_key=uuid4()
    ).data
    assert delivery_order is not None
    if release_do:
        delivery_order = service.release_delivery_order(
            ctx,
            delivery_order_id=delivery_order.id,
            idempotency_key=uuid4(),
            human_confirm=True,
        ).data
        assert delivery_order is not None
    invoice = service.create_ar_invoice(
        ctx, delivery_order_id=delivery_order.id, idempotency_key=uuid4()
    )
    if not release_do:
        return customer, delivery_order, invoice
    assert invoice.ok and invoice.data is not None
    assert invoice.data.status.value == "draft"
    return customer, delivery_order, invoice.data


def test_c15_issue_default_deny_is_audited() -> None:
    ctx = _ctx()
    service, audit = _service(ctx, grant_issue=False)
    _, _, invoice = _draft_invoice(service, ctx)
    denied = service.issue_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event
        for event in audit.list_events()
        if event.action.startswith("CRM.ARInvoice.Issue")
    ]
    assert [event.result for event in events] == ["attempted", "denied"]


def test_c15_issue_requires_human_confirm() -> None:
    ctx = _ctx()
    service, _ = _service(ctx)
    _, _, invoice = _draft_invoice(service, ctx)
    missing = service.issue_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
        human_confirm=False,
    )
    assert missing.error_code == ErrorCode.COMMON_VALIDATION_FAILED


def test_c15_issue_blocks_if_do_not_released() -> None:
    ctx = _ctx()
    service, _ = _service(ctx)
    # create_ar_invoice already requires released DO; force DO draft after create
    # to prove issue_ar_invoice re-checks the release gate.
    _, delivery_order, invoice = _draft_invoice(service, ctx, release_do=True)
    draft_do = replace(
        delivery_order,
        status=DeliveryOrderStatus.DRAFT,
        released_at=None,
        release_key=None,
        version=delivery_order.version + 1,
    )
    service._repository.save_delivery_order(
        draft_do, expected_version=delivery_order.version
    )
    blocked = service.issue_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert blocked.error_code == ErrorCode.COMMON_CONFLICT
    assert blocked.error_message == "delivery order must be released"


def test_c15_issue_blocks_when_commercially_held() -> None:
    ctx = _ctx()
    service, _ = _service(ctx)
    customer, _, invoice = _draft_invoice(service, ctx)
    assert service.set_customer_commercial_hold(
        ctx, customer_id=customer.id, commercial_hold=True, expected_version=1
    ).ok
    blocked = service.issue_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert blocked.error_code == ErrorCode.COMMON_CONFLICT
    assert blocked.error_message == "customer is on commercial hold"


def test_c15_issue_is_idempotent_and_wrong_key_conflicts() -> None:
    ctx = _ctx()
    service, _ = _service(ctx)
    _, _, invoice = _draft_invoice(service, ctx)
    key = uuid4()
    first = service.issue_ar_invoice(
        ctx, invoice_id=invoice.id, idempotency_key=key, human_confirm=True
    )
    retry = service.issue_ar_invoice(
        ctx, invoice_id=invoice.id, idempotency_key=key, human_confirm=True
    )
    assert first.ok and first.data is not None
    assert first.data.status.value == "issued"
    assert first.data.issued_at is not None
    assert retry.data is not None and retry.data.id == first.data.id
    conflict = service.issue_ar_invoice(
        ctx, invoice_id=invoice.id, idempotency_key=uuid4(), human_confirm=True
    )
    assert conflict.error_code == ErrorCode.COMMON_CONFLICT


def test_c15_draft_create_still_works_and_issue_transitions() -> None:
    ctx = _ctx()
    service, _ = _service(ctx)
    _, _, invoice = _draft_invoice(service, ctx)
    assert invoice.status.value == "draft"
    issued = service.issue_ar_invoice(
        ctx,
        invoice_id=invoice.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).data
    assert issued is not None and issued.status.value == "issued"
    fetched = service.get_ar_invoice(ctx, invoice_id=invoice.id).data
    assert fetched is not None and fetched.status.value == "issued"
