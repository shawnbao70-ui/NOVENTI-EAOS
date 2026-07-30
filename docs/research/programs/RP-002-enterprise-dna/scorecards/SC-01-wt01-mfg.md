# SC-01 — DNA Scorecard · WT-01 SynMfg-Alpha

**Research ID:** NRI-RP-002-SC-01  
**Program:** RP-002  
**Version:** 1.0  
**Status:** Synthetic Complete  
**Mode:** synthetic · **Tier:** T1  
**Dossier:** [WT-01](../../RP-001-enterprise-discovery/walkthroughs/WT-01-mid-mfg-synthetic.md)  
**Parent:** [EVIDENCE_PACK.md](../EVIDENCE_PACK.md)  
**As Of:** 2026-07-21 · **Rater:** NRI-desk (synthetic)

---

```text
dna_record_version: syn-sc01-1.0
enterprise_ref: WT-01 SynMfg-Alpha
as_of: 2026-07-21
authorization_input: never
```

## Axis Scores (1–5)

| Axis | Score | Narrative | Evidence | Confidence |
|------|-------|-----------|----------|------------|
| DX-01 Decision Gravity | 4 | Plant exceptions local; strategic/IT gravity at HQ | Org map; dual-site | medium |
| DX-02 Exception Density | 5 | Changeovers exception-heavy | DNA stub; Automation Readiness | medium |
| DX-03 Formality Preference | 4 | Quality-regulated formality | Profile regulatory envelope | medium |
| DX-04 Knowledge Stickiness | 5 | Senior tech OT know-how person-bound | Knowledge domain | medium |
| DX-05 Asset Intensity | 4 | Plants, MES, physical ops | Profile + Infra | medium |
| DX-06 Compliance Reflex | 5 | Strong compliance posture | DNA stub | medium |
| DX-07 Partner Embeddedness | 3 | OEM supplier; moderate ecosystem | Profile B2B OEM | low–medium |
| DX-08 Change Absorption | 3 | S3 stable; absorption uneven | Stage S3; Potential Moderate | medium |

**Anti-collapse check:** Axes do not collapse to one score (DX-02/04/06 high; DX-08 mid).

## Constraint Hints → RP-007

| Hint | REC Class | Action | Rationale |
|------|-----------|--------|-----------|
| H1 | REC-AUTO / REC-AI Agentize | **Hold** | DX-02 Extreme |
| H2 | REC-AI Workforce scale | **Caution** | DX-04 Extreme |
| H3 | REC-ROBOT unsupervised | **Hold** | DX-05 + DX-02; aligns TT-03 |
| H4 | REC-AI Assist (vision/SPC) | **Prefer** | Compliance supports advise path |
| H5 | REC-HOLD | **Prefer** on swarm autonomy | Roadmap step 3 |

## Hard Boundaries

Not Permission/Twin/Brain execute input. Retest stability **open** (single synthetic pass).
