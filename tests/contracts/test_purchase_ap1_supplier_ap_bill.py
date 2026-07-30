"""PHX-G324 Purchase Supplier + AP Bill draft AP1 package contracts."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from noventi.purchase.repository import InMemoryPurchaseRepository
from noventi.purchase.service import (
    AP_BILL_RESOURCE,
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
            resource_type=AP_BILL_RESOURCE,
            actions={"create", "read"},
            scope_level=ScopeLevel.TENANT,
        ).ok
    repository = InMemoryPurchaseRepository(tenant_id=ctx.tenant_id)
    return (
        PurchaseService(permission, repository=repository, audit_log=audit),
        repository,
        audit,
    )


def test_ap1_default_deny_supplier_create() -> None:
    ctx = _ctx(uuid4())
    service, repository, audit = _service(ctx, grant=False)

    denied = service.create_supplier(
        ctx,
        code="S-001",
        display_name="Denied Supplier",
    )

    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    assert repository.get_supplier(uuid4()) is None
    purchase_events = [
        event
        for event in audit.list_events()
        if event.action.startswith("Purchase.")
    ]
    assert [event.result for event in purchase_events] == [
        "attempted",
        "denied",
    ]


def test_ap1_supplier_and_ap_bill_draft_lifecycle() -> None:
    ctx = _ctx(uuid4())
    service, _, audit = _service(ctx, grant=True)

    supplier = service.create_supplier(
        ctx,
        code="SUP-100",
        display_name="Acme Parts",
    )
    assert supplier.ok and supplier.data is not None
    assert supplier.data.status.value == "active"

    updated = service.update_supplier(
        ctx,
        supplier_id=supplier.data.id,
        display_name="Acme Parts Ltd",
        expected_version=1,
    )
    assert updated.ok and updated.data is not None
    assert updated.data.display_name == "Acme Parts Ltd"
    assert updated.data.version == 2

    key = uuid4()
    bill = service.create_ap_bill(
        ctx,
        supplier_id=supplier.data.id,
        code="APB-001",
        currency="usd",
        total_amount=Decimal("100.00"),
        idempotency_key=key,
    )
    assert bill.ok and bill.data is not None
    assert bill.data.status.value == "draft"
    assert bill.data.currency == "USD"
    assert bill.data.total_amount == Decimal("100.00")

    replay = service.create_ap_bill(
        ctx,
        supplier_id=supplier.data.id,
        code="APB-001",
        currency="USD",
        total_amount=Decimal("100.00"),
        idempotency_key=key,
    )
    assert replay.ok and replay.data is not None
    assert replay.data.id == bill.data.id

    got = service.get_ap_bill(ctx, bill_id=bill.data.id)
    assert got.ok and got.data is not None
    assert got.data.code == "APB-001"

    archived = service.archive_supplier(
        ctx,
        supplier_id=supplier.data.id,
        reason="retired",
        expected_version=2,
    )
    assert archived.ok and archived.data is not None
    assert archived.data.status.value == "archived"

    blocked = service.create_ap_bill(
        ctx,
        supplier_id=supplier.data.id,
        code="APB-002",
        currency="USD",
        total_amount=Decimal("10.00"),
        idempotency_key=uuid4(),
    )
    assert blocked.error_code == ErrorCode.COMMON_CONFLICT

    actions = [
        event.action
        for event in audit.list_events()
        if event.action.startswith("Purchase.") and not event.action.endswith(".Intent")
    ]
    assert "Purchase.Supplier.Create" in actions
    assert "Purchase.ApBill.Create" in actions
    assert "Purchase.Supplier.Archive" in actions


def test_ap1_cross_tenant_resource_is_not_visible() -> None:
    subject = uuid4()
    tenant_a = uuid4()
    tenant_b = uuid4()
    service_a, _, _ = _service(_ctx(tenant_a, subject), grant=True)
    ctx_a = _ctx(tenant_a, subject)
    created = service_a.create_supplier(
        ctx_a,
        code="A-1",
        display_name="Tenant A Supplier",
    )
    assert created.ok and created.data is not None

    ctx_b = _ctx(tenant_b, subject)
    service_b, _, _ = _service(ctx_b, grant=True)
    hidden = service_b.get_supplier(ctx_b, supplier_id=created.data.id)
    assert hidden.error_code == ErrorCode.COMMON_NOT_FOUND


def test_ap1_missing_supplier_rejects_ap_bill() -> None:
    ctx = _ctx(uuid4())
    service, _, _ = _service(ctx, grant=True)
    missing = service.create_ap_bill(
        ctx,
        supplier_id=uuid4(),
        code="APB-X",
        currency="USD",
        total_amount=Decimal("1.00"),
        idempotency_key=uuid4(),
    )
    assert missing.error_code == ErrorCode.COMMON_NOT_FOUND
