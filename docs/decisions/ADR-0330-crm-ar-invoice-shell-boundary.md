# ADR-0330 — CRM AR Invoice Shell Boundary

**状态：** Accepted（design boundary only）  
**日期：** 2026-07-24  
**上位边界：** ADR-0315

## Decision

C10 creates one tenant-scoped `ARInvoice` draft shell from a C9 Delivery
Order. It references that DO and its confirmed Sales Order and freezes the
customer, currency and total source trace.

The shell is intentionally not issued or posted. It creates no receivable,
balance, tax fact, payment obligation, allocation or accounting entry.

Without a partial-invoicing model, tenant/DO and tenant/SO uniqueness prevent
duplicate amount claims. Permission is default-deny. Audit details exclude
commercial values and keys.

## Out

Issue/post/cancel, lines, tax/discount/FX, credit notes, receipts, allocations,
write-off, PSP, reconciliation, GL, AP and events.
