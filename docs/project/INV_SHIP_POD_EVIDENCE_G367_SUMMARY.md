# Inventory Ship POD / Evidence G367 Summary

**Status:** System-generated governance artifact — COMPLETE  
**Milestone:** PHX-G367  
**Authorization:** `INV_SHIP_POD_EVIDENCE_CODING_AUTHORIZATION_SUMMARY.md`

- Added Alembic revision `0089_inventory_ship_pod_g367`.
- Persist optional `pod_ref` / `pod_captured_at` on `inventory.delivery_ship_postings`.
- Tenant policy `ship_pod_required` (default false) at
  `/v1/inventory/policies/ship-pod`; when true, ship fails without `pod_ref`.
- Ship request accepts optional `pod_ref`; GET ship posting exposes evidence.
- Contract coverage verifies default optional path, required-policy reject/accept,
  GET exposure, and closed OpenAPI.

**TRACK-SHIP-POD COMPLETE / TRACK-G367 COMPLETE**
