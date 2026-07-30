# ADR-0339 — Finance AR Credit Note Shell Boundary

**状态：** Accepted（design boundary only）  
**日期：** 2026-07-25  
**里程碑（coding）：** PHX-G312

## Decision

Wave N / N1 adds an AR Credit Note shell under `noventi.finance` /
`pkg.finance.credit_note`. A credit note may be created against a same-tenant AR
Invoice whose status is `issued` or `voided`, with amount ≤ invoice total and
currency/customer inherited from the invoice. Lifecycle in this slice is
`draft` | `issued` where issue is a local document state — not GL posting and
not a PSP refund.

CRM invoices are observed through `ARInvoiceReadPort`. Permission is
default-deny. Audits record create/issue with empty details. Persistence is
Alembic revision `0048_finance_ar_credit_note_g312` in schema `finance`.

## Out

Full GL/chart-of-accounts/journal/period close; tax authority credit filing; PSP
refund execution; multi-invoice credit application engine; bad-debt write-off
automation; Brain/Twin.

## Consequences

- Contiguous coding milestone PHX-G312 after I1 / PHX-G311.
- TRACK-N1 COMPLETE then STOP; do not self-open Z1.
