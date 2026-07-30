"""PHX-G303 CRM AR Invoice shell C10 contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
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
from tests.contracts.test_crm_c9_delivery_order import _sales_order


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=uuid4(),
        correlation_id=f"corr-g303-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(ctx: ExecutionContext, *, grant_invoice: bool):
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
        SALES_ORDER_RESOURCE,
        DELIVERY_ORDER_RESOURCE,
    ]
    if grant_invoice:
        resources.append(AR_INVOICE_RESOURCE)
    for resource in resources:
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
                "release",
            },
            scope_level=ScopeLevel.TENANT,
        ).ok
    return CRMService(
        permission,
        repository=InMemoryCRMRepository(tenant_id=ctx.tenant_id),
        audit_log=audit,
    ), audit


def _delivery_order(service: CRMService, ctx: ExecutionContext):
    sales_order = _sales_order(service, ctx, confirmed=True)
    delivery_order = service.create_delivery_order(
        ctx, sales_order_id=sales_order.id, idempotency_key=uuid4()
    ).data
    assert delivery_order is not None
    delivery_order = service.release_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).data
    assert delivery_order is not None
    return sales_order, delivery_order


def test_c10_invoice_shell_is_idempotent_and_traces_so_do_customer() -> None:
    ctx = _ctx()
    service, audit = _service(ctx, grant_invoice=True)
    sales_order, delivery_order = _delivery_order(service, ctx)
    key = uuid4()
    first = service.create_ar_invoice(
        ctx, delivery_order_id=delivery_order.id, idempotency_key=key
    )
    retry = service.create_ar_invoice(
        ctx, delivery_order_id=delivery_order.id, idempotency_key=key
    )
    assert first.ok and first.data is not None
    assert retry.data is not None and retry.data.id == first.data.id
    assert first.data.status.value == "draft"
    assert first.data.delivery_order_id == delivery_order.id
    assert first.data.sales_order_id == sales_order.id
    assert first.data.total_amount == delivery_order.total_amount
    assert first.data.customer_id is not None
    details = " ".join(
        str(event.details)
        for event in audit.list_events()
        if event.action.startswith("CRM.ARInvoice")
    )
    assert "20.00" not in details
    assert str(key) not in details


def test_c10_second_key_conflicts() -> None:
    ctx = _ctx()
    service, _ = _service(ctx, grant_invoice=True)
    _, delivery_order = _delivery_order(service, ctx)
    assert service.create_ar_invoice(
        ctx, delivery_order_id=delivery_order.id, idempotency_key=uuid4()
    ).ok
    conflict = service.create_ar_invoice(
        ctx, delivery_order_id=delivery_order.id, idempotency_key=uuid4()
    )
    assert conflict.error_code == ErrorCode.COMMON_CONFLICT


def test_c10_permission_default_deny_is_audited() -> None:
    ctx = _ctx()
    service, audit = _service(ctx, grant_invoice=False)
    _, delivery_order = _delivery_order(service, ctx)
    denied = service.create_ar_invoice(
        ctx, delivery_order_id=delivery_order.id, idempotency_key=uuid4()
    )
    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event
        for event in audit.list_events()
        if event.action.startswith("CRM.ARInvoice")
    ]
    assert [event.result for event in events] == ["attempted", "denied"]
