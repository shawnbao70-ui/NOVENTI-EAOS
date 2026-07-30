"""PHX-G320 Finance GL2 period + close contracts."""

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
        correlation_id=f"corr-g320-{uuid4()}",
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


def _create_period(
    service: FinanceService,
    ctx: ExecutionContext,
    *,
    code: str = "2026-Q1",
):
    result = service.create_gl_period(
        ctx,
        code=code,
        name=code,
        start_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        end_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
    )
    assert result.ok and result.data is not None
    return result.data


def test_gl2_create_close_post_open_ok_closed_fails_reopen_unavailable() -> None:
    ctx = _ctx()
    service = _service(ctx)
    cash = _create_account(service, ctx, code="1000", account_type="asset")
    revenue = _create_account(
        service, ctx, code="4000", account_type="revenue"
    )
    period = _create_period(service, ctx)

    fetched = service.get_gl_period(ctx, period_id=period.id)
    assert fetched.ok and fetched.data is not None
    assert fetched.data.status.value == "open"
    by_code = service.get_gl_period_by_code(ctx, code="2026-Q1")
    assert by_code.ok and by_code.data is not None
    assert by_code.data.id == period.id

    draft_open = service.create_journal_entry(
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
                "credit": Decimal("10.00"),
            },
        ],
    )
    assert draft_open.ok and draft_open.data is not None
    assert draft_open.data.period_id == period.id

    posted = service.post_journal_entry(
        ctx,
        entry_id=draft_open.data.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert posted.ok and posted.data is not None
    assert posted.data.status.value == "posted"

    draft_later = service.create_journal_entry(
        ctx,
        currency="USD",
        period_id=period.id,
        idempotency_key=uuid4(),
        lines=[
            {
                "account_id": cash.id,
                "debit": Decimal("5.00"),
                "credit": Decimal("0"),
            },
            {
                "account_id": revenue.id,
                "debit": Decimal("0"),
                "credit": Decimal("5.00"),
            },
        ],
    )
    assert draft_later.ok and draft_later.data is not None

    close_key = uuid4()
    closed = service.close_gl_period(
        ctx,
        period_id=period.id,
        idempotency_key=close_key,
        human_confirm=True,
    )
    assert closed.ok and closed.data is not None
    assert closed.data.status.value == "closed"
    assert closed.data.closed_at is not None

    again = service.close_gl_period(
        ctx,
        period_id=period.id,
        idempotency_key=close_key,
        human_confirm=True,
    )
    assert again.ok and again.data is not None
    assert again.data.status.value == "closed"

    blocked_create = service.create_journal_entry(
        ctx,
        currency="USD",
        period_id=period.id,
        idempotency_key=uuid4(),
        lines=[
            {
                "account_id": cash.id,
                "debit": Decimal("1.00"),
                "credit": Decimal("0"),
            },
            {
                "account_id": revenue.id,
                "debit": Decimal("0"),
                "credit": Decimal("1.00"),
            },
        ],
    )
    assert blocked_create.error_code == ErrorCode.COMMON_CONFLICT
    assert blocked_create.error_message == "gl period is not open"

    blocked_post = service.post_journal_entry(
        ctx,
        entry_id=draft_later.data.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert blocked_post.error_code == ErrorCode.COMMON_CONFLICT
    assert blocked_post.error_message == "gl period is closed"

    assert not hasattr(service, "reopen_gl_period")
