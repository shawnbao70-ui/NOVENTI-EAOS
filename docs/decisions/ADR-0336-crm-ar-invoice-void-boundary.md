# ADR-0336 — CRM AR Invoice Void Boundary

**状态：** Accepted（design boundary only）  
**日期：** 2026-07-25  
**里程碑（coding）：** PHX-G309

## Decision

C16 adds ARInvoice status `voided` and `void_ar_invoice` as a local void
command. Void requires human confirmation and a non-empty reason (1..500),
applies only to issued invoices, is idempotent by `void_key`, and is authorized
by default-deny action `void` on `pkg.crm.ar_invoice`.

Voided is not a credit memo and does not reverse GL or AR ledger balances.
Reason is retained on the entity; audit details remain empty per CRM audit norms.
No cascade void of Delivery Order, Sales Order, or Quote. C12 confirm-approval
policy is not extended to void in this slice.

## Out

Credit note, AR reversal posting, GL/journal, receipt/payment/allocation, tax,
PSP, write-off, reopen-to-draft, WMS/ship, Approval Center expansion, email/PDF,
Brain/Twin, and C17+.
