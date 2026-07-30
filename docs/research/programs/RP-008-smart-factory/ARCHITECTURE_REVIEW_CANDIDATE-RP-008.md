# Architecture Review Candidate Package — RP-008 Smart Factory

**Document ID:** NRI-ARC-RP-008  
**Program:** RP-008 Smart Factory  
**Version:** 0.1  
**Status:** **Board Decision — Hold**（2026-07-22；PHX-G159 / DAL-G005）  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-22  
**Authority:** Research Track deepen under AED v1.1 / DAL-G003 + DAL-G004（**DAL-U021**）  
**Governing:** [RESEARCH_GOVERNANCE_CHARTER.md](../../RESEARCH_GOVERNANCE_CHARTER.md) · [RESEARCH_PROMOTION_RULES.md](../../RESEARCH_PROMOTION_RULES.md) · [DUAL_TRACK_GOVERNANCE.md](../../../project/DUAL_TRACK_GOVERNANCE.md) · [AUTONOMOUS_EXECUTION_DIRECTIVE.md](../../../project/AUTONOMOUS_EXECUTION_DIRECTIVE.md)

> **Board Decision — Hold** recorded under **DAL-G005** / PHX-G159（CA-authorized）.  
> Hold ≠ Promote ≠ Eng ingest ≠ Constitution/Blueprint edit. Remain Research Asset（T1 floor）.  
> **`mes_kernelization: never`** · **`machine_control_from_brain: never`** · **Twin authorize fail-closed** · **Brain execute fail-closed**.

---

## Linked artifacts

| Artifact | Path | Status |
|----------|------|--------|
| White Paper | [WHITE_PAPER-RP-008.md](WHITE_PAPER-RP-008.md) | **Accepted** (content; Research Library) |
| Smart Factory Specialization Model | [SMART_FACTORY_SPECIALIZATION_MODEL.md](SMART_FACTORY_SPECIALIZATION_MODEL.md) | Research Draft (SFSM) |
| Evidence Pack | [EVIDENCE_PACK.md](EVIDENCE_PACK.md) | Defined (Research) |
| Plant Overlays | [walkthroughs/](walkthroughs/) (PW-01…02) | Synthetic Complete |
| Peer Review | [PEER_REVIEW_PACKAGE.md](PEER_REVIEW_PACKAGE.md) | **Pass** — 臻宇 |
| Industry Analysis | [INDUSTRY_ANALYSIS.md](INDUSTRY_ANALYSIS.md) | Draft |
| Risk Analysis | [RISK_ANALYSIS.md](RISK_ANALYSIS.md) | Draft |
| Program README | [README.md](README.md) | Research |

---

## 1. Purpose

Present RP-008 Smart Factory (SFSM) to the Architecture Review Board as a **reviewable candidate** for ownership classification and Promote / Hold / Reject — without claiming Board authority, Eng soft-queue ingest, MES-as-Kernel fork, Brain machine control, Twin authorize, or production plant architecture change.

This is the Research Track default deepen output after Generation-1 WP Acceptance (AED v1.1), continuing the **Wave 3 AR set** after RP-006.

---

## 2. Maturity claim

| Claim | Honesty |
|-------|---------|
| Research Library White Paper | **Accepted** (content Acceptance under CA / DAL；peer Pass recorded — 臻宇) |
| Architecture Review | **Not started** — this package awaits Board |
| Eng ingest | **None** |
| Evidence floor | T1 synthetic present（PW-01…02 + SFSM + IND/RISK）；T2/T3 **planned** (not claimed live) |
| Plant invariants | **`mes_kernelization: never`**；**`machine_control_from_brain: never`**；safety-before-smart |

Maturity stage for promotion language: **Research Library WP Accepted** — ready to *propose* Architecture Review, not to assert Board completion.

---

## 3. Proposed ownership classification (candidates only)

Draft proposals for Board consideration — **not** binding:

| Concern | Proposed owner (candidate) | Notes |
|---------|----------------------------|-------|
| SFSM method / SF-01…08 domains (research) | NRI Research Asset (remain) until Promote | Permanent Library end-state allowed |
| Plant overlay descriptors (future) | Shared Package / Terminal / Event surfaces | Overlay only；not MES fork |
| Physical risk bands PR0–PR4 | Constraint gate with EEM HOLD | Safety-before-smart；no auto-act |
| Line-side Terminal UX | Smart Terminal (plant metaphors) | Terminal ≠ enterprise truth；≠ machine controller |
| OT safety islands | Shared with RP-006 ID-07 | Hybrid OT；Brain never direct control |
| MES / machine actuation | **Out of scope** for Kernel / Brain | **`mes_kernelization: never`**；**`machine_control_from_brain: never`** |

---

## 4. Promote / Hold / Reject — draft recommendations for Board

| Option | Draft recommendation | Rationale |
|--------|----------------------|-----------|
| **Promote** (partial) | Candidate for later Package/Terminal **descriptive** plant overlays **after** Board + Phoenix ADR | Peer-passed（臻宇）；MES/Brain machine-control never；ownership still additive |
| **Hold** | **Preferred default until live T2/T3 evidence or Board schedule** | Evidence floor honesty；no Eng invent from Research tip；plant invariants must not erode |
| **Reject** | Not recommended as wholesale reject | SFSM / PW discipline remain valuable Research Assets even if never productized |
| **Remain Research Asset** | **Draft NRI opinion (not Board decision):** acceptable permanent end-state | Plant overlay checklist useful without productize；authorization boundary preserved |

**Draft NRI opinion (labeled — not Board decision):** Prefer **Hold for live T2/T3** or **Remain Research Asset** until Board schedules ownership review. Do **not** Promote to Eng soft queue from this package alone. Do **not** kernelize MES or allow Brain machine control. Twin authorize / Brain execute remain fail-closed.

Board may choose any mix (e.g. Remain Asset + Hold product surfaces). Board decision block filled under **DAL-G005** / PHX-G159（CA-authorized；**Hold**）。

---

## 5. Constitution / Blueprint impact candidates (read-only)

**No edits authorized.** Candidates for future review only:

| Layer | Candidates | Stance |
|-------|------------|--------|
| Blueprint | Package / Terminal / Event | Read-only candidates |
| Constitution | Industry / safety books | Read-only candidates；no BOOK rewrite |
| ADR | ADR-0030 / ADR-0027 / ADR-0008 | Read-only；Brain execute / machine control fail-closed |

Any Const/BP change requires Architecture Review → Constitution Review → explicit editors — outside this package.

---

## 6. Eng ingest stance

**None until Promote + Phoenix ADR.**

RP-008 must not enter Engineering soft queue from this Candidate Package alone.  
**`mes_kernelization: never`** · **`machine_control_from_brain: never`**. See [ENG_SOFT_QUEUE_TIP.md](../../../project/ENG_SOFT_QUEUE_TIP.md) and Promotion Rules.

---

## 7. Hard non-outcomes

This package does **not**:

- Authorize Brain execute（fail-closed）  
- Authorize Twin authorize（**fail-closed**）  
- Fork MES into Core Kernel（**`mes_kernelization: never`**）  
- Allow Brain / Twin direct machine control（**`machine_control_from_brain: never`**）  
- Rewrite Constitution or Blueprint as production truth  
- Open WebAuthn ceremony / Role→grant mint / payment clearing  
- Self-certify Architecture Review Board Promote/Hold/Reject  
- Invent new RP IDs or Eng milestone numbers as product openings  

---

## 8. Evidence floor honesty

| Tier | Status |
|------|--------|
| T1 | Present — synthetic PW-01…02 + SFSM + IND/RISK desk analysis |
| T2 | **Planned** — not claimed complete |
| T3 | **Planned** — live plant retest not claimed |
| T4+ | Out of scope for this candidate |

Do not upgrade tier labels without new evidence artifacts.

**Walkthrough honesty:** PW-01 (discrete cell) + PW-02 (line-side Terminal + OT) — Synthetic Complete；`mes_kernelization: never` / `machine_control_from_brain: never` recorded；not live plant evidence.

---

## 9. Open questions for Board

1. Remain permanent Research Asset vs partial Promote of SF-01…08 plant overlay checklist only?  
2. Minimum live T2/T3 bar before any Eng thin plant Terminal surface?  
3. Ownership of MES≠Kernel / Brain≠machine-control relative to Runtime / OT — who enforces?  
4. Sequencing vs Wave 3 peers（RP-006 / RP-010）— review SFSM with AIRM OT islands first?  
5. How strictly to forbid MES-as-EAOS / Brain-actuates-line framing in any future product surface?

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
| 2026-07-21 | NRI-ARC-RP-008 opened — Candidate Package Awaiting Board（DAL-U021）；Wave 3 AR deepen；`mes_kernelization: never`；`machine_control_from_brain: never` |
| 2026-07-22 | Board Decision — **Hold**（PHX-G159 / DAL-G005；CA-authorized；T1 floor；no Eng ingest） |

**END OF NRI-ARC-RP-008**
