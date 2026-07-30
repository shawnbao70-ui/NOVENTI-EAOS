# PHX-G355 Summary — Controlled Unship

- Added Alembic revision `0079_inventory_controlled_unship_g355`. A ship posting records its `unshipped_at` timestamp and `unship_key`; the reversal is an immutable `do_unship` inventory ledger entry.
- `POST /v1/inventory/delivery-orders/{id}/unship` requires explicit human confirmation and `inventory.delivery_order.unship` Permission. It accepts only shipped delivery orders, is idempotent for the original key, and conflicts for a different key.
- A controlled unship restores inventory, decrements SO shipped quantity, restores SO fulfillment remaining quantity, and returns the DO to `released`. It neither reopens an order nor creates an RMA, credit note, or other return artifact.
