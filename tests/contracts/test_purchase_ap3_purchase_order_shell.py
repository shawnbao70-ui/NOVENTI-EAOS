"""PHX-G332 Purchase Order shell AP3 package contracts."""

from __future__ import annotations

from uuid import UUID, uuid4

from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from noventi.purchase.repository import InMemoryPurchaseRepository
from noventi.purchase.service import (
    PURCHASE_ORDER_RESOURCE,
    SUPPLIER_RESOURCE,
    PurchaseService,
)


class _AllowPrincipalEligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx(tenant_id: UUID, subject_id: UUID | None = None) -> ExecutionContext:
    return ExecutionContext(
        subject_id=subject_id or uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=tenant_id,
        correlation_id=f"corr-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(
    ctx: ExecutionContext,
    *,
    grant: bool,
) -> tuple[PurchaseService, InMemoryPurchaseRepository, InMemoryAuditLog]:
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_AllowPrincipalEligibility(),
    )
    if grant:
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=SUPPLIER_RESOURCE,
            actions={"create", "read", "update", "archive"},
            scope_level=ScopeLevel.TENANT,
        ).ok
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=PURCHASE_ORDER_RESOURCE,
            actions={"create", "read", "archive"},
            scope_level=ScopeLevel.TENANT,
        ).ok
    repository = InMemoryPurchaseRepository(tenant_id=ctx.tenant_id)
    return (
        PurchaseService(permission, repository=repository, audit_log=audit),
        repository,
        audit,
    )


def test_ap3_default_deny_purchase_order_create() -> None:
    ctx = _ctx(uuid4())
    service, repository, audit = _service(ctx, grant=False)

    denied = service.create_purchase_order(
        ctx,
        supplier_id=uuid4(),
        code="PO-001",
        currency="USD",
        idempotency_key=uuid4(),
    )

    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    assert repository.get_purchase_order(uuid4()) is None
    purchase_events = [
        event
        for event in audit.list_events()
        if event.action.startswith("Purchase.PurchaseOrder.")
    ]
    assert [event.result for event in purchase_events] == [
        "attempted",
        "denied",
    ]


def test_ap3_purchase_order_shell_lifecycle() -> None:
    ctx = _ctx(uuid4())
    service, _, audit = _service(ctx, grant=True)

    supplier = service.create_supplier(
        ctx, code="SUP-PO", display_name="PO Supplier"
    )
    assert supplier.ok and supplier.data is not None

    key = uuid4()
    created = service.create_purchase_order(
        ctx,
        supplier_id=supplier.data.id,
        code="PO-100",
        currency="usd",
        idempotency_key=key,
        notes="  rush  ",
    )
    assert created.ok and created.data is not None
    assert created.data.status.value == "draft"
    assert created.data.currency == "USD"
    assert created.data.notes == "rush"

    replay = service.create_purchase_order(
        ctx,
        supplier_id=supplier.data.id,
        code="PO-100",
        currency="USD",
        idempotency_key=key,
        notes="rush",
    )
    assert replay.ok and replay.data is not None
    assert replay.data.id == created.data.id

    conflict = service.create_purchase_order(
        ctx,
        supplier_id=supplier.data.id,
        code="PO-OTHER",
        currency="USD",
        idempotency_key=key,
    )
    assert conflict.error_code == ErrorCode.COMMON_CONFLICT

    got = service.get_purchase_order(
        ctx, purchase_order_id=created.data.id
    )
    assert got.ok and got.data is not None
    assert got.data.code == "PO-100"

    archived = service.archive_purchase_order(
        ctx,
        purchase_order_id=created.data.id,
        reason="cancelled",
        expected_version=1,
    )
    assert archived.ok and archived.data is not None
    assert archived.data.status.value == "archived"

    actions = [
        event.action
        for event in audit.list_events()
        if event.action.startswith("Purchase.")
        and not event.action.endswith(".Intent")
    ]
    assert "Purchase.PurchaseOrder.Create" in actions
    assert "Purchase.PurchaseOrder.Archive" in actions


def test_ap3_archived_supplier_rejects_purchase_order() -> None:
    ctx = _ctx(uuid4())
    service, _, _ = _service(ctx, grant=True)
    supplier = service.create_supplier(
        ctx, code="SUP-ARCH", display_name="Archived"
    )
    assert supplier.ok and supplier.data is not None
    archived = service.archive_supplier(
        ctx,
        supplier_id=supplier.data.id,
        reason="gone",
        expected_version=1,
    )
    assert archived.ok

    blocked = service.create_purchase_order(
        ctx,
        supplier_id=supplier.data.id,
        code="PO-X",
        currency="USD",
        idempotency_key=uuid4(),
    )
    assert blocked.error_code == ErrorCode.COMMON_CONFLICT


def test_ap3_cross_tenant_purchase_order_not_visible() -> None:
    subject = uuid4()
    tenant_a = uuid4()
    tenant_b = uuid4()
    service_a, _, _ = _service(_ctx(tenant_a, subject), grant=True)
    ctx_a = _ctx(tenant_a, subject)
    supplier = service_a.create_supplier(
        ctx_a, code="A-1", display_name="A"
    )
    assert supplier.ok and supplier.data is not None
    order = service_a.create_purchase_order(
        ctx_a,
        supplier_id=supplier.data.id,
        code="PO-A",
        currency="USD",
        idempotency_key=uuid4(),
    )
    assert order.ok and order.data is not None

    ctx_b = _ctx(tenant_b, subject)
    service_b, _, _ = _service(ctx_b, grant=True)
    hidden = service_b.get_purchase_order(
        ctx_b, purchase_order_id=order.data.id
    )
    assert hidden.error_code == ErrorCode.COMMON_NOT_FOUND
