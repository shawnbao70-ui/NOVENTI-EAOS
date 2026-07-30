# Decision Summary — CRM AR Invoice Issue (C15)

> ADR-0321 decision surface; ADR-0335 boundary applies.
> System-generated governance artifact from PO conversation authorization.

## Purpose

Add a local Draft→Issued gate for AR Invoice so the receivable document becomes
commercially issued without opening Finance engines (no post/ledger/tax/payment).

## Gate In

- ARInvoice status `issued` plus `issue_ar_invoice` (human_confirm)
- Preconditions: invoice draft; DO released; SO confirmed; customer hold clear
- Idempotent `issue_key`; Permission action `issue` on `pkg.crm.ar_invoice`
- Audited `CRM.ARInvoice.Issue` without commercial amounts/keys
- HTTP `POST /v1/crm/ar-invoices/{invoice_id}/issue`

## Gate Out

GL/journal posting, AR ledger balances, allocation, receipt/payment, settlement,
write-off, tax engine, credit note, PSP, WMS/ship, Brain/Twin, Customer360,
Approval Center expansion, email/PDF, cancel/void, C16+.

## Decisions

- Status set: keep `draft`, add `issued` only (no posted/cancelled/void): Accept.
- Columns `issued_at` + `issue_key`: Accept.
- Do not extend C12 confirm-approval policy to invoice issue: Defer.
- No amount/header edits after issued; no cancel/credit in C15: Accept (Defer reopen).

## Product Owner response

**Approve — 2026-07-25 conversation authorization (design only).**
