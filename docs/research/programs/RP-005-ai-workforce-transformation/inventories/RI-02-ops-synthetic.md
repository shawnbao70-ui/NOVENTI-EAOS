# RI-02 — Operations-Heavy Synthetic Role Inventory

**Research ID:** NRI-RP-005-RI-02  
**Program:** RP-005 AI Workforce Transformation  
**Version:** 1.0  
**Status:** Synthetic Complete (Research)  
**Mode:** synthetic  
**Evidence Tier Floor:** T1  
**Classification:** Research Only — Not Normative for Implementation  
**As Of:** 2026-07-21  
**Parent:** [EVIDENCE_PACK.md](../EVIDENCE_PACK.md)  
**RP-001 Ref:** [WT-01 SynMfg-Alpha](../../RP-001-enterprise-discovery/walkthroughs/WT-01-mid-mfg-synthetic.md)

---

## Inventory Record

```text
inventory_id: RI-02
enterprise_flavor: operations-heavy / manufacturing (discrete-hybrid)
mode: synthetic
as_of: 2026-07-21
role_classes_count: 14
actor_separation_ok: yes
title_neq_grant_ok: yes
rp001_dossier_refs: [WT-01 SynMfg-Alpha]
rp007_consumable: yes
auto_grant_minted: never
confidence_summary: medium (desk); RC5 safety path remains certified-human supervised
```

## 1. Stress Focus

Robot/Device duties; Cap≠title (Quality Dept ≠ Quality Containment capability); **RC5 Safety/Physical** very-low autonomy; OT knowledge stickiness from WT-01.

## 2. Role Class Inventory (≥12)

| # | Role Class | Primary Family (ANRF) | Human Residual | AI Pattern | Robot/Device | Max Risk Class | Fusion |
|---|------------|----------------------|----------------|------------|--------------|----------------|--------|
| 1 | Plant Manager | Ops / Executive | R1/R2 site outcomes | Ops synthesis advise | — | RC5 | F1 |
| 2 | Production Supervisor | Ops | R2 line output + exceptions | Schedule advise | Assist cells | RC5 | F1 |
| 3 | Process Owner | Mfg/Quality | R2 process definition | SPC/vision advise | — | RC5 | F1 |
| 4 | Quality Release Authority | Mfg/Quality | R1/R2 release sign-off | Defect detection assist | Inspection robots | RC5–RC6 | F1 |
| 5 | Maintenance Lead | Ops | R2 uptime ownership | Predictive advise | Collaborative robots | RC5 | F1 |
| 6 | EHS Officer | Risk / Safety | R1 safety attestations | Hazard sensing advise | Safety interlocks (device) | RC5–RC6 | F1 |
| 7 | Materials Planner | Supply Chain | R2 plan adherence | Forecast/replan advise | — | RC3 | F1–F2 |
| 8 | Warehouse Lead | Supply Chain | R2 inventory integrity | Cycle-count prioritize | Pick/pack robots | RC5 | F1–F2 |
| 9 | OT Systems Engineer | IT/OT | R2 MES/PLC integrity | Anomaly assist | PLCs/sensors (device) | RC7 | F1 |
| 10 | Master Data Steward | Knowledge/IT | R2 data authority | Suggest corrections | — | RC2 | F1 |
| 11 | Shift Technician (senior) | Ops | R2 exception resolve (sticky knowledge) | Procedure retrieval | — | RC5 | F1 |
| 12 | Supplier Quality Engineer | Quality/Commercial | R2 supplier disposition | Evidence pack assist | — | RC3 | F1 |
| 13 | Continuous Improvement Lead | Transformation | R2 kaizen portfolio | Opportunity mining | — | RC1 | F1–F2 |
| 14 | Site IT / IdP Owner | IT-Data | R2 identity landing | Ops assist; **no** self-grant | — | RC7 | F1 |

## 3. Risk Class Samples

| Role | Duty Sample | RC | Required Control |
|------|-------------|----|------------------|
| EHS Officer | Authorize energy isolation procedure | RC5 | Certified safety path; human |
| Quality Release Authority | Release shipment lot | RC5–RC6 | Human sign-off; AI detect only |
| Warehouse Lead | Autonomous robot aisle motion | RC5 | Safety interlocks + supervise |
| Materials Planner | Commit supplier order externally | RC3 | Human approve |
| OT Systems Engineer | Change PLC logic in prod | RC7 | Change board / governor — not job title |
| Shift Technician | Bypass interlock “to keep line up” | RC5 | **Refuse** AI-suggested bypass |

## 4. Cap ≠ Title Checks

| Check | Result |
|-------|--------|
| “Quality Department” used as capability name | **Rejected** — capability = Quality Containment (RP-001) |
| Org box “Maintenance” owns predictive model grants | **Rejected** — title ≠ grant |
| Shadow tech leads recorded as org/knowledge, not permission source | Pass (aligned WT-01) |

## 5. Fusion Candidates & Vetoes

| Candidate | Eligibility | Veto / Hold |
|-----------|-------------|-------------|
| Vision defect detection F1 | Yes | Release remains human |
| Predictive maintenance advise F1 | Yes | Work-order commit human |
| Unsupervised robot cell without interlocks | **Refuse** | RC5 |
| AI suggests safety interlock bypass | **Refuse** | Falsifier/safety |
| Robot “owns” injury liability | **Refuse** | C-AW-02/10 |
| Swarm autonomy on changeover-heavy lines | **Hold** | WT-01 Exception Density DNA |

## 6. BOOK03 Alignment Notes

| BOOK03 | RI-02 Use |
|--------|-----------|
| AI Assistant | Procedure retrieval, SPC explain |
| Agent | In-policy R6 only with approval bridge; never RC5 final |
| AI Employee | Non-legal durable assignment for assistive ops cells |
| Device / edge | Sensors, PLCs, interlocks as Device actors — not AI Employees |
| Human non-transfer | Safety and quality release stay human |

## 7. Legal Flags

1. Product liability for robots remains with accountable enterprise functions + suppliers.  
2. Safety certification paths are jurisdictional; research does not invent bypasses.  
3. Labor consultation before robotized cell scale-up may be required.  
4. OT data may be export-controlled — pilot data rules apply.

## 8. Title ≠ Grant Checks

| Anti-Pattern | Result |
|--------------|--------|
| “Plant Manager” auto `tenant_admin` | **Rejected** |
| Robot cell service account inherits human grants | **Rejected** |
| ANRF inventory → Permission SQL | **Rejected** |

## 9. Downstream (RP-007)

Evolution classes: `Assist` dominant; `Robotize` only with certified RC5 path; `Hold`/`Refuse` on interlock bypass and liability transfer; inventory feeds supervision-load estimates (sticky senior techs).

## 10. Hard Boundaries

No Constitution / Blueprint / Kernel / Runtime / DB / product changes.  
`auto_grant_minted: never`. No Eng Role→grant or safety-control openings from this inventory.
