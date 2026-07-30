"""PHX-G323 Finance GL5 bank reconciliation contracts."""

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
from noventi.finance.models import ARReceipt, ReceiptStatus
from noventi.finance.repository import InMemoryFinanceRepository
from noventi.finance.service import (
    BANK_STATEMENT_RESOURCE,
    GL_ACCOUNT_RESOURCE,
    GL_PERIOD_RESOURCE,
    JOURNAL_ENTRY_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
)


class _Invoices:
    def get_ar_invoice_snapshot(
        self, invoice_id: UUID
    ) -> ARInvoiceSnapshot | None:
        return None


class _Eligibility:
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool:
        return True


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        subject_id=uuid4(),
        subject_type=SubjectType.HUMAN,
        tenant_id=uuid4(),
        correlation_id=f"corr-g323-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(
    ctx: ExecutionContext,
) -> tuple[FinanceService, InMemoryFinanceRepository]:
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
        (BANK_STATEMENT_RESOURCE, {"create", "read", "match", "clear"}),
    ):
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=resource,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok
    repo = InMemoryFinanceRepository(tenant_id=ctx.tenant_id)
    return (
        FinanceService(
            permission,
            repository=repo,
            audit_log=audit,
            ar_invoice_reader=_Invoices(),
        ),
        repo,
    )


def test_gl5_create_match_clear_statement() -> None:
    ctx = _ctx()
    assert ctx.tenant_id is not None
    service, repo = _service(ctx)
    receipt = ARReceipt(
        id=uuid4(),
        tenant_id=ctx.tenant_id,
        customer_id=uuid4(),
        code="RCPT-BR",
        currency="USD",
        amount=Decimal("25.00"),
        idempotency_key=uuid4(),
        status=ReceiptStatus.APPLIED,
        created_at=datetime.now(timezone.utc),
        ar_invoice_id=uuid4(),
        ar_invoice_version=1,
        apply_key=uuid4(),
        applied_at=datetime.now(timezone.utc),
    )
    repo.add_receipt(receipt)

    created = service.create_bank_statement(
        ctx,
        account_ref="BANK-USD-001",
        statement_date=datetime(2026, 3, 1, tzinfo=timezone.utc),
        currency="USD",
        lines=[
            {"amount": Decimal("25.00"), "description": "incoming"},
            {"amount": Decimal("-5.00"), "description": "fee"},
        ],
    )
    assert created.ok and created.data is not None
    assert created.data.status.value == "open"
    assert len(created.data.lines) == 2
    line_a, line_b = created.data.lines

    blocked_clear = service.clear_bank_statement(
        ctx, statement_id=created.data.id, human_confirm=True
    )
    assert not blocked_clear.ok
    assert blocked_clear.error_message == "bank statement has unmatched lines"

    matched_a = service.match_bank_statement_line(
        ctx,
        statement_id=created.data.id,
        line_id=line_a.id,
        matched_receipt_id=receipt.id,
    )
    assert matched_a.ok and matched_a.data is not None
    assert matched_a.data.lines[0].status.value == "matched"

    # Second line matches via journal line after creating a journal.
    cash = service.create_gl_account(
        ctx, code="1000", name="Cash", account_type="asset"
    )
    assert cash.ok and cash.data is not None
    expense = service.create_gl_account(
        ctx, code="6000", name="Bank Fee", account_type="expense"
    )
    assert expense.ok and expense.data is not None
    period = service.create_gl_period(
        ctx,
        code="2026-Q1",
        name="2026 Q1",
        start_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        end_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
    )
    assert period.ok and period.data is not None
    journal = service.create_journal_entry(
        ctx,
        currency="USD",
        period_id=period.data.id,
        idempotency_key=uuid4(),
        lines=[
            {
                "account_id": expense.data.id,
                "debit": Decimal("5.00"),
                "credit": Decimal("0"),
            },
            {
                "account_id": cash.data.id,
                "debit": Decimal("0"),
                "credit": Decimal("5.00"),
            },
        ],
    )
    assert journal.ok and journal.data is not None
    fee_line_id = next(
        line.id for line in journal.data.lines if line.credit == Decimal("5.00")
    )
    matched_b = service.match_bank_statement_line(
        ctx,
        statement_id=created.data.id,
        line_id=line_b.id,
        matched_journal_line_id=fee_line_id,
    )
    assert matched_b.ok and matched_b.data is not None

    cleared = service.clear_bank_statement(
        ctx, statement_id=created.data.id, human_confirm=True
    )
    assert cleared.ok and cleared.data is not None
    assert cleared.data.status.value == "reconciled"
    assert all(line.status.value == "cleared" for line in cleared.data.lines)

    got = service.get_bank_statement(ctx, statement_id=created.data.id)
    assert got.ok and got.data is not None
    assert got.data.status.value == "reconciled"


def test_gl5_match_requires_exactly_one_target() -> None:
    ctx = _ctx()
    service, _repo = _service(ctx)
    created = service.create_bank_statement(
        ctx,
        account_ref="CASH",
        statement_date=datetime(2026, 3, 1, tzinfo=timezone.utc),
        currency="USD",
        lines=[{"amount": Decimal("1.00"), "description": "one"}],
    )
    assert created.ok and created.data is not None
    line_id = created.data.lines[0].id
    both = service.match_bank_statement_line(
        ctx,
        statement_id=created.data.id,
        line_id=line_id,
        matched_journal_line_id=uuid4(),
        matched_receipt_id=uuid4(),
    )
    assert not both.ok
    assert both.error_code == ErrorCode.COMMON_VALIDATION_FAILED
    neither = service.match_bank_statement_line(
        ctx,
        statement_id=created.data.id,
        line_id=line_id,
    )
    assert not neither.ok
    assert neither.error_message == "exactly one match target is required"
