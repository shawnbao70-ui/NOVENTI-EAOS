# RP-008 Commercial Exception Path Card

**Program:** Smart Factory  
**Status:** **Open** · **0 Complete**  
**Live plant / observer:** not supplied / not supplied  

## Theme and knowledge mapping

Observe plant/ERP/MES/OT/quality consequences of knowledge-package commercial exception conclusions without editing knowledge, inducing failures, or controlling machines.

## Exception path observation points

1. Empty-line Convert: whether plant demand/work instruction is absent, partial, or erroneously created.
2. SO without TC: whether specification/planning/release remains held and which evidence governs.
3. Reopen without inventory impact: confirm no reservation, lot, work, pick, or stock side effect.
4. Receipt≠AR: delivery/quality/return evidence versus billing/financial separation.
5. Dual-write drift: ERP/MES/warehouse/quality/historian/manual scan mismatch.
6. Partial/cancel/rework/scrap/substitution/return effects on lot/location/DO/Receipt.
7. Offline terminal/device replay causing duplicate/reordered state.
8. Missing reconciliation ownership/cadence/tolerance across plant/commercial systems.

## RP-008 scoring / HOLD

- Score SF-01…08 coverage, PR0–PR4 physical risk, source clocks, and safety controls.
- Preserve overlay—not MES Kernel—boundaries.
- HOLD on any safety, quality, worker, OT, provenance, or no-control uncertainty.

## Required live evidence

1. Authorized dated plant exception observation and induction/access record.
2. Tokenized SO/DO/inventory/Receipt/AR and ERP/MES/OT correlation.
3. Work/lot/quality/release/HOLD and physical inventory evidence.
4. Offline/replay/rework/return exception records.
5. Real plant/safety/OT/source custodians corroborated by artifacts.
6. Before/after state showing no unintended inventory impact on Reopen.
7. Restricted custody, minimization, integrity, retention, and falsifiers.

Without evidence, RP-008 stays **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor change, or Eng soft-queue ingest.
2. No knowledge/Const/BP/legacy extract/Kernel/API/UI/MES/package/code change.
3. No machine/robot/product CRUD, recipe/schedule/inventory/Receipt/AR mutation.
4. No Brain execute, Twin authorize, safety bypass, induced exception, or demo relabeling.

## Non-claim

This file **≠ Complete** and **≠ Eng soft-queue ingest**. It opens no plant or product authority.
