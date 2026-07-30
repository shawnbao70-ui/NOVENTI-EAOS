"""PHX-G305 CRM confirm approval hook C12 contracts."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from noventi.crm.approval import (
    AllowConfirmApprovalGate,
    DenyConfirmApprovalGate,
    UnavailableConfirmApprovalGate,
)
from noventi.crm.repository import InMemoryCRMRepository
from noventi.crm.service import (
    CONVERSION_RESOURCE,
    CUSTOMER_RESOURCE,
    DELIVERY_ORDER_RESOURCE,
    OPPORTUNITY_RESOURCE,
    POLICY_RESOURCE,
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
        correlation_id=f"corr-g305-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(
    ctx: ExecutionContext,
    *,
    gate=None,
    grant_policy_update: bool = True,
):
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
    ):
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=resource,
            actions={
                "create",
                "read",
                "update",
                "archive",
                "convert",
                "issue",
                "confirm",
            },
            scope_level=ScopeLevel.TENANT,
        ).ok
    policy_actions = {"read"}
    if grant_policy_update:
        policy_actions.add("update")
    assert permission.grant(
        ctx,
        principal_subject_id=ctx.subject_id,
        resource_type=POLICY_RESOURCE,
        actions=policy_actions,
        scope_level=ScopeLevel.TENANT,
    ).ok
    return CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=ctx.tenant_id),
        audit_log=audit,
        confirm_approval_gate=gate,
    ), audit


def _sales_order(service: CRMService, ctx: ExecutionContext):
    customer = service.create_customer(
        ctx, code=f"C12-{uuid4().hex[:8]}", display_name="C12 Customer"
    ).data
    assert customer is not None
    opportunity = service.create_opportunity(
        ctx, customer_id=customer.id, title="C12 Opportunity"
    ).data
    assert opportunity is not None
    requirement = service.create_requirement(
        ctx, opportunity_id=opportunity.id, title="C12 Requirement"
    ).data
    assert requirement is not None
    quote = service.create_quote(ctx, requirement_id=requirement.id).data
    assert quote is not None
    assert service.create_quote_line(
        ctx,
        quote_id=quote.id,
        description="C12 line",
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
    return sales_order


def test_c12_default_policy_false_allows_confirm() -> None:
    ctx = _ctx()
    service, _ = _service(ctx, gate=None)
    sales_order = _sales_order(service, ctx)
    policy = service.get_confirm_approval_policy(ctx).data
    assert policy is not None
    assert policy.confirm_approval_required is False
    assert policy.version == 0
    confirmed = service.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert confirmed.ok and confirmed.data is not None


def test_c12_required_with_unavailable_gate_fails_closed() -> None:
    ctx = _ctx()
    service, audit = _service(ctx, gate=UnavailableConfirmApprovalGate())
    sales_order = _sales_order(service, ctx)
    assert service.set_confirm_approval_policy(
        ctx, confirm_approval_required=True, expected_version=0
    ).ok
    result = service.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert result.error_code == ErrorCode.COMMON_CONFLICT
    assert result.error_message == "confirm approval gate is unavailable"
    blocked = [
        event
        for event in audit.list_events()
        if event.action == "CRM.SalesOrder.Confirm" and event.result == "blocked"
    ]
    assert len(blocked) == 1


def test_c12_required_with_deny_gate_fails_closed() -> None:
    ctx = _ctx()
    service, _ = _service(ctx, gate=DenyConfirmApprovalGate())
    sales_order = _sales_order(service, ctx)
    assert service.set_confirm_approval_policy(
        ctx, confirm_approval_required=True, expected_version=0
    ).ok
    result = service.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert result.error_code == ErrorCode.COMMON_CONFLICT
    assert result.error_message == "confirm approval is required"


def test_c12_required_with_allow_gate_confirms() -> None:
    ctx = _ctx()
    service, _ = _service(ctx, gate=AllowConfirmApprovalGate())
    sales_order = _sales_order(service, ctx)
    assert service.set_confirm_approval_policy(
        ctx, confirm_approval_required=True, expected_version=0
    ).ok
    confirmed = service.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert confirmed.ok and confirmed.data is not None
    assert confirmed.data.status.value == "confirmed"


def test_c12_required_without_gate_binding_fails_closed() -> None:
    ctx = _ctx()
    service, _ = _service(ctx, gate=None)
    sales_order = _sales_order(service, ctx)
    assert service.set_confirm_approval_policy(
        ctx, confirm_approval_required=True, expected_version=0
    ).ok
    result = service.confirm_sales_order(
        ctx,
        sales_order_id=sales_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert result.error_message == "confirm approval gate is unavailable"


def test_c12_policy_mutation_default_deny_is_audited() -> None:
    ctx = _ctx()
    service, audit = _service(ctx, grant_policy_update=False)
    denied = service.set_confirm_approval_policy(
        ctx, confirm_approval_required=True, expected_version=0
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event
        for event in audit.list_events()
        if event.action.startswith("CRM.Policy.ConfirmApproval.Set")
    ]
    assert [event.result for event in events] == ["attempted", "denied"]
