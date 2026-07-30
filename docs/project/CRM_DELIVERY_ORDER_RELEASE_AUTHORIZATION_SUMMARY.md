# Decision Summary — CRM Delivery Order Release (C14)

> ADR-0321 decision surface; ADR-0334 boundary applies.
> System-generated governance artifact from PO conversation authorization.

## Purpose

Add a local Draft→Released gate for Delivery Order so fulfillment can mark
“ready to execute” without opening inventory ledger or ship posting.

## Gate In

- DeliveryOrder status `released` plus `release_delivery_order`
  (human_confirm, SO confirmed, commercial_hold clear)
- Idempotent `release_key`; Permission action `release` on `pkg.crm.delivery_order`
- `create_ar_invoice` requires DO `released` (fail-closed tighten)
- Audited `CRM.DeliveryOrder.Release` without commercial amounts/keys
- HTTP `POST /v1/crm/delivery-orders/{id}/release`

## Gate Out

WMS/inventory ship/deduction/reservation, packing slips, carrier/tracking,
PSP, GL, AR invoice issue/post, Brain/Twin, Customer360, Approval Center
expansion, email/PDF, cancel/reopen, C15+.

## Decisions

- Status set: keep `draft`, add `released` only (no shipped/delivered): Accept.
- Columns `released_at` + `release_key` for idempotency parity: Accept.
- AR invoice shell requires released DO (not draft): Accept.
- No re-draft / cancel / reopen in this slice: Accept (Defer).

## Product Owner response

**Approve — 2026-07-25 conversation authorization (design only).**
