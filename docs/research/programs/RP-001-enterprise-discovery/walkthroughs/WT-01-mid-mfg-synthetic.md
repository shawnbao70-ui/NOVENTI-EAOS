# WT-01 — Mid-Market Manufacturing Synthetic Walkthrough

**Research ID:** NRI-RP-001-WT-01  
**Program:** RP-001 Enterprise Discovery  
**Version:** 1.0  
**Status:** Synthetic Complete (Research)  
**Mode:** synthetic  
**Evidence Tier Floor:** T1 (desk construct exercise); planned T2/T3 live later  
**Classification:** Research Only — Not Normative for Implementation  
**As Of:** 2026-07-21  
**Facilitator:** NRI (synthetic desk)  
**Dossier Version:** syn-wt01-1.0  
**Parent:** [EVIDENCE_PACK.md](../EVIDENCE_PACK.md)

---

## Walkthrough Record

```text
walkthrough_id: WT-01
enterprise_band: mid-market manufacturing
industry_flavor: discrete / hybrid (electronics assembly + light machining)
mode: synthetic
facilitator: NRI-desk
as_of: 2026-07-21
dossier_version: syn-wt01-1.0
domains_completed:
  [Profile, DNA, Capability, Organization, AI Readiness, Automation Readiness,
   Infrastructure, Knowledge, Growth Stage, Evolution Potential, AI Roadmap]
cap_org_separated: yes
auto_execution_implied: never
confidence_summary: medium (synthetic consistency); not field-validated
```

## 1. Synthetic Enterprise Sketch

**Codename:** `SynMfg-Alpha`  
**Profile highlights:** ~800 employees; 2 plants + HQ; B2B OEM supplier; ISO/IATF-like quality pressure; ERP + MES + tribal shop-floor knowledge.

**Stress focus (per Evidence Pack):** Capability ≠ Organization; OT/IT knowledge authority.

## 2. Domain Dossier Stub

| Domain | Synthetic Finding (abbrev.) | Evidence Note | Tier |
|--------|----------------------------|---------------|------|
| Profile | Discrete mfg; dual-site; quality-regulated | Desk industry pattern | T1 |
| DNA | High Exception Density on changeovers; high Knowledge Stickiness on senior techs; Compliance Reflex strong | Pattern synthesis | T1 |
| Capability | Strong: Order-to-Ship, Quality Containment; Weak: New Product Introduction cadence | Value-stream workshop fiction | T1 |
| Organization | Plant managers hold local exception rights; HQ IT owns systems; shadow “tech leads” decide line stops | Org≠Cap session fiction | T1 |
| AI Readiness | **Assistive-Ready** (process clarity uneven; approval culture present; landing zone partial) | Pillar scorecard fiction | T1 |
| Automation Readiness | Rules automation high on packing; low on exception-heavy changeover | Exception density link | T1 |
| Infrastructure | ERP/MES present; identity federation uneven across plants | Inventory fiction | T1 |
| Knowledge | OT know-how person-bound; IT docs in wiki with weak authority stamps | Authority interview fiction | T1 |
| Growth Stage | **S3 Managed Operations** (stable ops; transformation intent stated but uneven absorption) | Criterion checklist fiction | T1 |
| Evolution Potential | **Moderate** — compliance helps; stickiness caps AI workforce scale | Absorption narrative | T1 |
| AI Roadmap | (1) Assistive quality docs (2) Supervised exception triage (3) Hold swarm autonomy | Advisory sequence only | T1 |

## 3. Cap ≠ Org Separation Checklist

| Check | Result |
|-------|--------|
| Capability workshop held without org-chart labels as capability names | Pass (synthetic method) |
| Organization session mapped decision rights separately | Pass |
| “Quality Dept” not treated as Capability “Quality Containment” synonym | Pass — distinct nodes |
| Shadow OT tech leads recorded under Org/Knowledge, not Capability owners as persons | Pass |
| Collapse observed? | **not-triggered** (method held in desk exercise) |

## 4. Evidence Items → Claims

| Domain | Claim IDs | Tier | Source Note |
|--------|-----------|------|-------------|
| Capability / Organization | C-ED-02, C-ED-10 | T1 | Cap≠Org checklist |
| Knowledge | C-ED-01 | T1 | OT/IT authority split |
| AI Readiness / Roadmap | C-ED-03, C-ED-07 | T1 | Assistive-first roadmap ≠ vendor GPU list |
| Growth Stage | C-ED-04 | T1 | S3 criterion hits logged |
| DNA | C-ED-05 | T1 | Stickiness/exception axes set (stability unproven) |
| AI bands | C-ED-06 | T0–T1 | Band assigned; predictive validity **open** |
| Effort | C-ED-08 | T1 | Desk time ~1.5 day equivalent; within bound for synthetic |

## 5. Falsifier Observations

| Falsifier | Result | Note |
|-----------|--------|------|
| Cap/Org workshop collapse | not-triggered | Separation method held |
| AI bands ≤ coin-flip | open | No retrospective pilot outcomes |
| DNA instability across cycles | open | Single pass only |
| Roadmap ≈ vendor checklist | not-triggered (desk) | Roadmap tied to dossier constraints |
| Effort > decision value | not-triggered | Synthetic bound OK |

## 6. Downstream Notes

| Consumer | Consumable? | Fields Cited |
|----------|-------------|--------------|
| RP-005 | yes | Organization Map (decision rights); Capability Graph (Quality Containment); AI Readiness Assistive-Ready |
| RP-007 | yes | Stage S3; Evolution Potential Moderate; AI Roadmap steps; Open Risks (knowledge stickiness) |
| Auto-execution | **never** | Advisory only; Brain execute remains fail-closed |

## 7. Open Risks

1. Live plant OT interviews may reveal Cap/Org collapse under time pressure.  
2. Knowledge authority conflict between Quality and Production undocumented legally.  
3. MES data quality may falsify AI Readiness band downward.

## 8. Hard Boundaries

No Constitution / Blueprint / Kernel / Runtime / DB / product changes. No Eng ticket opened from this walkthrough.
