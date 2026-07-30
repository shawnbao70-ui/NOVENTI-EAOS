# Live vs Synthetic Evidence Fence

**Template ID:** NRI-TPL-LIVE-SYNTH-FENCE  
**Version:** 1.0  
**Status:** Active evidence-classification guardrail  
**Last Updated:** 2026-07-23  
**Governing:** [T2_T3_EVIDENCE_INTAKE.md](../T2_T3_EVIDENCE_INTAKE.md) · [T2_T3_EVIDENCE_READINESS.md](../T2_T3_EVIDENCE_READINESS.md)

> Synthetic/tabletop work is useful for protocol validation, but remains **T1**. It cannot be relabeled, combined, narrated, or attested into live T2/T3 evidence.

## Classification fence

| Dimension | Synthetic / dry run — T1 | Live — T2 | Live — T3 |
|-----------|---------------------------|-----------|-----------|
| Context | Invented, anonymized, transformed, sampled, or scripted scenario | Named controlled pilot/site/tenant/cohort | Production/multi-site/executive-attested operation |
| Participants | Role-played or unassigned roles | Real, named, consented observer(s) present | Real observer plus required T3 attestation/witness posture |
| Time | Exercise clock or fictional dates | Dated real observation window | Dated operational window plus retention/provenance |
| Data | Fake, generated, public sample, or irreversibly transformed fixture | Real scoped source evidence under authorized access | Operational evidence with durable controlled retention |
| Claim allowed | Protocol exercised; gaps found; **T1 only** | Candidate T2 after intake verification | Candidate T3 after all T2 and T3 gates |
| Registry effect | None; RP stays Open | In-progress until verified | In-progress until verified |

## Non-negotiable rules

1. Every dry-run output carries `mode: synthetic`, `tier: T1`, and `registry_effect: none`.
2. Dry-run IDs use `DR-YYYYMMDD-RP-00N-##`; live captures use distinct `LC-...` IDs.
3. A real person role-playing against fake data does not make evidence live.
4. Real data pasted into a synthetic scenario does not upgrade it; stop, quarantine it, and assess authorization.
5. An executive signature, peer review, observer statement, or Board discussion cannot turn synthetic artifacts into live evidence.
6. Aggregating many T1 exercises never yields T2/T3.
7. Reusing a dry-run structure for live collection requires a new LC record, real consent/access, a real window, and fresh artifact provenance.
8. Synthetic artifacts may be referenced only as design history and must not support the live-tier claim.

## Required synthetic fixture boundary

- Use fictitious organization/site/person names and non-routable identifiers.
- Use generated, public, or irreversibly transformed data with no recoverable tenant, personal, credential, security, production, or trade-secret content.
- Do not copy production screenshots, logs, dossiers, topology, workforce records, OT payloads, or board materials into fixtures.
- Label every file and screenshot visibly; keep a fixture manifest stating generator/source, transformation, date, and owner.
- If provenance is uncertain, treat the fixture as restricted and do not run the exercise.

## Exit decision

| Outcome | Required action |
|---------|-----------------|
| Protocol path exercised | Record `Dry-run closed — T1`; keep registry Open |
| Missing step/control found | Record gap and owner; keep registry Open |
| Real evidence unexpectedly appears | Stop; isolate material; do not relabel; start authorized LC intake separately |
| Any participant asks to mark Complete | Reject request and cite this fence |
| Live capture is later scheduled | Use a new LC ID and [LIVE_EVIDENCE_CAPTURE_TEMPLATE.md](LIVE_EVIDENCE_CAPTURE_TEMPLATE.md) from a clean copy |

**Invariant:** no verified live artifacts ⇒ **0 Complete**, no readiness-floor flip, no Board Promote, no Eng invent, and no Const/BP change.
