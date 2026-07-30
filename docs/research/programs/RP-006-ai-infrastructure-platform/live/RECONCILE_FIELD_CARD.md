# RP-006 Reconciliation Field Card

**Program:** AI Infrastructure Platform  
**Status:** **Open** · **0 Complete**  
**Live environment / observer:** not supplied / not supplied  
**Scenario:** [RECONCILE_SCENARIO](RECONCILE_SCENARIO.md)

## Field objective

Capture read-only infrastructure evidence explaining SO/DO/inventory/Receipt/AR drift, retries, dual-write, observability, isolation, and degraded reconciliation.

## Minimum field artifacts

1. Authorized source/integration/system/version inventory.
2. Tokenized SO/DO/inventory/Receipt/AR correlation IDs and source clocks.
3. Identity, tenant-isolation, approval-bridge, and access-audit evidence.
4. Retry/idempotency/order/replay and reconciliation-job telemetry.
5. Degraded/offline/cache/edge synchronization evidence.
6. Exception/failure ownership, alert, tolerance, and sign-off records.
7. Security custody, redaction, minimization, integrity, retention, and falsifiers.

## Reconciliation questions

1. Which source is authoritative for each fact and during which state/window?
2. Can retries, duplicates, ordering, cache lag, and replay explain the drift?
3. Does reconciliation fail closed without bypassing Permission/Workflow?
4. Are tenant/site boundaries preserved during correlation and exports?
5. Which unavailable evidence is a gap rather than a failed control?

## HARD HOLD

1. No active probing, configuration, production-impacting query, posting, or repair.
2. No credentials/secrets/vulnerability/topology/tenant leakage or Kernel bypass.
3. No Promote, floor change, Eng ingest, Brain execute, Twin authorize, or CRUD.
4. No knowledge/Const/BP/Kernel/API/UI/package/product-code modification.

## Non-claim

This card **≠ Complete** and **≠ Eng ingest**. RP-006 remains Open; it authorizes no infrastructure action.
