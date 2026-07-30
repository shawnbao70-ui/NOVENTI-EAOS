# RP-008 Reconciliation Field Card

**Program:** Smart Factory  
**Status:** **Open** · **0 Complete**  
**Live plant / observer:** not supplied / not supplied  
**Scenario:** [RECONCILE_SCENARIO](RECONCILE_SCENARIO.md)

## Field objective

Capture safe, read-only evidence reconciling commercial SO/DO/inventory/Receipt/AR with ERP/MES/warehouse/quality/OT and physical-flow facts.

## Minimum field artifacts

1. Tokenized SO specification/version and MES work/lot reference.
2. DO/release/shipment and quality-release/staging evidence.
3. ERP/MES/warehouse/physical inventory by lot/location/`as_of`.
4. Receipt/condition/damage/return and quality evidence.
5. AR/invoice/dispute linkage to delivery/quality facts.
6. Safety/HOLD/degraded/offline/replay and reconciliation records.
7. Restricted custody, site access, minimization, integrity, retention, and falsifiers.

## Reconciliation questions

1. Do SO specification and work/lot versions match?
2. Can DO release be corroborated by quality, staging, and physical evidence?
3. Which clock/location/lot explains inventory divergence?
4. Does Receipt/quality dispute correctly hold invoice/AR progression?
5. How are offline replay, rework, scrap, substitution, and returns reconciled?

## HARD HOLD

1. Stop on any safety risk, worker distraction, zone/access violation, or production impact.
2. No machine/robot command, recipe/schedule/inventory/shipment/Receipt/AR mutation.
3. No Brain execute, Twin authorize, MES kernelization, Promote, floor change, Eng ingest, or CRUD.
4. No knowledge/Const/BP/Kernel/API/UI/MES/package/product-code change.

## Non-claim

This card **≠ Complete** and **≠ Eng ingest**. RP-008 remains Open; no plant or Terminal demo is claimed as live evidence.
