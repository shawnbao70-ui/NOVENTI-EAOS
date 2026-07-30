# PHX-G349 — Fulfillment Qty Conservation Summary

System-generated implementation summary for the approved Fulfillment Qty
Conservation boundary (ADR-0381).

- Alembic tip: `0074_crm_fulfillment_qty_g349`.
- Delivery orders now persist positive quantities per sales-order line and one
  sales order can have multiple delivery orders.
- Creation defaults to remaining quantities and rejects quantities above the
  shipped remainder. Shipment consumes delivery-order quantities only.
- Sales orders aggregate shipped quantity and transition to
  `partially_shipped` or `shipped`; shipment remains idempotent.
- Carrier, WMS, POD, unship, and FX cash scope remain excluded.
