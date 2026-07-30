# ADR-0337 — Finance AR Receipt Shell Boundary

**状态：** Accepted（design boundary only）  
**日期：** 2026-07-25  
**里程碑（coding）：** PHX-G310

## Decision

Wave R / F1 opens `noventi.finance` with a minimal AR Receipt header owned by
`pkg.finance.receipt`. Receipt lifecycle in this slice is `draft` | `applied`
(local apply; no bank settle). `apply_receipt_to_invoice` requires a same-tenant
AR Invoice with `status == issued`, amount ≤ invoice total, currency match,
tenant isolation, and idempotency. CRM invoices are observed through
`ARInvoiceReadPort` — Finance does not call `CRMService` and is not Kernel.

Permission is default-deny. Audits record create/apply without PAN, card data,
or PSP secrets. Persistence is Alembic revision
`0046_finance_ar_receipt_g310` under schema `finance`.

## Out

Live PSP/card/ACH provider integration, webhooks, clearing house; multi-invoice
allocation engine; write-off; refunds; FX revaluation; GL journal posting; bank
reconciliation; statement engine; AP; tax filing; Brain/Twin; Inventory ship;
Customer360 product expansion.

## Consequences

- Contiguous coding milestone PHX-G310 after C16 / PHX-G309.
- TRACK-F1 COMPLETE then STOP; do not self-open I1 or live PSP.
- Remaining-balance / multi-receipt over-apply prevention is deferred to a later
  allocation slice.
