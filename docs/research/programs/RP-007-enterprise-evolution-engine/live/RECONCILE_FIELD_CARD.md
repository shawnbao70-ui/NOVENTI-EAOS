# RP-007 Reconciliation Field Card

**Program:** Enterprise Evolution Engine  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Scenario:** [RECONCILE_SCENARIO](RECONCILE_SCENARIO.md)

## Field objective

Capture frozen reconciliation drift evidence and human decisions needed to evaluate trigger/recommendation/HOLD hypotheses without executing changes.

## Minimum field artifacts

1. Frozen tokenized SO/DO/inventory/Receipt/AR source/version/time set.
2. Drift chronology and trigger-to-source trace.
3. Reconciliation cadence/tolerance/owner/exception artifacts.
4. Recommendation/HOLD ledger with confidence and competing causes.
5. Simulation assumptions, alternatives, and limitations.
6. Human accept/defer/reject/request-evidence and usefulness records.
7. Tool-call/zero-side-effect, custody, integrity, retention, and falsifier evidence.

## Reconciliation questions

1. Is the proposed trigger based on fresh provenance or duplicated/lagged facts?
2. Which competing cause would change recommendation into HOLD?
3. Are partial/return/dispute/chargeback paths represented in simulation?
4. Did accountable humans retain decision authority and reject/defer when needed?
5. Does the audit prove no recommendation caused a transaction/system side effect?

## HARD HOLD

1. No recommendation-triggered SO/DO/inventory/Receipt/AR mutation.
2. No accept-on-behalf, workflow commit, grant, Brain execute, or Twin authorize.
3. No Promote, floor flip, Eng ingest, product CRUD, or Terminal production action.
4. No knowledge/Const/BP/Kernel/API/UI/code modification.

## Non-claim

This card **≠ Complete** and **≠ Eng ingest**. RP-007 remains Open and `execution_authority=none`.
