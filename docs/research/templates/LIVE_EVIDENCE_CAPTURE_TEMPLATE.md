# Live Evidence Capture Template

**Template ID:** NRI-TPL-LIVE-EVID  
**Version:** 1.1  
**Status:** Template (copy per capture; do not mark Complete on the template itself)  
**Last Updated:** 2026-07-23  
**Governing:** [T2_T3_EVIDENCE_INTAKE.md](../T2_T3_EVIDENCE_INTAKE.md) · [T2_T3_EVIDENCE_READINESS.md](../T2_T3_EVIDENCE_READINESS.md) · [RESEARCH_VALIDATION_RULES.md](../RESEARCH_VALIDATION_RULES.md)

> Copy this file into the target program tree (e.g. `programs/RP-00N-…/live/LC-YYYYMMDD-….md`) when a **real** live capture occurs.  
> Leave fields blank only if not yet known — blank required fields ⇒ intake incomplete.
> A copied form starts as **Draft**. `Complete` is a registrar outcome, never a submitter assertion.

---

## Header

| Field | Value |
|-------|-------|
| Capture ID | LC-YYYYMMDD-RP-00N-## |
| Research Program | RP-00N — |
| Claimed tier | T2 / T3 |
| mode | live |
| Capture status | Draft / In-progress / Submitted / Verified-Complete / Rejected-incomplete |
| Submitted at (UTC) | |
| Verified at (UTC) | |
| as_of / window | |
| Site / tenant / cohort | |
| Observer (named) | |
| Observer affiliation / role | |
| Facilitator (if different) | |
| Submitter | |
| Evidence custodian / contact | |
| Linked Evidence Pack | `programs/…/EVIDENCE_PACK.md` |
| Related claims (C-*) | |
| Access classification | public / internal / restricted |
| Consent / collection basis | |

---

## Intake checklist (I1–I10)

| # | Check | Pass (yes/no) | Notes |
|---|-------|---------------|-------|
| I1 | RP in 001…010 | | |
| I2 | Tier T2 or T3 | | |
| I3 | Named site/tenant/cohort | | |
| I4 | Dated window | | |
| I5 | Named observer (no invented peers) | | |
| I6 | Repository paths resolve; external handles have custodian, access check, and retention | | |
| I7 | mode: live | | |
| I8 | Program invariants held | | |
| I9 | No Brain/Twin/Cap→grant/Const rewrite | | |
| I10 | Not a synthetic relabel | | |

**Intake result:** Pass / Fail

---

## Tier qualification

A T3 candidate must satisfy every T2 baseline item plus every T3 extension item.

| Dimension | T2 baseline evidence | T3 extension evidence | Recorded value / path | Pass |
|-----------|----------------------|-----------------------|-----------------------|------|
| Operating context | Named controlled pilot, site, tenant, or cohort | Production tenant, ≥2 sites, or executive-attested operation | | yes / no |
| Time | Dated start/end or `as_of` | Dated window plus retention/provenance record | | yes / no |
| Witness | Named observer who was present | Independent attestation or second witness; any exception is explicit and registrar-reviewed | | yes / no |
| Traceability | Existing artifact paths linked from Evidence Pack | Durable retention path or export handle in addition | | yes / no |
| Independence | Not a relabel of synthetic Input Freeze | Operational evidence independent of synthetic Input Freeze alone | | yes / no |

**Tier qualification result:** Pass / Fail  
**Missing items:**  

---

## Artifact manifest

Register every item used to support the claim. Repository paths must resolve. External items require a stable handle, custodian, access check, and retention location. Do not place secrets, personal data, tenant payloads, or restricted raw exports in this form.

| Artifact ID | Repository path or external handle | Kind / format | Source / producer | Collected at (UTC) | Integrity marker | Custodian | Retention / expiry | Access + redaction | Access checked |
|-------------|------------------------------------|---------------|-------------------|--------------------|------------------|-----------|--------------------|--------------------|----------------|
| A-01 | | | | | SHA-256 / export ID / n.a. + reason | | | | yes / no |

**Manifest completeness:** Pass / Fail  
**Missing, inaccessible, mutable, or expired items:**  

---

## Observation record

```text
capture_id:
program_id:
claimed_tier: T2 | T3
mode: live
capture_status: Draft | In-progress | Submitted | Verified-Complete | Rejected-incomplete
site_or_tenant:
cohort_notes:
observer:
observer_affiliation_or_role:
facilitator:
window_start:
window_end:
as_of:
domains_or_scopes_covered: []
claim_ids: []
artifact_ids: []
artifact_paths_or_handles: []
retention_or_provenance:
falsifier_observations: [{id, result}]
exceptions_or_gaps: []
downstream_notes:
  eng_ingest_implied: never
  board_promote_implied: never
  brain_execute: never
  twin_authorize: never
  auto_grant_minted: never
open_risks: []
confidence_summary:
honesty_affirmation: "This capture is live field/tenant evidence, not synthetic Input Freeze."
```

---

## Submitter attestations

| Attestation | Confirm | Notes |
|-------------|---------|-------|
| Observer, operating context, dates, and artifacts are real and not invented | yes / no | |
| Required access/consent exists; restricted material is not copied into this form | yes / no | |
| Synthetic material, if referenced, is labeled and is not the tier basis | yes / no | |
| Known gaps, failed falsifiers, and conflicting observations are disclosed | yes / no | |
| No Board Promote, Eng ingest, Const/BP rewrite, Brain/Twin authority, or grant mint is implied | yes / no | |

**Submitter name / date:**  

---

## Verification (V1–V7) — registrar only

Verification is two-phase: evaluate evidence first, then commit the paired registry/readiness updates. Before both phases finish, status remains **Submitted** or **In-progress**, never Complete.

### Phase A — evidence preflight

| # | Gate | Pass (yes/no) |
|---|------|---------------|
| V1 | I1–I10 and claimed-tier qualification Pass | |
| V2 | Template instance, manifest artifacts, and Evidence Pack links exist and are accessible | |
| V5 | Required DAL Usage Log row identified/recorded | |
| V6 | No Board re-Promote / Eng invent from this alone | |
| V7 | Package/Alembic and Const/BP posture respected | |

**Preflight result:** Pass / Fail  
**Registrar / date:**  

### Phase B — registration commit

Perform only after Phase A Pass. V3 and V4 are commit confirmations, not circular prerequisites.

| # | Commit confirmation | Done | Path / row reference |
|---|---------------------|------|----------------------|
| V3 | Intake registry row updated to Complete with capture ID, tier, date, and artifact references | yes / no | |
| V4 | Readiness floor changed for this RP only and Change Log appended | yes / no | |

**Verification result:** Pass / Fail (Pass requires Phase A Pass and V3–V4 done)  
**Floor flip committed?** yes / no  
**Partial commit handling:** revert the unpaired board edit or mark both records pending correction; do not leave a Complete/floor mismatch.

---

## Rejection / resubmission record

| Field | Value |
|-------|-------|
| Decision | Rejected-incomplete / Returned for correction |
| Missing or failed gates | |
| Registrar | |
| Decision date (UTC) | |
| Resubmission capture ID / revision | |

Rejection means the submitted material did not clear intake; it does not prove the underlying program claim false. A resubmission must preserve the prior decision trail.

---

## Explicit non-claims

This capture shall **not** by itself:

- Rewrite Constitution / Blueprint as production truth  
- Open Brain execute or Twin authorize  
- Mint Role→grant or Cap→grant  
- Eng soft-queue invent or payment clearing  
- Substitute for Architecture Review Board Promote  

---

**END OF NRI-TPL-LIVE-EVID**
