"""Tenant-bound repository contract for Finance documents."""

from __future__ import annotations

from typing import Protocol
from uuid import UUID

from noventi.finance.models import (
    ARCreditNote,
    ARRefund,
    ARReceipt,
    ARReceiptAllocation,
    ARWriteOff,
    BankStatement,
    CommissionEntry,
    GlAccount,
    GlBridgeMap,
    GlBridgePosting,
    GlBridgeSourceType,
    GlFxRevaluation,
    GlPeriod,
    JournalEntry,
    JournalLine,
    RealizedFxEvent,
    ReceiptStatus,
    TaxInvoice,
    TaxCreditLink,
    TaxRate,
    TenantReceiptPspPolicy,
    TenantTaxAuthorityPolicy,
    TreasuryTransfer,
)


class FinanceRepository(Protocol):
    def add_receipt(self, receipt: ARReceipt) -> None: ...

    def save_receipt(
        self, receipt: ARReceipt, *, expected_version: int
    ) -> None: ...

    def get_receipt(self, receipt_id: UUID) -> ARReceipt | None: ...

    def list_receipts_for_customer(
        self, customer_id: UUID
    ) -> list[ARReceipt]: ...

    def get_receipt_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ARReceipt | None: ...

    def add_receipt_allocation(self, allocation: ARReceiptAllocation) -> None: ...

    def get_receipt_allocation_by_key(
        self, allocation_key: UUID
    ) -> ARReceiptAllocation | None: ...

    def list_receipt_allocations(
        self, receipt_id: UUID
    ) -> list[ARReceiptAllocation]: ...

    def add_realized_fx_event(self, event: RealizedFxEvent) -> None: ...

    def get_realized_fx_event(self, event_id: UUID) -> RealizedFxEvent | None: ...

    def get_realized_fx_event_by_source(
        self, source_id: UUID
    ) -> RealizedFxEvent | None: ...

    def add_ar_write_off(self, write_off: ARWriteOff) -> None: ...

    def get_ar_write_off_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ARWriteOff | None: ...

    def list_ar_write_offs(self, invoice_id: UUID) -> list[ARWriteOff]: ...

    def get_receipt_psp_policy(self) -> TenantReceiptPspPolicy | None: ...

    def save_receipt_psp_policy(
        self,
        policy: TenantReceiptPspPolicy,
        *,
        expected_version: int,
    ) -> None: ...

    def get_tax_authority_policy(self) -> TenantTaxAuthorityPolicy | None: ...

    def save_tax_authority_policy(
        self,
        policy: TenantTaxAuthorityPolicy,
        *,
        expected_version: int,
    ) -> None: ...

    def add_tax_rate(self, tax_rate: TaxRate) -> None: ...

    def save_tax_rate(
        self, tax_rate: TaxRate, *, expected_version: int
    ) -> None: ...

    def get_tax_rate(self, tax_rate_id: UUID) -> TaxRate | None: ...

    def get_tax_rate_by_code(self, tax_code: str) -> TaxRate | None: ...

    def add_credit_note(self, credit_note: ARCreditNote) -> None: ...

    def save_credit_note(
        self, credit_note: ARCreditNote, *, expected_version: int
    ) -> None: ...

    def get_credit_note(self, credit_note_id: UUID) -> ARCreditNote | None: ...

    def get_credit_note_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ARCreditNote | None: ...

    def add_ar_refund(self, refund: ARRefund) -> None: ...

    def save_ar_refund(
        self, refund: ARRefund, *, expected_version: int
    ) -> None: ...

    def get_ar_refund(self, refund_id: UUID) -> ARRefund | None: ...

    def get_ar_refund_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ARRefund | None: ...

    def add_treasury_transfer(self, transfer: TreasuryTransfer) -> None: ...

    def save_treasury_transfer(
        self, transfer: TreasuryTransfer, *, expected_version: int
    ) -> None: ...

    def get_treasury_transfer(
        self, transfer_id: UUID
    ) -> TreasuryTransfer | None: ...

    def get_treasury_transfer_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> TreasuryTransfer | None: ...

    def add_commission(self, entry: CommissionEntry) -> None: ...

    def save_commission(
        self, entry: CommissionEntry, *, expected_version: int
    ) -> None: ...

    def get_commission(self, commission_id: UUID) -> CommissionEntry | None: ...

    def get_commission_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> CommissionEntry | None: ...

    def get_commission_by_invoice_beneficiary(
        self, invoice_id: UUID, beneficiary_subject_id: UUID
    ) -> CommissionEntry | None: ...

    def add_tax_invoice(self, tax_invoice: TaxInvoice) -> None: ...

    def save_tax_invoice(
        self, tax_invoice: TaxInvoice, *, expected_version: int
    ) -> None: ...

    def get_tax_invoice(self, tax_invoice_id: UUID) -> TaxInvoice | None: ...

    def get_tax_invoice_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> TaxInvoice | None: ...

    def get_red_credit_by_original_tax_invoice(
        self, original_tax_invoice_id: UUID
    ) -> TaxInvoice | None: ...

    def add_tax_credit_link(self, link: TaxCreditLink) -> None: ...

    def get_tax_credit_link(self, link_id: UUID) -> TaxCreditLink | None: ...

    def get_tax_credit_link_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> TaxCreditLink | None: ...

    def add_gl_account(self, account: GlAccount) -> None: ...

    def save_gl_account(
        self, account: GlAccount, *, expected_version: int
    ) -> None: ...

    def get_gl_account(self, account_id: UUID) -> GlAccount | None: ...

    def get_gl_account_by_code(self, code: str) -> GlAccount | None: ...

    def add_gl_period(self, period: GlPeriod) -> None: ...

    def save_gl_period(
        self, period: GlPeriod, *, expected_version: int
    ) -> None: ...

    def get_gl_period(self, period_id: UUID) -> GlPeriod | None: ...

    def get_gl_period_by_code(self, code: str) -> GlPeriod | None: ...

    def list_gl_periods(self) -> list[GlPeriod]: ...

    def add_journal_entry(self, entry: JournalEntry) -> None: ...

    def save_journal_entry(
        self, entry: JournalEntry, *, expected_version: int
    ) -> None: ...

    def get_journal_entry(self, entry_id: UUID) -> JournalEntry | None: ...

    def get_journal_entry_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> JournalEntry | None: ...

    def get_journal_line(self, line_id: UUID) -> JournalLine | None: ...

    def get_gl_bridge_map(self) -> GlBridgeMap | None: ...

    def save_gl_bridge_map(
        self, bridge_map: GlBridgeMap, *, expected_version: int
    ) -> None: ...

    def add_gl_bridge_posting(self, posting: GlBridgePosting) -> None: ...

    def get_gl_bridge_posting_by_source(
        self, source_type: GlBridgeSourceType, source_id: UUID
    ) -> GlBridgePosting | None: ...

    def get_gl_bridge_posting_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> GlBridgePosting | None: ...

    def add_gl_fx_revaluation(self, revaluation: GlFxRevaluation) -> None: ...

    def save_gl_fx_revaluation(
        self, revaluation: GlFxRevaluation, *, expected_version: int
    ) -> None: ...

    def get_gl_fx_revaluation(
        self, revaluation_id: UUID
    ) -> GlFxRevaluation | None: ...

    def get_gl_fx_revaluation_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> GlFxRevaluation | None: ...

    def add_bank_statement(self, statement: BankStatement) -> None: ...

    def save_bank_statement(
        self, statement: BankStatement, *, expected_version: int
    ) -> None: ...

    def get_bank_statement(
        self, statement_id: UUID
    ) -> BankStatement | None: ...


class InMemoryFinanceRepository:
    def __init__(self, *, tenant_id: UUID) -> None:
        self._tenant_id = tenant_id
        self._receipts: dict[UUID, ARReceipt] = {}
        self._receipt_allocations: dict[UUID, ARReceiptAllocation] = {}
        self._realized_fx_events: dict[UUID, RealizedFxEvent] = {}
        self._ar_write_offs: dict[UUID, ARWriteOff] = {}
        self._receipt_psp_policy: TenantReceiptPspPolicy | None = None
        self._tax_authority_policy: TenantTaxAuthorityPolicy | None = None
        self._tax_rates: dict[UUID, TaxRate] = {}
        self._credit_notes: dict[UUID, ARCreditNote] = {}
        self._ar_refunds: dict[UUID, ARRefund] = {}
        self._treasury_transfers: dict[UUID, TreasuryTransfer] = {}
        self._commissions: dict[UUID, CommissionEntry] = {}
        self._tax_invoices: dict[UUID, TaxInvoice] = {}
        self._tax_credit_links: dict[UUID, TaxCreditLink] = {}
        self._gl_accounts: dict[UUID, GlAccount] = {}
        self._gl_periods: dict[UUID, GlPeriod] = {}
        self._journal_entries: dict[UUID, JournalEntry] = {}
        self._gl_bridge_map: GlBridgeMap | None = None
        self._gl_bridge_postings: dict[UUID, GlBridgePosting] = {}
        self._gl_fx_revaluations: dict[UUID, GlFxRevaluation] = {}
        self._bank_statements: dict[UUID, BankStatement] = {}

    def add_receipt(self, receipt: ARReceipt) -> None:
        self._require_tenant(receipt.tenant_id)
        if receipt.id in self._receipts:
            raise ValueError("receipt already exists")
        if any(
            existing.idempotency_key == receipt.idempotency_key
            for existing in self._receipts.values()
        ):
            raise ValueError("receipt idempotency conflict")
        self._receipts[receipt.id] = receipt

    def save_receipt(
        self, receipt: ARReceipt, *, expected_version: int
    ) -> None:
        self._require_tenant(receipt.tenant_id)
        current = self.get_receipt(receipt.id)
        if current is None or current.version != expected_version:
            raise ValueError("receipt version conflict")
        self._receipts[receipt.id] = receipt

    def get_receipt(self, receipt_id: UUID) -> ARReceipt | None:
        receipt = self._receipts.get(receipt_id)
        if receipt is None or receipt.tenant_id != self._tenant_id:
            return None
        return receipt

    def list_receipts_for_customer(
        self, customer_id: UUID
    ) -> list[ARReceipt]:
        return sorted(
            (
                receipt
                for receipt in self._receipts.values()
                if receipt.tenant_id == self._tenant_id
                and receipt.customer_id == customer_id
            ),
            key=lambda item: (item.created_at, item.id),
        )

    def get_receipt_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ARReceipt | None:
        for receipt in self._receipts.values():
            if (
                receipt.tenant_id == self._tenant_id
                and receipt.idempotency_key == idempotency_key
            ):
                return receipt
        return None

    def add_receipt_allocation(self, allocation: ARReceiptAllocation) -> None:
        self._require_tenant(allocation.tenant_id)
        if allocation.id in self._receipt_allocations or any(
            existing.allocation_key == allocation.allocation_key
            for existing in self._receipt_allocations.values()
        ):
            raise ValueError("receipt allocation conflict")
        self._receipt_allocations[allocation.id] = allocation

    def get_receipt_allocation_by_key(
        self, allocation_key: UUID
    ) -> ARReceiptAllocation | None:
        return next(
            (
                allocation
                for allocation in self._receipt_allocations.values()
                if allocation.tenant_id == self._tenant_id
                and allocation.allocation_key == allocation_key
            ),
            None,
        )

    def list_receipt_allocations(
        self, receipt_id: UUID
    ) -> list[ARReceiptAllocation]:
        return sorted(
            (
                allocation
                for allocation in self._receipt_allocations.values()
                if allocation.tenant_id == self._tenant_id
                and allocation.receipt_id == receipt_id
            ),
            key=lambda item: (item.created_at, item.id),
        )

    def add_realized_fx_event(self, event: RealizedFxEvent) -> None:
        self._require_tenant(event.tenant_id)
        if event.id in self._realized_fx_events or any(
            existing.source_id == event.source_id
            for existing in self._realized_fx_events.values()
        ):
            raise ValueError("realized FX event conflict")
        self._realized_fx_events[event.id] = event

    def get_realized_fx_event(self, event_id: UUID) -> RealizedFxEvent | None:
        event = self._realized_fx_events.get(event_id)
        if event is None or event.tenant_id != self._tenant_id:
            return None
        return event

    def get_realized_fx_event_by_source(
        self, source_id: UUID
    ) -> RealizedFxEvent | None:
        return next(
            (
                event
                for event in self._realized_fx_events.values()
                if event.tenant_id == self._tenant_id
                and event.source_id == source_id
            ),
            None,
        )

    def add_ar_write_off(self, write_off: ARWriteOff) -> None:
        self._require_tenant(write_off.tenant_id)
        if write_off.id in self._ar_write_offs or any(
            item.idempotency_key == write_off.idempotency_key
            for item in self._ar_write_offs.values()
        ):
            raise ValueError("AR write-off conflict")
        self._ar_write_offs[write_off.id] = write_off

    def get_ar_write_off_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ARWriteOff | None:
        return next(
            (
                item
                for item in self._ar_write_offs.values()
                if item.tenant_id == self._tenant_id
                and item.idempotency_key == idempotency_key
            ),
            None,
        )

    def list_ar_write_offs(self, invoice_id: UUID) -> list[ARWriteOff]:
        return sorted(
            (
                item
                for item in self._ar_write_offs.values()
                if item.tenant_id == self._tenant_id
                and item.ar_invoice_id == invoice_id
            ),
            key=lambda item: (item.created_at, item.id),
        )

    def get_receipt_psp_policy(self) -> TenantReceiptPspPolicy | None:
        return self._receipt_psp_policy

    def save_receipt_psp_policy(
        self,
        policy: TenantReceiptPspPolicy,
        *,
        expected_version: int,
    ) -> None:
        self._require_tenant(policy.tenant_id)
        current = self._receipt_psp_policy
        if current is None:
            if expected_version != 0:
                raise ValueError("receipt PSP policy version conflict")
        elif current.version != expected_version:
            raise ValueError("receipt PSP policy version conflict")
        self._receipt_psp_policy = policy

    def get_tax_authority_policy(self) -> TenantTaxAuthorityPolicy | None:
        return self._tax_authority_policy

    def save_tax_authority_policy(
        self,
        policy: TenantTaxAuthorityPolicy,
        *,
        expected_version: int,
    ) -> None:
        self._require_tenant(policy.tenant_id)
        current = self._tax_authority_policy
        if current is None:
            if expected_version != 0:
                raise ValueError("tax authority policy version conflict")
        elif current.version != expected_version:
            raise ValueError("tax authority policy version conflict")
        self._tax_authority_policy = policy

    def add_tax_rate(self, tax_rate: TaxRate) -> None:
        self._require_tenant(tax_rate.tenant_id)
        if tax_rate.id in self._tax_rates:
            raise ValueError("tax rate already exists")
        if any(
            existing.tax_code == tax_rate.tax_code
            for existing in self._tax_rates.values()
        ):
            raise ValueError("tax rate code conflict")
        self._tax_rates[tax_rate.id] = tax_rate

    def save_tax_rate(
        self, tax_rate: TaxRate, *, expected_version: int
    ) -> None:
        self._require_tenant(tax_rate.tenant_id)
        current = self.get_tax_rate(tax_rate.id)
        if current is None or current.version != expected_version:
            raise ValueError("tax rate version conflict")
        self._tax_rates[tax_rate.id] = tax_rate

    def get_tax_rate(self, tax_rate_id: UUID) -> TaxRate | None:
        tax_rate = self._tax_rates.get(tax_rate_id)
        if tax_rate is None or tax_rate.tenant_id != self._tenant_id:
            return None
        return tax_rate

    def get_tax_rate_by_code(self, tax_code: str) -> TaxRate | None:
        for tax_rate in self._tax_rates.values():
            if (
                tax_rate.tenant_id == self._tenant_id
                and tax_rate.tax_code == tax_code
            ):
                return tax_rate
        return None

    def add_credit_note(self, credit_note: ARCreditNote) -> None:
        self._require_tenant(credit_note.tenant_id)
        if credit_note.id in self._credit_notes:
            raise ValueError("credit note already exists")
        if any(
            existing.idempotency_key == credit_note.idempotency_key
            for existing in self._credit_notes.values()
        ):
            raise ValueError("credit note idempotency conflict")
        self._credit_notes[credit_note.id] = credit_note

    def save_credit_note(
        self, credit_note: ARCreditNote, *, expected_version: int
    ) -> None:
        self._require_tenant(credit_note.tenant_id)
        current = self.get_credit_note(credit_note.id)
        if current is None or current.version != expected_version:
            raise ValueError("credit note version conflict")
        self._credit_notes[credit_note.id] = credit_note

    def get_credit_note(self, credit_note_id: UUID) -> ARCreditNote | None:
        credit_note = self._credit_notes.get(credit_note_id)
        if credit_note is None or credit_note.tenant_id != self._tenant_id:
            return None
        return credit_note

    def get_credit_note_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ARCreditNote | None:
        for credit_note in self._credit_notes.values():
            if (
                credit_note.tenant_id == self._tenant_id
                and credit_note.idempotency_key == idempotency_key
            ):
                return credit_note
        return None

    def add_ar_refund(self, refund: ARRefund) -> None:
        self._require_tenant(refund.tenant_id)
        if refund.id in self._ar_refunds or any(
            existing.idempotency_key == refund.idempotency_key
            for existing in self._ar_refunds.values()
        ):
            raise ValueError("AR refund conflict")
        self._ar_refunds[refund.id] = refund

    def save_ar_refund(
        self, refund: ARRefund, *, expected_version: int
    ) -> None:
        self._require_tenant(refund.tenant_id)
        current = self.get_ar_refund(refund.id)
        if current is None or current.version != expected_version:
            raise ValueError("AR refund version conflict")
        self._ar_refunds[refund.id] = refund

    def get_ar_refund(self, refund_id: UUID) -> ARRefund | None:
        refund = self._ar_refunds.get(refund_id)
        if refund is None or refund.tenant_id != self._tenant_id:
            return None
        return refund

    def get_ar_refund_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> ARRefund | None:
        for refund in self._ar_refunds.values():
            if (
                refund.tenant_id == self._tenant_id
                and refund.idempotency_key == idempotency_key
            ):
                return refund
        return None

    def add_treasury_transfer(self, transfer: TreasuryTransfer) -> None:
        self._require_tenant(transfer.tenant_id)
        if transfer.id in self._treasury_transfers or any(
            existing.idempotency_key == transfer.idempotency_key
            for existing in self._treasury_transfers.values()
        ):
            raise ValueError("treasury transfer conflict")
        self._treasury_transfers[transfer.id] = transfer

    def save_treasury_transfer(
        self, transfer: TreasuryTransfer, *, expected_version: int
    ) -> None:
        self._require_tenant(transfer.tenant_id)
        current = self.get_treasury_transfer(transfer.id)
        if current is None or current.version != expected_version:
            raise ValueError("treasury transfer version conflict")
        self._treasury_transfers[transfer.id] = transfer

    def get_treasury_transfer(
        self, transfer_id: UUID
    ) -> TreasuryTransfer | None:
        transfer = self._treasury_transfers.get(transfer_id)
        if transfer is None or transfer.tenant_id != self._tenant_id:
            return None
        return transfer

    def get_treasury_transfer_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> TreasuryTransfer | None:
        for transfer in self._treasury_transfers.values():
            if (
                transfer.tenant_id == self._tenant_id
                and transfer.idempotency_key == idempotency_key
            ):
                return transfer
        return None

    def list_applied_receipts_for_customer(
        self, customer_id: UUID
    ) -> list[ARReceipt]:
        return sorted(
            (
                receipt
                for receipt in self._receipts.values()
                if receipt.tenant_id == self._tenant_id
                and receipt.customer_id == customer_id
                and receipt.status == ReceiptStatus.APPLIED
                and receipt.ar_invoice_id is not None
            ),
            key=lambda item: (item.created_at, item.code, item.id),
        )

    def list_credit_notes_for_customer(
        self, customer_id: UUID
    ) -> list[ARCreditNote]:
        return sorted(
            (
                credit_note
                for credit_note in self._credit_notes.values()
                if credit_note.tenant_id == self._tenant_id
                and credit_note.customer_id == customer_id
            ),
            key=lambda item: (item.created_at, item.code, item.id),
        )

    def add_commission(self, entry: CommissionEntry) -> None:
        self._require_tenant(entry.tenant_id)
        if entry.id in self._commissions:
            raise ValueError("commission already exists")
        if any(
            existing.idempotency_key == entry.idempotency_key
            for existing in self._commissions.values()
        ):
            raise ValueError("commission idempotency conflict")
        if any(
            existing.source_invoice_id == entry.source_invoice_id
            and existing.beneficiary_subject_id == entry.beneficiary_subject_id
            for existing in self._commissions.values()
        ):
            raise ValueError("commission invoice beneficiary conflict")
        self._commissions[entry.id] = entry

    def save_commission(
        self, entry: CommissionEntry, *, expected_version: int
    ) -> None:
        self._require_tenant(entry.tenant_id)
        existing = self._commissions.get(entry.id)
        if existing is None or existing.version != expected_version:
            raise ValueError("commission version conflict")
        self._commissions[entry.id] = entry

    def get_commission(self, commission_id: UUID) -> CommissionEntry | None:
        entry = self._commissions.get(commission_id)
        if entry is None or entry.tenant_id != self._tenant_id:
            return None
        return entry

    def get_commission_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> CommissionEntry | None:
        for entry in self._commissions.values():
            if (
                entry.tenant_id == self._tenant_id
                and entry.idempotency_key == idempotency_key
            ):
                return entry
        return None

    def get_commission_by_invoice_beneficiary(
        self, invoice_id: UUID, beneficiary_subject_id: UUID
    ) -> CommissionEntry | None:
        for entry in self._commissions.values():
            if (
                entry.tenant_id == self._tenant_id
                and entry.source_invoice_id == invoice_id
                and entry.beneficiary_subject_id == beneficiary_subject_id
            ):
                return entry
        return None

    def add_tax_invoice(self, tax_invoice: TaxInvoice) -> None:
        self._require_tenant(tax_invoice.tenant_id)
        if tax_invoice.id in self._tax_invoices:
            raise ValueError("tax invoice already exists")
        if any(
            existing.idempotency_key == tax_invoice.idempotency_key
            for existing in self._tax_invoices.values()
        ):
            raise ValueError("tax invoice idempotency conflict")
        self._tax_invoices[tax_invoice.id] = tax_invoice

    def save_tax_invoice(
        self, tax_invoice: TaxInvoice, *, expected_version: int
    ) -> None:
        self._require_tenant(tax_invoice.tenant_id)
        current = self.get_tax_invoice(tax_invoice.id)
        if current is None or current.version != expected_version:
            raise ValueError("tax invoice version conflict")
        self._tax_invoices[tax_invoice.id] = tax_invoice

    def get_tax_invoice(self, tax_invoice_id: UUID) -> TaxInvoice | None:
        tax_invoice = self._tax_invoices.get(tax_invoice_id)
        if tax_invoice is None or tax_invoice.tenant_id != self._tenant_id:
            return None
        return tax_invoice

    def get_tax_invoice_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> TaxInvoice | None:
        for tax_invoice in self._tax_invoices.values():
            if (
                tax_invoice.tenant_id == self._tenant_id
                and tax_invoice.idempotency_key == idempotency_key
            ):
                return tax_invoice
        return None

    def get_red_credit_by_original_tax_invoice(
        self, original_tax_invoice_id: UUID
    ) -> TaxInvoice | None:
        return next(
            (
                tax_invoice
                for tax_invoice in self._tax_invoices.values()
                if tax_invoice.tenant_id == self._tenant_id
                and tax_invoice.original_tax_invoice_id == original_tax_invoice_id
                and tax_invoice.is_red_credit
            ),
            None,
        )

    def add_tax_credit_link(self, link: TaxCreditLink) -> None:
        self._require_tenant(link.tenant_id)
        if link.id in self._tax_credit_links or any(
            existing.idempotency_key == link.idempotency_key
            or (
                existing.tax_invoice_id == link.tax_invoice_id
                and existing.credit_note_id == link.credit_note_id
            )
            for existing in self._tax_credit_links.values()
        ):
            raise ValueError("tax credit link conflict")
        self._tax_credit_links[link.id] = link

    def get_tax_credit_link(self, link_id: UUID) -> TaxCreditLink | None:
        link = self._tax_credit_links.get(link_id)
        if link is None or link.tenant_id != self._tenant_id:
            return None
        return link

    def get_tax_credit_link_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> TaxCreditLink | None:
        for link in self._tax_credit_links.values():
            if (
                link.tenant_id == self._tenant_id
                and link.idempotency_key == idempotency_key
            ):
                return link
        return None

    def add_gl_account(self, account: GlAccount) -> None:
        self._require_tenant(account.tenant_id)
        if account.id in self._gl_accounts:
            raise ValueError("gl account already exists")
        if any(
            existing.code == account.code
            for existing in self._gl_accounts.values()
        ):
            raise ValueError("gl account code conflict")
        self._gl_accounts[account.id] = account

    def save_gl_account(
        self, account: GlAccount, *, expected_version: int
    ) -> None:
        self._require_tenant(account.tenant_id)
        current = self.get_gl_account(account.id)
        if current is None or current.version != expected_version:
            raise ValueError("gl account version conflict")
        self._gl_accounts[account.id] = account

    def get_gl_account(self, account_id: UUID) -> GlAccount | None:
        account = self._gl_accounts.get(account_id)
        if account is None or account.tenant_id != self._tenant_id:
            return None
        return account

    def get_gl_account_by_code(self, code: str) -> GlAccount | None:
        for account in self._gl_accounts.values():
            if account.tenant_id == self._tenant_id and account.code == code:
                return account
        return None

    def add_gl_period(self, period: GlPeriod) -> None:
        self._require_tenant(period.tenant_id)
        if period.id in self._gl_periods:
            raise ValueError("gl period already exists")
        if any(
            existing.code == period.code
            for existing in self._gl_periods.values()
        ):
            raise ValueError("gl period code conflict")
        self._gl_periods[period.id] = period

    def save_gl_period(
        self, period: GlPeriod, *, expected_version: int
    ) -> None:
        self._require_tenant(period.tenant_id)
        current = self.get_gl_period(period.id)
        if current is None or current.version != expected_version:
            raise ValueError("gl period version conflict")
        self._gl_periods[period.id] = period

    def get_gl_period(self, period_id: UUID) -> GlPeriod | None:
        period = self._gl_periods.get(period_id)
        if period is None or period.tenant_id != self._tenant_id:
            return None
        return period

    def get_gl_period_by_code(self, code: str) -> GlPeriod | None:
        for period in self._gl_periods.values():
            if period.tenant_id == self._tenant_id and period.code == code:
                return period
        return None

    def list_gl_periods(self) -> list[GlPeriod]:
        return [
            period
            for period in self._gl_periods.values()
            if period.tenant_id == self._tenant_id
        ]

    def add_journal_entry(self, entry: JournalEntry) -> None:
        self._require_tenant(entry.tenant_id)
        if entry.id in self._journal_entries:
            raise ValueError("journal entry already exists")
        if any(
            existing.idempotency_key == entry.idempotency_key
            for existing in self._journal_entries.values()
        ):
            raise ValueError("journal entry idempotency conflict")
        self._journal_entries[entry.id] = entry

    def save_journal_entry(
        self, entry: JournalEntry, *, expected_version: int
    ) -> None:
        self._require_tenant(entry.tenant_id)
        current = self.get_journal_entry(entry.id)
        if current is None or current.version != expected_version:
            raise ValueError("journal entry version conflict")
        self._journal_entries[entry.id] = entry

    def get_journal_entry(self, entry_id: UUID) -> JournalEntry | None:
        entry = self._journal_entries.get(entry_id)
        if entry is None or entry.tenant_id != self._tenant_id:
            return None
        return entry

    def get_journal_entry_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> JournalEntry | None:
        for entry in self._journal_entries.values():
            if (
                entry.tenant_id == self._tenant_id
                and entry.idempotency_key == idempotency_key
            ):
                return entry
        return None

    def get_journal_line(self, line_id: UUID) -> JournalLine | None:
        for entry in self._journal_entries.values():
            if entry.tenant_id != self._tenant_id:
                continue
            for line in entry.lines:
                if line.id == line_id:
                    return line
        return None

    def get_gl_bridge_map(self) -> GlBridgeMap | None:
        return self._gl_bridge_map

    def save_gl_bridge_map(
        self, bridge_map: GlBridgeMap, *, expected_version: int
    ) -> None:
        self._require_tenant(bridge_map.tenant_id)
        current = self._gl_bridge_map
        if current is None:
            if expected_version != 0:
                raise ValueError("gl bridge map version conflict")
        else:
            if current.version != expected_version:
                raise ValueError("gl bridge map version conflict")
        self._gl_bridge_map = bridge_map

    def add_gl_bridge_posting(self, posting: GlBridgePosting) -> None:
        self._require_tenant(posting.tenant_id)
        if posting.id in self._gl_bridge_postings:
            raise ValueError("gl bridge posting already exists")
        if any(
            existing.source_type == posting.source_type
            and existing.source_id == posting.source_id
            for existing in self._gl_bridge_postings.values()
        ):
            raise ValueError("gl bridge posting source conflict")
        if any(
            existing.idempotency_key == posting.idempotency_key
            for existing in self._gl_bridge_postings.values()
        ):
            raise ValueError("gl bridge posting idempotency conflict")
        self._gl_bridge_postings[posting.id] = posting

    def get_gl_bridge_posting_by_source(
        self, source_type: GlBridgeSourceType, source_id: UUID
    ) -> GlBridgePosting | None:
        for posting in self._gl_bridge_postings.values():
            if (
                posting.tenant_id == self._tenant_id
                and posting.source_type == source_type
                and posting.source_id == source_id
            ):
                return posting
        return None

    def get_gl_bridge_posting_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> GlBridgePosting | None:
        for posting in self._gl_bridge_postings.values():
            if (
                posting.tenant_id == self._tenant_id
                and posting.idempotency_key == idempotency_key
            ):
                return posting
        return None

    def add_gl_fx_revaluation(self, revaluation: GlFxRevaluation) -> None:
        self._require_tenant(revaluation.tenant_id)
        if revaluation.id in self._gl_fx_revaluations:
            raise ValueError("gl fx revaluation already exists")
        if any(
            existing.idempotency_key == revaluation.idempotency_key
            for existing in self._gl_fx_revaluations.values()
        ):
            raise ValueError("gl fx revaluation idempotency conflict")
        self._gl_fx_revaluations[revaluation.id] = revaluation

    def save_gl_fx_revaluation(
        self, revaluation: GlFxRevaluation, *, expected_version: int
    ) -> None:
        self._require_tenant(revaluation.tenant_id)
        current = self.get_gl_fx_revaluation(revaluation.id)
        if current is None or current.version != expected_version:
            raise ValueError("gl fx revaluation version conflict")
        self._gl_fx_revaluations[revaluation.id] = revaluation

    def get_gl_fx_revaluation(
        self, revaluation_id: UUID
    ) -> GlFxRevaluation | None:
        revaluation = self._gl_fx_revaluations.get(revaluation_id)
        if revaluation is None or revaluation.tenant_id != self._tenant_id:
            return None
        return revaluation

    def get_gl_fx_revaluation_by_idempotency_key(
        self, idempotency_key: UUID
    ) -> GlFxRevaluation | None:
        for revaluation in self._gl_fx_revaluations.values():
            if (
                revaluation.tenant_id == self._tenant_id
                and revaluation.idempotency_key == idempotency_key
            ):
                return revaluation
        return None

    def add_bank_statement(self, statement: BankStatement) -> None:
        self._require_tenant(statement.tenant_id)
        if statement.id in self._bank_statements:
            raise ValueError("bank statement already exists")
        self._bank_statements[statement.id] = statement

    def save_bank_statement(
        self, statement: BankStatement, *, expected_version: int
    ) -> None:
        self._require_tenant(statement.tenant_id)
        current = self.get_bank_statement(statement.id)
        if current is None or current.version != expected_version:
            raise ValueError("bank statement version conflict")
        self._bank_statements[statement.id] = statement

    def get_bank_statement(
        self, statement_id: UUID
    ) -> BankStatement | None:
        statement = self._bank_statements.get(statement_id)
        if statement is None or statement.tenant_id != self._tenant_id:
            return None
        return statement

    def _require_tenant(self, tenant_id: UUID) -> None:
        if tenant_id != self._tenant_id:
            raise ValueError("Finance record is outside repository tenant")
