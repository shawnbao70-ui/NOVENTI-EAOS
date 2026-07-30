# Artifact Acceptance Rubric

**Template ID:** NRI-TPL-ARTIFACT-RUBRIC  
**Version:** 1.0  
**Status:** Registrar assessment aid — not a Complete authority  
**Last Updated:** 2026-07-23  
**Governing:** [T2_T3_EVIDENCE_INTAKE.md](../T2_T3_EVIDENCE_INTAKE.md) · [LIVE_EVIDENCE_CAPTURE_TEMPLATE.md](LIVE_EVIDENCE_CAPTURE_TEMPLATE.md) · [LIVE_VS_SYNTHETIC_FENCE.md](LIVE_VS_SYNTHETIC_FENCE.md)

> Scoring supports consistent review; it does not replace intake gates. No score, reviewer signature, artifact count, executive title, or weighted average may self-certify Complete.

## 1. Preconditions before scoring

Reject from scoring if any condition fails:

- Capture has an LC ID, `mode: live`, claimed tier, real context, and real dated window.
- Observer/submitter identities are real and not role-play placeholders.
- Artifact references resolve or have controlled custodian-backed retrieval.
- Synthetic/dry-run material is labeled T1 and excluded from the live-tier basis.
- Collection access, consent, confidentiality, safety/security, and data-use basis are recorded.
- No artifact implies Brain execute, Twin authorize, Cap/Role→grant, product mutation, Const/BP rewrite, Board Promote, or Eng ingest.

Precondition failure outcome: **Rejected-incomplete** or **Returned for correction**, never Complete.

## 2. Common scoring scale

| Score | Meaning | Registrar interpretation |
|-------|---------|--------------------------|
| **0** | Missing / inaccessible / contradictory without resolution | Gate failure |
| **1** | Present but weak, ambiguous, mutable, or insufficiently traced | Material correction required |
| **2** | Adequate, resolvable, scoped, and independently reviewable | T2-quality evidence for this dimension |
| **3** | Strong operational provenance, durable retention, corroboration, and explicit limitations | T3-quality evidence for this dimension |

Do not average away a zero. Record evidence references and reasons for every score.

## 3. Core artifact dimensions

| # | Dimension | 0 | 1 | 2 — T2 bar | 3 — T3-strength |
|---|-----------|---|---|------------|-----------------|
| D1 | Real context identity | No named context | Vague/unverifiable context | Named controlled site/tenant/cohort | Production/multi-site/executive-attested context with corroboration |
| D2 | Temporal validity | No real timestamp/window | Partial or inconsistent dates | Dated real window/as_of with timezone | Operational window, collection timestamps, clock basis, retention chronology |
| D3 | Observer/attestation | Missing/invented/role-played | Identity present but role/presence unclear | Real named observer and role/presence confirmed | Independent witness/attestation with scope and timestamp |
| D4 | Source authenticity | Synthetic/relabelled/unknown | Source claimed but not verifiable | Real source producer/system and collection method verified | Corroborated operational source/export chain |
| D5 | Claim traceability | No claim/source link | Partial or manual narrative only | Claim IDs trace to artifact IDs and observations | Bidirectional trace with contradictions and supersession history |
| D6 | Integrity/version | No stable reference | Mutable link or version unclear | Hash/export ID/version or justified integrity method | Immutable/durable version plus chain of custody |
| D7 | Access/ethics | Missing access/consent basis | Basis incomplete or scope unclear | Authorized scoped collection with privacy/confidentiality controls | Independently reviewed controls and auditable access history |
| D8 | Retention/provenance | Unknown custodian/retention | Custodian or expiry incomplete | Custodian, source, transformations, retention and retrieval recorded | Durable retention, transfer history, expiry/disposition and reproducibility |
| D9 | Falsifiers/limitations | Adverse evidence omitted | Generic caveats only | Program falsifiers, gaps, conflicts, sampling and limitations recorded | Corroborated adverse tests and longitudinal/independent challenge |
| D10 | Invariant preservation | Forbidden authority/change implied | Boundary statement incomplete | Program invariants and non-claims explicitly preserved | Boundary verified by independent audit/side-effect evidence |

## 4. Tier-specific interpretation

### T2 candidate

All of the following are required:

- Preconditions pass.
- D1–D10 each score at least **2**.
- Total score is at least **20 / 30**.
- Real controlled context, named observer, dated window, resolvable artifacts, and program invariants are verified.
- No synthetic artifact is used as the live-tier basis.

Because every dimension must reach 2, the total threshold is a consistency check, not a shortcut.

### T3 candidate

All of the following are required:

- Every T2 requirement passes.
- D1, D2, D3, D4, D6, D7, and D8 each score **3**.
- D5, D9, and D10 each score at least **2**.
- Total score is at least **27 / 30**.
- The selected T3 route is explicit: production, multi-site, or executive-attested operation.
- Durable retention/provenance and operational corroboration exist.
- Executive attestation is supporting evidence, not a substitute for dated operational artifacts.

## 5. RP-specific acceptance overlay

The registrar must append criteria from the RP’s `live/FIELD_KIT.md`, `SITE_PLAN.md`, `GAP.md`, and program invariants.

| Criterion ID | RP-specific requirement | Artifact IDs | Score 0–3 | Notes / missing item |
|--------------|-------------------------|--------------|-----------|----------------------|
| P-01 | | | | |
| P-02 | | | | |
| P-03 | | | | |

A core passing score cannot compensate for a failed mandatory RP-specific criterion.

## 6. Per-artifact review sheet

| Field | Value |
|-------|-------|
| Artifact ID / capture ID | |
| Path or controlled handle | |
| Kind / producer / source system | |
| Collected at / context / version | |
| Claims supported | |
| Integrity marker | |
| Custodian / classification | |
| Retention / expiry | |
| Redaction / transformation / sampling | |
| Registrar access check | |
| Conflicts / limitations / falsifiers | |

| Dimension | Score | Evidence reference | Registrar rationale |
|-----------|-------|--------------------|---------------------|
| D1 | | | |
| D2 | | | |
| D3 | | | |
| D4 | | | |
| D5 | | | |
| D6 | | | |
| D7 | | | |
| D8 | | | |
| D9 | | | |
| D10 | | | |

## 7. Package-level decision

| Decision | Meaning | Registry/floor effect |
|----------|---------|-----------------------|
| **Rejected-incomplete** | Preconditions fail, synthetic relabel, inaccessible evidence, or hard invariant breach | None |
| **Returned for correction** | Correctable metadata, trace, retention, redaction, or access gap | None |
| **Accepted for verification** | Rubric and RP overlay meet claimed-tier quality | Still none; proceed to formal V1–V7 |
| **Verified registration committed** | Separate intake Phase A passed and paired V3/V4 completed | Only then may registry/floor reflect verified tier |

“Accepted for verification” is deliberately not “Complete.”

## 8. Anti-gaming rules

1. Never split one weak artifact into many rows to inflate evidence count.
2. Never average scores across sites, windows, claims, or artifacts to hide a failed hard dimension.
3. Never award live points for synthetic realism, peer review, role-play, or executive signature alone.
4. Never award provenance points for a bare URL, inaccessible system, mutable dashboard, or undocumented screenshot.
5. Never suppress contradictory/adverse artifacts; score the package’s handling of them.
6. Never let the submitter be the sole registrar for a disputed T3 dimension.
7. Never infer Board Promote, Eng readiness, product authority, or Const/BP truth from rubric results.

## 9. Registrar attestation

| Field | Value |
|-------|-------|
| Registrar real name / role | |
| Review timestamp (UTC) | |
| Claimed tier | |
| Preconditions | Pass / Fail |
| Core score | / 30 |
| RP overlay | Pass / Fail |
| Decision | Rejected-incomplete / Returned / Accepted for verification |
| Missing gates / dissent | |

**Invariant:** rubric score alone cannot mark Complete. Registry remains unchanged until the intake’s two-phase verification transaction succeeds.
