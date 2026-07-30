# T2 / T3 Evidence Gap Matrix

**Document ID:** NRI-T2-T3-GAP-MATRIX  
**Version:** 1.0  
**Status:** Active gap inventory — preparation only  
**Last Updated:** 2026-07-23  
**Governing:** [T2_T3_EVIDENCE_INTAKE.md](T2_T3_EVIDENCE_INTAKE.md) · [T2_T3_EVIDENCE_READINESS.md](T2_T3_EVIDENCE_READINESS.md) · [LIVE_VS_SYNTHETIC_FENCE.md](templates/LIVE_VS_SYNTHETIC_FENCE.md)

> No real live submission is registered. Every row is **Open** and every listed live prerequisite is missing/not supplied. Existing synthetic T1 artifacts and dry runs do not clear these gaps.

## Gap semantics

- **Missing artifacts:** no verified live capture form, live artifact manifest, or accessible live source bundle is registered.
- **Missing observer:** no real, named, consented observer is assigned or attested.
- **Missing site/context:** no authorized named site, tenant, cohort, environment, or real observation window is registered.
- “Missing” describes intake state, not evidence that a suitable source or participant cannot exist.

## RP-001…010 matrix

| RP | Program | Missing live artifacts | Missing observer | Missing site / system / cohort | Per-RP gap | Status |
|----|---------|------------------------|------------------|--------------------------------|------------|--------|
| <a id="rp-001"></a>RP-001 | Enterprise Discovery | Live dossier inputs, worksheets, versioned dossier, claim/source trace, provenance | Discovery lead/domain witness not supplied | Enterprise cohort/site/tenant + dated workshop window not supplied | [GAP](programs/RP-001-enterprise-discovery/live/GAP.md) | **Open** |
| <a id="rp-002"></a>RP-002 | Enterprise DNA | Live dossier references, baseline/follow-up scorecards, rater comparison, fit/confounder evidence | Measurement/domain/retest witness not supplied | Named cohort + baseline and follow-up windows not supplied | [GAP](programs/RP-002-enterprise-dna/live/GAP.md) | **Open** |
| <a id="rp-003"></a>RP-003 | Capability First | Live capability graph, source-to-node trace, maturity rationale, roadmap comparison | Capability/domain/comparison witness not supplied | Named mapping cohort + dated session/system access not supplied | [GAP](programs/RP-003-capability-first/live/GAP.md) | **Open** |
| <a id="rp-004"></a>RP-004 | Organization Neutrality | Comparable live context profiles, neutrality audits, defect examples, remediation trace | Neutrality reviewer + representatives of observed forms not supplied | At least two authorized real organization contexts/windows not supplied | [GAP](programs/RP-004-organization-neutrality/live/GAP.md) | **Open** |
| <a id="rp-005"></a>RP-005 | AI Workforce | Live role inventory, duty/responsibility matrix, legal/safety controls, handoff evidence | Workforce/domain/legal observer not supplied | Authorized workforce cohort/site + dated observation window not supplied | [GAP](programs/RP-005-ai-workforce-transformation/live/GAP.md) | **Open** |
| <a id="rp-006"></a>RP-006 | AI Infrastructure | Live topology/inventory references, readiness trace, approval/audit/isolation/supply-chain evidence | Environment custodian + security/OT reviewer not supplied | Authorized tenant/environment + read-only access window not supplied | [GAP](programs/RP-006-ai-infrastructure-platform/live/GAP.md) | **Open** |
| <a id="rp-007"></a>RP-007 | Evolution Engine | Real frozen dossier, trigger/recommendation ledger, simulation, decision/usefulness record | Decision representative + independent/boundary observer not supplied | Named enterprise decision context + dated review window not supplied | [GAP](programs/RP-007-enterprise-evolution-engine/live/GAP.md) | **Open** |
| <a id="rp-008"></a>RP-008 | Smart Factory | Live plant walkthrough, SF/risk assessment, safety approvals, OT/degraded-mode and source metrics | Plant/safety/OT observer not supplied | Authorized plant/cell + site/OT access and dated window not supplied | [GAP](programs/RP-008-smart-factory/live/GAP.md) | **Open** |
| <a id="rp-009"></a>RP-009 | Brain Evolution | Real dossier/input manifest, provenance graph, simulation review, anti-execution/tool audit | Domain/provenance/anti-execution observer not supplied | Authorized advisory environment + dated review window not supplied | [GAP](programs/RP-009-enterprise-brain-evolution/live/GAP.md) | **Open** |
| <a id="rp-010"></a>RP-010 | Future EOM | Real dossier, ES-01…07 trace, consistency/legal/neutrality audit, executive review evidence | Executive/domain/neutrality/boundary observer not supplied | Named enterprise/executive cohort + dated tabletop window not supplied | [GAP](programs/RP-010-future-enterprise-operating-model/live/GAP.md) | **Open** |

## Aggregate

| Measure | Value |
|---------|-------|
| RP rows with missing live artifacts | **10 / 10** |
| RP rows with missing real observer | **10 / 10** |
| RP rows with missing authorized site/context | **10 / 10** |
| Registry state | **10 Open · 0 In-progress · 0 Complete** |
| Readiness floor | **T1 for RP-001…010** |

## Closure rule

A gap cell changes only when a real LC candidate supplies resolvable evidence under the intake process. Clearing one cell does not imply Complete. No row can become Complete until all tier gates and the two-phase V3/V4 transaction pass; tier change still does not imply Board Promote or Eng ingest.
