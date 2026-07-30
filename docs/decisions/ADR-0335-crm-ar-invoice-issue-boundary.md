# ADR-0335 — CRM AR Invoice Issue Boundary

**状态：** Accepted（design boundary only）  
**日期：** 2026-07-25  
**里程碑（coding）：** PHX-G308

## Decision

C15 adds ARInvoice status `issued` and `issue_ar_invoice` as a local issue
command. Issue requires human confirmation, a draft invoice, a released Delivery
Order, a confirmed Sales Order, and a commercially clear customer. It is
idempotent by `issue_key` and authorized by default-deny action `issue` on
`pkg.crm.ar_invoice`.

Issued is not posted. No GL journal, AR ledger balance, tax fact, receipt,
payment, allocation, or credit-note product surfaces are opened. C12
confirm-approval policy is not extended to invoice issue in this slice.

## Out

GL/posting, ledger balances, tax, receipt/payment, settlement, write-off,
credit note, PSP, WMS/ship, Approval Center expansion, email/PDF, Brain/Twin,
and C16+.
