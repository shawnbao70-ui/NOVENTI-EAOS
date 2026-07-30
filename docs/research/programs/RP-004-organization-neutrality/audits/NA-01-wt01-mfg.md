# NA-01 — Neutrality Audit · WT-01 SynMfg-Alpha

**Research ID:** NRI-RP-004-NA-01  
**Program:** RP-004  
**Version:** 1.0  
**Status:** Synthetic Complete  
**Mode:** synthetic · **Tier:** T1  
**Corpus:** [WT-01](../../RP-001-enterprise-discovery/walkthroughs/WT-01-mid-mfg-synthetic.md) · [CG-01](../../RP-003-capability-first/graphs/CG-01-wt01-mfg.md)  
**Parent:** [EVIDENCE_PACK.md](../EVIDENCE_PACK.md)  
**As Of:** 2026-07-21 · **Auditor:** NRI-desk (synthetic)

---

```text
neutrality_audit_version: syn-na01-1.0
enterprise_ref: WT-01 SynMfg-Alpha
org_forms: [OF-01 classic hierarchy, OF-05 shop-floor/cell]
as_of: 2026-07-21
org_shape_grant: never
cap_ids_stable: yes
```

## 1. Form Contrast

| Form | Where it appears | Decision-rights sketch |
|------|------------------|------------------------|
| OF-01 | HQ IT / Eng / Supply gravity | Classic report-to for systems & NPI |
| OF-05 | Plant exception rights on line stops | Local cell/shop-floor authority |

Same Cap IDs (CAP-OTS…CAP-DAT) used without rename when switching form lens.

## 2. Neutrality Checklist N-01…08

| ID | Check | Result | Evidence / note |
|----|-------|--------|-----------------|
| N-01 | Advice without single manager approver | **Pass** | Plant exception rights + HQ IT split; not “ask plant manager only” |
| N-02 | Cap ownership = role class | **Pass** | CG-01 owner_role_class; Quality Dept = anchor only |
| N-03 | No ladder punishing OF-05 | **Pass** | Shop-floor not scored immature; Stage S3 separate |
| N-04 | Multi-entity / multi-site rights | **Pass (partial)** | Dual-site plants mapped; full federation OF-03 not stressed |
| N-05 | Non-manager UX metaphors | **Pass (advisory)** | Recommend “cell lead / tech authority” copy — not productized |
| N-06 | Package org assumptions | **N/A** | No Marketplace pack under audit |
| N-07 | Org shape ≠ grant | **Pass** | `org_shape_grant: never`; Permission not proposed |
| N-08 | Reorg without Cap ID rename | **Pass** | Cap IDs stable if Plant Ops renamed |

**Forced-assumption defects found:** 0 blocking; 1 advisory (N-05 UX not yet in Terminal artifacts — expected at Research).

## 3. Downstream Constraint Hits

| Consumer | Hit | Remediation if failed |
|----------|-----|------------------------|
| RP-001 | Org≠Cap held in WT-01 | — |
| RP-003 | CG-01 anchors descriptive | — |
| RP-007 | HOLD Agentize on CAP-CHG uses rights+affinity, not title | Prefer keep |

## 4. Hard Boundaries

No Kernel Organization schema edits. No Org-shape→grant. Synthetic T1 only.
