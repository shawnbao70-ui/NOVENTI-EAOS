# RP-007 Live Evidence Preparation

**Program:** RP-007 — Enterprise Evolution Engine  
**Intake status:** **Open**  
**Current evidence floor:** **T1 (synthetic)**  
**Registered live captures:** none  

This directory prepares advisory-only live evaluation of evolution recommendations. It cannot create execution authority or turn existing synthetic trigger tests into live evidence.

## Suggested observation points

- Run Evaluate → Trigger → Recommend → Explain/Simulate → Human Decide → Learn against a real, dated dossier.
- Include deliberate should-HOLD cases and all recommendation classes: ORG, AI, AUTO, ROBOT, CAP, TERM, and HOLD.
- Measure usefulness, provenance completeness, disagreement, acceptance/defer/reject outcomes, and checklist-baseline comparison.
- Verify recommendations do not self-execute, bypass Permission/Workflow, or imply Twin authorization.

## Required artifact types

- Versioned real-dossier reference and frozen input manifest.
- Trigger evaluation and recommendation ledger with evidence/provenance links.
- Simulation/explanation output and blind usefulness-scoring record.
- Human decision record, including HOLD, defer, reject, exceptions, and falsifiers.
- Real observer attestation with controlled retention/provenance metadata.

## Intake use

For a real advisory exercise, copy [the live capture template](../../../templates/LIVE_EVIDENCE_CAPTURE_TEMPLATE.md) as `LC-YYYYMMDD-RP-007-##.md`. Record decisions as observations, not as execution commands.

## Honest state

RP-007 remains **Open**, with **0 Complete** live captures. `execution_authority=none`; Brain execute and Twin authorize remain fail-closed. No readiness-floor change, Board Promote, Eng ingest, or Const/BP rewrite is implied.

Related: [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md) — Open / 0 Complete; observe/score/HOLD authz exceptions (≠ live evidence).
Related: [APPROVAL_BOUNDARY_CARD](APPROVAL_BOUNDARY_CARD.md) — Open / 0 Complete; observe/score/HOLD approval boundaries (≠ live evidence).
Related: [TAX_FX_APPROVAL_FIELD_CARD](TAX_FX_APPROVAL_FIELD_CARD.md) — Open / 0 Complete; observe/score/HOLD tax/FX/approval field boundaries (≠ live evidence).
