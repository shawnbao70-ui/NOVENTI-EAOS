# RP-009 Dual-Write Field Card

**Program:** Enterprise Brain Evolution  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md) · [RECONCILE_SCENARIO](RECONCILE_SCENARIO.md) · [RECONCILE_FIELD_CARD](RECONCILE_FIELD_CARD.md)

## Field objective

Observe, score, and HOLD dual-write / parallel-fact situations for SO/DO/inventory/Receipt/AR (and adjacent mirrors) through the **advise/HOLD only** lens — Brain may advise on dual-write risk; must not execute corrections. Do not edit `docs/knowledge/**` or treat knowledge-pack conclusions as live facts.

## Dual-write / parallel-fact observation points

1. Advice that picks one balance view as truth without custody
2. Advice to reship after Reopen when ghost ledger blocks
3. Advice to treat credit_limit as enforced when gates are absent
4. Advice conflating Complete with POD
5. Advice that invents AR allocation from Receipt totals
6. Any auto-write proposal against dual stores → HARD HOLD

## Scoring / HOLD (RP-009)

- Score provenance, clocks/`as_of`, completeness, contradiction, and which writer “won” last.
- Dossier every parallel store explicitly; label “not observed” versus “did not occur.”
- HOLD when a single-truth narrative would collapse dual writers without custody evidence.

## Required live evidence

1. Authorized, dated/tokenized extracts from each parallel store with version/`as_of`.
2. Before/after handles for at least one dual-write event (Ship, Receipt, Convert, Reopen, or Post AR).
3. Owner/cadence/tolerance/exception-queue evidence for reconciliation — or documented absence.
4. Retry/idempotency/dual-path audit for the same business key.
5. Real source-custodian accounts corroborated by artifacts.
6. Custody, minimization, integrity, retention, contradictions, and falsifiers.

Missing evidence keeps this RP **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, Kernel/API/UI, or product code change.
3. No Brain execute, Twin authorize, product CRUD, or acceptance-on-behalf writes.
4. No synthetic/demo dual-write relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no correction of dual stores.
