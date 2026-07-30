# NA-02 — Neutrality Audit · WT-02 SynSvc-Beta

**Research ID:** NRI-RP-004-NA-02  
**Program:** RP-004  
**Version:** 1.0  
**Status:** Synthetic Complete  
**Mode:** synthetic · **Tier:** T1  
**Corpus:** [WT-02](../../RP-001-enterprise-discovery/walkthroughs/WT-02-services-synthetic.md) · [CG-02](../../RP-003-capability-first/graphs/CG-02-wt02-svc.md)  
**Parent:** [EVIDENCE_PACK.md](../EVIDENCE_PACK.md)  
**As Of:** 2026-07-21 · **Auditor:** NRI-desk (synthetic)

---

```text
neutrality_audit_version: syn-na02-1.0
enterprise_ref: WT-02 SynSvc-Beta
org_forms: [OF-06 partnership/practice, OF-02 matrix stresses]
as_of: 2026-07-21
org_shape_grant: never
cap_ids_stable: yes
license_theater_rejected: yes
```

## 1. Form Contrast

| Form | Where it appears | Decision-rights sketch |
|------|------------------|------------------------|
| OF-06 | Practice leads + partners hold pricing exceptions | Partnership gravity |
| OF-02 | Practice vs project managers (matrix-like tension) | Dual solid/dotted style rights |

Same Cap IDs (CAP-PUR…CAP-ACC) used without rename under both lenses.

## 2. Neutrality Checklist N-01…08

| ID | Check | Result | Evidence / note |
|----|-------|--------|-----------------|
| N-01 | Advice without single manager approver | **Pass** | Partner exceptions + Delivery Lead class; not “ask practice manager only” |
| N-02 | Cap ownership = role class | **Pass** | CG-02; Consulting Practice ≠ CAP-DEL |
| N-03 | No ladder punishing OF-06/02 | **Pass** | Partnership not immature; Stage S4 separate |
| N-04 | Multi-entity rights | **Pass (partial)** | Multi-office; full OF-03 federation not stressed |
| N-05 | Non-manager UX metaphors | **Pass (advisory)** | “Partner commit / engagement lead” needed for RC3 Holds |
| N-06 | Package org assumptions | **N/A** | No Marketplace pack under audit |
| N-07 | Org shape ≠ grant | **Pass** | Title≠grant aligned with ANRF; `org_shape_grant: never` |
| N-08 | Reorg without Cap ID rename | **Pass** | Cap IDs stable if Practice renamed |

**Forced-assumption defects found:** 1 remediable advisory — REC language risk if templates say only “ask your manager” for client-facing AI send (should parameterize Partner / Engagement Lead). Logged for RP-007 template review; not Eng opening.

## 3. Downstream Constraint Hits

| Consumer | Hit | Remediation if failed |
|----------|-----|------------------------|
| RP-001 | License theater rejected without org dogma | — |
| RP-003 | CG-02 Cap≠Org held | — |
| RP-005 | Title≠grant; practice box ≠ Cap | — |
| RP-007 | HOLD agentic client actions via CAP-ACC/rights | Keep parameterized |

## 4. Hard Boundaries

No Kernel Organization schema edits. No Org-shape→grant. No Copilot-seat-as-org-maturity. Synthetic T1 only.
