# Decision Summary — CRM AR Invoice Void (C16)

> ADR-0321 decision surface; ADR-0336 boundary applies.
> System-generated governance artifact from PO conversation authorization.

## Purpose

Add a local Issued→Voided gate so operators can retract an issued-but-not-posted
AR Invoice without opening Finance credit/reversal engines.

## Gate In

- ARInvoice status `voided` plus `void_ar_invoice` (human_confirm, reason 1..500)
- Only issued invoices may void; draft conflicts; same void key idempotent
- Permission action `void` on `pkg.crm.ar_invoice` (default-deny)
- Entity columns `voided_at`, `void_key`, `void_reason`
- Audit `CRM.ARInvoice.Void` with empty details (reason on entity only)
- HTTP `POST /v1/crm/ar-invoices/{invoice_id}/void`

## Gate Out

Credit note, AR reversal posting, GL/journal, receipt/payment/allocation, tax,
PSP, write-off, reopen-to-draft, cascade void of DO/SO/Quote, Approval Center
expansion, email/PDF, C17+.

## Decisions

- Status set: keep `draft`/`issued`, add `voided` only: Accept.
- Reason stored on entity; excluded from audit details: Accept.
- Do not extend C12 confirm-approval to void (human_confirm only): Defer.
- No recreate/reissue from same DO after void in this slice: Accept (Defer).

## Product Owner response

**Approve — 2026-07-25 conversation authorization (design only).**
