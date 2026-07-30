# RP-006 Live Evidence Preparation

**Program:** RP-006 — AI Infrastructure Platform  
**Intake status:** **Open**  
**Current evidence floor:** **T1 (synthetic)**  
**Registered live captures:** none  

This directory prepares a future live infrastructure-readiness deep-dive. It records observable posture only and does not authorize infrastructure, Runtime, Kernel, package, or deployment changes.

## Suggested observation points

- Assess ID-01…08 across identity landing, model/tool hosting, approval bridges, observability, edge/OT coupling, supply-chain trust, isolation, and cost controls.
- Compare a named cloud-native or hybrid/OT context against I0–I4 readiness criteria.
- Trace approval, audit, tenant-isolation, signed-artifact, degraded-mode, and provenance gaps.
- Verify that infrastructure shortcuts never bypass Kernel, Permission, Workflow, or AI Runtime boundaries.

## Required artifact types

- Dated topology and service inventory references, suitably redacted.
- Completed readiness checklist/gap profile with criterion-to-source trace.
- Approval-flow, audit/observability, isolation, and model/tool supply-chain records.
- Edge/degraded-mode or failure-test observations where in scope.
- Real observer attestation plus custodian, access, integrity, and retention metadata.

## Intake use

Copy [the live capture template](../../../templates/LIVE_EVIDENCE_CAPTURE_TEMPLATE.md) as `LC-YYYYMMDD-RP-006-##.md` only after a real environment and observation window exist. Use controlled handles for sensitive topology or security records.

## Honest state

RP-006 remains **Open**, with **0 Complete** live captures. `kernel_bypass: never`. No readiness-floor change, Board Promote, Eng invent, package change, or Const/BP rewrite is implied.

Related: [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md) — Open / 0 Complete; observe/score/HOLD authz exceptions (≠ live evidence).
Related: [APPROVAL_BOUNDARY_CARD](APPROVAL_BOUNDARY_CARD.md) — Open / 0 Complete; observe/score/HOLD approval boundaries (≠ live evidence).
Related: [TAX_FX_APPROVAL_FIELD_CARD](TAX_FX_APPROVAL_FIELD_CARD.md) — Open / 0 Complete; observe/score/HOLD tax/FX/approval field boundaries (≠ live evidence).
