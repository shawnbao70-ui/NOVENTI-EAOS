# RP-003 Reconciliation Observation Scenario

**Program:** Capability First  
**Status:** **Open** · **0 Complete**  
**Assigned live context / observer:** none / none  

## Mapping theme

Observe the capabilities needed to reconcile parallel **SO/DO/inventory/Receipt/AR** facts, score their maturity/automation affinity, and hold unsupported mappings. Capabilities describe outcomes; they neither execute reconciliation nor grant authority.

| Fact family | Capability observation | Score / hold treatment |
|-------------|------------------------|------------------------|
| SO | Order-state integrity and change-control outcome | HOLD if node is merely a department/system |
| DO | Fulfillment commitment and release traceability | Score evidence/control maturity |
| Inventory | Inventory truth reconciliation across location/time | HOLD on ambiguous scope/as-of |
| Receipt | Delivery/receipt assurance and discrepancy resolution | Score outcome and exception evidence |
| AR | Receivable matching, dispute, allocation, and closure | HOLD on missing financial controls |

## RP-003 model treatment

1. Reconciliation outcomes become candidate capability nodes.
2. SO→DO→inventory→Receipt→AR dependencies become graph edges.
3. Evidence consistency and control repeatability support L0–L4 maturity.
4. Rule volume, exception density, risk, and supervision support A0–A4 affinity.
5. Ownership remains a role class; Capability≠Organization≠Permission.

## Observable reconciliation checkpoints

1. SO version/state drift reveals an order-integrity capability gap.
2. DO split/release/cancel lacks trace to SO commitment and approval.
3. Inventory allocation and shipment facts diverge by system/location/as-of.
4. Receipt partial/refusal/damage lacks an accountable discrepancy-resolution path.
5. AR invoice/open/paid state fails to reconcile to receipt/payment allocation.
6. Dual-write/manual bridge duplicates work or creates hidden dependencies.
7. Reconciliation/勾兑 absence has no capability owner, service level, tolerance, or evidence.
8. Exception paths cross departments but cannot be represented as end-to-end capability outcomes.
9. Automation appears feasible on happy path but fails under partial/return/dispute cases.

## Required live evidence

1. Dated/tokenized SO/DO/inventory/Receipt/AR observations.
2. Stage outcome, source, control, and owner-role evidence.
3. Versioned capability graph and source-to-node/dependency trace.
4. Reconciliation exception/cadence/tolerance/audit artifacts.
5. Maturity and automation-affinity rationale with counter-evidence.
6. Capability-versus-department comparison under a declared rubric.
7. Custody, access, minimization, integrity, retention, and falsifiers.

Until verified, RP-003 remains **Open / 0 Complete**.

## HARD HOLD / prohibited zones

- No Promote, floor change, or Eng soft-queue ingest.
- No Const/BP, `docs/knowledge/**`, Kernel/API/UI, package, or product-code change.
- No product CRUD, Brain execute, Twin authorize, or Capability→grant.
- No reconciliation posting, inventory adjustment, Receipt acceptance, or AR action.
- No synthetic graph/Terminal demo relabeled as live evidence.

## Explicit non-claims

This scenario **≠ Complete** and **≠ Eng soft-queue ingest**. It observes/scores/holds capability evidence and performs no execution.
