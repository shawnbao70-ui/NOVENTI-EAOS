# Inventory Controlled Reship G370 Summary

**Status:** System-generated governance artifact — COMPLETE  
**Milestone:** PHX-G370  
**Authorization:** `INV_CONTROLLED_RESHIP_CODING_AUTHORIZATION_SUMMARY.md`

- Added Alembic revision `0090_inventory_controlled_reship_g370` revising
  `0089_inventory_ship_pod_g367`.
- Dropped unique `(tenant_id, delivery_order_id)` on
  `inventory.delivery_ship_postings`; kept unique `(tenant_id, idempotency_key)`;
  added index `(tenant_id, delivery_order_id, status)`.
- After unship, a **new** ship with a **new** idempotency key creates a new
  posting identity; reuse of a prior (unshipped) ship key conflicts.
- At most one `shipped` posting per DO at a time; unshipped history is retained.
- Contract coverage: ship→unship→reship(new key) OK, old key rejected, stock
  decrements again; g355/g367 remain green.

**TRACK-CONTROLLED-RESHIP COMPLETE / TRACK-G370 COMPLETE**

Tip verified: `0090_inventory_controlled_reship_g370`  
Next: PHX-G371 (Treasury transfer + FX) queued.
