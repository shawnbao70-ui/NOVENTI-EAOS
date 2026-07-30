"""PHX-G325 CRM Return Authorization RET1 package contracts."""

from __future__ import annotations

from dataclasses import replace
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
    RETURN_AUTHORIZATION_RESOURCE,
    SALES_ORDER_RESOURCE,
    CRMService,
)
from noventi.inventory.repository import InMemoryInventoryRepository
from noventi.inventory.service import (
    DELIVERY_SHIP_RESOURCE,
    STOCK_RESOURCE,
    InventoryService,
)
from tests.contracts.test_inventory_i1_do_ship import (
    _CRMShipReader,
    _released_delivery_order,
)


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=uuid4(),
        correlation_id=f"corr-g325-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _services(ctx: ExecutionContext, *, grant_return: bool = True):
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
        STOCK_RESOURCE,
        DELIVERY_SHIP_RESOURCE,
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
                "release",
                "void",
                "adjust",
                "ship",
            },
            scope_level=ScopeLevel.TENANT,
        ).ok
    if grant_return:
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=RETURN_AUTHORIZATION_RESOURCE,
            actions={"create", "read"},
            scope_level=ScopeLevel.TENANT,
        ).ok
    crm_repo = InMemoryCRMRepository(tenant_id=ctx.tenant_id)

    def _mark_shipped(
        delivery_order_id: UUID,
        expected_version: int,
        _shipped_at,
    ) -> None:
        delivery_order = crm_repo.get_delivery_order(delivery_order_id)
        if delivery_order is None or delivery_order.version != expected_version:
            raise ValueError("delivery order ship status conflict")
        crm_repo.save_delivery_order(
            replace(
                delivery_order,
                status=DeliveryOrderStatus.SHIPPED,
                version=delivery_order.version + 1,
            ),
            expected_version=expected_version,
        )

    crm = CRMService(permission, repository=crm_repo, audit_log=audit)
    inventory = InventoryService(
        permission,
        repository=InMemoryInventoryRepository(
            tenant_id=ctx.tenant_id,
            mark_delivery_order_shipped=_mark_shipped,
        ),
        audit_log=audit,
        delivery_order_reader=_CRMShipReader(crm_repo),
    )
    return crm, inventory, audit, crm_repo


def _shipped_delivery_order(crm: CRMService, inventory: InventoryService, ctx):
    delivery_order, lines, customer = _released_delivery_order(crm, ctx)
    for line in lines:
        assert inventory.adjust_stock(
            ctx,
            sales_order_line_id=line.id,
            quantity_delta=line.quantity,
            idempotency_key=uuid4(),
        ).ok
    shipped = inventory.ship_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert shipped.ok and shipped.data is not None
    do = crm.get_delivery_order(
        ctx, delivery_order_id=delivery_order.id
    ).data
    assert do is not None
    assert do.status == DeliveryOrderStatus.SHIPPED
    return do, customer


def test_ret1_default_deny_create() -> None:
    ctx = _ctx()
    crm, inventory, audit, _ = _services(ctx, grant_return=False)
    delivery_order, _ = _shipped_delivery_order(crm, inventory, ctx)

    denied = crm.create_return_authorization(
        ctx,
        delivery_order_id=delivery_order.id,
        reason="damaged",
        idempotency_key=uuid4(),
        human_confirm=True,
    )

    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    events = [
        event
        for event in audit.list_events()
        if event.action.startswith("CRM.ReturnAuthorization.")
    ]
    assert [event.result for event in events] == ["attempted", "denied"]


def test_ret1_create_get_idempotent_draft_shell() -> None:
    ctx = _ctx()
    crm, inventory, audit, _ = _services(ctx)
    delivery_order, _ = _shipped_delivery_order(crm, inventory, ctx)
    key = uuid4()

    created = crm.create_return_authorization(
        ctx,
        delivery_order_id=delivery_order.id,
        reason="wrong item",
        idempotency_key=key,
        human_confirm=True,
    )
    assert created.ok and created.data is not None
    assert created.data.status.value == "draft"
    assert created.data.delivery_order_id == delivery_order.id
    assert created.data.invoice_id is None
    assert created.data.reason == "wrong item"

    replay = crm.create_return_authorization(
        ctx,
        delivery_order_id=delivery_order.id,
        reason="wrong item",
        idempotency_key=key,
        human_confirm=True,
    )
    assert replay.ok and replay.data is not None
    assert replay.data.id == created.data.id

    got = crm.get_return_authorization(
        ctx, return_authorization_id=created.data.id
    )
    assert got.ok and got.data is not None
    assert got.data.code == created.data.code

    conflict = crm.create_return_authorization(
        ctx,
        delivery_order_id=delivery_order.id,
        reason="other",
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert conflict.error_code == ErrorCode.COMMON_CONFLICT

    actions = [
        event.action
        for event in audit.list_events()
        if event.action.startswith("CRM.ReturnAuthorization.")
        and not event.action.endswith(".Intent")
    ]
    assert "CRM.ReturnAuthorization.Create" in actions


def test_ret1_requires_shipped_do_and_human_confirm() -> None:
    ctx = _ctx()
    crm, inventory, _, _ = _services(ctx)
    delivery_order, lines, _ = _released_delivery_order(crm, ctx)

    not_shipped = crm.create_return_authorization(
        ctx,
        delivery_order_id=delivery_order.id,
        reason="early return",
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert not_shipped.error_code == ErrorCode.COMMON_CONFLICT
    assert not_shipped.error_message == "delivery order must be shipped"

    for line in lines:
        assert inventory.adjust_stock(
            ctx,
            sales_order_line_id=line.id,
            quantity_delta=line.quantity,
            idempotency_key=uuid4(),
        ).ok
    assert inventory.ship_delivery_order(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    ).ok

    missing_confirm = crm.create_return_authorization(
        ctx,
        delivery_order_id=delivery_order.id,
        reason="needs confirm",
        idempotency_key=uuid4(),
        human_confirm=False,
    )
    assert missing_confirm.error_code == ErrorCode.COMMON_VALIDATION_FAILED
    assert (
        missing_confirm.error_message == "human confirmation is required"
    )


def test_ret1_optional_invoice_lineage_and_status() -> None:
    ctx = _ctx()
    crm, inventory, _, _ = _services(ctx)
    delivery_order, _ = _shipped_delivery_order(crm, inventory, ctx)

    draft = crm.create_ar_invoice(
        ctx,
        delivery_order_id=delivery_order.id,
        idempotency_key=uuid4(),
    )
    assert draft.ok and draft.data is not None
    blocked_draft = crm.create_return_authorization(
        ctx,
        delivery_order_id=delivery_order.id,
        reason="with draft invoice",
        idempotency_key=uuid4(),
        human_confirm=True,
        invoice_id=draft.data.id,
    )
    assert blocked_draft.error_code == ErrorCode.COMMON_CONFLICT
    assert blocked_draft.error_message == "AR invoice must be issued or voided"

    issued = crm.issue_ar_invoice(
        ctx,
        invoice_id=draft.data.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert issued.ok and issued.data is not None
    created = crm.create_return_authorization(
        ctx,
        delivery_order_id=delivery_order.id,
        reason="with issued invoice",
        idempotency_key=uuid4(),
        human_confirm=True,
        invoice_id=issued.data.id,
    )
    assert created.ok and created.data is not None
    assert created.data.invoice_id == issued.data.id


def test_ret1_commercial_hold_does_not_block_create() -> None:
    ctx = _ctx()
    crm, inventory, _, _ = _services(ctx)
    delivery_order, customer = _shipped_delivery_order(crm, inventory, ctx)
    assert crm.set_customer_commercial_hold(
        ctx,
        customer_id=customer.id,
        commercial_hold=True,
        expected_version=customer.version,
    ).ok

    created = crm.create_return_authorization(
        ctx,
        delivery_order_id=delivery_order.id,
        reason="hold must not block",
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert created.ok and created.data is not None
    assert created.data.status.value == "draft"


def test_ret1_cross_tenant_not_visible() -> None:
    subject = uuid4()
    tenant_a = uuid4()
    tenant_b = uuid4()
    ctx_a = ExecutionContext(
        subject_id=subject,
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant_a,
        correlation_id="corr-a",
        request_time=ExecutionContext.utc_now(),
    )
    crm_a, inventory_a, _, _ = _services(ctx_a)
    delivery_order, _ = _shipped_delivery_order(crm_a, inventory_a, ctx_a)
    created = crm_a.create_return_authorization(
        ctx_a,
        delivery_order_id=delivery_order.id,
        reason="tenant a",
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert created.ok and created.data is not None

    ctx_b = ExecutionContext(
        subject_id=subject,
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant_b,
        correlation_id="corr-b",
        request_time=ExecutionContext.utc_now(),
    )
    crm_b, _, _, _ = _services(ctx_b)
    hidden = crm_b.get_return_authorization(
        ctx_b, return_authorization_id=created.data.id
    )
    assert hidden.error_code == ErrorCode.COMMON_NOT_FOUND
