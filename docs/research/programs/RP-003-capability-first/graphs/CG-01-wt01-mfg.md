# CG-01 — Capability Graph · WT-01 SynMfg-Alpha

**Research ID:** NRI-RP-003-CG-01  
**Program:** RP-003  
**Version:** 1.0  
**Status:** Synthetic Complete  
**Mode:** synthetic · **Tier:** T1  
**Dossier:** [WT-01](../../RP-001-enterprise-discovery/walkthroughs/WT-01-mid-mfg-synthetic.md)  
**Parent:** [EVIDENCE_PACK.md](../EVIDENCE_PACK.md)  
**As Of:** 2026-07-21 · **Facilitator:** NRI-desk (synthetic)

---

```text
capability_graph_version: syn-cg01-1.0
enterprise_ref: WT-01 SynMfg-Alpha
as_of: 2026-07-21
cap_org_separated: yes
auto_grant_minted: never
permission_input: never
```

## 1. Cap ≠ Org Checklist

| Check | Result |
|-------|--------|
| Capability names exclude department labels as synonyms | **Pass** |
| “Quality Dept” ≠ CAP-QC Quality Containment | **Pass** |
| Plant managers recorded as org_anchors, not capability_id | **Pass** |
| Shadow OT tech leads under Knowledge authority, not Cap owners-as-persons | **Pass** |
| Collapse observed? | **not-triggered** |

## 2. Capability Nodes

| capability_id | name | outcome | level | affinity | knowledge_authority | owner_role_class | org_anchors (descriptive) | confidence |
|---------------|------|---------|-------|----------|---------------------|------------------|---------------------------|------------|
| CAP-OTS | Order-to-Ship | On-time complete orders shipped | L3 | A1 | MES + planner class | Ops Lead class | Plant ops | medium |
| CAP-QC | Quality Containment | Defects contained; escape rate bounded | L3 | A1 | QA procedure authority | Quality Lead class | Quality Dept *(anchor only)* | medium |
| CAP-CHG | Changeover Execution | Line changeovers within takt window | L2 | A0 | Senior tech OT (person-bound) | Manufacturing Eng class | Plants | medium |
| CAP-NPI | New Product Introduction | New SKUs production-ready on cadence | L1 | A1 | Mixed Eng/Quality | NPI Lead class | HQ Eng | medium |
| CAP-MNT | Equipment Maintainability | Unplanned downtime within band | L2 | A3 | OT maintenance know-how | Maintenance Lead class | Plants | medium |
| CAP-MAT | Material Availability | Shortage-caused stops reduced | L2 | A1 | ERP MRP planners | Supply Lead class | HQ Supply | low–medium |
| CAP-DAT | OT/IT Data Integrity | Shop-floor ↔ ERP truth reconciled | L1 | A1 | Split OT/IT stamps weak | Data Steward class | HQ IT + Plants | medium |

## 3. Dependency Edges

| From | Type | To | Note |
|------|------|-----|------|
| CAP-MAT | requires | CAP-OTS | Shortage blocks ship |
| CAP-QC | amplifies | CAP-OTS | Escape control protects ship outcome |
| CAP-CHG | feeds | CAP-OTS | Changeover delays starve OTS |
| CAP-DAT | requires | CAP-QC | Bad MES truth → false containment |
| CAP-DAT | requires | CAP-MAT | MRP fidelity |
| CAP-NPI | requires | CAP-QC | Launch without containment = risk |
| CAP-NPI | amplifies | CAP-CHG | New SKUs raise changeover load |
| CAP-MNT | amplifies | CAP-OTS | Downtime cuts throughput |
| CAP-CHG | conflicts | CAP-NPI | Concurrent NPI + unstable changeover contention |

## 4. Critical Path & Gaps

| Path / Gap | Signal | Planning implication (advisory) |
|------------|--------|----------------------------------|
| Critical path | CAP-DAT → CAP-MAT → CAP-OTS | Data integrity before AI packing assist scale |
| Gap G1 | CAP-NPI at L1 | Hold aggressive “AI NPI” packaging; prefer Assist docs |
| Gap G2 | CAP-CHG affinity A0 + high DX-02 (SC-01) | Prefer REC-HOLD Agentize on changeover |
| Gap G3 | CAP-MNT A3 | Robot/physical only with RC5-class case later |

**Dept-roadmap contrast:** Org-first would fund “Quality Dept AI” and “IT Copilot seats”; graph prioritizes CAP-DAT + CAP-CHG constraints first.

## 5. Export Hints (RP-005 / RP-007)

| Consumer | Hint | Bound |
|----------|------|-------|
| RP-005 | AI staffing candidates on CAP-QC / CAP-OTS Assist only | no grant mint |
| RP-007 | HOLD Agentize on CAP-CHG; Prefer Assist on CAP-QC | execution_authority=none |
| Eng / Permission | — | **never** from this graph |

## 6. Hard Boundaries

Not Kernel schema; not Runtime grant; not Twin authorize / Brain execute. Synthetic T1 only.
