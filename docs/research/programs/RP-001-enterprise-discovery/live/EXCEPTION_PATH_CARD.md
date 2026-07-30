# RP-001 Commercial Exception Path Card

**Program:** Enterprise Discovery  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  

## Theme and knowledge mapping

Observe, score, dossier, and HOLD commercial-chain exception paths described by the existing knowledge package—without editing `docs/knowledge/**` or treating its conclusions as live facts. Terms such as **TC** retain the knowledge-package label; the field capture must verify their local meaning. RP-001 discovers evidence and gaps only.

## Exception path observation points

1. **Empty-line Convert:** conversion is attempted with no effective line; capture validation, resulting state, error/audit, and whether a partial object exists.
2. **SO without TC:** observe whether an SO can exist without TC, which rule/exception permits it, and which downstream stages HOLD.
3. **Reopen without inventory impact:** verify reopening changes commercial state but does not reserve/release/adjust inventory unexpectedly.
4. **Receipt ≠ AR:** observe Receipt creation/change while AR remains absent, delayed, disputed, duplicated, or independently controlled.
5. **Dual-write drift:** compare source, integration, spreadsheet/manual, and reporting states after one path succeeds/fails.
6. **Partial/cancel/reject:** trace SO/DO/inventory/Receipt/AR after partial conversion, cancellation, rejection, return, or reversal.
7. **Retry/idempotency:** determine whether repeated Convert/post/reconcile attempts duplicate facts or preserve stable IDs.
8. **Missing reconciliation:** identify absent owner, cadence, tolerance, exception queue, and sign-off.

## RP-001 scoring / HOLD

- Score source identity, timestamps, state/version trace, completeness, contradiction, and falsifiers.
- Dossier every parallel fact and explicitly label “not observed” versus “did not occur.”
- HOLD any conclusion when TC meaning, line semantics, inventory scope, Receipt/AR linkage, or dual-write chronology is unverified.

## Required live evidence

1. Authorized dated/tokenized exception instance(s) and observation log.
2. Before/after SO/DO/inventory/Receipt/AR state/version handles.
3. Convert/reopen/Receipt/AR validation, error, and audit records.
4. TC rule/definition/owner and documented exception basis.
5. Integration/retry/idempotency/dual-write and reconciliation evidence.
6. Real source-custodian accounts corroborated by artifacts.
7. Custody, minimization, integrity, retention, contradictions, and falsifiers.

Missing evidence keeps RP-001 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, legacy extract, Kernel/API/UI, or code change.
3. No Brain execute, Twin authorize, product CRUD, Convert/reopen/post/reconcile action, or acceptance-on-behalf.
4. No synthetic/demo path relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no exception execution or correction.
