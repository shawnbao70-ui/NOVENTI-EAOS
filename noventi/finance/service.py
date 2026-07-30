"""Permissioned Finance AR Receipt service (PHX-G310 / F1)."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Protocol
from uuid import UUID, uuid4

from kernel.permission.models import PermissionEffect, Resource
from kernel.shared.audit import AuditLog
from kernel.shared.context import ExecutionContext, require_context
from kernel.shared.errors import ErrorCode, KernelError
from kernel.shared.results import KernelResult
from noventi.finance.models import (
    ARCreditNote,
    ARRefund,
    ARRefundStatus,
    ARReceipt,
    ARReceiptAllocation,
    ARWriteOff,
    BankStatement,
    BankStatementLine,
    BankStatementLineStatus,
    BankStatementStatus,
    CommissionEntry,
    CommissionStatus,
    CreditNoteStatus,
    GlAccount,
    GlAccountStatus,
    GlAccountType,
    GlBridgeMap,
    GlBridgePosting,
    GlBridgeSourceType,
    GlFxRevaluation,
    GlFxRevaluationSide,
    GlFxRevaluationStatus,
    GlPeriod,
    GlPeriodStatus,
    JournalEntry,
    JournalEntryStatus,
    JournalLine,
    RealizedFxEvent,
    RealizedFxSide,
    ReceiptStatus,
    TaxInvoice,
    TaxCreditLink,
    TaxInvoiceStatus,
    TaxRate,
    TaxRateStatus,
    TenantReceiptPspPolicy,
    TenantTaxAuthorityPolicy,
    TreasuryTransfer,
    TreasuryTransferStatus,
)
from noventi.finance.repository import FinanceRepository

AR_RECEIPT_RESOURCE = "pkg.finance.receipt"
AR_WRITE_OFF_RESOURCE = "pkg.finance.ar_write_off"
AR_CREDIT_NOTE_RESOURCE = "pkg.finance.credit_note"
AR_REFUND_RESOURCE = "pkg.finance.ar_refund"
TREASURY_TRANSFER_RESOURCE = "pkg.finance.treasury_transfer"
TAX_INVOICE_RESOURCE = "pkg.finance.tax_invoice"
TAX_CREDIT_LINK_RESOURCE = "pkg.finance.tax_credit_link"
TAX_RATE_RESOURCE = "pkg.finance.tax_rate"
TAX_AUTHORITY_POLICY_RESOURCE = "pkg.finance.tax_authority_policy"
COMMISSION_RESOURCE = "pkg.finance.commission"
RECEIPT_PSP_POLICY_RESOURCE = "pkg.finance.receipt_psp_policy"
GL_ACCOUNT_RESOURCE = "pkg.finance.gl_account"
GL_PERIOD_RESOURCE = "pkg.finance.gl_period"
JOURNAL_ENTRY_RESOURCE = "pkg.finance.journal_entry"
GL_BRIDGE_RESOURCE = "pkg.finance.gl_bridge"
GL_FX_REVALUATION_RESOURCE = "pkg.finance.gl_fx_revaluation"
BANK_STATEMENT_RESOURCE = "pkg.finance.bank_statement"
_GL_ACCOUNT_TYPES = frozenset(item.value for item in GlAccountType)
AMOUNT_QUANTUM = Decimal("0.01")
RATE_PERCENT_QUANTUM = Decimal("0.0001")
FX_RATE_QUANTUM = Decimal("0.00000001")
MAX_AMOUNT = Decimal("9999999999999999.99")
MAX_RATE_PERCENT = Decimal("999.9999")
MAX_FX_RATE = Decimal("9999999999.99999999")
_CREDITABLE_INVOICE_STATUSES = frozenset({"issued", "voided"})
_TAXABLE_INVOICE_STATUSES = frozenset({"issued"})


class PermissionEvaluator(Protocol):
    def evaluate(
        self,
        ctx: ExecutionContext,
        *,
        principal_subject_id: UUID,
        action: str,
        resource: Resource,
    ) -> KernelResult: ...


@dataclass(frozen=True, slots=True)
class ARInvoiceSnapshot:
    id: UUID
    tenant_id: UUID
    customer_id: UUID
    currency: str
    total_amount: Decimal
    status: str
    version: int
    functional_currency: str = ""
    fx_rate: Decimal = Decimal("1.00000000")


class ARInvoiceReadPort(Protocol):
    def get_ar_invoice_snapshot(
        self, invoice_id: UUID
    ) -> ARInvoiceSnapshot | None: ...

    def list_ar_invoice_snapshots_for_customer(
        self, customer_id: UUID
    ) -> list[ARInvoiceSnapshot]: ...


class ARInvoiceClosePort(Protocol):
    def close_ar_invoice(
        self, *, invoice_id: UUID, expected_version: int
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class RmaCreditNoteLink:
    return_authorization_id: UUID
    invoice_id: UUID | None
    restocked: bool
    version: int


class RmaCreditNoteLinkPort(Protocol):
    def get_return_authorization_by_credit_note_id(
        self, credit_note_id: UUID
    ) -> RmaCreditNoteLink | None: ...

    def mark_credit_note_issued(
        self,
        *,
        return_authorization_id: UUID,
        expected_version: int,
        issued_at: datetime,
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class ApBillSnapshot:
    id: UUID
    tenant_id: UUID
    currency: str
    total_amount: Decimal
    status: str


class ApBillReadPort(Protocol):
    def get_ap_bill_snapshot(self, bill_id: UUID) -> ApBillSnapshot | None: ...


@dataclass(frozen=True, slots=True)
class CustomerBalance:
    customer_id: UUID
    balances: dict[str, Decimal]
    unallocated_receipts: dict[str, Decimal]


@dataclass(frozen=True, slots=True)
class ApPaymentSnapshot:
    id: UUID
    tenant_id: UUID
    currency: str
    amount: Decimal
    status: str


class ApPaymentReadPort(Protocol):
    def get_ap_payment_snapshot(
        self, payment_id: UUID
    ) -> ApPaymentSnapshot | None: ...


class BeneficiaryEligibilityPort(Protocol):
    def is_eligible(self, *, subject_id: UUID, tenant_id: UUID) -> bool: ...


@dataclass(frozen=True, slots=True)
class PspReceiptResult:
    psp_ref: str
    psp_status: str


class PspPort(Protocol):
    def apply_receipt(
        self, *, receipt: ARReceipt, invoice: ARInvoiceSnapshot
    ) -> PspReceiptResult: ...


class RejectAllPsp:
    """Fail-closed default; no live PSP transport is supplied by this package."""

    def apply_receipt(
        self, *, receipt: ARReceipt, invoice: ARInvoiceSnapshot
    ) -> PspReceiptResult:
        raise KernelError(
            ErrorCode.COMMON_CONFLICT, "PSP port is unavailable"
        )


class InMemoryFakePsp:
    """Deterministic test-only PSP port."""

    def apply_receipt(
        self, *, receipt: ARReceipt, invoice: ARInvoiceSnapshot
    ) -> PspReceiptResult:
        return PspReceiptResult(
            psp_ref=f"fake-psp-{receipt.id.hex}",
            psp_status="applied",
        )


@dataclass(frozen=True, slots=True)
class TaxAuthorityResult:
    authority_ref: str
    authority_status: str


class TaxAuthorityPort(Protocol):
    def validate_rate(
        self, *, tax_invoice: TaxInvoice, tax_rate: TaxRate
    ) -> TaxAuthorityResult: ...


class RejectAllTaxAuthority:
    """Fail-closed default; no live tax authority transport is supplied."""

    def validate_rate(
        self, *, tax_invoice: TaxInvoice, tax_rate: TaxRate
    ) -> TaxAuthorityResult:
        raise KernelError(
            ErrorCode.COMMON_CONFLICT, "Tax authority port is unavailable"
        )


class InMemoryFakeTaxAuthority:
    """Deterministic test-only tax authority port."""

    def validate_rate(
        self, *, tax_invoice: TaxInvoice, tax_rate: TaxRate
    ) -> TaxAuthorityResult:
        return TaxAuthorityResult(
            authority_ref=f"fake-authority-{tax_invoice.id.hex}",
            authority_status="validated",
        )


class FxRatePort(Protocol):
    def get_rate(
        self, *, from_currency: str, to_currency: str
    ) -> Decimal: ...


class RejectAllFxRate:
    """Fail-closed default; no live FX market transport is supplied."""

    def get_rate(self, *, from_currency: str, to_currency: str) -> Decimal:
        raise KernelError(
            ErrorCode.COMMON_CONFLICT, "FX rate port is unavailable"
        )


class InMemoryFakeFxRate:
    """Deterministic test-only FX rate port."""

    def __init__(
        self, rates: dict[tuple[str, str], Decimal] | None = None
    ) -> None:
        self._rates = rates or {("USD", "EUR"): Decimal("0.92000000")}

    def get_rate(self, *, from_currency: str, to_currency: str) -> Decimal:
        key = (from_currency.upper(), to_currency.upper())
        if key not in self._rates:
            raise KernelError(
                ErrorCode.COMMON_NOT_FOUND, "FX rate not found"
            )
        return self._rates[key]


class FinanceService:
    def __init__(
        self,
        permission: PermissionEvaluator,
        *,
        repository: FinanceRepository,
        audit_log: AuditLog,
        ar_invoice_reader: ARInvoiceReadPort,
        ar_invoice_closer: ARInvoiceClosePort | None = None,
        ap_bill_reader: ApBillReadPort | None = None,
        ap_payment_reader: ApPaymentReadPort | None = None,
        beneficiary_eligibility: BeneficiaryEligibilityPort | None = None,
        psp_port: PspPort | None = None,
        tax_authority_port: TaxAuthorityPort | None = None,
        fx_rate_port: FxRatePort | None = None,
        rma_credit_note_link_port: RmaCreditNoteLinkPort | None = None,
    ) -> None:
        self._permission = permission
        self._repository = repository
        self._audit = audit_log
        self._ar_invoice_reader = ar_invoice_reader
        self._ar_invoice_closer = ar_invoice_closer
        self._ap_bill_reader = ap_bill_reader
        self._ap_payment_reader = ap_payment_reader
        self._beneficiary_eligibility = beneficiary_eligibility
        self._rma_credit_note_link_port = rma_credit_note_link_port
        self._fx_rate_port = fx_rate_port or RejectAllFxRate()
        if psp_port is not None:
            self._psp_port = psp_port
        else:
            # Lazy import avoids cycle with psp_provider_adapter → service.
            from noventi.finance.psp_provider_adapter import resolve_psp_port

            self._psp_port = resolve_psp_port()
        if tax_authority_port is not None:
            self._tax_authority_port = tax_authority_port
        else:
            # Lazy import avoids cycle with tax_authority_adapter → service.
            from noventi.finance.tax_authority_adapter import (
                resolve_tax_authority_port,
            )

            self._tax_authority_port = resolve_tax_authority_port()

    def create_receipt(
        self,
        ctx: ExecutionContext,
        *,
        customer_id: UUID,
        amount: Decimal,
        currency: str,
        idempotency_key: UUID,
        functional_currency: str | None = None,
        fx_rate: Decimal | None = None,
        functional_amount: Decimal | None = None,
    ) -> KernelResult[ARReceipt]:
        receipt_id = uuid4()
        try:
            self._write_intent(
                ctx, "Finance.ARReceipt.Create", AR_RECEIPT_RESOURCE, receipt_id
            )
            denied = self._authorize(
                ctx, "create", AR_RECEIPT_RESOURCE, customer_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.ARReceipt.Create",
                    AR_RECEIPT_RESOURCE,
                    receipt_id,
                    denied,
                )
            normalized_amount = self._amount(amount)
            normalized_currency = self._currency(currency)
            (
                normalized_functional_currency,
                normalized_fx_rate,
                normalized_functional_amount,
            ) = self._cash_event_fx(
                currency=normalized_currency,
                amount=normalized_amount,
                functional_currency=functional_currency,
                fx_rate=fx_rate,
                functional_amount=functional_amount,
            )
            existing = self._repository.get_receipt_by_idempotency_key(idempotency_key)
            if existing is not None:
                if (
                    existing.customer_id != customer_id
                    or existing.amount != normalized_amount
                    or existing.currency != normalized_currency
                    or existing.functional_currency != normalized_functional_currency
                    or existing.fx_rate != normalized_fx_rate
                    or existing.functional_amount != normalized_functional_amount
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "receipt idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx,
                    "Finance.ARReceipt.Create",
                    AR_RECEIPT_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            if normalized_amount <= 0:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "receipt amount must be positive",
                )
            receipt = ARReceipt(
                id=receipt_id,
                tenant_id=self._tenant_id(ctx),
                customer_id=customer_id,
                code=f"RCPT-{receipt_id.hex[:12].upper()}",
                currency=normalized_currency,
                amount=normalized_amount,
                functional_currency=normalized_functional_currency,
                fx_rate=normalized_fx_rate,
                functional_amount=normalized_functional_amount,
                idempotency_key=idempotency_key,
                status=ReceiptStatus.DRAFT,
                created_at=datetime.now(timezone.utc),
            )
            self._repository.add_receipt(receipt)
            audit = self._write_result(
                ctx,
                "Finance.ARReceipt.Create",
                AR_RECEIPT_RESOURCE,
                receipt.id,
                "ok",
            )
            return KernelResult.success(receipt, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "receipt create conflict"
            )

    def get_customer_balance(
        self, ctx: ExecutionContext, *, customer_id: UUID
    ) -> KernelResult[CustomerBalance]:
        """Compute cleared AR; unallocated receipts are disclosed separately."""
        try:
            denied = self._authorize(ctx, "read", "pkg.crm.customer", customer_id)
            if denied is not None:
                return denied
            invoices = self._ar_invoice_reader.list_ar_invoice_snapshots_for_customer(
                customer_id
            )
            balances: dict[str, Decimal] = {}
            issued_ids: set[UUID] = set()
            for invoice in invoices:
                if invoice.status != "issued":
                    continue
                issued_ids.add(invoice.id)
                balances[invoice.currency] = (
                    balances.get(invoice.currency, Decimal("0.00"))
                    + invoice.total_amount
                )
            for receipt in self._repository.list_receipts_for_customer(customer_id):
                for allocation in self._repository.list_receipt_allocations(receipt.id):
                    if allocation.ar_invoice_id in issued_ids:
                        invoice = next(
                            item
                            for item in invoices
                            if item.id == allocation.ar_invoice_id
                        )
                        balances[invoice.currency] -= allocation.amount
            for invoice in invoices:
                if invoice.id not in issued_ids:
                    continue
                balances[invoice.currency] -= sum(
                    (item.amount for item in self._repository.list_ar_write_offs(invoice.id)),
                    Decimal("0.00"),
                )
            unallocated: dict[str, Decimal] = {}
            for receipt in self._repository.list_receipts_for_customer(customer_id):
                residual = receipt.amount - receipt.allocated_amount
                if residual:
                    unallocated[receipt.currency] = (
                        unallocated.get(receipt.currency, Decimal("0.00"))
                        + residual
                    )
            audit = self._write_result(
                ctx,
                "Finance.CustomerBalance.Read",
                "pkg.crm.customer",
                customer_id,
                "ok",
            )
            return KernelResult.success(
                CustomerBalance(
                    customer_id=customer_id,
                    balances=dict(sorted(balances.items())),
                    unallocated_receipts=dict(sorted(unallocated.items())),
                ),
                audit_id=audit.id,
            )
        except KernelError as err:
            return KernelResult.from_error(err)

    def apply_receipt_to_invoice(
        self,
        ctx: ExecutionContext,
        *,
        receipt_id: UUID,
        invoice_id: UUID,
        idempotency_key: UUID,
    ) -> KernelResult[ARReceipt]:
        receipt = self._repository.get_receipt(receipt_id)
        if receipt is None:
            return KernelResult.failure(
                ErrorCode.COMMON_NOT_FOUND, "receipt not found"
            )
        if (
            receipt.status == ReceiptStatus.APPLIED
            and receipt.apply_key == idempotency_key
            and receipt.ar_invoice_id == invoice_id
        ):
            return KernelResult.success(receipt)
        invoice = self._ar_invoice_reader.get_ar_invoice_snapshot(invoice_id)
        if (
            invoice is not None
            and invoice.status == "issued"
            and invoice.customer_id == receipt.customer_id
            and invoice.currency == receipt.currency
            and receipt.amount - receipt.allocated_amount > invoice.total_amount
        ):
            return KernelResult.failure(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "receipt amount exceeds AR invoice total",
            )
        return self.allocate_receipt_to_invoice(
            ctx,
            receipt_id=receipt_id,
            invoice_id=invoice_id,
            amount=receipt.amount - receipt.allocated_amount,
            allocation_key=idempotency_key,
        )

    def allocate_receipt_to_invoice(
        self,
        ctx: ExecutionContext,
        *,
        receipt_id: UUID,
        invoice_id: UUID,
        amount: Decimal,
        allocation_key: UUID,
    ) -> KernelResult[ARReceipt]:
        try:
            self._write_intent(
                ctx, "Finance.ARReceipt.Allocate", AR_RECEIPT_RESOURCE, receipt_id
            )
            denied = self._authorize(
                ctx, "apply", AR_RECEIPT_RESOURCE, receipt_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.ARReceipt.Allocate",
                    AR_RECEIPT_RESOURCE,
                    receipt_id,
                    denied,
                )
            receipt = self._repository.get_receipt(receipt_id)
            if receipt is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "receipt not found"
                )
            normalized_amount = self._amount(amount)
            existing = self._repository.get_receipt_allocation_by_key(
                allocation_key
            )
            if existing is not None:
                if (
                    existing.receipt_id == receipt_id
                    and existing.ar_invoice_id == invoice_id
                    and existing.amount == normalized_amount
                ):
                    audit = self._write_result(
                        ctx,
                        "Finance.ARReceipt.Allocate",
                        AR_RECEIPT_RESOURCE,
                        receipt.id,
                        "ok",
                    )
                    return KernelResult.success(receipt, audit_id=audit.id)
                raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                    "receipt allocation key was used for another request",
                )
            if normalized_amount <= 0:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "allocation amount must be positive",
                )
            unallocated = receipt.amount - receipt.allocated_amount
            if normalized_amount > unallocated:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "allocation amount exceeds receipt unallocated amount",
                )
            invoice = self._ar_invoice_reader.get_ar_invoice_snapshot(
                invoice_id
            )
            if invoice is None or invoice.tenant_id != self._tenant_id(ctx):
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "AR invoice not found"
                )
            if invoice.status != "issued":
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "AR invoice must be issued",
                )
            if invoice.customer_id != receipt.customer_id:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "receipt customer does not match AR invoice",
                )
            realized_fx_event: RealizedFxEvent | None = None
            if invoice.currency != receipt.currency:
                if (
                    not receipt.functional_currency
                    or not invoice.functional_currency
                    or receipt.functional_currency != invoice.functional_currency
                    or receipt.fx_rate <= 0
                    or invoice.fx_rate <= 0
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "cross-currency allocation requires compatible FX snapshots",
                    )
                # A positive delta means the receipt's functional value exceeds
                # the invoice's functional value and is therefore a gain.
                receipt_functional = self._amount(
                    normalized_amount * receipt.fx_rate
                )
                invoice_functional = self._amount(
                    normalized_amount * invoice.fx_rate
                )
                realized_delta = receipt_functional - invoice_functional
                if realized_delta != 0:
                    realized_fx_event = RealizedFxEvent(
                        id=uuid4(),
                        tenant_id=self._tenant_id(ctx),
                        source_type="allocation",
                        source_id=uuid4(),
                        amount=abs(realized_delta),
                        currency=receipt.functional_currency,
                        side=(
                            RealizedFxSide.GAIN
                            if realized_delta > 0
                            else RealizedFxSide.LOSS
                        ),
                        receipt_id=receipt.id,
                        invoice_id=invoice.id,
                        created_at=datetime.now(timezone.utc),
                    )
            psp_result: PspReceiptResult | None = None
            if self._receipt_psp_policy_or_default(ctx).receipt_psp_required:
                psp_result = self._psp_port.apply_receipt(
                    receipt=receipt, invoice=invoice
                )
            now = datetime.now(timezone.utc)
            allocated_amount = receipt.allocated_amount + normalized_amount
            allocation = ARReceiptAllocation(
                id=uuid4(),
                tenant_id=self._tenant_id(ctx),
                receipt_id=receipt.id,
                ar_invoice_id=invoice.id,
                amount=normalized_amount,
                allocation_key=allocation_key,
                created_at=now,
            )
            if realized_fx_event is not None:
                realized_fx_event = replace(
                    realized_fx_event,
                    source_id=allocation.id,
                    created_at=now,
                )
            applied = replace(
                receipt,
                status=(
                    ReceiptStatus.APPLIED
                    if allocated_amount == receipt.amount
                    else ReceiptStatus.DRAFT
                ),
                # Compatibility pointer remains the first allocated invoice.
                ar_invoice_id=receipt.ar_invoice_id or invoice.id,
                ar_invoice_version=receipt.ar_invoice_version or invoice.version,
                apply_key=receipt.apply_key or allocation_key,
                applied_at=now if allocated_amount == receipt.amount else None,
                psp_ref=psp_result.psp_ref if psp_result else None,
                psp_status=psp_result.psp_status if psp_result else None,
                allocated_amount=allocated_amount,
                version=receipt.version + 1,
            )
            self._repository.add_receipt_allocation(allocation)
            if realized_fx_event is not None:
                self._repository.add_realized_fx_event(realized_fx_event)
            self._repository.save_receipt(
                applied, expected_version=receipt.version
            )
            audit = self._write_result(
                ctx,
                "Finance.ARReceipt.Allocate",
                AR_RECEIPT_RESOURCE,
                receipt.id,
                "ok",
            )
            return KernelResult.success(applied, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "receipt allocation conflict"
            )

    def list_receipt_allocations(
        self, ctx: ExecutionContext, *, receipt_id: UUID
    ) -> KernelResult[list[ARReceiptAllocation]]:
        try:
            denied = self._authorize(ctx, "read", AR_RECEIPT_RESOURCE, receipt_id)
            if denied is not None:
                return denied
            if self._repository.get_receipt(receipt_id) is None:
                raise KernelError(ErrorCode.COMMON_NOT_FOUND, "receipt not found")
            allocations = self._repository.list_receipt_allocations(receipt_id)
            return KernelResult.success(
                [
                    replace(
                        allocation,
                        realized_fx_amount=event.amount,
                        realized_fx_side=event.side,
                    )
                    if (
                        event := self._repository.get_realized_fx_event_by_source(
                            allocation.id
                        )
                    )
                    else allocation
                    for allocation in allocations
                ]
            )
        except KernelError as err:
            return KernelResult.from_error(err)

    def create_ar_write_off(
        self,
        ctx: ExecutionContext,
        *,
        invoice_id: UUID,
        amount: Decimal,
        idempotency_key: UUID,
        human_confirm: bool = True,
        reason: str | None = None,
    ) -> KernelResult[ARWriteOff]:
        write_off_id = uuid4()
        try:
            self._write_intent(
                ctx, "Finance.ARWriteOff.Create", AR_WRITE_OFF_RESOURCE, write_off_id
            )
            denied = self._authorize(ctx, "create", AR_WRITE_OFF_RESOURCE, invoice_id)
            if denied is not None:
                return self._write_denied(
                    ctx, "Finance.ARWriteOff.Create", AR_WRITE_OFF_RESOURCE,
                    write_off_id, denied,
                )
            if not human_confirm:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required for AR write-off",
                )
            normalized_amount = self._amount(amount)
            if normalized_amount <= 0:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "write-off amount must be positive",
                )
            existing = self._repository.get_ar_write_off_by_idempotency_key(
                idempotency_key
            )
            if existing is not None:
                if (
                    existing.ar_invoice_id != invoice_id
                    or existing.amount != normalized_amount
                    or existing.reason != reason
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "write-off idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx, "Finance.ARWriteOff.Create", AR_WRITE_OFF_RESOURCE,
                    existing.id, "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            invoice = self._issued_invoice(ctx, invoice_id)
            remaining = self._ar_invoice_remaining(invoice)
            if normalized_amount > remaining:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "write-off amount exceeds AR invoice remaining amount",
                )
            write_off = ARWriteOff(
                id=write_off_id,
                tenant_id=self._tenant_id(ctx),
                ar_invoice_id=invoice_id,
                amount=normalized_amount,
                currency=invoice.currency,
                idempotency_key=idempotency_key,
                reason=reason,
                created_at=datetime.now(timezone.utc),
            )
            self._repository.add_ar_write_off(write_off)
            audit = self._write_result(
                ctx, "Finance.ARWriteOff.Create", AR_WRITE_OFF_RESOURCE,
                write_off.id, "ok",
            )
            return KernelResult.success(write_off, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "AR write-off create conflict"
            )

    def close_ar_invoice(
        self, ctx: ExecutionContext, *, invoice_id: UUID, human_confirm: bool = True
    ) -> KernelResult[ARInvoiceSnapshot]:
        try:
            self._write_intent(
                ctx, "Finance.ARInvoice.Close", AR_WRITE_OFF_RESOURCE, invoice_id
            )
            denied = self._authorize(ctx, "update", AR_WRITE_OFF_RESOURCE, invoice_id)
            if denied is not None:
                return self._write_denied(
                    ctx, "Finance.ARInvoice.Close", AR_WRITE_OFF_RESOURCE,
                    invoice_id, denied,
                )
            if not human_confirm:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required for AR invoice close",
                )
            invoice = self._ar_invoice_reader.get_ar_invoice_snapshot(invoice_id)
            if invoice is None or invoice.tenant_id != self._tenant_id(ctx):
                raise KernelError(ErrorCode.COMMON_NOT_FOUND, "AR invoice not found")
            if invoice.status == "closed":
                return KernelResult.success(invoice)
            invoice = self._issued_invoice(ctx, invoice_id)
            if self._ar_invoice_remaining(invoice) != Decimal("0.00"):
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "AR invoice cannot close until remaining amount is zero",
                )
            if self._ar_invoice_closer is None:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT, "AR invoice close port is unavailable"
                )
            self._ar_invoice_closer.close_ar_invoice(
                invoice_id=invoice.id, expected_version=invoice.version
            )
            closed = self._ar_invoice_reader.get_ar_invoice_snapshot(invoice_id)
            assert closed is not None
            audit = self._write_result(
                ctx, "Finance.ARInvoice.Close", AR_WRITE_OFF_RESOURCE, invoice_id, "ok"
            )
            return KernelResult.success(closed, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "AR invoice close conflict"
            )

    def get_receipt_psp_policy(
        self, ctx: ExecutionContext
    ) -> KernelResult[TenantReceiptPspPolicy]:
        try:
            denied = self._authorize(ctx, "read", RECEIPT_PSP_POLICY_RESOURCE)
            if denied is not None:
                return denied
            return KernelResult.success(self._receipt_psp_policy_or_default(ctx))
        except KernelError as err:
            return KernelResult.from_error(err)

    def set_receipt_psp_policy(
        self,
        ctx: ExecutionContext,
        *,
        receipt_psp_required: bool,
        expected_version: int,
    ) -> KernelResult[TenantReceiptPspPolicy]:
        try:
            tenant_id = self._tenant_id(ctx)
            self._write_intent(
                ctx, "Finance.Policy.ReceiptPsp.Set",
                RECEIPT_PSP_POLICY_RESOURCE, tenant_id
            )
            denied = self._authorize(ctx, "update", RECEIPT_PSP_POLICY_RESOURCE)
            if denied is not None:
                return self._write_denied(
                    ctx, "Finance.Policy.ReceiptPsp.Set",
                    RECEIPT_PSP_POLICY_RESOURCE, tenant_id, denied
                )
            current = self._repository.get_receipt_psp_policy()
            if current is None:
                if expected_version != 0:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "receipt PSP policy version conflict",
                    )
                version = 1
            else:
                if current.version != expected_version:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "receipt PSP policy version conflict",
                    )
                version = current.version + 1
            policy = TenantReceiptPspPolicy(
                tenant_id=tenant_id,
                receipt_psp_required=bool(receipt_psp_required),
                updated_at=datetime.now(timezone.utc),
                version=version,
            )
            self._repository.save_receipt_psp_policy(
                policy, expected_version=expected_version
            )
            audit = self._write_result(
                ctx, "Finance.Policy.ReceiptPsp.Set",
                RECEIPT_PSP_POLICY_RESOURCE, tenant_id, "ok"
            )
            return KernelResult.success(policy, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "receipt PSP policy version conflict"
            )

    def get_receipt(
        self,
        ctx: ExecutionContext,
        *,
        receipt_id: UUID,
    ) -> KernelResult[ARReceipt]:
        try:
            denied = self._authorize(
                ctx, "read", AR_RECEIPT_RESOURCE, receipt_id
            )
            if denied is not None:
                return denied
            receipt = self._repository.get_receipt(receipt_id)
            if receipt is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "receipt not found"
                )
            return KernelResult.success(receipt)
        except KernelError as err:
            return KernelResult.from_error(err)

    def create_credit_note(
        self,
        ctx: ExecutionContext,
        *,
        invoice_id: UUID,
        amount: Decimal,
        idempotency_key: UUID,
    ) -> KernelResult[ARCreditNote]:
        credit_note_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "Finance.ARCreditNote.Create",
                AR_CREDIT_NOTE_RESOURCE,
                credit_note_id,
            )
            denied = self._authorize(
                ctx, "create", AR_CREDIT_NOTE_RESOURCE, invoice_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.ARCreditNote.Create",
                    AR_CREDIT_NOTE_RESOURCE,
                    credit_note_id,
                    denied,
                )
            existing = self._repository.get_credit_note_by_idempotency_key(
                idempotency_key
            )
            normalized_amount = self._amount(amount)
            if existing is not None:
                if (
                    existing.ar_invoice_id != invoice_id
                    or existing.amount != normalized_amount
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "credit note idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx,
                    "Finance.ARCreditNote.Create",
                    AR_CREDIT_NOTE_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            if normalized_amount <= 0:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "credit note amount must be positive",
                )
            invoice = self._ar_invoice_reader.get_ar_invoice_snapshot(
                invoice_id
            )
            if invoice is None or invoice.tenant_id != self._tenant_id(ctx):
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "AR invoice not found"
                )
            if invoice.status not in _CREDITABLE_INVOICE_STATUSES:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "AR invoice must be issued or voided",
                )
            if normalized_amount > invoice.total_amount:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "credit note amount exceeds AR invoice total",
                )
            credit_note = ARCreditNote(
                id=credit_note_id,
                tenant_id=self._tenant_id(ctx),
                customer_id=invoice.customer_id,
                ar_invoice_id=invoice.id,
                ar_invoice_version=invoice.version,
                code=f"CN-{credit_note_id.hex[:12].upper()}",
                currency=invoice.currency,
                amount=normalized_amount,
                idempotency_key=idempotency_key,
                status=CreditNoteStatus.DRAFT,
                created_at=datetime.now(timezone.utc),
            )
            self._repository.add_credit_note(credit_note)
            audit = self._write_result(
                ctx,
                "Finance.ARCreditNote.Create",
                AR_CREDIT_NOTE_RESOURCE,
                credit_note.id,
                "ok",
            )
            return KernelResult.success(credit_note, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "credit note create conflict"
            )

    def issue_credit_note(
        self,
        ctx: ExecutionContext,
        *,
        credit_note_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
    ) -> KernelResult[ARCreditNote]:
        try:
            self._write_intent(
                ctx,
                "Finance.ARCreditNote.Issue",
                AR_CREDIT_NOTE_RESOURCE,
                credit_note_id,
            )
            denied = self._authorize(
                ctx, "issue", AR_CREDIT_NOTE_RESOURCE, credit_note_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.ARCreditNote.Issue",
                    AR_CREDIT_NOTE_RESOURCE,
                    credit_note_id,
                    denied,
                )
            credit_note = self._repository.get_credit_note(credit_note_id)
            if credit_note is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "credit note not found"
                )
            if credit_note.status == CreditNoteStatus.ISSUED:
                if credit_note.issue_key == idempotency_key:
                    audit = self._write_result(
                        ctx,
                        "Finance.ARCreditNote.Issue",
                        AR_CREDIT_NOTE_RESOURCE,
                        credit_note.id,
                        "ok",
                    )
                    return KernelResult.success(
                        credit_note, audit_id=audit.id
                    )
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "credit note is already issued",
                )
            if credit_note.status != CreditNoteStatus.DRAFT:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "credit note cannot be issued",
                )
            if human_confirm is not True:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required to issue",
                )
            rma_link = None
            if self._rma_credit_note_link_port is not None:
                rma_link = (
                    self._rma_credit_note_link_port
                    .get_return_authorization_by_credit_note_id(credit_note.id)
                )
                if rma_link is not None and (
                    not rma_link.restocked
                    or rma_link.invoice_id != credit_note.ar_invoice_id
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "linked return authorization has invalid credit note lineage",
                    )
            issued_at = datetime.now(timezone.utc)
            issued = replace(
                credit_note,
                status=CreditNoteStatus.ISSUED,
                issued_at=issued_at,
                issue_key=idempotency_key,
                version=credit_note.version + 1,
            )
            self._repository.save_credit_note(
                issued, expected_version=credit_note.version
            )
            if rma_link is not None:
                self._rma_credit_note_link_port.mark_credit_note_issued(
                    return_authorization_id=rma_link.return_authorization_id,
                    expected_version=rma_link.version,
                    issued_at=issued_at,
                )
            audit = self._write_result(
                ctx,
                "Finance.ARCreditNote.Issue",
                AR_CREDIT_NOTE_RESOURCE,
                credit_note.id,
                "ok",
            )
            return KernelResult.success(issued, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "credit note issue conflict"
            )

    def get_credit_note(
        self,
        ctx: ExecutionContext,
        *,
        credit_note_id: UUID,
    ) -> KernelResult[ARCreditNote]:
        try:
            denied = self._authorize(
                ctx, "read", AR_CREDIT_NOTE_RESOURCE, credit_note_id
            )
            if denied is not None:
                return denied
            credit_note = self._repository.get_credit_note(credit_note_id)
            if credit_note is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "credit note not found"
                )
            return KernelResult.success(credit_note)
        except KernelError as err:
            return KernelResult.from_error(err)

    def create_ar_refund(
        self,
        ctx: ExecutionContext,
        *,
        credit_note_id: UUID,
        amount: Decimal,
        currency: str,
        idempotency_key: UUID,
    ) -> KernelResult[ARRefund]:
        refund_id = uuid4()
        try:
            self._write_intent(
                ctx, "Finance.ARRefund.Create", AR_REFUND_RESOURCE, refund_id
            )
            denied = self._authorize(
                ctx, "create", AR_REFUND_RESOURCE, credit_note_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.ARRefund.Create",
                    AR_REFUND_RESOURCE,
                    refund_id,
                    denied,
                )
            normalized_amount = self._amount(amount)
            normalized_currency = self._currency(currency)
            existing = self._repository.get_ar_refund_by_idempotency_key(
                idempotency_key
            )
            if existing is not None:
                if (
                    existing.credit_note_id != credit_note_id
                    or existing.amount != normalized_amount
                    or existing.currency != normalized_currency
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "AR refund idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx,
                    "Finance.ARRefund.Create",
                    AR_REFUND_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            if normalized_amount <= 0:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "AR refund amount must be positive",
                )
            credit_note = self._repository.get_credit_note(credit_note_id)
            if credit_note is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "credit note not found"
                )
            if credit_note.status != CreditNoteStatus.ISSUED:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "credit note must be issued",
                )
            if normalized_currency != credit_note.currency:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "AR refund currency must match credit note currency",
                )
            if normalized_amount > credit_note.amount:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "AR refund amount exceeds credit note amount",
                )
            refund = ARRefund(
                id=refund_id,
                tenant_id=self._tenant_id(ctx),
                credit_note_id=credit_note.id,
                customer_id=credit_note.customer_id,
                currency=credit_note.currency,
                amount=normalized_amount,
                idempotency_key=idempotency_key,
                status=ARRefundStatus.DRAFT,
                created_at=datetime.now(timezone.utc),
            )
            self._repository.add_ar_refund(refund)
            audit = self._write_result(
                ctx, "Finance.ARRefund.Create", AR_REFUND_RESOURCE, refund.id, "ok"
            )
            return KernelResult.success(refund, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "AR refund create conflict"
            )

    def post_ar_refund(
        self,
        ctx: ExecutionContext,
        *,
        refund_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
    ) -> KernelResult[ARRefund]:
        try:
            self._write_intent(
                ctx, "Finance.ARRefund.Post", AR_REFUND_RESOURCE, refund_id
            )
            denied = self._authorize(
                ctx, "post", AR_REFUND_RESOURCE, refund_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.ARRefund.Post",
                    AR_REFUND_RESOURCE,
                    refund_id,
                    denied,
                )
            refund = self._repository.get_ar_refund(refund_id)
            if refund is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "AR refund not found"
                )
            if refund.status == ARRefundStatus.POSTED:
                if refund.post_key == idempotency_key:
                    audit = self._write_result(
                        ctx,
                        "Finance.ARRefund.Post",
                        AR_REFUND_RESOURCE,
                        refund.id,
                        "ok",
                    )
                    return KernelResult.success(refund, audit_id=audit.id)
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT, "AR refund is already posted"
                )
            if human_confirm is not True:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required to post",
                )
            posted = replace(
                refund,
                status=ARRefundStatus.POSTED,
                posted_at=datetime.now(timezone.utc),
                post_key=idempotency_key,
                version=refund.version + 1,
            )
            self._repository.save_ar_refund(
                posted, expected_version=refund.version
            )
            audit = self._write_result(
                ctx, "Finance.ARRefund.Post", AR_REFUND_RESOURCE, posted.id, "ok"
            )
            return KernelResult.success(posted, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "AR refund post conflict"
            )

    def create_treasury_transfer(
        self,
        ctx: ExecutionContext,
        *,
        from_account_ref: str,
        to_account_ref: str,
        amount: Decimal,
        currency: str,
        idempotency_key: UUID,
        functional_currency: str | None = None,
        fx_rate: Decimal | None = None,
        functional_amount: Decimal | None = None,
    ) -> KernelResult[TreasuryTransfer]:
        transfer_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "Finance.TreasuryTransfer.Create",
                TREASURY_TRANSFER_RESOURCE,
                transfer_id,
            )
            denied = self._authorize(
                ctx, "create", TREASURY_TRANSFER_RESOURCE, transfer_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.TreasuryTransfer.Create",
                    TREASURY_TRANSFER_RESOURCE,
                    transfer_id,
                    denied,
                )
            normalized_from = self._account_ref(from_account_ref)
            normalized_to = self._account_ref(to_account_ref)
            if normalized_from == normalized_to:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "from_account_ref and to_account_ref must differ",
                )
            normalized_amount = self._amount(amount)
            normalized_currency = self._currency(currency)
            (
                normalized_functional_currency,
                normalized_fx_rate,
                normalized_functional_amount,
            ) = self._cash_event_fx(
                currency=normalized_currency,
                amount=normalized_amount,
                functional_currency=functional_currency,
                fx_rate=fx_rate,
                functional_amount=functional_amount,
            )
            existing = self._repository.get_treasury_transfer_by_idempotency_key(
                idempotency_key
            )
            if existing is not None:
                if (
                    existing.from_account_ref != normalized_from
                    or existing.to_account_ref != normalized_to
                    or existing.amount != normalized_amount
                    or existing.currency != normalized_currency
                    or existing.functional_currency
                    != normalized_functional_currency
                    or existing.fx_rate != normalized_fx_rate
                    or existing.functional_amount
                    != normalized_functional_amount
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "treasury transfer idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx,
                    "Finance.TreasuryTransfer.Create",
                    TREASURY_TRANSFER_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            if normalized_amount <= 0:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "treasury transfer amount must be positive",
                )
            transfer = TreasuryTransfer(
                id=transfer_id,
                tenant_id=self._tenant_id(ctx),
                from_account_ref=normalized_from,
                to_account_ref=normalized_to,
                currency=normalized_currency,
                amount=normalized_amount,
                functional_currency=normalized_functional_currency,
                fx_rate=normalized_fx_rate,
                functional_amount=normalized_functional_amount,
                idempotency_key=idempotency_key,
                status=TreasuryTransferStatus.DRAFT,
                created_at=datetime.now(timezone.utc),
            )
            self._repository.add_treasury_transfer(transfer)
            audit = self._write_result(
                ctx,
                "Finance.TreasuryTransfer.Create",
                TREASURY_TRANSFER_RESOURCE,
                transfer.id,
                "ok",
            )
            return KernelResult.success(transfer, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "treasury transfer create conflict"
            )

    def get_treasury_transfer(
        self,
        ctx: ExecutionContext,
        *,
        transfer_id: UUID,
    ) -> KernelResult[TreasuryTransfer]:
        try:
            denied = self._authorize(
                ctx, "read", TREASURY_TRANSFER_RESOURCE, transfer_id
            )
            if denied is not None:
                return denied
            transfer = self._repository.get_treasury_transfer(transfer_id)
            if transfer is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "treasury transfer not found"
                )
            return KernelResult.success(transfer)
        except KernelError as err:
            return KernelResult.from_error(err)

    def post_treasury_transfer(
        self,
        ctx: ExecutionContext,
        *,
        transfer_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
    ) -> KernelResult[TreasuryTransfer]:
        try:
            self._write_intent(
                ctx,
                "Finance.TreasuryTransfer.Post",
                TREASURY_TRANSFER_RESOURCE,
                transfer_id,
            )
            denied = self._authorize(
                ctx, "post", TREASURY_TRANSFER_RESOURCE, transfer_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.TreasuryTransfer.Post",
                    TREASURY_TRANSFER_RESOURCE,
                    transfer_id,
                    denied,
                )
            transfer = self._repository.get_treasury_transfer(transfer_id)
            if transfer is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "treasury transfer not found"
                )
            if transfer.status == TreasuryTransferStatus.POSTED:
                if transfer.post_key == idempotency_key:
                    audit = self._write_result(
                        ctx,
                        "Finance.TreasuryTransfer.Post",
                        TREASURY_TRANSFER_RESOURCE,
                        transfer.id,
                        "ok",
                    )
                    return KernelResult.success(transfer, audit_id=audit.id)
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "treasury transfer is already posted",
                )
            if human_confirm is not True:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required to post",
                )
            posted = replace(
                transfer,
                status=TreasuryTransferStatus.POSTED,
                posted_at=datetime.now(timezone.utc),
                post_key=idempotency_key,
                version=transfer.version + 1,
            )
            self._repository.save_treasury_transfer(
                posted, expected_version=transfer.version
            )
            audit = self._write_result(
                ctx,
                "Finance.TreasuryTransfer.Post",
                TREASURY_TRANSFER_RESOURCE,
                posted.id,
                "ok",
            )
            return KernelResult.success(posted, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "treasury transfer post conflict"
            )

    def create_tax_invoice(
        self,
        ctx: ExecutionContext,
        *,
        invoice_id: UUID,
        amount: Decimal,
        idempotency_key: UUID,
        tax_code: str | None = None,
    ) -> KernelResult[TaxInvoice]:
        tax_invoice_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "Finance.TaxInvoice.Create",
                TAX_INVOICE_RESOURCE,
                tax_invoice_id,
            )
            denied = self._authorize(
                ctx, "create", TAX_INVOICE_RESOURCE, invoice_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.TaxInvoice.Create",
                    TAX_INVOICE_RESOURCE,
                    tax_invoice_id,
                    denied,
                )
            existing = self._repository.get_tax_invoice_by_idempotency_key(
                idempotency_key
            )
            normalized_amount = self._amount(amount)
            normalized_tax_code = self._optional_tax_code(tax_code)
            if existing is not None:
                if (
                    existing.ar_invoice_id != invoice_id
                    or existing.amount != normalized_amount
                    or existing.tax_code != normalized_tax_code
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "tax invoice idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx,
                    "Finance.TaxInvoice.Create",
                    TAX_INVOICE_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            if normalized_amount <= 0:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "tax invoice amount must be positive",
                )
            invoice = self._ar_invoice_reader.get_ar_invoice_snapshot(
                invoice_id
            )
            if invoice is None or invoice.tenant_id != self._tenant_id(ctx):
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "AR invoice not found"
                )
            if invoice.status not in _TAXABLE_INVOICE_STATUSES:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "AR invoice must be issued",
                )
            if normalized_amount > invoice.total_amount:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "tax invoice amount exceeds AR invoice total",
                )
            tax_invoice = TaxInvoice(
                id=tax_invoice_id,
                tenant_id=self._tenant_id(ctx),
                customer_id=invoice.customer_id,
                ar_invoice_id=invoice.id,
                ar_invoice_version=invoice.version,
                code=f"TI-{tax_invoice_id.hex[:12].upper()}",
                currency=invoice.currency,
                amount=normalized_amount,
                idempotency_key=idempotency_key,
                status=TaxInvoiceStatus.DRAFT,
                created_at=datetime.now(timezone.utc),
                tax_code=normalized_tax_code,
            )
            self._repository.add_tax_invoice(tax_invoice)
            audit = self._write_result(
                ctx,
                "Finance.TaxInvoice.Create",
                TAX_INVOICE_RESOURCE,
                tax_invoice.id,
                "ok",
            )
            return KernelResult.success(tax_invoice, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "tax invoice create conflict"
            )

    def create_tax_red_credit(
        self,
        ctx: ExecutionContext,
        *,
        original_id: UUID,
        amount: Decimal | None,
        idempotency_key: UUID,
        human_confirm: bool = True,
    ) -> KernelResult[TaxInvoice]:
        tax_invoice_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "Finance.TaxInvoice.RedCredit.Create",
                TAX_INVOICE_RESOURCE,
                tax_invoice_id,
            )
            denied = self._authorize(
                ctx, "create", TAX_INVOICE_RESOURCE, original_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.TaxInvoice.RedCredit.Create",
                    TAX_INVOICE_RESOURCE,
                    tax_invoice_id,
                    denied,
                )
            if human_confirm is not True:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required to create a red credit",
                )
            existing = self._repository.get_tax_invoice_by_idempotency_key(
                idempotency_key
            )
            original = self._repository.get_tax_invoice(original_id)
            if original is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "original tax invoice not found"
                )
            normalized_amount = (
                original.amount if amount is None else self._amount(amount)
            )
            if existing is not None:
                if (
                    existing.original_tax_invoice_id != original_id
                    or not existing.is_red_credit
                    or existing.amount != normalized_amount
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "tax red-credit idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx,
                    "Finance.TaxInvoice.RedCredit.Create",
                    TAX_INVOICE_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            if original.status != TaxInvoiceStatus.ISSUED or original.is_red_credit:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "only issued non-credit tax invoices can be red-credited",
                )
            if normalized_amount <= 0 or normalized_amount > original.amount:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "red-credit amount must be positive and not exceed the original",
                )
            if (
                self._repository.get_red_credit_by_original_tax_invoice(original.id)
                is not None
            ):
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "tax invoice already has a red credit",
                )
            red_credit = TaxInvoice(
                id=tax_invoice_id,
                tenant_id=self._tenant_id(ctx),
                customer_id=original.customer_id,
                ar_invoice_id=original.ar_invoice_id,
                ar_invoice_version=original.ar_invoice_version,
                code=f"TI-RC-{tax_invoice_id.hex[:9].upper()}",
                currency=original.currency,
                amount=normalized_amount,
                idempotency_key=idempotency_key,
                status=TaxInvoiceStatus.DRAFT,
                created_at=datetime.now(timezone.utc),
                tax_code=original.tax_code,
                original_tax_invoice_id=original.id,
                is_red_credit=True,
            )
            self._repository.add_tax_invoice(red_credit)
            audit = self._write_result(
                ctx,
                "Finance.TaxInvoice.RedCredit.Create",
                TAX_INVOICE_RESOURCE,
                red_credit.id,
                "ok",
            )
            return KernelResult.success(red_credit, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "tax red-credit create conflict"
            )

    def link_tax_invoice_to_credit_note(
        self,
        ctx: ExecutionContext,
        *,
        tax_invoice_id: UUID,
        credit_note_id: UUID,
        idempotency_key: UUID,
    ) -> KernelResult[TaxCreditLink]:
        link_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "Finance.TaxCreditLink.Create",
                TAX_CREDIT_LINK_RESOURCE,
                link_id,
            )
            denied = self._authorize(
                ctx, "create", TAX_CREDIT_LINK_RESOURCE, tax_invoice_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.TaxCreditLink.Create",
                    TAX_CREDIT_LINK_RESOURCE,
                    link_id,
                    denied,
                )
            existing = self._repository.get_tax_credit_link_by_idempotency_key(
                idempotency_key
            )
            if existing is not None:
                if (
                    existing.tax_invoice_id != tax_invoice_id
                    or existing.credit_note_id != credit_note_id
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "tax credit link idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx,
                    "Finance.TaxCreditLink.Create",
                    TAX_CREDIT_LINK_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            tax_invoice = self._repository.get_tax_invoice(tax_invoice_id)
            if tax_invoice is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "tax invoice not found"
                )
            if tax_invoice.status != TaxInvoiceStatus.ISSUED:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "tax invoice must be issued",
                )
            credit_note = self._repository.get_credit_note(credit_note_id)
            if credit_note is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "credit note not found"
                )
            if credit_note.status not in {
                CreditNoteStatus.DRAFT,
                CreditNoteStatus.ISSUED,
            }:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "credit note must be draft or issued",
                )
            if (
                tax_invoice.customer_id != credit_note.customer_id
                or tax_invoice.ar_invoice_id != credit_note.ar_invoice_id
            ):
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "tax invoice and credit note must share customer and AR invoice lineage",
                )
            link = TaxCreditLink(
                id=link_id,
                tenant_id=self._tenant_id(ctx),
                tax_invoice_id=tax_invoice.id,
                credit_note_id=credit_note.id,
                status="linked",
                idempotency_key=idempotency_key,
                created_at=datetime.now(timezone.utc),
            )
            self._repository.add_tax_credit_link(link)
            audit = self._write_result(
                ctx,
                "Finance.TaxCreditLink.Create",
                TAX_CREDIT_LINK_RESOURCE,
                link.id,
                "ok",
            )
            return KernelResult.success(link, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "tax credit link create conflict"
            )

    def get_tax_credit_link(
        self, ctx: ExecutionContext, *, link_id: UUID
    ) -> KernelResult[TaxCreditLink]:
        try:
            denied = self._authorize(
                ctx, "read", TAX_CREDIT_LINK_RESOURCE, link_id
            )
            if denied is not None:
                return denied
            link = self._repository.get_tax_credit_link(link_id)
            if link is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "tax credit link not found"
                )
            return KernelResult.success(link)
        except KernelError as err:
            return KernelResult.from_error(err)

    def issue_tax_invoice(
        self,
        ctx: ExecutionContext,
        *,
        tax_invoice_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
        tax_code: str | None = None,
    ) -> KernelResult[TaxInvoice]:
        try:
            self._write_intent(
                ctx,
                "Finance.TaxInvoice.Issue",
                TAX_INVOICE_RESOURCE,
                tax_invoice_id,
            )
            denied = self._authorize(
                ctx, "issue", TAX_INVOICE_RESOURCE, tax_invoice_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.TaxInvoice.Issue",
                    TAX_INVOICE_RESOURCE,
                    tax_invoice_id,
                    denied,
                )
            tax_invoice = self._repository.get_tax_invoice(tax_invoice_id)
            if tax_invoice is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "tax invoice not found"
                )
            if tax_invoice.status == TaxInvoiceStatus.ISSUED:
                if tax_invoice.issue_key == idempotency_key:
                    audit = self._write_result(
                        ctx,
                        "Finance.TaxInvoice.Issue",
                        TAX_INVOICE_RESOURCE,
                        tax_invoice.id,
                        "ok",
                    )
                    return KernelResult.success(
                        tax_invoice, audit_id=audit.id
                    )
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "tax invoice is already issued",
                )
            if tax_invoice.status != TaxInvoiceStatus.DRAFT:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "tax invoice cannot be issued",
                )
            if human_confirm is not True:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required to issue",
                )
            invoice = self._ar_invoice_reader.get_ar_invoice_snapshot(
                tax_invoice.ar_invoice_id
            )
            if invoice is None or invoice.tenant_id != self._tenant_id(ctx):
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "AR invoice not found"
                )
            if invoice.status not in _TAXABLE_INVOICE_STATUSES:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "AR invoice must be issued",
                )
            bound_tax_code = self._optional_tax_code(tax_code)
            if bound_tax_code is None:
                bound_tax_code = tax_invoice.tax_code
            authority_ref: str | None = None
            authority_status: str | None = None
            if self._tax_authority_policy_or_default(
                ctx
            ).tax_authority_required:
                if bound_tax_code is None:
                    raise KernelError(
                        ErrorCode.COMMON_VALIDATION_FAILED,
                        "tax_code is required when tax authority is required",
                    )
                tax_rate = self._repository.get_tax_rate_by_code(
                    bound_tax_code
                )
                if tax_rate is None:
                    raise KernelError(
                        ErrorCode.COMMON_NOT_FOUND, "tax rate not found"
                    )
                if tax_rate.status != TaxRateStatus.ACTIVE:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "tax rate is not active",
                    )
                draft_for_port = replace(
                    tax_invoice, tax_code=bound_tax_code
                )
                authority = self._tax_authority_port.validate_rate(
                    tax_invoice=draft_for_port, tax_rate=tax_rate
                )
                authority_ref = authority.authority_ref
                authority_status = authority.authority_status
            issued = replace(
                tax_invoice,
                status=TaxInvoiceStatus.ISSUED,
                issued_at=datetime.now(timezone.utc),
                issue_key=idempotency_key,
                tax_code=bound_tax_code,
                authority_ref=authority_ref,
                authority_status=authority_status,
                version=tax_invoice.version + 1,
            )
            self._repository.save_tax_invoice(
                issued, expected_version=tax_invoice.version
            )
            audit = self._write_result(
                ctx,
                "Finance.TaxInvoice.Issue",
                TAX_INVOICE_RESOURCE,
                tax_invoice.id,
                "ok",
            )
            return KernelResult.success(issued, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "tax invoice issue conflict"
            )

    def create_tax_rate(
        self,
        ctx: ExecutionContext,
        *,
        tax_code: str,
        tax_name: str,
        rate_percent: Decimal,
    ) -> KernelResult[TaxRate]:
        tax_rate_id = uuid4()
        try:
            self._write_intent(
                ctx, "Finance.TaxRate.Create", TAX_RATE_RESOURCE, tax_rate_id
            )
            denied = self._authorize(ctx, "create", TAX_RATE_RESOURCE)
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.TaxRate.Create",
                    TAX_RATE_RESOURCE,
                    tax_rate_id,
                    denied,
                )
            normalized_code = self._required_tax_code(tax_code)
            normalized_name = self._tax_name(tax_name)
            normalized_rate = self._rate_percent(rate_percent)
            if self._repository.get_tax_rate_by_code(normalized_code) is not None:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "tax rate code already exists",
                )
            now = datetime.now(timezone.utc)
            tax_rate = TaxRate(
                id=tax_rate_id,
                tenant_id=self._tenant_id(ctx),
                tax_code=normalized_code,
                tax_name=normalized_name,
                rate_percent=normalized_rate,
                status=TaxRateStatus.ACTIVE,
                created_at=now,
                updated_at=now,
            )
            self._repository.add_tax_rate(tax_rate)
            audit = self._write_result(
                ctx,
                "Finance.TaxRate.Create",
                TAX_RATE_RESOURCE,
                tax_rate.id,
                "ok",
            )
            return KernelResult.success(tax_rate, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "tax rate create conflict"
            )

    def get_tax_rate(
        self,
        ctx: ExecutionContext,
        *,
        tax_rate_id: UUID,
    ) -> KernelResult[TaxRate]:
        try:
            denied = self._authorize(
                ctx, "read", TAX_RATE_RESOURCE, tax_rate_id
            )
            if denied is not None:
                return denied
            tax_rate = self._repository.get_tax_rate(tax_rate_id)
            if tax_rate is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "tax rate not found"
                )
            return KernelResult.success(tax_rate)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_tax_rate_by_code(
        self,
        ctx: ExecutionContext,
        *,
        tax_code: str,
    ) -> KernelResult[TaxRate]:
        try:
            denied = self._authorize(ctx, "read", TAX_RATE_RESOURCE)
            if denied is not None:
                return denied
            tax_rate = self._repository.get_tax_rate_by_code(
                self._required_tax_code(tax_code)
            )
            if tax_rate is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "tax rate not found"
                )
            return KernelResult.success(tax_rate)
        except KernelError as err:
            return KernelResult.from_error(err)

    def archive_tax_rate(
        self,
        ctx: ExecutionContext,
        *,
        tax_rate_id: UUID,
        expected_version: int,
    ) -> KernelResult[TaxRate]:
        try:
            self._write_intent(
                ctx, "Finance.TaxRate.Archive", TAX_RATE_RESOURCE, tax_rate_id
            )
            denied = self._authorize(
                ctx, "archive", TAX_RATE_RESOURCE, tax_rate_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.TaxRate.Archive",
                    TAX_RATE_RESOURCE,
                    tax_rate_id,
                    denied,
                )
            current = self._repository.get_tax_rate(tax_rate_id)
            if current is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "tax rate not found"
                )
            if current.version != expected_version:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT, "tax rate version conflict"
                )
            if current.status == TaxRateStatus.ARCHIVED:
                audit = self._write_result(
                    ctx,
                    "Finance.TaxRate.Archive",
                    TAX_RATE_RESOURCE,
                    current.id,
                    "ok",
                )
                return KernelResult.success(current, audit_id=audit.id)
            archived = replace(
                current,
                status=TaxRateStatus.ARCHIVED,
                updated_at=datetime.now(timezone.utc),
                version=current.version + 1,
            )
            self._repository.save_tax_rate(
                archived, expected_version=current.version
            )
            audit = self._write_result(
                ctx,
                "Finance.TaxRate.Archive",
                TAX_RATE_RESOURCE,
                archived.id,
                "ok",
            )
            return KernelResult.success(archived, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "tax rate version conflict"
            )

    def get_tax_authority_policy(
        self, ctx: ExecutionContext
    ) -> KernelResult[TenantTaxAuthorityPolicy]:
        try:
            denied = self._authorize(ctx, "read", TAX_AUTHORITY_POLICY_RESOURCE)
            if denied is not None:
                return denied
            return KernelResult.success(
                self._tax_authority_policy_or_default(ctx)
            )
        except KernelError as err:
            return KernelResult.from_error(err)

    def set_tax_authority_policy(
        self,
        ctx: ExecutionContext,
        *,
        tax_authority_required: bool,
        expected_version: int,
    ) -> KernelResult[TenantTaxAuthorityPolicy]:
        try:
            tenant_id = self._tenant_id(ctx)
            self._write_intent(
                ctx,
                "Finance.Policy.TaxAuthority.Set",
                TAX_AUTHORITY_POLICY_RESOURCE,
                tenant_id,
            )
            denied = self._authorize(
                ctx, "update", TAX_AUTHORITY_POLICY_RESOURCE
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.Policy.TaxAuthority.Set",
                    TAX_AUTHORITY_POLICY_RESOURCE,
                    tenant_id,
                    denied,
                )
            current = self._repository.get_tax_authority_policy()
            if current is None:
                if expected_version != 0:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "tax authority policy version conflict",
                    )
                version = 1
            else:
                if current.version != expected_version:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "tax authority policy version conflict",
                    )
                version = current.version + 1
            policy = TenantTaxAuthorityPolicy(
                tenant_id=tenant_id,
                tax_authority_required=bool(tax_authority_required),
                updated_at=datetime.now(timezone.utc),
                version=version,
            )
            self._repository.save_tax_authority_policy(
                policy, expected_version=expected_version
            )
            audit = self._write_result(
                ctx,
                "Finance.Policy.TaxAuthority.Set",
                TAX_AUTHORITY_POLICY_RESOURCE,
                tenant_id,
                "ok",
            )
            return KernelResult.success(policy, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT,
                "tax authority policy version conflict",
            )

    def void_tax_invoice(
        self,
        ctx: ExecutionContext,
        *,
        tax_invoice_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
        reason: str,
    ) -> KernelResult[TaxInvoice]:
        try:
            self._write_intent(
                ctx,
                "Finance.TaxInvoice.Void",
                TAX_INVOICE_RESOURCE,
                tax_invoice_id,
            )
            denied = self._authorize(
                ctx, "void", TAX_INVOICE_RESOURCE, tax_invoice_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.TaxInvoice.Void",
                    TAX_INVOICE_RESOURCE,
                    tax_invoice_id,
                    denied,
                )
            tax_invoice = self._repository.get_tax_invoice(tax_invoice_id)
            if tax_invoice is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "tax invoice not found"
                )
            if tax_invoice.status == TaxInvoiceStatus.VOIDED:
                if tax_invoice.void_key != idempotency_key:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "tax invoice is already voided",
                    )
                audit = self._write_result(
                    ctx,
                    "Finance.TaxInvoice.Void",
                    TAX_INVOICE_RESOURCE,
                    tax_invoice.id,
                    "ok",
                )
                return KernelResult.success(tax_invoice, audit_id=audit.id)
            if tax_invoice.status != TaxInvoiceStatus.ISSUED:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "only issued tax invoices can be voided",
                )
            if human_confirm is not True:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required to void",
                )
            normalized_reason = (
                reason.strip() if isinstance(reason, str) else ""
            )
            if not normalized_reason or len(normalized_reason) > 500:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "void reason is required",
                )
            voided = replace(
                tax_invoice,
                status=TaxInvoiceStatus.VOIDED,
                voided_at=datetime.now(timezone.utc),
                void_key=idempotency_key,
                void_reason=normalized_reason,
                version=tax_invoice.version + 1,
            )
            self._repository.save_tax_invoice(
                voided, expected_version=tax_invoice.version
            )
            audit = self._write_result(
                ctx,
                "Finance.TaxInvoice.Void",
                TAX_INVOICE_RESOURCE,
                tax_invoice.id,
                "ok",
            )
            return KernelResult.success(voided, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "tax invoice void conflict"
            )

    def get_tax_invoice(
        self,
        ctx: ExecutionContext,
        *,
        tax_invoice_id: UUID,
    ) -> KernelResult[TaxInvoice]:
        try:
            denied = self._authorize(
                ctx, "read", TAX_INVOICE_RESOURCE, tax_invoice_id
            )
            if denied is not None:
                return denied
            tax_invoice = self._repository.get_tax_invoice(tax_invoice_id)
            if tax_invoice is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "tax invoice not found"
                )
            return KernelResult.success(tax_invoice)
        except KernelError as err:
            return KernelResult.from_error(err)

    def accrue_commission(
        self,
        ctx: ExecutionContext,
        *,
        invoice_id: UUID,
        beneficiary_subject_id: UUID,
        amount: Decimal,
        currency: str,
        idempotency_key: UUID,
    ) -> KernelResult[CommissionEntry]:
        entry_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "Finance.Commission.Accrue",
                COMMISSION_RESOURCE,
                entry_id,
            )
            denied = self._authorize(
                ctx, "create", COMMISSION_RESOURCE, invoice_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.Commission.Accrue",
                    COMMISSION_RESOURCE,
                    entry_id,
                    denied,
                )
            normalized_amount = self._amount(amount)
            normalized_currency = self._currency(currency)
            existing = self._repository.get_commission_by_idempotency_key(
                idempotency_key
            )
            if existing is not None:
                if (
                    existing.source_invoice_id != invoice_id
                    or existing.beneficiary_subject_id != beneficiary_subject_id
                    or existing.amount != normalized_amount
                    or existing.currency != normalized_currency
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "commission idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx,
                    "Finance.Commission.Accrue",
                    COMMISSION_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            duplicate = self._repository.get_commission_by_invoice_beneficiary(
                invoice_id, beneficiary_subject_id
            )
            if duplicate is not None:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "commission already accrued for invoice beneficiary",
                )
            if normalized_amount <= 0:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "commission amount must be positive",
                )
            invoice = self._ar_invoice_reader.get_ar_invoice_snapshot(
                invoice_id
            )
            if invoice is None or invoice.tenant_id != self._tenant_id(ctx):
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "AR invoice not found"
                )
            if invoice.status != "issued":
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "AR invoice must be issued",
                )
            if normalized_currency != invoice.currency:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "commission currency must match AR invoice",
                )
            if (
                self._beneficiary_eligibility is not None
                and not self._beneficiary_eligibility.is_eligible(
                    subject_id=beneficiary_subject_id,
                    tenant_id=self._tenant_id(ctx),
                )
            ):
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "commission beneficiary is not eligible",
                )
            entry = CommissionEntry(
                id=entry_id,
                tenant_id=self._tenant_id(ctx),
                source_invoice_id=invoice.id,
                beneficiary_subject_id=beneficiary_subject_id,
                code=f"COMM-{entry_id.hex[:12].upper()}",
                currency=normalized_currency,
                amount=normalized_amount,
                idempotency_key=idempotency_key,
                status=CommissionStatus.ACCRUED,
                created_at=datetime.now(timezone.utc),
            )
            self._repository.add_commission(entry)
            audit = self._write_result(
                ctx,
                "Finance.Commission.Accrue",
                COMMISSION_RESOURCE,
                entry.id,
                "ok",
            )
            return KernelResult.success(entry, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "commission accrue conflict"
            )

    def get_commission(
        self,
        ctx: ExecutionContext,
        *,
        commission_id: UUID,
    ) -> KernelResult[CommissionEntry]:
        try:
            denied = self._authorize(
                ctx, "read", COMMISSION_RESOURCE, commission_id
            )
            if denied is not None:
                return denied
            entry = self._repository.get_commission(commission_id)
            if entry is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "commission entry not found"
                )
            return KernelResult.success(entry)
        except KernelError as err:
            return KernelResult.from_error(err)

    def mark_commission_payable(
        self,
        ctx: ExecutionContext,
        *,
        commission_id: UUID,
    ) -> KernelResult[CommissionEntry]:
        return self._transition_commission(
            ctx,
            commission_id=commission_id,
            expected_status=CommissionStatus.ACCRUED,
            target_status=CommissionStatus.PAYABLE,
            action="Finance.Commission.MarkPayable",
        )

    def mark_commission_paid(
        self,
        ctx: ExecutionContext,
        *,
        commission_id: UUID,
    ) -> KernelResult[CommissionEntry]:
        return self._transition_commission(
            ctx,
            commission_id=commission_id,
            expected_status=CommissionStatus.PAYABLE,
            target_status=CommissionStatus.PAID,
            action="Finance.Commission.MarkPaid",
        )

    def _transition_commission(
        self,
        ctx: ExecutionContext,
        *,
        commission_id: UUID,
        expected_status: CommissionStatus,
        target_status: CommissionStatus,
        action: str,
    ) -> KernelResult[CommissionEntry]:
        try:
            self._write_intent(ctx, action, COMMISSION_RESOURCE, commission_id)
            denied = self._authorize(
                ctx, "update", COMMISSION_RESOURCE, commission_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx, action, COMMISSION_RESOURCE, commission_id, denied
                )
            entry = self._repository.get_commission(commission_id)
            if entry is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "commission entry not found"
                )
            if entry.status != expected_status:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    f"commission must be {expected_status.value} before "
                    f"marking {target_status.value}",
                )
            transitioned = replace(
                entry,
                status=target_status,
                version=entry.version + 1,
            )
            self._repository.save_commission(
                transitioned, expected_version=entry.version
            )
            audit = self._write_result(
                ctx, action, COMMISSION_RESOURCE, entry.id, "ok"
            )
            return KernelResult.success(transitioned, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "commission transition conflict"
            )

    def create_gl_account(
        self,
        ctx: ExecutionContext,
        *,
        code: str,
        name: str,
        account_type: str,
    ) -> KernelResult[GlAccount]:
        account_id = uuid4()
        try:
            self._write_intent(
                ctx, "Finance.GlAccount.Create", GL_ACCOUNT_RESOURCE, account_id
            )
            denied = self._authorize(ctx, "create", GL_ACCOUNT_RESOURCE)
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.GlAccount.Create",
                    GL_ACCOUNT_RESOURCE,
                    account_id,
                    denied,
                )
            normalized_code = self._gl_account_code(code)
            normalized_name = self._gl_account_name(name)
            normalized_type = self._gl_account_type(account_type)
            if self._repository.get_gl_account_by_code(normalized_code) is not None:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "gl account code already exists",
                )
            account = GlAccount(
                id=account_id,
                tenant_id=self._tenant_id(ctx),
                code=normalized_code,
                name=normalized_name,
                account_type=normalized_type,
                status=GlAccountStatus.ACTIVE,
                created_at=datetime.now(timezone.utc),
            )
            self._repository.add_gl_account(account)
            audit = self._write_result(
                ctx,
                "Finance.GlAccount.Create",
                GL_ACCOUNT_RESOURCE,
                account.id,
                "ok",
            )
            return KernelResult.success(account, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "gl account create conflict"
            )

    def get_gl_account(
        self,
        ctx: ExecutionContext,
        *,
        account_id: UUID,
    ) -> KernelResult[GlAccount]:
        try:
            denied = self._authorize(
                ctx, "read", GL_ACCOUNT_RESOURCE, account_id
            )
            if denied is not None:
                return denied
            account = self._repository.get_gl_account(account_id)
            if account is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "gl account not found"
                )
            return KernelResult.success(account)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_gl_account_by_code(
        self,
        ctx: ExecutionContext,
        *,
        code: str,
    ) -> KernelResult[GlAccount]:
        try:
            denied = self._authorize(ctx, "read", GL_ACCOUNT_RESOURCE)
            if denied is not None:
                return denied
            account = self._repository.get_gl_account_by_code(
                self._gl_account_code(code)
            )
            if account is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "gl account not found"
                )
            return KernelResult.success(account)
        except KernelError as err:
            return KernelResult.from_error(err)

    def archive_gl_account(
        self,
        ctx: ExecutionContext,
        *,
        account_id: UUID,
        expected_version: int,
    ) -> KernelResult[GlAccount]:
        try:
            self._write_intent(
                ctx,
                "Finance.GlAccount.Archive",
                GL_ACCOUNT_RESOURCE,
                account_id,
            )
            denied = self._authorize(
                ctx, "archive", GL_ACCOUNT_RESOURCE, account_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.GlAccount.Archive",
                    GL_ACCOUNT_RESOURCE,
                    account_id,
                    denied,
                )
            current = self._repository.get_gl_account(account_id)
            if current is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "gl account not found"
                )
            if current.version != expected_version:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT, "gl account version conflict"
                )
            if current.status == GlAccountStatus.ARCHIVED:
                audit = self._write_result(
                    ctx,
                    "Finance.GlAccount.Archive",
                    GL_ACCOUNT_RESOURCE,
                    current.id,
                    "ok",
                )
                return KernelResult.success(current, audit_id=audit.id)
            archived = replace(
                current,
                status=GlAccountStatus.ARCHIVED,
                version=current.version + 1,
            )
            self._repository.save_gl_account(
                archived, expected_version=current.version
            )
            audit = self._write_result(
                ctx,
                "Finance.GlAccount.Archive",
                GL_ACCOUNT_RESOURCE,
                archived.id,
                "ok",
            )
            return KernelResult.success(archived, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "gl account version conflict"
            )

    def create_gl_period(
        self,
        ctx: ExecutionContext,
        *,
        code: str,
        start_at: datetime,
        end_at: datetime,
        name: str | None = None,
    ) -> KernelResult[GlPeriod]:
        period_id = uuid4()
        try:
            self._write_intent(
                ctx, "Finance.GlPeriod.Create", GL_PERIOD_RESOURCE, period_id
            )
            denied = self._authorize(ctx, "create", GL_PERIOD_RESOURCE)
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.GlPeriod.Create",
                    GL_PERIOD_RESOURCE,
                    period_id,
                    denied,
                )
            normalized_code = self._gl_period_code(code)
            normalized_name = self._gl_period_name(
                name if name is not None else normalized_code
            )
            normalized_start, normalized_end = self._gl_period_bounds(
                start_at, end_at
            )
            if self._repository.get_gl_period_by_code(normalized_code) is not None:
                raise KernelError(
                ErrorCode.COMMON_CONFLICT,
                    "gl period code already exists",
                )
            for existing in self._repository.list_gl_periods():
                if (
                    normalized_start < existing.end_at
                    and normalized_end > existing.start_at
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "gl period overlaps an existing period",
                    )
            period = GlPeriod(
                id=period_id,
                tenant_id=self._tenant_id(ctx),
                code=normalized_code,
                name=normalized_name,
                start_at=normalized_start,
                end_at=normalized_end,
                status=GlPeriodStatus.OPEN,
                created_at=datetime.now(timezone.utc),
            )
            self._repository.add_gl_period(period)
            audit = self._write_result(
                ctx,
                "Finance.GlPeriod.Create",
                GL_PERIOD_RESOURCE,
                period.id,
                "ok",
            )
            return KernelResult.success(period, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "gl period create conflict"
            )

    def get_gl_period(
        self,
        ctx: ExecutionContext,
        *,
        period_id: UUID,
    ) -> KernelResult[GlPeriod]:
        try:
            denied = self._authorize(
                ctx, "read", GL_PERIOD_RESOURCE, period_id
            )
            if denied is not None:
                return denied
            period = self._repository.get_gl_period(period_id)
            if period is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "gl period not found"
                )
            return KernelResult.success(period)
        except KernelError as err:
            return KernelResult.from_error(err)

    def get_gl_period_by_code(
        self,
        ctx: ExecutionContext,
        *,
        code: str,
    ) -> KernelResult[GlPeriod]:
        try:
            denied = self._authorize(ctx, "read", GL_PERIOD_RESOURCE)
            if denied is not None:
                return denied
            period = self._repository.get_gl_period_by_code(
                self._gl_period_code(code)
            )
            if period is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "gl period not found"
                )
            return KernelResult.success(period)
        except KernelError as err:
            return KernelResult.from_error(err)

    def close_gl_period(
        self,
        ctx: ExecutionContext,
        *,
        period_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
    ) -> KernelResult[GlPeriod]:
        try:
            self._write_intent(
                ctx, "Finance.GlPeriod.Close", GL_PERIOD_RESOURCE, period_id
            )
            denied = self._authorize(
                ctx, "close", GL_PERIOD_RESOURCE, period_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.GlPeriod.Close",
                    GL_PERIOD_RESOURCE,
                    period_id,
                    denied,
                )
            period = self._repository.get_gl_period(period_id)
            if period is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "gl period not found"
                )
            if period.status == GlPeriodStatus.CLOSED:
                if period.close_key == idempotency_key:
                    audit = self._write_result(
                        ctx,
                        "Finance.GlPeriod.Close",
                        GL_PERIOD_RESOURCE,
                        period.id,
                        "ok",
                    )
                    return KernelResult.success(period, audit_id=audit.id)
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "gl period is already closed",
                )
            if period.status != GlPeriodStatus.OPEN:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "gl period cannot be closed",
                )
            if human_confirm is not True:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required to close",
                )
            closed = replace(
                period,
                status=GlPeriodStatus.CLOSED,
                closed_at=datetime.now(timezone.utc),
                close_key=idempotency_key,
                version=period.version + 1,
            )
            self._repository.save_gl_period(
                closed, expected_version=period.version
            )
            audit = self._write_result(
                ctx,
                "Finance.GlPeriod.Close",
                GL_PERIOD_RESOURCE,
                closed.id,
                "ok",
            )
            return KernelResult.success(closed, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "gl period version conflict"
            )

    def create_journal_entry(
        self,
        ctx: ExecutionContext,
        *,
        currency: str,
        period_id: UUID,
        lines: list[dict],
        idempotency_key: UUID,
        memo: str | None = None,
    ) -> KernelResult[JournalEntry]:
        entry_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "Finance.JournalEntry.Create",
                JOURNAL_ENTRY_RESOURCE,
                entry_id,
            )
            denied = self._authorize(ctx, "create", JOURNAL_ENTRY_RESOURCE)
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.JournalEntry.Create",
                    JOURNAL_ENTRY_RESOURCE,
                    entry_id,
                    denied,
                )
            existing = self._repository.get_journal_entry_by_idempotency_key(
                idempotency_key
            )
            normalized_currency = self._currency(currency)
            normalized_memo = self._optional_memo(memo)
            normalized_lines = self._journal_lines(lines)
            if existing is not None:
                if (
                    existing.currency != normalized_currency
                    or existing.period_id != period_id
                    or existing.memo != normalized_memo
                    or not self._journal_lines_match(
                        existing.lines, normalized_lines
                    )
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "journal entry idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx,
                    "Finance.JournalEntry.Create",
                    JOURNAL_ENTRY_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            period = self._repository.get_gl_period(period_id)
            if period is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "gl period not found"
                )
            if period.status != GlPeriodStatus.OPEN:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "gl period is not open",
                )
            for line in normalized_lines:
                account = self._repository.get_gl_account(line.account_id)
                if account is None:
                    raise KernelError(
                        ErrorCode.COMMON_NOT_FOUND, "gl account not found"
                    )
            entry = JournalEntry(
                id=entry_id,
                tenant_id=self._tenant_id(ctx),
                code=f"JE-{entry_id.hex[:12].upper()}",
                currency=normalized_currency,
                period_id=period_id,
                memo=normalized_memo,
                idempotency_key=idempotency_key,
                status=JournalEntryStatus.DRAFT,
                created_at=datetime.now(timezone.utc),
                lines=normalized_lines,
            )
            self._repository.add_journal_entry(entry)
            audit = self._write_result(
                ctx,
                "Finance.JournalEntry.Create",
                JOURNAL_ENTRY_RESOURCE,
                entry.id,
                "ok",
            )
            return KernelResult.success(entry, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "journal entry create conflict"
            )

    def get_journal_entry(
        self,
        ctx: ExecutionContext,
        *,
        entry_id: UUID,
    ) -> KernelResult[JournalEntry]:
        try:
            denied = self._authorize(
                ctx, "read", JOURNAL_ENTRY_RESOURCE, entry_id
            )
            if denied is not None:
                return denied
            entry = self._repository.get_journal_entry(entry_id)
            if entry is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "journal entry not found"
                )
            return KernelResult.success(entry)
        except KernelError as err:
            return KernelResult.from_error(err)

    def post_journal_entry(
        self,
        ctx: ExecutionContext,
        *,
        entry_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
    ) -> KernelResult[JournalEntry]:
        try:
            self._write_intent(
                ctx,
                "Finance.JournalEntry.Post",
                JOURNAL_ENTRY_RESOURCE,
                entry_id,
            )
            denied = self._authorize(
                ctx, "post", JOURNAL_ENTRY_RESOURCE, entry_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.JournalEntry.Post",
                    JOURNAL_ENTRY_RESOURCE,
                    entry_id,
                    denied,
                )
            entry = self._repository.get_journal_entry(entry_id)
            if entry is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "journal entry not found"
                )
            if entry.status == JournalEntryStatus.POSTED:
                if entry.post_key == idempotency_key:
                    audit = self._write_result(
                        ctx,
                        "Finance.JournalEntry.Post",
                        JOURNAL_ENTRY_RESOURCE,
                        entry.id,
                        "ok",
                    )
                    return KernelResult.success(entry, audit_id=audit.id)
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "journal entry is already posted",
                )
            if entry.status != JournalEntryStatus.DRAFT:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "journal entry cannot be posted",
                )
            if human_confirm is not True:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required to post",
                )
            period = self._repository.get_gl_period(entry.period_id)
            if period is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "gl period not found"
                )
            if period.status != GlPeriodStatus.OPEN:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "gl period is closed",
                )
            for line in entry.lines:
                account = self._repository.get_gl_account(line.account_id)
                if account is None:
                    raise KernelError(
                        ErrorCode.COMMON_NOT_FOUND, "gl account not found"
                    )
                if account.status != GlAccountStatus.ACTIVE:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "gl account is not active",
                    )
            posted = replace(
                entry,
                status=JournalEntryStatus.POSTED,
                posted_at=datetime.now(timezone.utc),
                post_key=idempotency_key,
                version=entry.version + 1,
            )
            self._repository.save_journal_entry(
                posted, expected_version=entry.version
            )
            audit = self._write_result(
                ctx,
                "Finance.JournalEntry.Post",
                JOURNAL_ENTRY_RESOURCE,
                entry.id,
                "ok",
            )
            return KernelResult.success(posted, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "journal entry post conflict"
            )

    def get_gl_bridge_map(
        self, ctx: ExecutionContext
    ) -> KernelResult[GlBridgeMap]:
        try:
            denied = self._authorize(ctx, "read", GL_BRIDGE_RESOURCE)
            if denied is not None:
                return denied
            bridge_map = self._repository.get_gl_bridge_map()
            if bridge_map is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "gl bridge map not found"
                )
            return KernelResult.success(bridge_map)
        except KernelError as err:
            return KernelResult.from_error(err)

    def set_gl_bridge_map(
        self,
        ctx: ExecutionContext,
        *,
        ar_control: UUID,
        cash: UUID,
        revenue: UUID,
        tax_payable: UUID,
        commission_expense: UUID,
        commission_payable: UUID,
        expected_version: int,
        fx_gain: UUID | None = None,
        fx_loss: UUID | None = None,
        ap_control: UUID | None = None,
        ap_expense: UUID | None = None,
    ) -> KernelResult[GlBridgeMap]:
        try:
            tenant_id = self._tenant_id(ctx)
            self._write_intent(
                ctx, "Finance.GlBridgeMap.Set", GL_BRIDGE_RESOURCE, tenant_id
            )
            denied = self._authorize(ctx, "update", GL_BRIDGE_RESOURCE)
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.GlBridgeMap.Set",
                    GL_BRIDGE_RESOURCE,
                    tenant_id,
                    denied,
                )
            roles = {
                "ar_control": ar_control,
                "cash": cash,
                "revenue": revenue,
                "tax_payable": tax_payable,
                "commission_expense": commission_expense,
                "commission_payable": commission_payable,
            }
            if fx_gain is not None:
                roles["fx_gain"] = fx_gain
            if fx_loss is not None:
                roles["fx_loss"] = fx_loss
            if ap_control is not None:
                roles["ap_control"] = ap_control
            if ap_expense is not None:
                roles["ap_expense"] = ap_expense
            for role, account_id in roles.items():
                account = self._repository.get_gl_account(account_id)
                if account is None:
                    raise KernelError(
                        ErrorCode.COMMON_NOT_FOUND,
                        f"gl bridge map account not found: {role}",
                    )
                if account.status != GlAccountStatus.ACTIVE:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        f"gl bridge map account is not active: {role}",
                    )
            current = self._repository.get_gl_bridge_map()
            if current is None:
                if expected_version != 0:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "gl bridge map version conflict",
                    )
                version = 1
            else:
                if current.version != expected_version:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "gl bridge map version conflict",
                    )
                version = current.version + 1
            bridge_map = GlBridgeMap(
                tenant_id=tenant_id,
                ar_control=ar_control,
                cash=cash,
                revenue=revenue,
                tax_payable=tax_payable,
                commission_expense=commission_expense,
                commission_payable=commission_payable,
                fx_gain=fx_gain,
                fx_loss=fx_loss,
                ap_control=ap_control,
                ap_expense=ap_expense,
                updated_at=datetime.now(timezone.utc),
                version=version,
            )
            self._repository.save_gl_bridge_map(
                bridge_map, expected_version=expected_version
            )
            audit = self._write_result(
                ctx,
                "Finance.GlBridgeMap.Set",
                GL_BRIDGE_RESOURCE,
                tenant_id,
                "ok",
            )
            return KernelResult.success(bridge_map, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "gl bridge map version conflict"
            )

    def bridge_ar_invoice_issue(
        self,
        ctx: ExecutionContext,
        *,
        invoice_id: UUID,
        period_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
    ) -> KernelResult[GlBridgePosting]:
        return self._bridge_source(
            ctx,
            source_type=GlBridgeSourceType.AR_INVOICE,
            source_id=invoice_id,
            period_id=period_id,
            idempotency_key=idempotency_key,
            human_confirm=human_confirm,
            action="Finance.GlBridge.ArInvoiceIssue",
        )

    def bridge_ar_receipt_apply(
        self,
        ctx: ExecutionContext,
        *,
        receipt_id: UUID,
        period_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
    ) -> KernelResult[GlBridgePosting]:
        return self._bridge_source(
            ctx,
            source_type=GlBridgeSourceType.AR_RECEIPT,
            source_id=receipt_id,
            period_id=period_id,
            idempotency_key=idempotency_key,
            human_confirm=human_confirm,
            action="Finance.GlBridge.ArReceiptApply",
        )

    def bridge_ap_bill_post(
        self,
        ctx: ExecutionContext,
        *,
        ap_bill_id: UUID,
        period_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool = True,
    ) -> KernelResult[GlBridgePosting]:
        return self._bridge_source(
            ctx,
            source_type=GlBridgeSourceType.AP_BILL,
            source_id=ap_bill_id,
            period_id=period_id,
            idempotency_key=idempotency_key,
            human_confirm=human_confirm,
            action="Finance.GlBridge.ApBillPost",
        )

    def bridge_ap_payment_apply(
        self,
        ctx: ExecutionContext,
        *,
        ap_payment_id: UUID,
        period_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool = True,
    ) -> KernelResult[GlBridgePosting]:
        return self._bridge_source(
            ctx,
            source_type=GlBridgeSourceType.AP_PAYMENT,
            source_id=ap_payment_id,
            period_id=period_id,
            idempotency_key=idempotency_key,
            human_confirm=human_confirm,
            action="Finance.GlBridge.ApPaymentApply",
        )

    def bridge_tax_invoice_issue(
        self,
        ctx: ExecutionContext,
        *,
        tax_invoice_id: UUID,
        period_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
    ) -> KernelResult[GlBridgePosting]:
        return self._bridge_source(
            ctx,
            source_type=GlBridgeSourceType.TAX_INVOICE,
            source_id=tax_invoice_id,
            period_id=period_id,
            idempotency_key=idempotency_key,
            human_confirm=human_confirm,
            action="Finance.GlBridge.TaxInvoiceIssue",
        )

    def bridge_commission_accrue(
        self,
        ctx: ExecutionContext,
        *,
        commission_id: UUID,
        period_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
    ) -> KernelResult[GlBridgePosting]:
        return self._bridge_source(
            ctx,
            source_type=GlBridgeSourceType.COMMISSION,
            source_id=commission_id,
            period_id=period_id,
            idempotency_key=idempotency_key,
            human_confirm=human_confirm,
            action="Finance.GlBridge.CommissionAccrue",
        )

    def bridge_realized_fx(
        self,
        ctx: ExecutionContext,
        *,
        realized_fx_event_id: UUID,
        period_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool = True,
    ) -> KernelResult[GlBridgePosting]:
        return self._bridge_source(
            ctx,
            source_type=GlBridgeSourceType.REALIZED_FX,
            source_id=realized_fx_event_id,
            period_id=period_id,
            idempotency_key=idempotency_key,
            human_confirm=human_confirm,
            action="Finance.GlBridge.RealizedFx",
        )

    def _bridge_source(
        self,
        ctx: ExecutionContext,
        *,
        source_type: GlBridgeSourceType,
        source_id: UUID,
        period_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
        action: str,
    ) -> KernelResult[GlBridgePosting]:
        posting_id = uuid4()
        try:
            self._write_intent(ctx, action, GL_BRIDGE_RESOURCE, posting_id)
            denied = self._authorize(ctx, "bridge", GL_BRIDGE_RESOURCE)
            if denied is not None:
                return self._write_denied(
                    ctx, action, GL_BRIDGE_RESOURCE, posting_id, denied
                )
            if human_confirm is not True:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required to bridge",
                )
            by_key = self._repository.get_gl_bridge_posting_by_idempotency_key(
                idempotency_key
            )
            if by_key is not None:
                if (
                    by_key.source_type != source_type
                    or by_key.source_id != source_id
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "gl bridge idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx, action, GL_BRIDGE_RESOURCE, by_key.id, "ok"
                )
                return KernelResult.success(by_key, audit_id=audit.id)
            by_source = self._repository.get_gl_bridge_posting_by_source(
                source_type, source_id
            )
            if by_source is not None:
                if by_source.idempotency_key != idempotency_key:
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "source already bridged with a different key",
                    )
                audit = self._write_result(
                    ctx, action, GL_BRIDGE_RESOURCE, by_source.id, "ok"
                )
                return KernelResult.success(by_source, audit_id=audit.id)
            period = self._repository.get_gl_period(period_id)
            if period is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "gl period not found"
                )
            if period.status != GlPeriodStatus.OPEN:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT, "gl period is not open"
                )
            bridge_map = self._repository.get_gl_bridge_map()
            if bridge_map is None:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT, "gl bridge map is incomplete"
                )
            currency, amount, lines, memo = self._bridge_journal_parts(
                source_type=source_type,
                source_id=source_id,
                bridge_map=bridge_map,
            )
            now = datetime.now(timezone.utc)
            entry = JournalEntry(
                id=uuid4(),
                tenant_id=self._tenant_id(ctx),
                code=f"JE-{uuid4().hex[:12].upper()}",
                currency=currency,
                period_id=period_id,
                memo=memo,
                idempotency_key=idempotency_key,
                status=JournalEntryStatus.POSTED,
                created_at=now,
                posted_at=now,
                post_key=idempotency_key,
                lines=lines,
            )
            self._repository.add_journal_entry(entry)
            posting = GlBridgePosting(
                id=posting_id,
                tenant_id=self._tenant_id(ctx),
                source_type=source_type,
                source_id=source_id,
                journal_entry_id=entry.id,
                idempotency_key=idempotency_key,
                created_at=now,
            )
            self._repository.add_gl_bridge_posting(posting)
            audit = self._write_result(
                ctx, action, GL_BRIDGE_RESOURCE, posting.id, "ok"
            )
            return KernelResult.success(posting, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "gl bridge conflict"
            )

    def _bridge_journal_parts(
        self,
        *,
        source_type: GlBridgeSourceType,
        source_id: UUID,
        bridge_map: GlBridgeMap,
    ) -> tuple[str, Decimal, list[JournalLine], str]:
        if source_type == GlBridgeSourceType.AR_INVOICE:
            invoice = self._ar_invoice_reader.get_ar_invoice_snapshot(source_id)
            if invoice is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "ar invoice not found"
                )
            if invoice.status != "issued":
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "ar invoice is not issued",
                )
            amount = self._positive_amount(invoice.total_amount)
            lines = [
                JournalLine(
                    id=uuid4(),
                    account_id=bridge_map.ar_control,
                    debit=amount,
                    credit=Decimal("0.00"),
                ),
                JournalLine(
                    id=uuid4(),
                    account_id=bridge_map.revenue,
                    debit=Decimal("0.00"),
                    credit=amount,
                ),
            ]
            return invoice.currency, amount, lines, f"bridge ar_invoice {source_id}"
        if source_type == GlBridgeSourceType.AR_RECEIPT:
            receipt = self._repository.get_receipt(source_id)
            if receipt is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "ar receipt not found"
                )
            if receipt.status != ReceiptStatus.APPLIED:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "ar receipt is not applied",
                )
            amount = self._positive_amount(receipt.amount)
            lines = [
                JournalLine(
                    id=uuid4(),
                    account_id=bridge_map.cash,
                    debit=amount,
                    credit=Decimal("0.00"),
                ),
                JournalLine(
                    id=uuid4(),
                    account_id=bridge_map.ar_control,
                    debit=Decimal("0.00"),
                    credit=amount,
                ),
            ]
            return receipt.currency, amount, lines, f"bridge ar_receipt {source_id}"
        if source_type == GlBridgeSourceType.TAX_INVOICE:
            tax_invoice = self._repository.get_tax_invoice(source_id)
            if tax_invoice is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "tax invoice not found"
                )
            if tax_invoice.status != TaxInvoiceStatus.ISSUED:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "tax invoice is not issued",
                )
            amount = self._positive_amount(tax_invoice.amount)
            lines = [
                JournalLine(
                    id=uuid4(),
                    account_id=bridge_map.ar_control,
                    debit=amount,
                    credit=Decimal("0.00"),
                ),
                JournalLine(
                    id=uuid4(),
                    account_id=bridge_map.tax_payable,
                    debit=Decimal("0.00"),
                    credit=amount,
                ),
            ]
            return (
                tax_invoice.currency,
                amount,
                lines,
                f"bridge tax_invoice {source_id}",
            )
        if source_type == GlBridgeSourceType.COMMISSION:
            commission = self._repository.get_commission(source_id)
            if commission is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "commission not found"
                )
            if commission.status != CommissionStatus.ACCRUED:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "commission is not accrued",
                )
            amount = self._positive_amount(commission.amount)
            lines = [
                JournalLine(
                    id=uuid4(),
                    account_id=bridge_map.commission_expense,
                    debit=amount,
                    credit=Decimal("0.00"),
                ),
                JournalLine(
                    id=uuid4(),
                    account_id=bridge_map.commission_payable,
                    debit=Decimal("0.00"),
                    credit=amount,
                ),
            ]
            return (
                commission.currency,
                amount,
                lines,
                f"bridge commission {source_id}",
            )
        if source_type == GlBridgeSourceType.AP_BILL:
            if bridge_map.ap_control is None or bridge_map.ap_expense is None:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "gl bridge map ap accounts are incomplete",
                )
            if self._ap_bill_reader is None:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT, "ap bill read port is unavailable"
                )
            bill = self._ap_bill_reader.get_ap_bill_snapshot(source_id)
            if bill is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "ap bill not found"
                )
            if bill.status not in {"posted", "partially_paid", "paid"}:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT, "ap bill is not posted"
                )
            amount = self._positive_amount(bill.total_amount)
            lines = [
                JournalLine(
                    id=uuid4(),
                    account_id=bridge_map.ap_expense,
                    debit=amount,
                    credit=Decimal("0.00"),
                ),
                JournalLine(
                    id=uuid4(),
                    account_id=bridge_map.ap_control,
                    debit=Decimal("0.00"),
                    credit=amount,
                ),
            ]
            return bill.currency, amount, lines, f"bridge ap_bill {source_id}"
        if source_type == GlBridgeSourceType.AP_PAYMENT:
            if bridge_map.ap_control is None:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "gl bridge map ap accounts are incomplete",
                )
            if self._ap_payment_reader is None:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "ap payment read port is unavailable",
                )
            payment = self._ap_payment_reader.get_ap_payment_snapshot(source_id)
            if payment is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "ap payment not found"
                )
            if payment.status != "applied":
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT, "ap payment is not applied"
                )
            amount = self._positive_amount(payment.amount)
            lines = [
                JournalLine(
                    id=uuid4(),
                    account_id=bridge_map.ap_control,
                    debit=amount,
                    credit=Decimal("0.00"),
                ),
                JournalLine(
                    id=uuid4(),
                    account_id=bridge_map.cash,
                    debit=Decimal("0.00"),
                    credit=amount,
                ),
            ]
            return payment.currency, amount, lines, f"bridge ap_payment {source_id}"
        if source_type == GlBridgeSourceType.REALIZED_FX:
            if bridge_map.fx_gain is None or bridge_map.fx_loss is None:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "gl bridge map fx accounts are incomplete",
                )
            event = self._repository.get_realized_fx_event(source_id)
            if event is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "realized fx event not found"
                )
            amount = self._positive_amount(event.amount)
            # Convention: gain Dr ar_control / Cr fx_gain;
            # loss Dr fx_loss / Cr ar_control (AR clearing contra).
            if event.side == RealizedFxSide.GAIN:
                lines = [
                    JournalLine(
                        id=uuid4(),
                        account_id=bridge_map.ar_control,
                        debit=amount,
                        credit=Decimal("0.00"),
                    ),
                    JournalLine(
                        id=uuid4(),
                        account_id=bridge_map.fx_gain,
                        debit=Decimal("0.00"),
                        credit=amount,
                    ),
                ]
            else:
                lines = [
                    JournalLine(
                        id=uuid4(),
                        account_id=bridge_map.fx_loss,
                        debit=amount,
                        credit=Decimal("0.00"),
                    ),
                    JournalLine(
                        id=uuid4(),
                        account_id=bridge_map.ar_control,
                        debit=Decimal("0.00"),
                        credit=amount,
                    ),
                ]
            return (
                event.currency,
                amount,
                lines,
                f"bridge realized_fx {source_id}",
            )
        raise KernelError(
            ErrorCode.COMMON_VALIDATION_FAILED,
            "gl bridge source type is invalid",
        )

    def create_fx_revaluation(
        self,
        ctx: ExecutionContext,
        *,
        period_id: UUID,
        from_currency: str,
        to_currency: str,
        amount: Decimal,
        side: str,
        idempotency_key: UUID,
        rate: Decimal | None = None,
    ) -> KernelResult[GlFxRevaluation]:
        revaluation_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "Finance.GlFxRevaluation.Create",
                GL_FX_REVALUATION_RESOURCE,
                revaluation_id,
            )
            denied = self._authorize(
                ctx, "create", GL_FX_REVALUATION_RESOURCE
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.GlFxRevaluation.Create",
                    GL_FX_REVALUATION_RESOURCE,
                    revaluation_id,
                    denied,
                )
            normalized_from = self._currency(from_currency)
            normalized_to = self._currency(to_currency)
            if normalized_from == normalized_to:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "FX currencies must differ",
                )
            normalized_amount = self._positive_amount(amount)
            normalized_side = self._fx_side(side)
            if rate is None:
                resolved_rate = self._fx_rate(
                    self._fx_rate_port.get_rate(
                        from_currency=normalized_from,
                        to_currency=normalized_to,
                    )
                )
            else:
                resolved_rate = self._fx_rate(rate)
            existing = self._repository.get_gl_fx_revaluation_by_idempotency_key(
                idempotency_key
            )
            if existing is not None:
                if (
                    existing.period_id != period_id
                    or existing.from_currency != normalized_from
                    or existing.to_currency != normalized_to
                    or existing.amount != normalized_amount
                    or existing.side != normalized_side
                    or existing.rate != resolved_rate
                ):
                    raise KernelError(
                        ErrorCode.COMMON_CONFLICT,
                        "fx revaluation idempotency key was used for another request",
                    )
                audit = self._write_result(
                    ctx,
                    "Finance.GlFxRevaluation.Create",
                    GL_FX_REVALUATION_RESOURCE,
                    existing.id,
                    "ok",
                )
                return KernelResult.success(existing, audit_id=audit.id)
            period = self._repository.get_gl_period(period_id)
            if period is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "gl period not found"
                )
            if period.status != GlPeriodStatus.OPEN:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT, "gl period is not open"
                )
            bridge_map = self._repository.get_gl_bridge_map()
            if (
                bridge_map is None
                or bridge_map.fx_gain is None
                or bridge_map.fx_loss is None
            ):
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "gl bridge map fx accounts are incomplete",
                )
            revaluation = GlFxRevaluation(
                id=revaluation_id,
                tenant_id=self._tenant_id(ctx),
                period_id=period_id,
                from_currency=normalized_from,
                to_currency=normalized_to,
                rate=resolved_rate,
                amount=normalized_amount,
                side=normalized_side,
                idempotency_key=idempotency_key,
                status=GlFxRevaluationStatus.DRAFT,
                created_at=datetime.now(timezone.utc),
            )
            self._repository.add_gl_fx_revaluation(revaluation)
            audit = self._write_result(
                ctx,
                "Finance.GlFxRevaluation.Create",
                GL_FX_REVALUATION_RESOURCE,
                revaluation.id,
                "ok",
            )
            return KernelResult.success(revaluation, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "fx revaluation create conflict"
            )

    def get_fx_revaluation(
        self,
        ctx: ExecutionContext,
        *,
        revaluation_id: UUID,
    ) -> KernelResult[GlFxRevaluation]:
        try:
            denied = self._authorize(
                ctx, "read", GL_FX_REVALUATION_RESOURCE, revaluation_id
            )
            if denied is not None:
                return denied
            revaluation = self._repository.get_gl_fx_revaluation(revaluation_id)
            if revaluation is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "fx revaluation not found"
                )
            return KernelResult.success(revaluation)
        except KernelError as err:
            return KernelResult.from_error(err)

    def post_fx_revaluation(
        self,
        ctx: ExecutionContext,
        *,
        revaluation_id: UUID,
        idempotency_key: UUID,
        human_confirm: bool,
    ) -> KernelResult[GlFxRevaluation]:
        try:
            self._write_intent(
                ctx,
                "Finance.GlFxRevaluation.Post",
                GL_FX_REVALUATION_RESOURCE,
                revaluation_id,
            )
            denied = self._authorize(
                ctx, "post", GL_FX_REVALUATION_RESOURCE, revaluation_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.GlFxRevaluation.Post",
                    GL_FX_REVALUATION_RESOURCE,
                    revaluation_id,
                    denied,
                )
            revaluation = self._repository.get_gl_fx_revaluation(revaluation_id)
            if revaluation is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "fx revaluation not found"
                )
            if revaluation.status == GlFxRevaluationStatus.POSTED:
                if revaluation.post_key == idempotency_key:
                    audit = self._write_result(
                        ctx,
                        "Finance.GlFxRevaluation.Post",
                        GL_FX_REVALUATION_RESOURCE,
                        revaluation.id,
                        "ok",
                    )
                    return KernelResult.success(revaluation, audit_id=audit.id)
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "fx revaluation is already posted",
                )
            if revaluation.status != GlFxRevaluationStatus.DRAFT:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "fx revaluation cannot be posted",
                )
            if human_confirm is not True:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required to post",
                )
            period = self._repository.get_gl_period(revaluation.period_id)
            if period is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "gl period not found"
                )
            if period.status != GlPeriodStatus.OPEN:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT, "gl period is not open"
                )
            bridge_map = self._repository.get_gl_bridge_map()
            if (
                bridge_map is None
                or bridge_map.fx_gain is None
                or bridge_map.fx_loss is None
                or bridge_map.cash is None
            ):
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "gl bridge map fx accounts are incomplete",
                )
            amount = revaluation.amount
            if revaluation.side == GlFxRevaluationSide.GAIN:
                lines = [
                    JournalLine(
                        id=uuid4(),
                        account_id=bridge_map.cash,
                        debit=amount,
                        credit=Decimal("0.00"),
                    ),
                    JournalLine(
                        id=uuid4(),
                        account_id=bridge_map.fx_gain,
                        debit=Decimal("0.00"),
                        credit=amount,
                    ),
                ]
            else:
                lines = [
                    JournalLine(
                        id=uuid4(),
                        account_id=bridge_map.fx_loss,
                        debit=amount,
                        credit=Decimal("0.00"),
                    ),
                    JournalLine(
                        id=uuid4(),
                        account_id=bridge_map.cash,
                        debit=Decimal("0.00"),
                        credit=amount,
                    ),
                ]
            now = datetime.now(timezone.utc)
            entry = JournalEntry(
                id=uuid4(),
                tenant_id=self._tenant_id(ctx),
                code=f"JE-{uuid4().hex[:12].upper()}",
                currency=revaluation.to_currency,
                period_id=revaluation.period_id,
                memo=f"fx revaluation {revaluation.id}",
                idempotency_key=idempotency_key,
                status=JournalEntryStatus.POSTED,
                created_at=now,
                posted_at=now,
                post_key=idempotency_key,
                lines=lines,
            )
            self._repository.add_journal_entry(entry)
            posted = replace(
                revaluation,
                status=GlFxRevaluationStatus.POSTED,
                journal_entry_id=entry.id,
                posted_at=now,
                post_key=idempotency_key,
                version=revaluation.version + 1,
            )
            self._repository.save_gl_fx_revaluation(
                posted, expected_version=revaluation.version
            )
            audit = self._write_result(
                ctx,
                "Finance.GlFxRevaluation.Post",
                GL_FX_REVALUATION_RESOURCE,
                posted.id,
                "ok",
            )
            return KernelResult.success(posted, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "fx revaluation post conflict"
            )

    def create_bank_statement(
        self,
        ctx: ExecutionContext,
        *,
        account_ref: str,
        statement_date: datetime,
        currency: str,
        lines: list[dict],
    ) -> KernelResult[BankStatement]:
        statement_id = uuid4()
        try:
            self._write_intent(
                ctx,
                "Finance.BankStatement.Create",
                BANK_STATEMENT_RESOURCE,
                statement_id,
            )
            denied = self._authorize(ctx, "create", BANK_STATEMENT_RESOURCE)
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.BankStatement.Create",
                    BANK_STATEMENT_RESOURCE,
                    statement_id,
                    denied,
                )
            normalized_ref = self._account_ref(account_ref)
            normalized_currency = self._currency(currency)
            normalized_date = self._statement_date(statement_date)
            normalized_lines = self._bank_statement_lines(
                statement_id, lines
            )
            statement = BankStatement(
                id=statement_id,
                tenant_id=self._tenant_id(ctx),
                account_ref=normalized_ref,
                statement_date=normalized_date,
                currency=normalized_currency,
                status=BankStatementStatus.OPEN,
                created_at=datetime.now(timezone.utc),
                lines=normalized_lines,
            )
            self._repository.add_bank_statement(statement)
            audit = self._write_result(
                ctx,
                "Finance.BankStatement.Create",
                BANK_STATEMENT_RESOURCE,
                statement.id,
                "ok",
            )
            return KernelResult.success(statement, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "bank statement create conflict"
            )

    def get_bank_statement(
        self,
        ctx: ExecutionContext,
        *,
        statement_id: UUID,
    ) -> KernelResult[BankStatement]:
        try:
            denied = self._authorize(
                ctx, "read", BANK_STATEMENT_RESOURCE, statement_id
            )
            if denied is not None:
                return denied
            statement = self._repository.get_bank_statement(statement_id)
            if statement is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "bank statement not found"
                )
            return KernelResult.success(statement)
        except KernelError as err:
            return KernelResult.from_error(err)

    def match_bank_statement_line(
        self,
        ctx: ExecutionContext,
        *,
        statement_id: UUID,
        line_id: UUID,
        matched_journal_line_id: UUID | None = None,
        matched_receipt_id: UUID | None = None,
    ) -> KernelResult[BankStatement]:
        try:
            self._write_intent(
                ctx,
                "Finance.BankStatement.MatchLine",
                BANK_STATEMENT_RESOURCE,
                statement_id,
            )
            denied = self._authorize(
                ctx, "match", BANK_STATEMENT_RESOURCE, statement_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.BankStatement.MatchLine",
                    BANK_STATEMENT_RESOURCE,
                    statement_id,
                    denied,
                )
            if (matched_journal_line_id is None) == (
                matched_receipt_id is None
            ):
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "exactly one match target is required",
                )
            statement = self._repository.get_bank_statement(statement_id)
            if statement is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "bank statement not found"
                )
            if statement.status != BankStatementStatus.OPEN:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "bank statement is not open",
                )
            target = next(
                (line for line in statement.lines if line.id == line_id),
                None,
            )
            if target is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "bank statement line not found"
                )
            if target.status != BankStatementLineStatus.UNMATCHED:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "bank statement line is already matched",
                )
            if matched_receipt_id is not None:
                receipt = self._repository.get_receipt(matched_receipt_id)
                if receipt is None:
                    raise KernelError(
                        ErrorCode.COMMON_NOT_FOUND, "ar receipt not found"
                    )
            if matched_journal_line_id is not None:
                line = self._repository.get_journal_line(
                    matched_journal_line_id
                )
                if line is None:
                    raise KernelError(
                        ErrorCode.COMMON_NOT_FOUND,
                        "journal line not found",
                    )
            updated_lines = [
                (
                    replace(
                        line,
                        status=BankStatementLineStatus.MATCHED,
                        matched_journal_line_id=matched_journal_line_id,
                        matched_receipt_id=matched_receipt_id,
                    )
                    if line.id == line_id
                    else line
                )
                for line in statement.lines
            ]
            updated = replace(
                statement,
                lines=updated_lines,
                version=statement.version + 1,
            )
            self._repository.save_bank_statement(
                updated, expected_version=statement.version
            )
            audit = self._write_result(
                ctx,
                "Finance.BankStatement.MatchLine",
                BANK_STATEMENT_RESOURCE,
                updated.id,
                "ok",
            )
            return KernelResult.success(updated, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "bank statement match conflict"
            )

    def clear_bank_statement(
        self,
        ctx: ExecutionContext,
        *,
        statement_id: UUID,
        human_confirm: bool,
    ) -> KernelResult[BankStatement]:
        try:
            self._write_intent(
                ctx,
                "Finance.BankStatement.Clear",
                BANK_STATEMENT_RESOURCE,
                statement_id,
            )
            denied = self._authorize(
                ctx, "clear", BANK_STATEMENT_RESOURCE, statement_id
            )
            if denied is not None:
                return self._write_denied(
                    ctx,
                    "Finance.BankStatement.Clear",
                    BANK_STATEMENT_RESOURCE,
                    statement_id,
                    denied,
                )
            if human_confirm is not True:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "human confirmation is required to clear",
                )
            statement = self._repository.get_bank_statement(statement_id)
            if statement is None:
                raise KernelError(
                    ErrorCode.COMMON_NOT_FOUND, "bank statement not found"
                )
            if statement.status == BankStatementStatus.RECONCILED:
                audit = self._write_result(
                    ctx,
                    "Finance.BankStatement.Clear",
                    BANK_STATEMENT_RESOURCE,
                    statement.id,
                    "ok",
                )
                return KernelResult.success(statement, audit_id=audit.id)
            if statement.status != BankStatementStatus.OPEN:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "bank statement cannot be cleared",
                )
            if not statement.lines:
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "bank statement has no lines",
                )
            if any(
                line.status != BankStatementLineStatus.MATCHED
                for line in statement.lines
            ):
                raise KernelError(
                    ErrorCode.COMMON_CONFLICT,
                    "bank statement has unmatched lines",
                )
            cleared_lines = [
                replace(line, status=BankStatementLineStatus.CLEARED)
                for line in statement.lines
            ]
            cleared = replace(
                statement,
                status=BankStatementStatus.RECONCILED,
                cleared_at=datetime.now(timezone.utc),
                lines=cleared_lines,
                version=statement.version + 1,
            )
            self._repository.save_bank_statement(
                cleared, expected_version=statement.version
            )
            audit = self._write_result(
                ctx,
                "Finance.BankStatement.Clear",
                BANK_STATEMENT_RESOURCE,
                cleared.id,
                "ok",
            )
            return KernelResult.success(cleared, audit_id=audit.id)
        except KernelError as err:
            return KernelResult.from_error(err)
        except ValueError:
            return KernelResult.failure(
                ErrorCode.COMMON_CONFLICT, "bank statement clear conflict"
            )

    @staticmethod
    def _account_ref(account_ref: str) -> str:
        if not isinstance(account_ref, str):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "account_ref is invalid"
            )
        normalized = account_ref.strip()
        if not normalized or len(normalized) > 128:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "account_ref is invalid"
            )
        return normalized

    @staticmethod
    def _statement_date(statement_date: datetime) -> datetime:
        if not isinstance(statement_date, datetime):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "statement_date is invalid",
            )
        if statement_date.tzinfo is None:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "statement_date must be timezone-aware",
            )
        return statement_date.astimezone(timezone.utc)

    def _bank_statement_lines(
        self, statement_id: UUID, lines: list[dict]
    ) -> list[BankStatementLine]:
        if not isinstance(lines, list) or not lines:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "bank statement requires at least one line",
            )
        normalized: list[BankStatementLine] = []
        for raw in lines:
            if not isinstance(raw, dict):
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "bank statement line is invalid",
                )
            description = raw.get("description")
            if not isinstance(description, str):
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "bank statement line description is invalid",
                )
            desc = description.strip()
            if not desc or len(desc) > 500:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "bank statement line description is invalid",
                )
            amount = self._amount(Decimal(raw.get("amount", 0)))
            if amount == 0:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "bank statement line amount must be non-zero",
                )
            normalized.append(
                BankStatementLine(
                    id=uuid4(),
                    statement_id=statement_id,
                    amount=amount,
                    description=desc,
                    status=BankStatementLineStatus.UNMATCHED,
                )
            )
        return normalized

    @staticmethod
    def _fx_side(side: str) -> GlFxRevaluationSide:
        if not isinstance(side, str):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "fx side is invalid"
            )
        normalized = side.strip().lower()
        if normalized not in {"gain", "loss"}:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "fx side is invalid"
            )
        return GlFxRevaluationSide(normalized)

    @staticmethod
    def _fx_rate(rate: Decimal) -> Decimal:
        try:
            value = Decimal(rate)
        except (InvalidOperation, TypeError, ValueError) as err:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "fx rate is invalid"
            ) from err
        quantized = value.quantize(FX_RATE_QUANTUM, rounding=ROUND_HALF_UP)
        if quantized <= 0 or quantized > MAX_FX_RATE:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "fx rate is invalid"
            )
        return quantized

    def _cash_event_fx(
        self,
        *,
        currency: str,
        amount: Decimal,
        functional_currency: str | None,
        fx_rate: Decimal | None,
        functional_amount: Decimal | None,
    ) -> tuple[str, Decimal, Decimal]:
        normalized_functional_currency = self._currency(
            functional_currency or currency
        )
        if normalized_functional_currency == currency:
            normalized_fx_rate = (
                Decimal("1.00000000")
                if fx_rate is None
                else self._fx_rate(fx_rate)
            )
            if normalized_fx_rate != Decimal("1.00000000"):
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "same-currency cash event must use fx_rate 1",
                )
            expected_functional_amount = amount
        else:
            if fx_rate is None:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "fx_rate is required when currencies differ",
                )
            normalized_fx_rate = self._fx_rate(fx_rate)
            expected_functional_amount = self._amount(
                amount * normalized_fx_rate
            )
        normalized_functional_amount = (
            expected_functional_amount
            if functional_amount is None
            else self._amount(functional_amount)
        )
        if normalized_functional_amount != expected_functional_amount:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "functional_amount must equal amount multiplied by fx_rate",
            )
        return (
            normalized_functional_currency,
            normalized_fx_rate,
            normalized_functional_amount,
        )

    def _authorize(
        self,
        ctx: ExecutionContext,
        action: str,
        resource_type: str,
        resource_id: UUID | None = None,
    ) -> KernelResult | None:
        tenant_id = self._tenant_id(ctx)
        result = self._permission.evaluate(
            ctx,
            principal_subject_id=ctx.subject_id,
            action=action,
            resource=Resource(
                tenant_id=tenant_id,
                resource_type=resource_type,
                resource_id=resource_id,
            ),
        )
        if not result.ok:
            return result
        decision = result.data
        if decision is None or decision.effect != PermissionEffect.ALLOW:
            return KernelResult.failure(
                ErrorCode.PERMISSION_DENIED,
                "Finance action is denied by Permission",
                details={
                    "reason_code": (
                        decision.reason_code
                        if decision is not None
                        else "PERMISSION_DENIED"
                    )
                },
            )
        return None

    def _issued_invoice(
        self, ctx: ExecutionContext, invoice_id: UUID
    ) -> ARInvoiceSnapshot:
        invoice = self._ar_invoice_reader.get_ar_invoice_snapshot(invoice_id)
        if invoice is None or invoice.tenant_id != self._tenant_id(ctx):
            raise KernelError(ErrorCode.COMMON_NOT_FOUND, "AR invoice not found")
        if invoice.status != "issued":
            raise KernelError(
                ErrorCode.COMMON_CONFLICT, "AR invoice must be issued"
            )
        return invoice

    def _ar_invoice_remaining(self, invoice: ARInvoiceSnapshot) -> Decimal:
        allocations = sum(
            (
                allocation.amount
                for receipt in self._repository.list_receipts_for_customer(
                    invoice.customer_id
                )
                for allocation in self._repository.list_receipt_allocations(receipt.id)
                if allocation.ar_invoice_id == invoice.id
            ),
            Decimal("0.00"),
        )
        write_offs = sum(
            (item.amount for item in self._repository.list_ar_write_offs(invoice.id)),
            Decimal("0.00"),
        )
        return invoice.total_amount - allocations - write_offs

    def _write_intent(
        self,
        ctx: ExecutionContext,
        action: str,
        resource_type: str,
        resource_id: UUID,
    ) -> None:
        self._tenant_id(ctx)
        self._audit.record(
            ctx,
            action=f"{action}.Intent",
            resource=f"{resource_type}:{resource_id}",
            result="attempted",
            details={},
        )

    def _write_result(
        self,
        ctx: ExecutionContext,
        action: str,
        resource_type: str,
        resource_id: UUID,
        result: str,
    ):
        return self._audit.record(
            ctx,
            action=action,
            resource=f"{resource_type}:{resource_id}",
            result=result,
            details={},
        )

    def _write_denied(
        self,
        ctx: ExecutionContext,
        action: str,
        resource_type: str,
        resource_id: UUID,
        denied: KernelResult,
    ) -> KernelResult:
        audit = self._write_result(
            ctx, action, resource_type, resource_id, "denied"
        )
        return KernelResult.failure(
            denied.error_code or ErrorCode.PERMISSION_DENIED,
            denied.error_message or "Finance action is denied by Permission",
            details=denied.details,
            audit_id=audit.id,
        )

    @staticmethod
    def _tenant_id(ctx: ExecutionContext) -> UUID:
        require_context(ctx)
        if ctx.tenant_id is None or ctx.platform_scope:
            raise KernelError(
                ErrorCode.CTX_INVALID,
                "Finance requires a tenant data-plane context",
            )
        return ctx.tenant_id

    def _receipt_psp_policy_or_default(
        self, ctx: ExecutionContext
    ) -> TenantReceiptPspPolicy:
        return self._repository.get_receipt_psp_policy() or TenantReceiptPspPolicy(
            tenant_id=self._tenant_id(ctx),
            receipt_psp_required=False,
            updated_at=datetime.now(timezone.utc),
            version=0,
        )

    def _tax_authority_policy_or_default(
        self, ctx: ExecutionContext
    ) -> TenantTaxAuthorityPolicy:
        return self._repository.get_tax_authority_policy() or (
            TenantTaxAuthorityPolicy(
                tenant_id=self._tenant_id(ctx),
                tax_authority_required=False,
                updated_at=datetime.now(timezone.utc),
                version=0,
            )
        )

    @staticmethod
    def _optional_tax_code(tax_code: str | None) -> str | None:
        if tax_code is None:
            return None
        return FinanceService._required_tax_code(tax_code)

    @staticmethod
    def _required_tax_code(tax_code: str) -> str:
        if not isinstance(tax_code, str):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "tax_code is invalid"
            )
        normalized = tax_code.strip()
        if not normalized or len(normalized) > 64:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "tax_code is invalid"
            )
        return normalized

    @staticmethod
    def _tax_name(tax_name: str) -> str:
        if not isinstance(tax_name, str):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "tax_name is invalid"
            )
        normalized = tax_name.strip()
        if not normalized or len(normalized) > 128:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "tax_name is invalid"
            )
        return normalized

    @staticmethod
    def _rate_percent(rate_percent: Decimal) -> Decimal:
        try:
            value = Decimal(rate_percent)
        except (InvalidOperation, TypeError, ValueError) as err:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "rate_percent is invalid",
            ) from err
        quantized = value.quantize(
            RATE_PERCENT_QUANTUM, rounding=ROUND_HALF_UP
        )
        if quantized < 0 or quantized > MAX_RATE_PERCENT:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "rate_percent is invalid",
            )
        return quantized

    @staticmethod
    def _currency(currency: str) -> str:
        normalized = currency.strip().upper()
        if len(normalized) != 3 or not normalized.isalpha():
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "currency must be a 3-letter ISO code",
            )
        return normalized

    @staticmethod
    def _amount(amount: Decimal) -> Decimal:
        try:
            value = Decimal(amount)
        except (InvalidOperation, TypeError, ValueError) as err:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "amount is invalid",
            ) from err
        quantized = value.quantize(AMOUNT_QUANTUM, rounding=ROUND_HALF_UP)
        if quantized > MAX_AMOUNT:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "amount exceeds maximum",
            )
        return quantized

    @staticmethod
    def _gl_account_code(code: str) -> str:
        if not isinstance(code, str):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "gl account code is invalid"
            )
        normalized = code.strip()
        if not normalized or len(normalized) > 64:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "gl account code is invalid"
            )
        return normalized

    @staticmethod
    def _gl_account_name(name: str) -> str:
        if not isinstance(name, str):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "gl account name is invalid"
            )
        normalized = name.strip()
        if not normalized or len(normalized) > 128:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "gl account name is invalid"
            )
        return normalized

    @staticmethod
    def _gl_period_code(code: str) -> str:
        if not isinstance(code, str):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "gl period code is invalid"
            )
        normalized = code.strip()
        if not normalized or len(normalized) > 64:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "gl period code is invalid"
            )
        return normalized

    @staticmethod
    def _gl_period_name(name: str) -> str:
        if not isinstance(name, str):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "gl period name is invalid"
            )
        normalized = name.strip()
        if not normalized or len(normalized) > 128:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "gl period name is invalid"
            )
        return normalized

    @staticmethod
    def _gl_period_bounds(
        start_at: datetime, end_at: datetime
    ) -> tuple[datetime, datetime]:
        if not isinstance(start_at, datetime) or not isinstance(end_at, datetime):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "gl period bounds are invalid",
            )
        if start_at.tzinfo is None or end_at.tzinfo is None:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "gl period bounds must be timezone-aware",
            )
        normalized_start = start_at.astimezone(timezone.utc)
        normalized_end = end_at.astimezone(timezone.utc)
        if normalized_start >= normalized_end:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "gl period start_at must be before end_at",
            )
        return normalized_start, normalized_end

    @staticmethod
    def _gl_account_type(account_type: str) -> GlAccountType:
        if not isinstance(account_type, str):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "gl account type is invalid",
            )
        normalized = account_type.strip().lower()
        if normalized not in _GL_ACCOUNT_TYPES:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "gl account type is invalid",
            )
        return GlAccountType(normalized)

    @staticmethod
    def _optional_memo(memo: str | None) -> str | None:
        if memo is None:
            return None
        if not isinstance(memo, str):
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "memo is invalid"
            )
        normalized = memo.strip()
        if not normalized:
            return None
        if len(normalized) > 500:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED, "memo is invalid"
            )
        return normalized

    @staticmethod
    def _positive_amount(amount: Decimal) -> Decimal:
        quantized = FinanceService._amount(amount)
        if quantized <= 0:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "amount must be positive",
            )
        return quantized

    def _journal_lines(self, lines: list[dict]) -> list[JournalLine]:
        if not isinstance(lines, list) or len(lines) < 2:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "journal entry requires at least two lines",
            )
        normalized: list[JournalLine] = []
        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")
        for raw in lines:
            if not isinstance(raw, dict):
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "journal line is invalid",
                )
            account_id = raw.get("account_id")
            if not isinstance(account_id, UUID):
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "journal line account_id is invalid",
                )
            debit_raw = raw.get("debit", Decimal("0"))
            credit_raw = raw.get("credit", Decimal("0"))
            try:
                debit_value = Decimal(debit_raw)
                credit_value = Decimal(credit_raw)
            except (InvalidOperation, TypeError, ValueError) as err:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "journal line amount is invalid",
                ) from err
            debit = self._amount(debit_value)
            credit = self._amount(credit_value)
            if debit < 0 or credit < 0:
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "journal line amounts must be non-negative",
                )
            if (debit > 0 and credit > 0) or (debit == 0 and credit == 0):
                raise KernelError(
                    ErrorCode.COMMON_VALIDATION_FAILED,
                    "journal line must have exactly one of debit or credit",
                )
            if debit > 0:
                debit = self._positive_amount(debit)
            if credit > 0:
                credit = self._positive_amount(credit)
            total_debit += debit
            total_credit += credit
            normalized.append(
                JournalLine(
                    id=uuid4(),
                    account_id=account_id,
                    debit=debit,
                    credit=credit,
                )
            )
        if total_debit != total_credit:
            raise KernelError(
                ErrorCode.COMMON_VALIDATION_FAILED,
                "journal entry must be balanced",
            )
        return normalized

    @staticmethod
    def _journal_lines_match(
        left: list[JournalLine], right: list[JournalLine]
    ) -> bool:
        if len(left) != len(right):
            return False
        return all(
            a.account_id == b.account_id
            and a.debit == b.debit
            and a.credit == b.credit
            for a, b in zip(left, right, strict=True)
        )
