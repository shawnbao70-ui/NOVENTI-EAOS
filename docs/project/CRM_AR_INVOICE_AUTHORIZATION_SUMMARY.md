# Decision Summary — CRM AR Invoice Shell (C10)

> ADR-0321 decision surface; ADR-0315 rewrite boundary applies.

## Purpose

Create an auditable draft AR Invoice header that traces a Delivery Order and
its confirmed Sales Order without opening a receivable or posting accounting.

## Gate In

- One idempotent draft invoice shell per same-tenant Delivery Order
- Mandatory trace to the DO and its confirmed SO
- Frozen customer, currency and total source trace
- Default-deny create/read on `pkg.crm.ar_invoice`
- Audited create without commercial values or idempotency data

## Gate Out

Issue/post/cancel/credit note, AR ledger, allocation, receipt, settlement,
write-off, tax calculation, GL, PSP, AP and events.

## Decisions

- Exactly one shell per DO until partial invoicing has a Product Gate: Accept.
- `draft` is not an opened receivable or tax invoice: Accept.
- Source amount is trace evidence only; no balance is created: Accept.

## Product Owner response

**Approve — 2026-07-24 conversation authorization (design only).**
