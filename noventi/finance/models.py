"""Finance-owned AR Receipt, Credit Note, Commission, Tax, and GL models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID


class ReceiptStatus(StrEnum):
    DRAFT = "draft"
    APPLIED = "applied"


class CreditNoteStatus(StrEnum):
    DRAFT = "draft"
    ISSUED = "issued"


class ARRefundStatus(StrEnum):
    DRAFT = "draft"
    POSTED = "posted"


class TreasuryTransferStatus(StrEnum):
    DRAFT = "draft"
    POSTED = "posted"


class TaxInvoiceStatus(StrEnum):
    DRAFT = "draft"
    ISSUED = "issued"
    VOIDED = "voided"


class TaxRateStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class GlAccountType(StrEnum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class GlAccountStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class JournalEntryStatus(StrEnum):
    DRAFT = "draft"
    POSTED = "posted"


class GlPeriodStatus(StrEnum):
    OPEN = "open"
    CLOSED = "closed"


class CommissionStatus(StrEnum):
    ACCRUED = "accrued"
    PAYABLE = "payable"
    PAID = "paid"


@dataclass(slots=True)
class ARReceipt:
    id: UUID
    tenant_id: UUID
    customer_id: UUID
    code: str
    currency: str
    amount: Decimal
    idempotency_key: UUID
    status: ReceiptStatus
    created_at: datetime
    functional_currency: str = ""
    fx_rate: Decimal = Decimal("1.00000000")
    functional_amount: Decimal = Decimal("0.00")
    ar_invoice_id: UUID | None = None
    ar_invoice_version: int | None = None
    apply_key: UUID | None = None
    applied_at: datetime | None = None
    psp_ref: str | None = None
    psp_status: str | None = None
    allocated_amount: Decimal = Decimal("0")
    version: int = 1


@dataclass(slots=True)
class ARReceiptAllocation:
    id: UUID
    tenant_id: UUID
    receipt_id: UUID
    ar_invoice_id: UUID
    amount: Decimal
    allocation_key: UUID
    created_at: datetime
    version: int = 1
    realized_fx_amount: Decimal | None = None
    realized_fx_side: RealizedFxSide | None = None


class RealizedFxSide(StrEnum):
    GAIN = "gain"
    LOSS = "loss"


@dataclass(slots=True)
class RealizedFxEvent:
    id: UUID
    tenant_id: UUID
    source_type: str
    source_id: UUID
    amount: Decimal
    currency: str
    side: RealizedFxSide
    receipt_id: UUID
    invoice_id: UUID
    created_at: datetime
    version: int = 1


@dataclass(slots=True)
class ARWriteOff:
    id: UUID
    tenant_id: UUID
    ar_invoice_id: UUID
    amount: Decimal
    currency: str
    idempotency_key: UUID
    created_at: datetime
    reason: str | None = None
    version: int = 1


@dataclass(slots=True)
class TenantReceiptPspPolicy:
    tenant_id: UUID
    receipt_psp_required: bool
    updated_at: datetime
    version: int = 1


@dataclass(slots=True)
class TenantTaxAuthorityPolicy:
    tenant_id: UUID
    tax_authority_required: bool
    updated_at: datetime
    version: int = 1


@dataclass(slots=True)
class TaxRate:
    id: UUID
    tenant_id: UUID
    tax_code: str
    tax_name: str
    rate_percent: Decimal
    status: TaxRateStatus
    created_at: datetime
    updated_at: datetime
    version: int = 1


@dataclass(slots=True)
class ARCreditNote:
    id: UUID
    tenant_id: UUID
    customer_id: UUID
    ar_invoice_id: UUID
    ar_invoice_version: int
    code: str
    currency: str
    amount: Decimal
    idempotency_key: UUID
    status: CreditNoteStatus
    created_at: datetime
    issued_at: datetime | None = None
    issue_key: UUID | None = None
    version: int = 1


@dataclass(slots=True)
class ARRefund:
    id: UUID
    tenant_id: UUID
    credit_note_id: UUID
    customer_id: UUID
    currency: str
    amount: Decimal
    idempotency_key: UUID
    status: ARRefundStatus
    created_at: datetime
    posted_at: datetime | None = None
    post_key: UUID | None = None
    version: int = 1


@dataclass(slots=True)
class TreasuryTransfer:
    id: UUID
    tenant_id: UUID
    from_account_ref: str
    to_account_ref: str
    currency: str
    amount: Decimal
    functional_currency: str
    fx_rate: Decimal
    functional_amount: Decimal
    idempotency_key: UUID
    status: TreasuryTransferStatus
    created_at: datetime
    posted_at: datetime | None = None
    post_key: UUID | None = None
    version: int = 1


@dataclass(slots=True)
class CommissionEntry:
    id: UUID
    tenant_id: UUID
    source_invoice_id: UUID
    beneficiary_subject_id: UUID
    code: str
    currency: str
    amount: Decimal
    idempotency_key: UUID
    status: CommissionStatus
    created_at: datetime
    version: int = 1


@dataclass(slots=True)
class TaxInvoice:
    id: UUID
    tenant_id: UUID
    customer_id: UUID
    ar_invoice_id: UUID
    ar_invoice_version: int
    code: str
    currency: str
    amount: Decimal
    idempotency_key: UUID
    status: TaxInvoiceStatus
    created_at: datetime
    issued_at: datetime | None = None
    issue_key: UUID | None = None
    voided_at: datetime | None = None
    void_key: UUID | None = None
    void_reason: str | None = None
    tax_code: str | None = None
    authority_ref: str | None = None
    authority_status: str | None = None
    original_tax_invoice_id: UUID | None = None
    is_red_credit: bool = False
    version: int = 1


@dataclass(slots=True)
class TaxCreditLink:
    id: UUID
    tenant_id: UUID
    tax_invoice_id: UUID
    credit_note_id: UUID
    status: str
    idempotency_key: UUID
    created_at: datetime
    version: int = 1


@dataclass(slots=True)
class GlAccount:
    id: UUID
    tenant_id: UUID
    code: str
    name: str
    account_type: GlAccountType
    status: GlAccountStatus
    created_at: datetime
    version: int = 1


@dataclass(slots=True)
class JournalLine:
    id: UUID
    account_id: UUID
    debit: Decimal
    credit: Decimal


@dataclass(slots=True)
class GlPeriod:
    id: UUID
    tenant_id: UUID
    code: str
    name: str
    start_at: datetime
    end_at: datetime
    status: GlPeriodStatus
    created_at: datetime
    closed_at: datetime | None = None
    close_key: UUID | None = None
    version: int = 1


@dataclass(slots=True)
class JournalEntry:
    id: UUID
    tenant_id: UUID
    code: str
    currency: str
    period_id: UUID
    idempotency_key: UUID
    status: JournalEntryStatus
    created_at: datetime
    lines: list[JournalLine] = field(default_factory=list)
    memo: str | None = None
    posted_at: datetime | None = None
    post_key: UUID | None = None
    version: int = 1


class GlBridgeSourceType(StrEnum):
    AR_INVOICE = "ar_invoice"
    AR_RECEIPT = "ar_receipt"
    TAX_INVOICE = "tax_invoice"
    COMMISSION = "commission"
    AP_BILL = "ap_bill"
    AP_PAYMENT = "ap_payment"
    REALIZED_FX = "realized_fx"


@dataclass(slots=True)
class GlBridgeMap:
    tenant_id: UUID
    ar_control: UUID
    cash: UUID
    revenue: UUID
    tax_payable: UUID
    commission_expense: UUID
    commission_payable: UUID
    updated_at: datetime
    fx_gain: UUID | None = None
    fx_loss: UUID | None = None
    ap_control: UUID | None = None
    ap_expense: UUID | None = None
    version: int = 1


@dataclass(slots=True)
class GlBridgePosting:
    id: UUID
    tenant_id: UUID
    source_type: GlBridgeSourceType
    source_id: UUID
    journal_entry_id: UUID
    idempotency_key: UUID
    created_at: datetime


class GlFxRevaluationStatus(StrEnum):
    DRAFT = "draft"
    POSTED = "posted"


class GlFxRevaluationSide(StrEnum):
    GAIN = "gain"
    LOSS = "loss"


@dataclass(slots=True)
class GlFxRevaluation:
    id: UUID
    tenant_id: UUID
    period_id: UUID
    from_currency: str
    to_currency: str
    rate: Decimal
    amount: Decimal
    side: GlFxRevaluationSide
    idempotency_key: UUID
    status: GlFxRevaluationStatus
    created_at: datetime
    journal_entry_id: UUID | None = None
    posted_at: datetime | None = None
    post_key: UUID | None = None
    version: int = 1


class BankStatementStatus(StrEnum):
    OPEN = "open"
    RECONCILED = "reconciled"


class BankStatementLineStatus(StrEnum):
    UNMATCHED = "unmatched"
    MATCHED = "matched"
    CLEARED = "cleared"


@dataclass(slots=True)
class BankStatementLine:
    id: UUID
    statement_id: UUID
    amount: Decimal
    description: str
    status: BankStatementLineStatus
    matched_journal_line_id: UUID | None = None
    matched_receipt_id: UUID | None = None


@dataclass(slots=True)
class BankStatement:
    id: UUID
    tenant_id: UUID
    account_ref: str
    statement_date: datetime
    currency: str
    status: BankStatementStatus
    created_at: datetime
    lines: list[BankStatementLine] = field(default_factory=list)
    cleared_at: datetime | None = None
    version: int = 1
