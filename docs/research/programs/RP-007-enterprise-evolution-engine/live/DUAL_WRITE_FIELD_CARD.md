# RP-007 Dual-Write Field Card

**Program:** Enterprise Evolution Engine  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md) · [RECONCILE_SCENARIO](RECONCILE_SCENARIO.md) · [RECONCILE_FIELD_CARD](RECONCILE_FIELD_CARD.md)

## Field objective

Observe, score, and HOLD dual-write / parallel-fact situations for SO/DO/inventory/Receipt/AR (and adjacent mirrors) through the **evolution proposals** lens — HOLD evolution proposals that assume single-writer truth. Do not edit `docs/knowledge/**` or treat knowledge-pack conclusions as live facts.

## Dual-write / parallel-fact observation points

1. Evolution candidate that collapses Receipt and AR without evidence
2. Proposal to treat Reopen as inventory reversal without ledger link
3. Proposal to normalize quote statuses across dual vocabularies
4. Proposal for multi-DO without remaining-qty capability
5. Proposal for credit hold without gate evidence
6. Proposal for numbering sequences without collision disposition

## Scoring / HOLD (RP-007)

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
