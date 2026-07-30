"""PHX-G329 Purchase AP Bill Line AP2 package contracts."""

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
    AP_BILL_LINE_RESOURCE,
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
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=AP_BILL_LINE_RESOURCE,
            actions={"create", "read", "archive"},
            scope_level=ScopeLevel.TENANT,
        ).ok
    repository = InMemoryPurchaseRepository(tenant_id=ctx.tenant_id)
    return (
        PurchaseService(permission, repository=repository, audit_log=audit),
        repository,
        audit,
    )


def _draft_bill(service: PurchaseService, ctx: ExecutionContext):
    supplier = service.create_supplier(
        ctx, code="SUP-AP2", display_name="Line Supplier"
    )
    assert supplier.ok and supplier.data is not None
    bill = service.create_ap_bill(
        ctx,
        supplier_id=supplier.data.id,
        code="APB-AP2",
        currency="USD",
        total_amount=Decimal("0.00"),
        idempotency_key=uuid4(),
    )
    assert bill.ok and bill.data is not None
    return bill.data


def test_ap2_default_deny_line_create() -> None:
    ctx = _ctx(uuid4())
    service, _, audit = _service(ctx, grant=False)

    denied = service.create_ap_bill_line(
        ctx,
        ap_bill_id=uuid4(),
        description="Widget",
        quantity=Decimal("1"),
        unit_price=Decimal("10.00"),
    )

    assert denied.error_code == ErrorCode.PERMISSION_DENIED
    purchase_events = [
        event
        for event in audit.list_events()
        if event.action.startswith("Purchase.ApBillLine.")
    ]
    assert [event.result for event in purchase_events] == [
        "attempted",
        "denied",
    ]


def test_ap2_line_create_recomputes_bill_total_and_archive() -> None:
    ctx = _ctx(uuid4())
    service, _, audit = _service(ctx, grant=True)
    bill = _draft_bill(service, ctx)

    line = service.create_ap_bill_line(
        ctx,
        ap_bill_id=bill.id,
        description="Bolt pack",
        quantity=Decimal("2.5"),
        unit_price=Decimal("4.00"),
    )
    assert line.ok and line.data is not None
    assert line.data.amount == Decimal("10.00")
    assert line.data.line_number == 1
    assert line.data.status.value == "active"

    refreshed = service.get_ap_bill(ctx, bill_id=bill.id)
    assert refreshed.ok and refreshed.data is not None
    assert refreshed.data.total_amount == Decimal("10.00")
    assert refreshed.data.version == 2

    second = service.create_ap_bill_line(
        ctx,
        ap_bill_id=bill.id,
        description="Nut pack",
        quantity=Decimal("1"),
        unit_price=Decimal("3.50"),
    )
    assert second.ok and second.data is not None
    assert second.data.line_number == 2

    refreshed = service.get_ap_bill(ctx, bill_id=bill.id)
    assert refreshed.ok and refreshed.data is not None
    assert refreshed.data.total_amount == Decimal("13.50")
    assert refreshed.data.version == 3

    listed = service.list_ap_bill_lines(ctx, ap_bill_id=bill.id)
    assert listed.ok and listed.data is not None
    assert len(listed.data) == 2

    got = service.get_ap_bill_line(
        ctx, ap_bill_id=bill.id, line_id=line.data.id
    )
    assert got.ok and got.data is not None
    assert got.data.description == "Bolt pack"

    archived = service.archive_ap_bill_line(
        ctx,
        ap_bill_id=bill.id,
        line_id=line.data.id,
        reason="wrong qty",
        expected_version=1,
    )
    assert archived.ok and archived.data is not None
    assert archived.data.status.value == "archived"

    refreshed = service.get_ap_bill(ctx, bill_id=bill.id)
    assert refreshed.ok and refreshed.data is not None
    assert refreshed.data.total_amount == Decimal("3.50")

    actions = [
        event.action
        for event in audit.list_events()
        if event.action.startswith("Purchase.ApBillLine.")
        and not event.action.endswith(".Intent")
    ]
    assert "Purchase.ApBillLine.Create" in actions
    assert "Purchase.ApBillLine.Archive" in actions


def test_ap2_missing_bill_rejects_line() -> None:
    ctx = _ctx(uuid4())
    service, _, _ = _service(ctx, grant=True)
    missing = service.create_ap_bill_line(
        ctx,
        ap_bill_id=uuid4(),
        description="Missing parent",
        quantity=Decimal("1"),
        unit_price=Decimal("1.00"),
    )
    assert missing.error_code == ErrorCode.COMMON_NOT_FOUND
