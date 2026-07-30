# RP-008 Commercial Chain Scenario

**Program:** Smart Factory  
**Status:** **Open** · **0 Complete**  
**Live chain/observer assigned:** none / none  
**Protocol:** [COMMERCIAL_CHAIN_OBSERVATION](../../../templates/COMMERCIAL_CHAIN_OBSERVATION.md) · **Terminal lens:** [TERMINAL_SCENARIO_CARD](../../../templates/TERMINAL_SCENARIO_CARD.md)

## Research purpose

Trace a sample-to-cash chain through plant/product/quality/warehouse/OT touchpoints to test Smart Factory overlay evidence while preserving safety and no machine control.

## Chain observation points

1. **Sample:** product/specification, sample build/pick, quality evidence, and Human/Robot/Device duties.
2. **Quote:** manufacturability/capacity/lead-time evidence and approved constraints.
3. **Order:** configuration/specification release, planning, hold/change, and traceability.
4. **Production/shipment:** work/lot/serial events, quality release, pick/pack, safety, and logistics.
5. **Receipt/invoice:** proof, damage/quality dispute, return, and billing trigger.
6. **Payment:** commercial closure signals without exposing/altering financial controls.
7. **Cross-stage:** ERP/MES/quality/historian/warehouse/carrier ID and clock correlation.
8. **Degraded/exception:** offline terminal, delayed event, rework, substitution, safety HOLD, or partial shipment.

## RP model mapping

1. Plant stages map to SF-01…08 domain coverage.
2. Physical duties/exceptions map to PR0–PR4 risk.
3. ERP/MES/OT correlation tests overlay—not MES Kernel—boundaries.
4. Terminal/degraded observations map to line-side supervision needs.
5. Quality/OEE/maintenance/shipment evidence supports bounded evolution/HOLD signals.

## HARD HOLD / prohibited zones

1. HARD HOLD on unsafe access, worker distraction, machine/robot command, recipe/schedule change, or induced failure.
2. HARD HOLD on unrestricted OT topology, vulnerabilities, production payloads, worker identity, or trade secrets.
3. HARD HOLD if Brain/recommendation/Terminal attempts direct machine or shipment control.
4. HARD HOLD on MES kernelization, Twin authorize, Promote/Eng opening, or Const/BP change.

## Required artifacts

1. Dated/tokenized chain and plant observation log.
2. Stage-to-ERP/MES/OT/quality/warehouse/carrier correlation matrix.
3. Process/event-flow and Human/AI/Robot/Device duty map.
4. SF-01…08/PR0–PR4 assessment.
5. Safety/quality/release/HOLD/degraded-mode controlled evidence.
6. Source-backed operational metric and calculation notes.
7. Custody, minimization, integrity, access, retention, gap, and falsifier records.

## Terminal research lens

A future line-side card may show read-only chain evidence, quality/safety gate, degraded state, and accountable HOLD. It cannot command machines, release shipment, or post transactions.

## Cross-reference and non-claim

- Plant/site safety: [SITE_PLAN](SITE_PLAN.md)
- Plant/OT interview guide: [INTERVIEW_PLAN](INTERVIEW_PLAN.md)
- OT/worker/metric custody: [CUSTODY_PLAN](CUSTODY_PLAN.md)

RP-008 remains Open. This scenario does not authorize plant/commercial action, mark Complete, flip a floor, Promote, open Eng work, or change Const/BP.
