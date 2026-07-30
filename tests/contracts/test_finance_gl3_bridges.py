"""PHX-G321 Finance GL3 bridge contracts."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from kernel.permission.models import ScopeLevel
from kernel.permission.service import PermissionService
from kernel.shared.audit import InMemoryAuditLog
from kernel.shared.context import ExecutionContext, SubjectType
from kernel.shared.errors import ErrorCode
from noventi.crm.repository import InMemoryCRMRepository  # noqa: F401
from noventi.finance.repository import InMemoryFinanceRepository
from noventi.finance.service import (
    GL_ACCOUNT_RESOURCE,
    GL_BRIDGE_RESOURCE,
    GL_PERIOD_RESOURCE,
    JOURNAL_ENTRY_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
)
from noventi.finance.models import (
    ARReceipt,
    CommissionEntry,
    CommissionStatus,
    ReceiptStatus,
    TaxInvoice,
    TaxInvoiceStatus,
)


class _Invoices:
    def __init__(self) -> None:
        self._items: dict[UUID, ARInvoiceSnapshot] = {}

    def put(self, snap: ARInvoiceSnapshot) -> None:
        self._items[snap.id] = snap

    def get_ar_invoice_snapshot(
        self, invoice_id: UUID
    ) -> ARInvoiceSnapshot | None:
        return self._items.get(invoice_id)


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=uuid4(),
        correlation_id=f"corr-g321-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(
    ctx: ExecutionContext, invoices: _Invoices | None = None
) -> tuple[FinanceService, InMemoryFinanceRepository, _Invoices]:
    assert ctx.tenant_id is not None
    audit = InMemoryAuditLog()
    permission = PermissionService(
        audit_log=audit,
        grant_administrators={ctx.subject_id},
        principal_eligibility=_Eligibility(),
    )
    for resource, actions in (
        (GL_ACCOUNT_RESOURCE, {"create", "read", "archive"}),
        (GL_PERIOD_RESOURCE, {"create", "read", "close"}),
        (JOURNAL_ENTRY_RESOURCE, {"create", "read", "post"}),
        (GL_BRIDGE_RESOURCE, {"read", "update", "bridge"}),
    ):
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=resource,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok
    reader = invoices or _Invoices()
    repo = InMemoryFinanceRepository(tenant_id=ctx.tenant_id)
    return (
        FinanceService(
            permission,
            repository=repo,
            audit_log=audit,
            ar_invoice_reader=reader,
        ),
        repo,
        reader,
    )


def _account(service: FinanceService, ctx: ExecutionContext, code: str, typ: str):
    result = service.create_gl_account(
        ctx, code=code, name=code, account_type=typ
    )
    assert result.ok and result.data is not None
    return result.data


def _period(service: FinanceService, ctx: ExecutionContext):
    result = service.create_gl_period(
        ctx,
        code="2026-Q1",
        name="2026 Q1",
        start_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        end_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
    )
    assert result.ok and result.data is not None
    return result.data


def _set_map(service: FinanceService, ctx: ExecutionContext, accounts: dict):
    result = service.set_gl_bridge_map(
        ctx,
        ar_control=accounts["ar"].id,
        cash=accounts["cash"].id,
        revenue=accounts["rev"].id,
        tax_payable=accounts["tax"].id,
        commission_expense=accounts["cexp"].id,
        commission_payable=accounts["cpay"].id,
        expected_version=0,
    )
    assert result.ok and result.data is not None
    return result.data


def _accounts(service: FinanceService, ctx: ExecutionContext) -> dict:
    return {
        "ar": _account(service, ctx, "1100", "asset"),
        "cash": _account(service, ctx, "1000", "asset"),
        "rev": _account(service, ctx, "4000", "revenue"),
        "tax": _account(service, ctx, "2100", "liability"),
        "cexp": _account(service, ctx, "5100", "expense"),
        "cpay": _account(service, ctx, "2200", "liability"),
    }


def test_gl3_bridge_map_and_ar_invoice_idempotent() -> None:
    ctx = _ctx()
    service, repo, invoices = _service(ctx)
    accounts = _accounts(service, ctx)
    period = _period(service, ctx)
    bridge_map = _set_map(service, ctx, accounts)
    assert bridge_map.version == 1
    got = service.get_gl_bridge_map(ctx)
    assert got.ok and got.data is not None
    assert got.data.ar_control == accounts["ar"].id

    invoice_id = uuid4()
    invoices.put(
        ARInvoiceSnapshot(
            id=invoice_id,
            tenant_id=ctx.tenant_id,  # type: ignore[arg-type]
            customer_id=uuid4(),
            currency="USD",
            total_amount=Decimal("100.00"),
            status="issued",
            version=1,
        )
    )
    key = uuid4()
    first = service.bridge_ar_invoice_issue(
        ctx,
        invoice_id=invoice_id,
        period_id=period.id,
        idempotency_key=key,
        human_confirm=True,
    )
    assert first.ok and first.data is not None
    journal = service.get_journal_entry(
        ctx, entry_id=first.data.journal_entry_id
    )
    assert journal.ok and journal.data is not None
    assert journal.data.status.value == "posted"
    assert journal.data.period_id == period.id
    assert sum(line.debit for line in journal.data.lines) == Decimal("100.00")

    again = service.bridge_ar_invoice_issue(
        ctx,
        invoice_id=invoice_id,
        period_id=period.id,
        idempotency_key=key,
        human_confirm=True,
    )
    assert again.ok and again.data is not None
    assert again.data.id == first.data.id
    assert again.data.journal_entry_id == first.data.journal_entry_id

    conflict = service.bridge_ar_invoice_issue(
        ctx,
        invoice_id=invoice_id,
        period_id=period.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert not conflict.ok
    assert conflict.error_code == ErrorCode.COMMON_CONFLICT
    assert conflict.error_message == "source already bridged with a different key"
    assert repo.get_gl_bridge_posting_by_source(
        first.data.source_type, invoice_id
    ) is not None


def test_gl3_fail_closed_incomplete_map_closed_period_missing_source() -> None:
    ctx = _ctx()
    service, _repo, invoices = _service(ctx)
    accounts = _accounts(service, ctx)
    period = _period(service, ctx)

    missing_map = service.bridge_ar_invoice_issue(
        ctx,
        invoice_id=uuid4(),
        period_id=period.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert not missing_map.ok
    assert missing_map.error_message == "gl bridge map is incomplete"

    _set_map(service, ctx, accounts)
    missing_source = service.bridge_ar_invoice_issue(
        ctx,
        invoice_id=uuid4(),
        period_id=period.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert not missing_source.ok
    assert missing_source.error_code == ErrorCode.COMMON_NOT_FOUND

    invoice_id = uuid4()
    invoices.put(
        ARInvoiceSnapshot(
            id=invoice_id,
            tenant_id=ctx.tenant_id,  # type: ignore[arg-type]
            customer_id=uuid4(),
            currency="USD",
            total_amount=Decimal("10.00"),
            status="issued",
            version=1,
        )
    )
    closed = service.close_gl_period(
        ctx,
        period_id=period.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert closed.ok
    blocked = service.bridge_ar_invoice_issue(
        ctx,
        invoice_id=invoice_id,
        period_id=period.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert not blocked.ok
    assert blocked.error_message == "gl period is not open"


def test_gl3_receipt_tax_commission_bridges() -> None:
    ctx = _ctx()
    assert ctx.tenant_id is not None
    service, repo, invoices = _service(ctx)
    accounts = _accounts(service, ctx)
    period = _period(service, ctx)
    _set_map(service, ctx, accounts)

    invoice_id = uuid4()
    invoices.put(
        ARInvoiceSnapshot(
            id=invoice_id,
            tenant_id=ctx.tenant_id,
            customer_id=uuid4(),
            currency="USD",
            total_amount=Decimal("50.00"),
            status="issued",
            version=2,
        )
    )
    receipt = ARReceipt(
        id=uuid4(),
        tenant_id=ctx.tenant_id,
        customer_id=uuid4(),
        code="RCPT-1",
        currency="USD",
        amount=Decimal("50.00"),
        idempotency_key=uuid4(),
        status=ReceiptStatus.APPLIED,
        created_at=datetime.now(timezone.utc),
        ar_invoice_id=invoice_id,
        ar_invoice_version=2,
        apply_key=uuid4(),
        applied_at=datetime.now(timezone.utc),
    )
    repo.add_receipt(receipt)
    tax = TaxInvoice(
        id=uuid4(),
        tenant_id=ctx.tenant_id,
        customer_id=uuid4(),
        ar_invoice_id=invoice_id,
        ar_invoice_version=2,
        code="TAX-1",
        currency="USD",
        amount=Decimal("5.00"),
        idempotency_key=uuid4(),
        status=TaxInvoiceStatus.ISSUED,
        created_at=datetime.now(timezone.utc),
        issued_at=datetime.now(timezone.utc),
        issue_key=uuid4(),
    )
    repo.add_tax_invoice(tax)
    commission = CommissionEntry(
        id=uuid4(),
        tenant_id=ctx.tenant_id,
        source_invoice_id=invoice_id,
        beneficiary_subject_id=uuid4(),
        code="COM-1",
        currency="USD",
        amount=Decimal("7.00"),
        idempotency_key=uuid4(),
        status=CommissionStatus.ACCRUED,
        created_at=datetime.now(timezone.utc),
    )
    repo.add_commission(commission)

    r = service.bridge_ar_receipt_apply(
        ctx,
        receipt_id=receipt.id,
        period_id=period.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert r.ok and r.data is not None
    t = service.bridge_tax_invoice_issue(
        ctx,
        tax_invoice_id=tax.id,
        period_id=period.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert t.ok and t.data is not None
    c = service.bridge_commission_accrue(
        ctx,
        commission_id=commission.id,
        period_id=period.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert c.ok and c.data is not None
