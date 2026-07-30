# RP-008 EAOS Rewrite Note

**Program:** Smart Factory  
**Status:** **Open** · **0 Complete**  
**Candidate authority:** Research only — no Promote / no Eng invent  
**Base:** [EAOS_REWRITE_CANDIDATE](../../../templates/EAOS_REWRITE_CANDIDATE.md) · [TERMINAL_DEMO_GAP](../../../templates/TERMINAL_DEMO_GAP.md)

## Context

Translate observed Legacy plant/commercial-chain knowledge into Smart Factory overlay candidates without MES kernelization, OT control, or product changes. Chain basis: [CHAIN_SCENARIO](CHAIN_SCENARIO.md).

## RP model mapping

1. Plant chain stages map to SF-01…08 domain evidence.
2. Human/AI/Robot/Device duties/exceptions map to PR0–PR4 risk.
3. ERP/MES/OT/quality correlations map to overlay integration boundaries.
4. Terminal/degraded evidence maps to line-side supervision hypotheses.
5. Quality/OEE/maintenance/shipment outcomes map to bounded evolution/HOLD signals.

## Rewrite candidates

1. Candidate plant-chain evidence overlay linking commercial stage to lot/serial/process/quality/shipment facts.
2. Candidate safety/release/HOLD fact vocabulary that never commands equipment.
3. Candidate degraded/offline/reconciliation knowledge record with source clocks and custody.
4. Candidate line-side Terminal read-only evidence card with safety gate and no machine action.

## HARD HOLD / prohibited zones

1. HARD HOLD on MES/OT schema/API/event implementation, machine command, recipe/schedule/safety-control change, or induced test.
2. HARD HOLD on worker surveillance, OT vulnerability/topology leakage, or production secrets.
3. HARD HOLD if Brain/Twin/Terminal candidates control machines, release shipment, or authorize safety.
4. HARD HOLD on MES kernelization, knowledge/Const/BP rewrite, Promote, or Eng invent.

## Required live evidence

1. Dated authorized plant and commercial-chain observation.
2. ERP/MES/OT/quality/warehouse event/source correlation.
3. Safety/release/HOLD/degraded-mode controlled artifacts.
4. Real plant/safety/OT roles’ accounts corroborated by records.
5. Source-backed quality/OEE/maintenance calculations and falsifiers.
6. Restricted custody, minimization, integrity, access, and retention records.

## Research disposition

Candidates remain overlay research. RP-008 remains Open; this note does not authorize plant/product change, mark Complete, flip a floor, Promote, open Eng work, or change Const/BP.
