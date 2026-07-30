# Decision Summary — CRM Delivery Order Shell (C9)

> ADR-0321 decision surface; ADR-0314 rewrite boundary applies.

## Purpose

Create an auditable Delivery Order instruction header from a confirmed Sales
Order without allocating or deducting inventory.

## Gate In

- One idempotent Delivery Order shell per confirmed same-tenant SO
- Frozen SO/Quote/Requirement, currency and total trace
- Opaque ID, system code, `draft` status
- Default-deny create/read on `pkg.crm.delivery_order`
- Audited create without commercial values or idempotency data

## Gate Out

Delivery lines/partial quantities, reservation, warehouse, pick/pack, stock
deduction, Ship/Complete/Reopen, carrier/POD, returns and Finance.

## Decisions

- Exactly one shell per SO until a quantity-allocation Gate exists: Accept.
- `draft` means instruction header only, not shipment evidence: Accept.
- SO remains `confirmed`; C9 performs no fulfillment status mutation: Accept.

## Product Owner response

**Approve — 2026-07-24 conversation authorization (design only).**
