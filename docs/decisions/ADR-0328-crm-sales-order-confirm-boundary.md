# ADR-0328 — CRM Sales Order Confirmation Boundary

**状态：** Accepted（design boundary only）  
**日期：** 2026-07-24

## Decision

C8 confirms a `created` Sales Order only after explicit human confirmation,
an unchanged Quote-version snapshot and at least one active Quote Line.

One transaction copies active Quote Lines into immutable Sales Order Lines,
computes `total_amount`, records `confirmed_at` and transitions the order to
`confirmed`. A confirmation idempotency key makes retries stable.

Permission uses `confirm` on `pkg.crm.sales_order`. Audit details exclude line
text, monetary values and keys.

## Out

Central approval, inventory/fulfillment/shipping, delivery, returns,
Finance/AR/PSP, payment, invoices, commissions and events.
