# Decision Summary — CRM Sales Order Confirmation (C8)

> ADR-0321 decision surface; C7 PHX-G300 is complete.

## Purpose

Confirm a C6 Sales Order by freezing current C7 Quote Lines into immutable
Sales Order line snapshots.

## Gate In

- Human confirmation flag and client idempotency key
- Sales Order must be `created`
- Quote must remain active at the conversion's frozen version
- At least one active Quote Line
- Atomic line snapshot, total calculation and `created → confirmed`
- Default-deny `confirm` action on `pkg.crm.sales_order`
- Audited intent/result without text, money or idempotency data

## Gate Out

Approval Center, inventory reservation, fulfillment/release, shipment,
delivery, invoice, Finance/AR/PSP, payment and runtime events.

## Decisions

- Confirmation proves human snapshot acceptance only, not approval, delivery
  or payment: Accept.
- Same idempotency key retries return the confirmed SO; another key conflicts:
  Accept.
- SO lines are immutable snapshots in C8: Accept.

## Product Owner response

**Approve — 2026-07-24 conversation authorization (design only).**
