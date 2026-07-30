"""HTTP schemas for Finance AR Receipt F1 (PHX-G310)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _ClosedModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreateARReceiptRequest(_ClosedModel):
    customer_id: UUID
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3)
    functional_currency: str | None = Field(
        default=None, min_length=3, max_length=3
    )
    fx_rate: Decimal | None = Field(
        default=None, gt=0, max_digits=18, decimal_places=8
    )
    functional_amount: Decimal | None = Field(
        default=None, gt=0, max_digits=18, decimal_places=2
    )
    idempotency_key: UUID


class ApplyARReceiptRequest(_ClosedModel):
    invoice_id: UUID
    idempotency_key: UUID


class AllocateARReceiptRequest(_ClosedModel):
    invoice_id: UUID
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    allocation_key: UUID


class ARReceiptAllocationView(_ClosedModel):
    id: UUID
    receipt_id: UUID
    ar_invoice_id: UUID
    amount: Decimal
    allocation_key: UUID
    created_at: datetime
    version: int
    realized_fx_amount: Decimal | None
    realized_fx_side: Literal["gain", "loss"] | None


class ARReceiptAllocationEnvelope(_ClosedModel):
    data: ARReceiptAllocationView
    audit_id: UUID | None = None


class ARReceiptAllocationListEnvelope(_ClosedModel):
    data: list[ARReceiptAllocationView]


class ARReceiptView(_ClosedModel):
    id: UUID
    customer_id: UUID
    code: str
    currency: str
    amount: Decimal
    functional_currency: str
    fx_rate: Decimal
    functional_amount: Decimal
    allocated_amount: Decimal
    unallocated_amount: Decimal
    status: Literal["draft", "applied"]
    ar_invoice_id: UUID | None
    ar_invoice_version: int | None
    created_at: datetime
    applied_at: datetime | None
    psp_ref: str | None
    psp_status: str | None
    version: int


class ARReceiptEnvelope(_ClosedModel):
    data: ARReceiptView
    audit_id: UUID | None = None


class CreateARWriteOffRequest(_ClosedModel):
    invoice_id: UUID
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    idempotency_key: UUID
    human_confirm: Literal[True]
    reason: str | None = Field(default=None, min_length=1, max_length=500)


class ARWriteOffView(_ClosedModel):
    id: UUID
    ar_invoice_id: UUID
    amount: Decimal
    currency: str
    reason: str | None
    created_at: datetime
    version: int


class ARWriteOffEnvelope(_ClosedModel):
    data: ARWriteOffView
    audit_id: UUID | None = None


class CloseARInvoiceRequest(_ClosedModel):
    human_confirm: Literal[True]


class CloseARInvoiceView(_ClosedModel):
    id: UUID
    status: Literal["closed"]
    version: int


class CloseARInvoiceEnvelope(_ClosedModel):
    data: CloseARInvoiceView
    audit_id: UUID | None = None


class CustomerBalanceView(_ClosedModel):
    customer_id: UUID
    balances: dict[str, Decimal]
    unallocated_receipts: dict[str, Decimal]
    unallocated_receipts_note: Literal[
        "NOT part of cleared balance"
    ]


class CustomerBalanceEnvelope(_ClosedModel):
    data: CustomerBalanceView
    audit_id: UUID | None = None


class SetReceiptPspPolicyRequest(_ClosedModel):
    receipt_psp_required: bool
    expected_version: int = Field(ge=0)


class ReceiptPspPolicyView(_ClosedModel):
    receipt_psp_required: bool
    updated_at: datetime
    version: int


class ReceiptPspPolicyEnvelope(_ClosedModel):
    data: ReceiptPspPolicyView
    audit_id: UUID | None = None


class CreateARCreditNoteRequest(_ClosedModel):
    invoice_id: UUID
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    idempotency_key: UUID


class IssueARCreditNoteRequest(_ClosedModel):
    idempotency_key: UUID
    human_confirm: Literal[True]


class ARCreditNoteView(_ClosedModel):
    id: UUID
    customer_id: UUID
    ar_invoice_id: UUID
    ar_invoice_version: int
    code: str
    currency: str
    amount: Decimal
    status: Literal["draft", "issued"]
    created_at: datetime
    issued_at: datetime | None
    version: int


class ARCreditNoteEnvelope(_ClosedModel):
    data: ARCreditNoteView
    audit_id: UUID | None = None


class CreateARRefundRequest(_ClosedModel):
    credit_note_id: UUID
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3)
    idempotency_key: UUID


class PostARRefundRequest(_ClosedModel):
    idempotency_key: UUID
    human_confirm: Literal[True]


class ARRefundView(_ClosedModel):
    id: UUID
    credit_note_id: UUID
    customer_id: UUID
    currency: str
    amount: Decimal
    status: Literal["draft", "posted"]
    created_at: datetime
    posted_at: datetime | None
    version: int


class ARRefundEnvelope(_ClosedModel):
    data: ARRefundView
    audit_id: UUID | None = None


class CreateTreasuryTransferRequest(_ClosedModel):
    from_account_ref: str = Field(min_length=1, max_length=128)
    to_account_ref: str = Field(min_length=1, max_length=128)
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3)
    functional_currency: str | None = Field(
        default=None, min_length=3, max_length=3
    )
    fx_rate: Decimal | None = Field(
        default=None, gt=0, max_digits=18, decimal_places=8
    )
    functional_amount: Decimal | None = Field(
        default=None, gt=0, max_digits=18, decimal_places=2
    )
    idempotency_key: UUID


class PostTreasuryTransferRequest(_ClosedModel):
    idempotency_key: UUID
    human_confirm: Literal[True]


class TreasuryTransferView(_ClosedModel):
    id: UUID
    from_account_ref: str
    to_account_ref: str
    currency: str
    amount: Decimal
    functional_currency: str
    fx_rate: Decimal
    functional_amount: Decimal
    status: Literal["draft", "posted"]
    created_at: datetime
    posted_at: datetime | None
    version: int


class TreasuryTransferEnvelope(_ClosedModel):
    data: TreasuryTransferView
    audit_id: UUID | None = None


class CreateTaxCreditLinkRequest(_ClosedModel):
    tax_invoice_id: UUID
    credit_note_id: UUID
    idempotency_key: UUID


class TaxCreditLinkView(_ClosedModel):
    id: UUID
    tax_invoice_id: UUID
    credit_note_id: UUID
    status: Literal["linked"]
    created_at: datetime
    version: int


class TaxCreditLinkEnvelope(_ClosedModel):
    data: TaxCreditLinkView
    audit_id: UUID | None = None


class AccrueCommissionRequest(_ClosedModel):
    invoice_id: UUID
    beneficiary_subject_id: UUID
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3)
    idempotency_key: UUID


class CommissionEntryView(_ClosedModel):
    id: UUID
    source_invoice_id: UUID
    beneficiary_subject_id: UUID
    code: str
    currency: str
    amount: Decimal
    status: Literal["accrued", "payable", "paid"]
    created_at: datetime
    version: int


class CommissionEntryEnvelope(_ClosedModel):
    data: CommissionEntryView
    audit_id: UUID | None = None


class CreateTaxInvoiceRequest(_ClosedModel):
    invoice_id: UUID
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    idempotency_key: UUID
    tax_code: str | None = Field(default=None, min_length=1, max_length=64)


class IssueTaxInvoiceRequest(_ClosedModel):
    idempotency_key: UUID
    human_confirm: Literal[True]
    tax_code: str | None = Field(default=None, min_length=1, max_length=64)


class CreateTaxRedCreditRequest(_ClosedModel):
    amount: Decimal | None = Field(
        default=None, gt=0, max_digits=18, decimal_places=2
    )
    idempotency_key: UUID
    human_confirm: Literal[True]


class VoidTaxInvoiceRequest(_ClosedModel):
    idempotency_key: UUID
    human_confirm: Literal[True]
    reason: str = Field(min_length=1, max_length=500)


class TaxInvoiceView(_ClosedModel):
    id: UUID
    customer_id: UUID
    ar_invoice_id: UUID
    ar_invoice_version: int
    code: str
    currency: str
    amount: Decimal
    status: Literal["draft", "issued", "voided"]
    created_at: datetime
    issued_at: datetime | None
    voided_at: datetime | None = None
    void_reason: str | None = None
    tax_code: str | None = None
    authority_ref: str | None = None
    authority_status: str | None = None
    original_tax_invoice_id: UUID | None = None
    is_red_credit: bool
    version: int


class TaxInvoiceEnvelope(_ClosedModel):
    data: TaxInvoiceView
    audit_id: UUID | None = None


class CreateTaxRateRequest(_ClosedModel):
    tax_code: str = Field(min_length=1, max_length=64)
    tax_name: str = Field(min_length=1, max_length=128)
    rate_percent: Decimal = Field(ge=0, max_digits=9, decimal_places=4)


class TaxRateView(_ClosedModel):
    id: UUID
    tax_code: str
    tax_name: str
    rate_percent: Decimal
    status: Literal["active", "archived"]
    created_at: datetime
    updated_at: datetime
    version: int


class TaxRateEnvelope(_ClosedModel):
    data: TaxRateView
    audit_id: UUID | None = None


class SetTaxAuthorityPolicyRequest(_ClosedModel):
    tax_authority_required: bool
    expected_version: int = Field(ge=0)


class TaxAuthorityPolicyView(_ClosedModel):
    tax_authority_required: bool
    updated_at: datetime
    version: int


class TaxAuthorityPolicyEnvelope(_ClosedModel):
    data: TaxAuthorityPolicyView
    audit_id: UUID | None = None


class TaxAuthorityAdapterStatusView(_ClosedModel):
    network_flag_enabled: bool
    adapter_kind: Literal["reject_all", "network_stub", "http_live"]
    live_transport: bool
    endpoint_configured: bool


class TaxAuthorityAdapterStatusEnvelope(_ClosedModel):
    data: TaxAuthorityAdapterStatusView


class PspAdapterStatusView(_ClosedModel):
    provider: Literal["off", "fake", "stripe_like"]
    network_flag_enabled: bool
    adapter_kind: Literal[
        "reject_all", "fake", "stripe_like_stub", "http_live"
    ]
    live_transport: bool
    endpoint_configured: bool


class PspAdapterStatusEnvelope(_ClosedModel):
    data: PspAdapterStatusView


class CreateGlAccountRequest(_ClosedModel):
    code: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    account_type: Literal[
        "asset", "liability", "equity", "revenue", "expense"
    ]


class GlAccountView(_ClosedModel):
    id: UUID
    code: str
    name: str
    account_type: Literal[
        "asset", "liability", "equity", "revenue", "expense"
    ]
    status: Literal["active", "archived"]
    created_at: datetime
    version: int


class GlAccountEnvelope(_ClosedModel):
    data: GlAccountView
    audit_id: UUID | None = None


class JournalLineInput(_ClosedModel):
    account_id: UUID
    debit: Decimal = Field(ge=0, max_digits=18, decimal_places=2)
    credit: Decimal = Field(ge=0, max_digits=18, decimal_places=2)


class CreateGlPeriodRequest(_ClosedModel):
    code: str = Field(min_length=1, max_length=64)
    start_at: datetime
    end_at: datetime
    name: str | None = Field(default=None, min_length=1, max_length=128)


class CloseGlPeriodRequest(_ClosedModel):
    idempotency_key: UUID
    human_confirm: Literal[True]


class GlPeriodView(_ClosedModel):
    id: UUID
    code: str
    name: str
    start_at: datetime
    end_at: datetime
    status: Literal["open", "closed"]
    created_at: datetime
    closed_at: datetime | None
    version: int


class GlPeriodEnvelope(_ClosedModel):
    data: GlPeriodView
    audit_id: UUID | None = None


class CreateJournalEntryRequest(_ClosedModel):
    currency: str = Field(min_length=3, max_length=3)
    period_id: UUID
    lines: list[JournalLineInput] = Field(min_length=2)
    idempotency_key: UUID
    memo: str | None = Field(default=None, max_length=500)


class PostJournalEntryRequest(_ClosedModel):
    idempotency_key: UUID
    human_confirm: Literal[True]


class JournalLineView(_ClosedModel):
    id: UUID
    account_id: UUID
    debit: Decimal
    credit: Decimal


class JournalEntryView(_ClosedModel):
    id: UUID
    code: str
    currency: str
    period_id: UUID
    memo: str | None
    status: Literal["draft", "posted"]
    created_at: datetime
    posted_at: datetime | None
    version: int
    lines: list[JournalLineView]


class JournalEntryEnvelope(_ClosedModel):
    data: JournalEntryView
    audit_id: UUID | None = None


class SetGlBridgeMapRequest(_ClosedModel):
    ar_control: UUID
    cash: UUID
    revenue: UUID
    tax_payable: UUID
    commission_expense: UUID
    commission_payable: UUID
    expected_version: int = Field(ge=0)
    fx_gain: UUID | None = None
    fx_loss: UUID | None = None
    ap_control: UUID | None = None
    ap_expense: UUID | None = None


class GlBridgeMapView(_ClosedModel):
    ar_control: UUID
    cash: UUID
    revenue: UUID
    tax_payable: UUID
    commission_expense: UUID
    commission_payable: UUID
    fx_gain: UUID | None
    fx_loss: UUID | None
    ap_control: UUID | None
    ap_expense: UUID | None
    updated_at: datetime
    version: int


class GlBridgeMapEnvelope(_ClosedModel):
    data: GlBridgeMapView
    audit_id: UUID | None = None


class BridgeSourceRequest(_ClosedModel):
    source_id: UUID
    period_id: UUID
    idempotency_key: UUID
    human_confirm: Literal[True]


class GlBridgePostingView(_ClosedModel):
    id: UUID
    source_type: Literal[
        "ar_invoice",
        "ar_receipt",
        "tax_invoice",
        "commission",
        "ap_bill",
        "ap_payment",
        "realized_fx",
    ]
    source_id: UUID
    journal_entry_id: UUID
    created_at: datetime


class GlBridgePostingEnvelope(_ClosedModel):
    data: GlBridgePostingView
    audit_id: UUID | None = None


class CreateGlFxRevaluationRequest(_ClosedModel):
    period_id: UUID
    from_currency: str = Field(min_length=3, max_length=3)
    to_currency: str = Field(min_length=3, max_length=3)
    amount: Decimal = Field(gt=0, max_digits=18, decimal_places=2)
    side: Literal["gain", "loss"]
    idempotency_key: UUID
    rate: Decimal | None = Field(
        default=None, gt=0, max_digits=18, decimal_places=8
    )


class PostGlFxRevaluationRequest(_ClosedModel):
    idempotency_key: UUID
    human_confirm: Literal[True]


class GlFxRevaluationView(_ClosedModel):
    id: UUID
    period_id: UUID
    from_currency: str
    to_currency: str
    rate: Decimal
    amount: Decimal
    side: Literal["gain", "loss"]
    status: Literal["draft", "posted"]
    journal_entry_id: UUID | None
    created_at: datetime
    posted_at: datetime | None
    version: int


class GlFxRevaluationEnvelope(_ClosedModel):
    data: GlFxRevaluationView
    audit_id: UUID | None = None


class BankStatementLineInput(_ClosedModel):
    amount: Decimal = Field(max_digits=18, decimal_places=2)
    description: str = Field(min_length=1, max_length=500)


class CreateBankStatementRequest(_ClosedModel):
    account_ref: str = Field(min_length=1, max_length=128)
    statement_date: datetime
    currency: str = Field(min_length=3, max_length=3)
    lines: list[BankStatementLineInput] = Field(min_length=1)


class MatchBankStatementLineRequest(_ClosedModel):
    matched_journal_line_id: UUID | None = None
    matched_receipt_id: UUID | None = None


class ClearBankStatementRequest(_ClosedModel):
    human_confirm: Literal[True]


class BankStatementLineView(_ClosedModel):
    id: UUID
    amount: Decimal
    description: str
    status: Literal["unmatched", "matched", "cleared"]
    matched_journal_line_id: UUID | None
    matched_receipt_id: UUID | None


class BankStatementView(_ClosedModel):
    id: UUID
    account_ref: str
    statement_date: datetime
    currency: str
    status: Literal["open", "reconciled"]
    created_at: datetime
    cleared_at: datetime | None
    version: int
    lines: list[BankStatementLineView]


class BankStatementEnvelope(_ClosedModel):
    data: BankStatementView
    audit_id: UUID | None = None


class FinanceStatusData(_ClosedModel):
    """Finance foundation posture for Terminal strip (PHX-G394 / Batch-G)."""

    writable: Literal[False] = False
    commercial_auto_write: Literal[False] = False
    holds_business_truth: Literal[True] = True
    terminal_holds_business_truth: Literal[False] = False
    bank_file_import: Literal["deferred"] = "deferred"
    external_psp_network_default: Literal["off"] = "off"
    gl_period_status_surface: Literal[True] = True
    party_balance_projection: Literal[True] = True
    treasury_transfer_surface: Literal[True] = True
    crm_quote_so_do_state_consistency: Literal[True] = True
    ar_receipt_credit_boundary: Literal["internal_records_only"] = "internal_records_only"
    commission_settlement_mode: Literal["read_only_status"] = "read_only_status"
    crm_finance_handoff_audit: Literal[True] = True
    purchase_order_observability: Literal[True] = True
    inventory_movement_observability: Literal[True] = True
    receiving_return_boundary: Literal["kernel_records_only"] = "kernel_records_only"
    purchase_inventory_cross_contract: Literal[True] = True
    supported_surfaces: list[str] = Field(min_length=1)


class FinanceStatusEnvelope(_ClosedModel):
    data: FinanceStatusData
