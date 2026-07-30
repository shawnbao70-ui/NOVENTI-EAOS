# Decision Summary — CRM Quote Line (C7)

> ADR-0321 decision surface; C1–C6 are complete.

## Purpose

Add the smallest honest commercial line snapshot to a draft Quote without
opening a pricing engine.

## Gate In

- QuoteLine under one active same-tenant draft Quote
- Opaque ID, immutable line number, required description
- Positive quantity, non-negative manually supplied unit price
- Server-computed `amount = quantity × unit_price`, rounded to two decimals
- `active` / `archived`, optimistic versioning
- Quote version increments atomically on every line mutation
- Resource `pkg.crm.quote_line`; default-deny, audited writes

## Gate Out

Product/catalog, cost, margin, discount, tax, FX execution, inventory,
approval, automatic pricing, Finance/AR/PSP and fulfillment.

## Decisions

- Manual price is a snapshot, not a recommendation or pricing rule: Accept.
- At least one line is not required to save a draft; C8 confirmation owns that
  gate: Accept.
- Quote line mutation invalidates earlier conversion snapshots through Quote
  versioning: Accept.

## Product Owner response

**Approve — 2026-07-24 conversation authorization (design only).**
