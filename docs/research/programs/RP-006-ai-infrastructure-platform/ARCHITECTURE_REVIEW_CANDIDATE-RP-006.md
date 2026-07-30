# Architecture Review Candidate Package — RP-006 AI Infrastructure Platform

**Document ID:** NRI-ARC-RP-006  
**Program:** RP-006 AI Infrastructure Platform  
**Version:** 0.1  
**Status:** **Board Decision — Hold**（2026-07-22；PHX-G159 / DAL-G005）  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-22  
**Authority:** Research Track deepen under AED v1.1 / DAL-G003 + DAL-G004（**DAL-U020**）  
**Governing:** [RESEARCH_GOVERNANCE_CHARTER.md](../../RESEARCH_GOVERNANCE_CHARTER.md) · [RESEARCH_PROMOTION_RULES.md](../../RESEARCH_PROMOTION_RULES.md) · [DUAL_TRACK_GOVERNANCE.md](../../../project/DUAL_TRACK_GOVERNANCE.md) · [AUTONOMOUS_EXECUTION_DIRECTIVE.md](../../../project/AUTONOMOUS_EXECUTION_DIRECTIVE.md)

> **Board Decision — Hold** recorded under **DAL-G005** / PHX-G159（CA-authorized）.  
> Hold ≠ Promote ≠ Eng ingest ≠ Constitution/Blueprint edit. Remain Research Asset（T1 floor）.  
> **`kernel_bypass: never`** · **Twin authorize fail-closed** · **Brain execute fail-closed**.

---

## Linked artifacts

| Artifact | Path | Status |
|----------|------|--------|
| White Paper | [WHITE_PAPER-RP-006.md](WHITE_PAPER-RP-006.md) | **Accepted** (content; Research Library) |
| AI Infrastructure Reference Model | [AI_INFRASTRUCTURE_REFERENCE_MODEL.md](AI_INFRASTRUCTURE_REFERENCE_MODEL.md) | Research Draft (AIRM) |
| Evidence Pack | [EVIDENCE_PACK.md](EVIDENCE_PACK.md) | Defined (Research) |
| Gap Profiles | [gap-profiles/](gap-profiles/) (GP-01…02) | Synthetic Complete |
| Peer Review | [PEER_REVIEW_PACKAGE.md](PEER_REVIEW_PACKAGE.md) | **Pass** — 臻宇 |
| Industry Analysis | [INDUSTRY_ANALYSIS.md](INDUSTRY_ANALYSIS.md) | Draft |
| Risk Analysis | [RISK_ANALYSIS.md](RISK_ANALYSIS.md) | Draft |
| Program README | [README.md](README.md) | Research |

---

## 1. Purpose

Present RP-006 AI Infrastructure Platform (AIRM) to the Architecture Review Board as a **reviewable candidate** for ownership classification and Promote / Hold / Reject — without claiming Board authority, Eng soft-queue ingest, Kernel bypass via infra shortcuts, Twin authorize, or production Runtime architecture change.

This is the Research Track default deepen output after Generation-1 WP Acceptance (AED v1.1), opening the **Wave 3 AR set** for remaining G1 programs (RP-006 / RP-008 / RP-010).

---

## 2. Maturity claim

| Claim | Honesty |
|-------|---------|
| Research Library White Paper | **Accepted** (content Acceptance under CA / DAL；peer Pass recorded — 臻宇) |
| Architecture Review | **Not started** — this package awaits Board |
| Eng ingest | **None** |
| Evidence floor | T1 synthetic present（GP-01…02 + AIRM + IND/RISK）；T2/T3 **planned** (not claimed live) |
| Infra invariants | **`kernel_bypass: never`**；governance-before-GPU；approval bridge critical-path |

Maturity stage for promotion language: **Research Library WP Accepted** — ready to *propose* Architecture Review, not to assert Board completion.

---

## 3. Proposed ownership classification (candidates only)

Draft proposals for Board consideration — **not** binding:

| Concern | Proposed owner (candidate) | Notes |
|---------|----------------------------|-------|
| AIRM method / ID-01…08 domains (research) | NRI Research Asset (remain) until Promote | Permanent Library end-state allowed |
| Landing-zone / model-host readiness descriptors | Shared Runtime / AI Runtime surfaces | Readiness bands only；no Kernel shortcut |
| Approval bridge hosting (ID-04) | Workflow + AI Runtime boundary | Must remain Workflow-gated；ADR-0008 |
| Edge/OT safety island scoring (ID-07) | Shared with RP-008 OT overlays | Hybrid OT；no machine-control from Brain |
| Supply-chain trust (ID-08) | Marketplace / release chain (later) | Signed packages；post-Promote only |
| Kernel Permission / Identity | **Out of scope** for infra bypass | **`kernel_bypass: never`** |

---

## 4. Promote / Hold / Reject — draft recommendations for Board

| Option | Draft recommendation | Rationale |
|--------|----------------------|-----------|
| **Promote** (partial) | Candidate for later Runtime/AI **descriptive** readiness surfaces **after** Board + Phoenix ADR | Peer-passed（臻宇）；kernel_bypass never；ownership still additive |
| **Hold** | **Preferred default until live T2/T3 evidence or Board schedule** | Evidence floor honesty；no Eng invent from Research tip；infra must not erode Kernel |
| **Reject** | Not recommended as wholesale reject | AIRM / GP discipline remain valuable Research Assets even if never productized |
| **Remain Research Asset** | **Draft NRI opinion (not Board decision):** acceptable permanent end-state | Readiness checklist useful without productize；authorization boundary preserved |

**Draft NRI opinion (labeled — not Board decision):** Prefer **Hold for live T2/T3** or **Remain Research Asset** until Board schedules ownership review. Do **not** Promote to Eng soft queue from this package alone. Do **not** treat infra readiness as Kernel bypass. Twin authorize / Brain execute remain fail-closed.

Board may choose any mix (e.g. Remain Asset + Hold product surfaces). Board decision block filled under **DAL-G005** / PHX-G159（CA-authorized；**Hold**）。

---

## 5. Constitution / Blueprint impact candidates (read-only)

**No edits authorized.** Candidates for future review only:

| Layer | Candidates | Stance |
|-------|------------|--------|
| Blueprint | BP-RUNTIME / BP-AI / topology | Read-only candidates |
| Constitution | Security / AI governance books | Read-only candidates；no BOOK rewrite |
| ADR | ADR-0027 / ADR-0008 / ADR-0007 | Read-only；Kernel bypass must remain fail-closed |

Any Const/BP change requires Architecture Review → Constitution Review → explicit editors — outside this package.

---

## 6. Eng ingest stance

**None until Promote + Phoenix ADR.**

RP-006 must not enter Engineering soft queue from this Candidate Package alone.  
**`kernel_bypass: never`** — infra must never shortcut Kernel Permission/Workflow. See [ENG_SOFT_QUEUE_TIP.md](../../../project/ENG_SOFT_QUEUE_TIP.md) and Promotion Rules.

---

## 7. Hard non-outcomes

This package does **not**:

- Authorize Brain execute（fail-closed）  
- Authorize Twin authorize（**fail-closed**）  
- Bypass Kernel Permission / Workflow via infra shortcuts（**`kernel_bypass: never`**）  
- Rewrite Constitution or Blueprint as production truth  
- Open WebAuthn ceremony / Role→grant mint / payment clearing  
- Self-certify Architecture Review Board Promote/Hold/Reject  
- Invent new RP IDs or Eng milestone numbers as product openings  

---

## 8. Evidence floor honesty

| Tier | Status |
|------|--------|
| T1 | Present — synthetic GP-01…02 + AIRM + IND/RISK desk analysis |
| T2 | **Planned** — not claimed complete |
| T3 | **Planned** — live multi-site infra retest not claimed |
| T4+ | Out of scope for this candidate |

Do not upgrade tier labels without new evidence artifacts.

**Gap-profile honesty:** GP-01 (cloud-native landing) + GP-02 (hybrid OT) — Synthetic Complete；`kernel_bypass: never` recorded；not live plant/cloud retest evidence.

---

## 9. Open questions for Board

1. Remain permanent Research Asset vs partial Promote of ID-01…08 readiness checklist only?  
2. Minimum live T2/T3 bar before any Eng thin infra readiness surface?  
3. Ownership of `kernel_bypass: never` relative to Runtime / AI Runtime — who enforces?  
4. Sequencing vs Wave 3 peers（RP-008 / RP-010）— review AIRM before plant overlays / EOM synthesis?  
5. How strictly to forbid GPU-first / shadow-AI framing in any future product surface?

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
| 2026-07-21 | NRI-ARC-RP-006 opened — Candidate Package Awaiting Board（DAL-U020）；Wave 3 AR set；`kernel_bypass: never` |
| 2026-07-22 | Board Decision — **Hold**（PHX-G159 / DAL-G005；CA-authorized；T1 floor；no Eng ingest） |

**END OF NRI-ARC-RP-006**
