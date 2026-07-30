# RP-008 Live Evidence Preparation

**Program:** RP-008 — Smart Factory  
**Intake status:** **Open**  
**Current evidence floor:** **T1 (synthetic)**  
**Registered live captures:** none  

This directory prepares an observational plant capture for the Smart Factory specialization overlay. It does not authorize machine control, safety changes, MES modification, or an EAOS core fork.

## Suggested observation points

- Apply SF-01…08 and PR0–PR4 to a named plant/cell with a real safety stakeholder present.
- Observe Human/AI/Robot/Device duties, line-side terminal use, approval handoffs, OT events, and degraded/offline behavior.
- Trace safety vetoes, exception density, OEE/quality/maintenance claims, and simulation-before-change behavior.
- Verify the specialization remains an overlay: no MES kernelization and no Brain-to-machine control path.

## Required artifact types

- Dated plant/cell scope and redacted walkthrough record.
- SF domain/risk assessment, process or event-flow map, and actor-duty matrix.
- Safety-case references, approval/veto records, and degraded-mode observations.
- Redacted OEE/quality/maintenance evidence with source and calculation notes.
- Named safety observer attestation and retention/provenance metadata when real evidence exists.

## Intake use

Copy [the live capture template](../../../templates/LIVE_EVIDENCE_CAPTURE_TEMPLATE.md) as `LC-YYYYMMDD-RP-008-##.md` only for a real plant observation. Keep safety, OT, tenant, and production payloads in controlled stores.

## Honest state

RP-008 remains **Open**, with **0 Complete** live captures. `mes_kernelization: never`; `machine_control_from_brain: never`. No readiness-floor change, Board Promote, Eng invent, or Const/BP rewrite is implied.

Related: [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md) — Open / 0 Complete; observe/score/HOLD authz exceptions (≠ live evidence).
Related: [APPROVAL_BOUNDARY_CARD](APPROVAL_BOUNDARY_CARD.md) — Open / 0 Complete; observe/score/HOLD approval boundaries (≠ live evidence).
Related: [TAX_FX_APPROVAL_FIELD_CARD](TAX_FX_APPROVAL_FIELD_CARD.md) — Open / 0 Complete; observe/score/HOLD tax/FX/approval field boundaries (≠ live evidence).
