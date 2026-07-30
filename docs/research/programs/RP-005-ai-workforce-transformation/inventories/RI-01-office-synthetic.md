# RI-01 — Office-Heavy Synthetic Role Inventory

**Research ID:** NRI-RP-005-RI-01  
**Program:** RP-005 AI Workforce Transformation  
**Version:** 1.0  
**Status:** Synthetic Complete (Research)  
**Mode:** synthetic  
**Evidence Tier Floor:** T1  
**Classification:** Research Only — Not Normative for Implementation  
**As Of:** 2026-07-21  
**Parent:** [EVIDENCE_PACK.md](../EVIDENCE_PACK.md)  
**RP-001 Ref:** [WT-02 SynSvc-Beta](../../RP-001-enterprise-discovery/walkthroughs/WT-02-services-synthetic.md)

---

## Inventory Record

```text
inventory_id: RI-01
enterprise_flavor: office-heavy / knowledge services
mode: synthetic
as_of: 2026-07-21
role_classes_count: 14
actor_separation_ok: yes
title_neq_grant_ok: yes
rp001_dossier_refs: [WT-02 SynSvc-Beta]
rp007_consumable: yes
auto_grant_minted: never
confidence_summary: medium (desk); legal peer still required for WP
```

## 1. Stress Focus

License theater rejection; **RC3 External Commit** Holds; human residual R1/R2 on client-facing acts; title ≠ Permission grant.

## 2. Role Class Inventory (≥12)

| # | Role Class | Primary Family (ANRF) | Human Residual | AI Pattern | Robot/Device | Max Risk Class | Fusion |
|---|------------|----------------------|----------------|------------|--------------|----------------|--------|
| 1 | Managing Partner / Practice Lead | Executive | R1/R2 strategy & client ownership | Assistive scenario advise | — | RC6 | F1 only |
| 2 | Engagement Manager | Commercial / Ops | R2 delivery outcome | Status synthesis, risk flags | — | RC3 | F1–F2 draft |
| 3 | Pursuit Lead | Commercial | R2 win/loss ownership | Proposal drafting assist | — | RC3 | F1 |
| 4 | Delivery Consultant | Knowledge / Ops | R2 work product quality | Research assist, draft | — | RC2 | F1 |
| 5 | Knowledge Manager | Knowledge | R2 authority of published IP | Capture/suggest; human validate | — | RC2 | F1 |
| 6 | Finance Controller | Finance | R1/R2 attestations; payment approve | Recon assist, anomaly | — | RC4 | F1 |
| 7 | Billing Specialist | Finance | R2 invoice accuracy | Invoice draft, policy check | — | RC3 | F1–F2 |
| 8 | People Partner (HR) | People | R1/R2 employment decisions | Screening assist; **no** unilateral terminate | — | RC6 | F1 |
| 9 | Risk / Compliance Officer | Risk-Legal | R1 regulated posture | Policy gap sensing | — | RC6 | F1 |
| 10 | General Counsel Desk | Risk-Legal | R1 legal sign-off | Clause retrieval assist | — | RC6 | F1 |
| 11 | IT / Platform Owner | IT-Data | R2 landing zone & IdP | Ops assist; **no** RC7 self-grant | — | RC7 | F1 |
| 12 | AI Product Sponsor | Transformation | R2 business need for AI staffing | Capacity forecast assist | — | RC2 | F1 |
| 13 | Client Success Lead | Commercial | R2 external commitments | Draft comms; human send | — | RC3 | F1 |
| 14 | PMO / Transformation Analyst | Transformation | R2 program truthfulness | Progress synthesis | — | RC1 | F1–F2 |

## 3. Risk Class Samples

| Role | Duty Sample | RC | Required Control |
|------|-------------|----|------------------|
| Engagement Manager | Promise delivery date to client | RC3 | Human approval before send |
| Finance Controller | Release payment > threshold | RC4 | Dual control / policy |
| People Partner | Termination decision | RC6 | Human only; AI evidence pack max |
| IT Platform Owner | Change production access | RC7 | Governor / approval path — **not** from role title |
| Knowledge Manager | Publish client-derived IP to firm wiki | RC2 | Human validate + provenance |
| Pursuit Lead | Submit priced proposal | RC3 | Partner approve |

## 4. Fusion Candidates & Vetoes

| Candidate | Eligibility | Veto / Hold |
|-----------|-------------|-------------|
| Proposal drafting F1 | Yes | RC3 send remains human |
| Invoice preparation F2 | Conditional | Policy-complete data only |
| Agentic client-email send | **Refuse** | RC3 + WT-02 license-theater stress |
| AI “owns” engagement liability | **Refuse** | C-AW-02/10; legal person ban |
| Seat-count = Workforce-Ready | **Refuse** | Readiness from RP-001, not SKUs |

## 5. BOOK03 Alignment Notes

| BOOK03 | RI-01 Use |
|--------|-----------|
| AI Assistant | Default for F1 pairs (draft/summarize) |
| Agent | Only inside AI Runtime for in-policy R6 with approval bridge |
| AI Employee | Durable assignment metaphor for sponsored AI staffing — **non-legal** |
| Digital Human | Optional UX; not a liability bearer |
| Human responsibility non-transfer | Hard pass on all RC3+ samples |

## 6. Legal Flags

1. Client-data regimes may block even assistive drafting without DPIA-class review.  
2. Works-council consultation may apply before scale fusion (jurisdiction-dependent).  
3. Regulated advice professions: AI final acts forbidden regardless of readiness.  
4. **Demand that AI hold legal ownership** → design Hold (falsifier #1).

## 7. Title ≠ Grant Checks

| Anti-Pattern | Result |
|--------------|--------|
| “Partner” title auto-mints `platform_governor` | **Rejected** |
| “AI Employee” assignment auto-grants workflow approve | **Rejected** |
| Role inventory exported as Permission policy | **Rejected** — potential notes only |

## 8. Downstream (RP-007)

Recommended evolution classes from this inventory: mostly `Assist` / `Hold`; `Agentize` only for RC0–RC1 with audit; `Refuse` for RC3 unsupervised send and any liability transfer.

## 9. Hard Boundaries

No Constitution / Blueprint / Kernel / Runtime / DB / product changes.  
`auto_grant_minted: never`. No Eng Role→grant ticket from this inventory.
