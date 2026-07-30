# Decision Summary — CRM Sales Order Trace (C6)

> ADR-0321 decision surface; ADR-0312 rewrite boundary applies.

## Purpose

Create the minimal Sales Order trace header by consuming one C5 conversion
instruction. This is not fulfillment or finance.

## Gate In

- One Sales Order per same-tenant `ready` QuoteConversion
- Frozen Quote/Requirement/currency trace and system code
- Separate client idempotency key
- Atomic SO creation + conversion `ready → consumed`
- Resource `pkg.crm.sales_order`; default-deny create/read; audited write

## Gate Out

Lines, quantity, price, amount, terms, approval, Finance/AR/PSP, inventory,
allocation, shipment, delivery, returns, commissions and events.

## Decisions

- Current Quote version must equal the conversion snapshot: Accept.
- SO status is only `created`; no fulfillment lifecycle: Accept.
- Retry with same key returns existing SO; another key conflicts: Accept.

## Product Owner response

**Approve — 2026-07-24 conversation preauthorization (design only).**
