# ADR-0338 — Inventory DO Ship Ledger Boundary

**状态：** Accepted（design boundary only）  
**日期：** 2026-07-25  
**里程碑（coding）：** PHX-G311

## Decision

Wave I / I1 opens `noventi.inventory` with a minimal Delivery Order ship
command. Shipping a released DO (confirmed SO, customer not on commercial hold)
requires human confirmation and an idempotency key, creates exactly one ship
posting per DO, writes `do_ship` ledger rows, and decrements on_hand with a
fail-closed availability check.

CRM Delivery Order status mirrors to `shipped`. Inventory observes CRM state
through `DeliveryOrderShipReadPort` and updates CRM DO status in the same
persistence unit of work without calling `CRMService`. This is EAOS inventory
truth, not an external WMS integration.

## Out

External WMS/3PL adapters, ASN, wave picking, advanced serial/lot, transfers,
returns/RMA, reservations beyond ship, manufacturing, Finance postings, PSP,
Brain/Twin.

## Consequences

- Contiguous coding milestone PHX-G311 after F1 / PHX-G310.
- Alembic `0047_inventory_do_ship_g311` owns inventory schema and the CRM DO
  status vocabulary expansion to include `shipped`.
- TRACK-I1 COMPLETE then STOP; do not self-open N1.
