# RP-008 Reconciliation Observation Scenario

**Program:** Smart Factory  
**Status:** **Open** · **0 Complete**  
**Assigned live plant / observer:** none / none  

## Mapping theme

Observe how commercial **SO/DO/inventory/Receipt/AR** facts reconcile with plant, MES, warehouse, quality, OT, and physical-flow facts. RP-008 evaluates overlay/risk evidence; it never changes MES/ERP, inventory, machines, shipment, Receipt, or AR.

| Fact family | Smart Factory observation | Score / hold treatment |
|-------------|---------------------------|------------------------|
| SO | configured product/quantity/date versus plant demand/specification | HOLD on version mismatch |
| DO | release/allocation/shipment versus work/lot/quality readiness | No release action |
| Inventory | ERP/MES/warehouse/physical on-hand/allocated/in-transit | Score site/clock/lot evidence |
| Receipt | delivery/proof/condition/return versus quality/lot records | HOLD on missing safety/quality proof |
| AR | invoice/payment state versus delivery/quality dispute | Observe only; no financial action |

## RP-008 model treatment

1. Cross-system facts map to SF-01…08 domain evidence.
2. Physical/quality/safety exceptions map to PR0–PR4 risk.
3. ERP/MES/OT correlation tests overlay, not MES Kernel, boundaries.
4. Offline/replay/manual work maps to degraded-mode evidence.
5. Reconciliation drift may inform advisory HOLD only.

## Observable reconciliation checkpoints

1. SO configuration/version differs from MES work instruction or product specification.
2. DO release/shipment state conflicts with quality release, lot readiness, or physical staging.
3. ERP, MES, warehouse, historian, and physical inventory disagree by lot/location/as-of.
4. Receipt quantity/condition differs from shipment, quality, damage, or return evidence.
5. AR invoice/open/paid state proceeds despite quality/Receipt dispute.
6. Dual-write/manual scan/spreadsheet updates one system but not others.
7. Reconciliation/勾兑 ownership/cadence/tolerance is absent across ERP/MES/warehouse.
8. Offline terminal/device replay duplicates or reorders inventory/Receipt events.
9. Partial/rework/scrap/substitution/return paths break chain correlation.

## Required live evidence

1. Authorized dated plant/commercial observation and tokenized chain IDs.
2. ERP/MES/warehouse/quality/OT/physical inventory correlation evidence.
3. SO-spec/work-order and DO-quality/shipment controlled artifacts.
4. Receipt/damage/return and AR-dispute linkage.
5. Safety/quality/release/HOLD and degraded/replay evidence.
6. Real plant/safety/OT/source custodians corroborated by artifacts.
7. Restricted custody, minimization, integrity, access, retention, and falsifiers.

Until verified, RP-008 stays **Open / 0 Complete**.

## HARD HOLD / prohibited zones

- No Promote, floor change, or Eng soft-queue ingest.
- No Const/BP, `docs/knowledge/**`, Kernel/API/UI, MES, package, or product CRUD/code change.
- No machine/robot command, recipe/schedule/inventory/shipment/Receipt/AR mutation.
- No Brain execute, Twin authorize, MES kernelization, or safety bypass.
- No plant/Terminal demo relabeled live Complete.

## Explicit non-claims

This file **≠ Complete** and **≠ Eng soft-queue ingest**. It observes/scores/holds Smart Factory reconciliation evidence only.
