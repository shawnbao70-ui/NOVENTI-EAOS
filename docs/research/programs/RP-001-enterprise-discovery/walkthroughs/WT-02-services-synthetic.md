# WT-02 — Services / Knowledge-Work Synthetic Walkthrough

**Research ID:** NRI-RP-001-WT-02  
**Program:** RP-001 Enterprise Discovery  
**Version:** 1.0  
**Status:** Synthetic Complete (Research)  
**Mode:** synthetic  
**Evidence Tier Floor:** T1 (desk construct exercise); planned T2/T3 live later  
**Classification:** Research Only — Not Normative for Implementation  
**As Of:** 2026-07-21  
**Facilitator:** NRI (synthetic desk)  
**Dossier Version:** syn-wt02-1.0  
**Parent:** [EVIDENCE_PACK.md](../EVIDENCE_PACK.md)

---

## Walkthrough Record

```text
walkthrough_id: WT-02
enterprise_band: mid-market services
industry_flavor: knowledge-work heavy (professional services / B2B consulting ops)
mode: synthetic
facilitator: NRI-desk
as_of: 2026-07-21
dossier_version: syn-wt02-1.0
domains_completed:
  [Profile, DNA, Capability, Organization, AI Readiness, Automation Readiness,
   Infrastructure, Knowledge, Growth Stage, Evolution Potential, AI Roadmap]
cap_org_separated: yes
auto_execution_implied: never
confidence_summary: medium (synthetic); license-theater anti-pattern explicitly tested
```

## 1. Synthetic Enterprise Sketch

**Codename:** `SynSvc-Beta`  
**Profile highlights:** ~350 employees; multi-office; project delivery + retainer; CRM + PSA + document lakes; strong desire to “buy Copilot licenses” as transformation.

**Stress focus:** AI Readiness vs license theater.

## 2. Domain Dossier Stub

| Domain | Synthetic Finding (abbrev.) | Evidence Note | Tier |
|--------|----------------------------|---------------|------|
| Profile | B2B professional services; IP-sensitive client data | Desk pattern | T1 |
| DNA | High Formality on client delivery; high Knowledge Stickiness on partners; Partner Embeddedness high | Pattern synthesis | T1 |
| Capability | Strong: Client Pursuit, Delivery Governance; Weak: Knowledge Reuse across engagements | Workshop fiction | T1 |
| Organization | Practice leads vs project managers; partners hold pricing exceptions | Org session fiction | T1 |
| AI Readiness | **Unready → Assistive-Ready (borderline)** — licenses purchased; retrieval governance weak; accountability design incomplete | Pillar scorecard stresses license ≠ readiness | T1 |
| Automation Readiness | Proposal assembly semi-automatable; exception-heavy scoping resists | Exception density | T1 |
| Infrastructure | SaaS CRM/PSA; uneven IdP; no governed AI landing zone | Inventory fiction | T1 |
| Knowledge | Engagement IP fragmented; “who may cite what” unclear | Authority fiction | T1 |
| Growth Stage | **S4 Expanding Platforms** (tool sprawl; ops maturity uneven) | Criterion fiction | T1 |
| Evolution Potential | **Moderate–Low** until knowledge authority + approval culture harden | Absorption narrative | T1 |
| AI Roadmap | (1) Knowledge authority + retrieval rules (2) Assistive drafting with human commit (3) Hold agentic client actions | Explicitly rejects license-first roadmap | T1 |

## 3. License Theater Probe

| Probe | Result |
|-------|--------|
| Seat count / SKU inventory treated as AI Readiness? | **Rejected** — recorded as Infrastructure/Commercial signal only |
| Data & Knowledge pillar scored independently | Pass — Weak |
| Accountability Design named residual humans for AI drafts | Partial — roles named, RACI incomplete |
| Risk Posture allows unsupervised client-facing send? | **No** — Hold |
| Vendor checklist equivalence of roadmap? | **Avoided** — roadmap starts with authority, not model SKUs |

## 4. Cap ≠ Org Separation Checklist

| Check | Result |
|-------|--------|
| “Consulting Practice” not equated to Capability “Delivery Governance” | Pass |
| Partner titles vs capability owners separated | Pass |
| Collapse observed? | **not-triggered** |

## 5. Evidence Items → Claims

| Domain | Claim IDs | Tier | Source Note |
|--------|-----------|------|-------------|
| AI Readiness | C-ED-01, C-ED-06, C-ED-07 | T1 | License theater rejected |
| Capability / Organization | C-ED-02, C-ED-10 | T1 | Cap≠Org held |
| Roadmap / Brain boundary | C-ED-03 | T1 | No auto client-send |
| Growth Stage | C-ED-04 | T1 | S4 tool-sprawl evidence |
| Effort | C-ED-08 | T1 | Desk ~1 day; useful for rejecting false AI urgency |

## 6. Falsifier Observations

| Falsifier | Result | Note |
|-----------|--------|------|
| Cap/Org collapse | not-triggered | |
| AI bands ≤ coin-flip | open | Band deliberately conservative |
| DNA instability | open | Single pass |
| Roadmap ≈ vendor checklist | not-triggered | Anti-theater design |
| Effort > decision value | not-triggered | High decision value (stopped license-first plan) |

## 7. Downstream Notes

| Consumer | Consumable? | Fields Cited |
|----------|-------------|--------------|
| RP-005 | yes / partial | Role classes (practice lead, PM); AI Readiness weak literacy/accountability |
| RP-007 | yes | Stage S4; Potential Moderate–Low; Roadmap Hold on agentic client actions → maps to `REC-HOLD` class |
| Auto-execution | **never** | |

## 8. Open Risks

1. Commercial pressure may reintroduce license-theater narratives in live pilots.  
2. Client-data regimes may block even assistive drafting without legal review.  
3. Partner politics may falsify Organization Map completeness.

## 9. Hard Boundaries

No Constitution / Blueprint / Kernel / Runtime / DB / product changes. No Eng ticket opened from this walkthrough.
