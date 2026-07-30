# Decision Summary — Inventory DO Ship Ledger (I1 / Wave I)

> ADR-0321 decision surface; ADR-0338 boundary applies.
> System-generated governance artifact from PO conversation authorization.

## Package

`noventi.inventory` — `pkg.inventory.stock` / `pkg.inventory.delivery_ship`

## Purpose

Ship a released Delivery Order once, writing an inventory ledger and decrementing
on_hand. EAOS inventory truth only — not external WMS.

## Scope

### Gate In

- Preconditions: DO `released`; SO `confirmed`; customer not on commercial hold
- `human_confirm` + idempotency; one ship per DO (unique posting)
- Stock availability hard-check fail-closed; ledger entry type `do_ship`
- DO status → `shipped` (CRM status mirror; Inventory owns ship posting)
- Alembic `0047_inventory_do_ship_g311`
- HTTP under `/v1/inventory/...`

### Gate Out

External WMS/3PL adapters, ASN, wave picking, serial/lot advanced, transfers;
returns/RMA; reservations beyond ship; manufacturing; Finance postings; PSP;
Brain/Twin.

## Major architectural decisions

- Inventory observes CRM DO/SO/customer via `DeliveryOrderShipReadPort`.
- Ship posting + ledger + stock balances live in `inventory` schema.
- CRM DO status gains `shipped`; AR create/issue accept released or shipped.

## Open decisions requiring Product Owner input

None for I1 — locked by Wave I instruction.

## Risks

- Ship-before-invoice requires CRM AR guards to accept `shipped` (accepted).
- Stock keyed by sales_order_line_id is a minimal truth model (not SKU warehouse).

## Recommendation

Approve design boundary and authorize coding as PHX-G311.

## Product Owner response

**Approve — 2026-07-25 conversation authorization (design + coding PHX-G311).**
