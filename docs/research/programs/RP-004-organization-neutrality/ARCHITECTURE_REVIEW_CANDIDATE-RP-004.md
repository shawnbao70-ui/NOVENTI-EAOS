# Architecture Review Candidate Package — RP-004 Organization Neutrality

**Document ID:** NRI-ARC-RP-004  
**Program:** RP-004 Organization Neutrality  
**Version:** 0.1  
**Status:** **Board Decision — Hold**（2026-07-22；PHX-G159 / DAL-G005）  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-22  
**Authority:** Research Track deepen under AED v1.1 / DAL-G003 + DAL-G004（**DAL-U019**）  
**Governing:** [RESEARCH_GOVERNANCE_CHARTER.md](../../RESEARCH_GOVERNANCE_CHARTER.md) · [RESEARCH_PROMOTION_RULES.md](../../RESEARCH_PROMOTION_RULES.md) · [DUAL_TRACK_GOVERNANCE.md](../../../project/DUAL_TRACK_GOVERNANCE.md) · [AUTONOMOUS_EXECUTION_DIRECTIVE.md](../../../project/AUTONOMOUS_EXECUTION_DIRECTIVE.md)

> **Board Decision — Hold** recorded under **DAL-G005** / PHX-G159（CA-authorized）.  
> Hold ≠ Promote ≠ Eng ingest ≠ Constitution/Blueprint edit. Remain Research Asset（T1 floor）.  
> **Structure ≠ Permission** · **`org_shape_grant: never`** · **Cap≠Org** · **Twin authorize fail-closed** · **Brain execute fail-closed**.

---

## Linked artifacts

| Artifact | Path | Status |
|----------|------|--------|
| White Paper | [WHITE_PAPER-RP-004.md](WHITE_PAPER-RP-004.md) | **Accepted** (content; Research Library) |
| Organization Neutrality Model | [ORGANIZATION_NEUTRALITY_MODEL.md](ORGANIZATION_NEUTRALITY_MODEL.md) | Research Draft (ONM) |
| Evidence Pack | [EVIDENCE_PACK.md](EVIDENCE_PACK.md) | Defined (Research) |
| Neutrality Audits | [audits/](audits/) (NA-01…02) | Synthetic Complete |
| Peer Review | [PEER_REVIEW_PACKAGE.md](PEER_REVIEW_PACKAGE.md) | **Pass** — 臻宇 |
| Industry Analysis | [INDUSTRY_ANALYSIS.md](INDUSTRY_ANALYSIS.md) | Draft |
| Risk Analysis | [RISK_ANALYSIS.md](RISK_ANALYSIS.md) | Draft |
| Program README | [README.md](README.md) | Research |

---

## 1. Purpose

Present RP-004 Organization Neutrality (ONM) to the Architecture Review Board as a **reviewable candidate** for ownership classification and Promote / Hold / Reject — without claiming Board authority, Eng soft-queue ingest, Org-shape→grant, Twin authorize, or production architecture change.

This is the Research Track default deepen output after Generation-1 WP Acceptance (AED v1.1), continuing the **Wave 2 AR set** after RP-002 / RP-009 deepenings.

---

## 2. Maturity claim

| Claim | Honesty |
|-------|---------|
| Research Library White Paper | **Accepted** (content Acceptance under CA / DAL；peer Pass recorded — 臻宇) |
| Architecture Review | **Not started** — this package awaits Board |
| Eng ingest | **None** |
| Evidence floor | T1 synthetic present（NA-01…02 + ONM + IND/RISK）；T2/T3 **planned** (not claimed live) |
| Neutrality invariants | **Structure ≠ Permission**；**`org_shape_grant: never`**；**Cap≠Org** |

Maturity stage for promotion language: **Research Library WP Accepted** — ready to *propose* Architecture Review, not to assert Board completion.

---

## 3. Proposed ownership classification (candidates only)

Draft proposals for Board consideration — **not** binding:

| Concern | Proposed owner (candidate) | Notes |
|---------|----------------------------|-------|
| ONM method / N-01…08 checklist (research) | NRI Research Asset (remain) until Promote | Permanent Library end-state allowed |
| Org-form pluralism descriptors (future) | Shared Capability / Org-facing surfaces | **Cap≠Org**；Structure ≠ Permission |
| Neutrality gate on Discovery / Cap / Evolution advice | Constraint gate across RP-001/003/005/007 | Checklist only；no grant mint |
| Assessment UX | Smart Terminal (plural org metaphors) | Terminal ≠ enterprise truth source；no manager-only hard-code |
| Twin / Brain org-shape attachment (later) | Twin/Brain data shape candidates | Twin authorize remains **fail-closed**；org shape never grant input |
| Permission / Grant | **Out of scope** for org form | Cap≠grant；**`org_shape_grant: never`** |

---

## 4. Promote / Hold / Reject — draft recommendations for Board

| Option | Draft recommendation | Rationale |
|--------|----------------------|-----------|
| **Promote** (partial) | Candidate for later Org/Terminal **descriptive** neutrality surfaces **after** Board + Phoenix ADR | Peer-passed（臻宇）；org_shape_grant never；ownership still additive |
| **Hold** | **Preferred default until live T2/T3 evidence or Board schedule** | Evidence floor honesty；no Eng invent from Research tip；Structure ≠ Permission must not erode |
| **Reject** | Not recommended as wholesale reject | ONM / NA discipline remain valuable Research Assets even if never productized |
| **Remain Research Asset** | **Draft NRI opinion (not Board decision):** acceptable permanent end-state | Neutrality checklist useful without productize；authorization boundary preserved |

**Draft NRI opinion (labeled — not Board decision):** Prefer **Hold for live T2/T3** or **Remain Research Asset** until Board schedules ownership review. Do **not** Promote to Eng soft queue from this package alone. Do **not** treat org shape as grant or Permission input. Twin authorize / Brain execute remain fail-closed.

Board may choose any mix (e.g. Remain Asset + Hold product surfaces). Board decision block filled under **DAL-G005** / PHX-G159（CA-authorized；**Hold**）。

---

## 5. Constitution / Blueprint impact candidates (read-only)

**No edits authorized.** Candidates for future review only:

| Layer | Candidates | Stance |
|-------|------------|--------|
| Blueprint | Org-facing BP language / Terminal / Package | Read-only candidates |
| Constitution | BOOK02（organizational pluralism） | Read-only candidates；no BOOK rewrite |
| ADR | ADR-0019 / ADR-0022 Org/Permission separation | Read-only；must remain fail-closed for Org→grant |

Any Const/BP change requires Architecture Review → Constitution Review → explicit editors — outside this package.

---

## 6. Eng ingest stance

**None until Promote + Phoenix ADR.**

RP-004 must not enter Engineering soft queue from this Candidate Package alone.  
**`org_shape_grant: never`** — org form must never mint Permission or feed Runtime authorization. See [ENG_SOFT_QUEUE_TIP.md](../../../project/ENG_SOFT_QUEUE_TIP.md) and Promotion Rules.

---

## 7. Hard non-outcomes

This package does **not**:

- Authorize Brain execute（fail-closed）  
- Authorize Twin authorize（**fail-closed**）  
- Treat org shape as grant or Permission input（**Structure ≠ Permission**；**`org_shape_grant: never`**；**Cap≠Org**）  
- Rewrite Constitution or Blueprint as production truth  
- Open WebAuthn ceremony / Role→grant mint / payment clearing  
- Self-certify Architecture Review Board Promote/Hold/Reject  
- Invent new RP IDs or Eng milestone numbers as product openings  

---

## 8. Evidence floor honesty

| Tier | Status |
|------|--------|
| T1 | Present — synthetic NA-01…02 + ONM + IND/RISK desk analysis |
| T2 | **Planned** — not claimed complete |
| T3 | **Planned** — live multi-form enterprise retest not claimed |
| T4+ | Out of scope for this candidate |

Do not upgrade tier labels without new evidence artifacts.

**Audit honesty:** NA-01 (WT-01 mfg；OF-01 + OF-05) + NA-02 (WT-02 svc；OF-06 + OF-02) — Synthetic Complete；`org_shape_grant: never` / Structure ≠ Permission / Cap≠Org recorded；not live plant/executive retest evidence.

---

## 9. Open questions for Board

1. Remain permanent Research Asset vs partial Promote of N-01…08 neutrality checklist only?  
2. Minimum live T2/T3 bar before any Eng thin org-neutral surface?  
3. Ownership of Cap≠Org / Structure ≠ Permission relative to Identity / Permission — who enforces `org_shape_grant: never`?  
4. Sequencing vs Wave 2 peers（RP-002 / RP-003 / RP-009）— review RP-004 with Cap/DNA first or as a neutrality-gate set?  
5. How strictly to forbid Org-shape→grant framing in any future product surface?

---

## 10. Board decision block

| Field | Value |
|-------|-------|
| Decision | **Board Decision — Hold**（CA-authorized session **PHX-G159** / **DAL-G005**） |
| Date | 2026-07-22 |
| Promote / Hold / Reject | **Hold** |
| Conditions | Remain Research Asset；evidence floor remains **T1**；no Eng soft-queue ingest；no Const/BP rewrite as production truth；Brain execute / Twin authorize fail-closed；revisit after live T2/T3 per [T2_T3_EVIDENCE_READINESS.md](../../T2_T3_EVIDENCE_READINESS.md) |
| Follow-on ADR (if Promote) | —（not Promote） |
| Recorder | Operating agent under **DAL-G005**（CA/PO cue: Architecture Review Board 填 Promote/Hold/Reject） |
| Session | PHX-G159 Generation-1 Architecture Review Board Session |

**Authority note:** Explicit CA/PO cue 2026-07-22 — **not** silent self-certify.  
**Eng ingest:** **None**（Hold ≠ Promote ≠ Eng soft-queue）.

---

## Change Log

| Date | Change |
|------|--------|
| 2026-07-21 | NRI-ARC-RP-004 opened — Candidate Package Awaiting Board（DAL-U019）；Wave 2 AR deepen；Structure ≠ Permission；`org_shape_grant: never`；Cap≠Org |
| 2026-07-22 | Board Decision — **Hold**（PHX-G159 / DAL-G005；CA-authorized；T1 floor；no Eng ingest） |

**END OF NRI-ARC-RP-004**
