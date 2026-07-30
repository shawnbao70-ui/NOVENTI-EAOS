"""PHX-G319 Finance GL1 chart of accounts + journal contracts."""

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
        correlation_id=f"corr-g319-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(ctx: ExecutionContext) -> FinanceService:
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
    ):
        assert permission.grant(
            ctx,
            principal_subject_id=ctx.subject_id,
            resource_type=resource,
            actions=actions,
            scope_level=ScopeLevel.TENANT,
        ).ok
    return FinanceService(
        permission,
        repository=InMemoryFinanceRepository(tenant_id=ctx.tenant_id),
        audit_log=audit,
        ar_invoice_reader=_Invoices(),
    )


def _create_account(
    service: FinanceService,
    ctx: ExecutionContext,
    *,
    code: str,
    account_type: str = "asset",
):
    result = service.create_gl_account(
        ctx,
        code=code,
        name=f"Account {code}",
        account_type=account_type,
    )
    assert result.ok and result.data is not None
    return result.data


def _create_period(service: FinanceService, ctx: ExecutionContext):
    result = service.create_gl_period(
        ctx,
        code="2026-Q1",
        start_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        end_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
    )
    assert result.ok and result.data is not None
    return result.data


def test_gl1_create_accounts_unbalanced_fails_balanced_draft_and_post() -> None:
    ctx = _ctx()
    service = _service(ctx)
    cash = _create_account(service, ctx, code="1000", account_type="asset")
    revenue = _create_account(
        service, ctx, code="4000", account_type="revenue"
    )
    period = _create_period(service, ctx)

    fetched = service.get_gl_account(ctx, account_id=cash.id)
    assert fetched.ok and fetched.data is not None
    assert fetched.data.code == "1000"
    by_code = service.get_gl_account_by_code(ctx, code="4000")
    assert by_code.ok and by_code.data is not None
    assert by_code.data.id == revenue.id

    unbalanced = service.create_journal_entry(
        ctx,
        currency="USD",
        period_id=period.id,
        idempotency_key=uuid4(),
        lines=[
            {
                "account_id": cash.id,
                "debit": Decimal("10.00"),
                "credit": Decimal("0"),
            },
            {
                "account_id": revenue.id,
                "debit": Decimal("0"),
                "credit": Decimal("9.00"),
            },
        ],
    )
    assert unbalanced.error_code == ErrorCode.COMMON_VALIDATION_FAILED
    assert unbalanced.error_message == "journal entry must be balanced"

    draft = service.create_journal_entry(
        ctx,
        currency="USD",
        period_id=period.id,
        memo="sale",
        idempotency_key=uuid4(),
        lines=[
            {
                "account_id": cash.id,
                "debit": Decimal("10.00"),
                "credit": Decimal("0"),
            },
            {
                "account_id": revenue.id,
                "debit": Decimal("0"),
                "credit": Decimal("10.00"),
            },
        ],
    )
    assert draft.ok and draft.data is not None
    assert draft.data.status.value == "draft"
    assert len(draft.data.lines) == 2

    post_key = uuid4()
    posted = service.post_journal_entry(
        ctx,
        entry_id=draft.data.id,
        idempotency_key=post_key,
        human_confirm=True,
    )
    assert posted.ok and posted.data is not None
    assert posted.data.status.value == "posted"
    assert posted.data.posted_at is not None

    again = service.post_journal_entry(
        ctx,
        entry_id=draft.data.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert again.error_code == ErrorCode.COMMON_CONFLICT
    assert again.error_message == "journal entry is already posted"
    current = service.get_journal_entry(ctx, entry_id=draft.data.id)
    assert current.ok and current.data is not None
    assert current.data.status.value == "posted"


def test_gl1_archived_account_blocks_post() -> None:
    ctx = _ctx()
    service = _service(ctx)
    cash = _create_account(service, ctx, code="1100")
    expense = _create_account(
        service, ctx, code="5000", account_type="expense"
    )
    period = _create_period(service, ctx)
    draft = service.create_journal_entry(
        ctx,
        currency="USD",
        period_id=period.id,
        idempotency_key=uuid4(),
        lines=[
            {
                "account_id": expense.id,
                "debit": Decimal("5.00"),
                "credit": Decimal("0"),
            },
            {
                "account_id": cash.id,
                "debit": Decimal("0"),
                "credit": Decimal("5.00"),
            },
        ],
    )
    assert draft.ok and draft.data is not None

    archived = service.archive_gl_account(
        ctx, account_id=cash.id, expected_version=cash.version
    )
    assert archived.ok and archived.data is not None
    assert archived.data.status.value == "archived"

    blocked = service.post_journal_entry(
        ctx,
        entry_id=draft.data.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert blocked.error_code == ErrorCode.COMMON_CONFLICT
    assert blocked.error_message == "gl account is not active"
    still_draft = service.get_journal_entry(ctx, entry_id=draft.data.id)
    assert still_draft.ok and still_draft.data is not None
    assert still_draft.data.status.value == "draft"
