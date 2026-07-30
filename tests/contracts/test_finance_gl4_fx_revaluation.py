"""PHX-G322 Finance GL4 FX revaluation contracts."""

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
    GL_FX_REVALUATION_RESOURCE,
    GL_PERIOD_RESOURCE,
    JOURNAL_ENTRY_RESOURCE,
    ARInvoiceSnapshot,
    FinanceService,
    InMemoryFakeFxRate,
    RejectAllFxRate,
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
        correlation_id=f"corr-g322-{uuid4()}",
        request_time=ExecutionContext.utc_now(),
    )


def _service(ctx: ExecutionContext, *, fx_port=None) -> FinanceService:
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
        (GL_FX_REVALUATION_RESOURCE, {"create", "read", "post"}),
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
        fx_rate_port=fx_port or InMemoryFakeFxRate(),
    )


def _setup(service: FinanceService, ctx: ExecutionContext):
    accounts = {}
    for code, typ, key in (
        ("1100", "asset", "ar"),
        ("1000", "asset", "cash"),
        ("4000", "revenue", "rev"),
        ("2100", "liability", "tax"),
        ("5100", "expense", "cexp"),
        ("2200", "liability", "cpay"),
        ("7100", "revenue", "fxg"),
        ("7200", "expense", "fxl"),
    ):
        result = service.create_gl_account(
            ctx, code=code, name=code, account_type=typ
        )
        assert result.ok and result.data is not None
        accounts[key] = result.data
    period = service.create_gl_period(
        ctx,
        code="2026-Q1",
        name="2026 Q1",
        start_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        end_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
    )
    assert period.ok and period.data is not None
    mapped = service.set_gl_bridge_map(
        ctx,
        ar_control=accounts["ar"].id,
        cash=accounts["cash"].id,
        revenue=accounts["rev"].id,
        tax_payable=accounts["tax"].id,
        commission_expense=accounts["cexp"].id,
        commission_payable=accounts["cpay"].id,
        expected_version=0,
        fx_gain=accounts["fxg"].id,
        fx_loss=accounts["fxl"].id,
    )
    assert mapped.ok
    return period.data


def test_gl4_create_post_idempotent_and_port_rate() -> None:
    ctx = _ctx()
    service = _service(ctx)
    period = _setup(service, ctx)

    created = service.create_fx_revaluation(
        ctx,
        period_id=period.id,
        from_currency="USD",
        to_currency="EUR",
        amount=Decimal("12.50"),
        side="gain",
        idempotency_key=uuid4(),
    )
    assert created.ok and created.data is not None
    assert created.data.status.value == "draft"
    assert created.data.rate == Decimal("0.92000000")

    key = uuid4()
    posted = service.post_fx_revaluation(
        ctx,
        revaluation_id=created.data.id,
        idempotency_key=key,
        human_confirm=True,
    )
    assert posted.ok and posted.data is not None
    assert posted.data.status.value == "posted"
    assert posted.data.journal_entry_id is not None
    journal = service.get_journal_entry(
        ctx, entry_id=posted.data.journal_entry_id
    )
    assert journal.ok and journal.data is not None
    assert journal.data.status.value == "posted"

    again = service.post_fx_revaluation(
        ctx,
        revaluation_id=created.data.id,
        idempotency_key=key,
        human_confirm=True,
    )
    assert again.ok and again.data is not None
    assert again.data.journal_entry_id == posted.data.journal_entry_id


def test_gl4_reject_all_port_and_closed_period() -> None:
    ctx = _ctx()
    service = _service(ctx, fx_port=RejectAllFxRate())
    period = _setup(service, ctx)

    no_rate = service.create_fx_revaluation(
        ctx,
        period_id=period.id,
        from_currency="USD",
        to_currency="EUR",
        amount=Decimal("1.00"),
        side="loss",
        idempotency_key=uuid4(),
    )
    assert not no_rate.ok
    assert no_rate.error_message == "FX rate port is unavailable"

    with_rate = service.create_fx_revaluation(
        ctx,
        period_id=period.id,
        from_currency="USD",
        to_currency="EUR",
        amount=Decimal("1.00"),
        side="loss",
        idempotency_key=uuid4(),
        rate=Decimal("0.91000000"),
    )
    assert with_rate.ok and with_rate.data is not None

    closed = service.close_gl_period(
        ctx,
        period_id=period.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert closed.ok
    blocked = service.post_fx_revaluation(
        ctx,
        revaluation_id=with_rate.data.id,
        idempotency_key=uuid4(),
        human_confirm=True,
    )
    assert not blocked.ok
    assert blocked.error_code == ErrorCode.COMMON_CONFLICT
    assert blocked.error_message == "gl period is not open"
