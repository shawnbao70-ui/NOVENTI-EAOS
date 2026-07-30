# EVIDENCE-PACK-RP-001 — Enterprise Discovery

**Research ID:** NRI-RP-001-EVID  
**Program:** RP-001 Enterprise Discovery  
**Version:** 1.0  
**Status:** Defined (Research)  
**Objective:** Define the evidence schema, claim map, walkthrough protocol, and White Paper freeze gate for EDF — without executing live enterprise pilots yet  
**Scope:** In: evidence pack definition, synthetic walkthrough templates, claim→tier map / Out: Runtime, Kernel, Source Code, Database, Constitution, Blueprint, Implementation; live T3/T4 field capture (planned)  
**Author:** NRI  
**Reviewer:** 臻宇（decision Pending）  
**Approval:** Pending  
**Dependencies:** [NRI-RP-001-EDF](ENTERPRISE_DISCOVERY_FRAMEWORK.md); [NRI-RP-001](README.md)  
**Related Capability:** Enterprise Discovery  
**Related Blueprint:** BP-KNOWLEDGE, BP-AI, BP-SMART-TERMINAL *(candidates — read-only)*  
**Related Constitution:** BOOK02, BOOK04 *(candidates — read-only)*  
**Related ADR:** None (research only)  
**Promotion Status:** Research Library  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-21  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](../../RESEARCH_GOVERNANCE_CHARTER.md)  
**Validation:** [RESEARCH_VALIDATION_RULES.md](../../RESEARCH_VALIDATION_RULES.md) V-ED-01…04 · V-01…V-12  
**Deliverables:** [DELIVERABLES-RP-001.md](DELIVERABLES-RP-001.md)  
**Walkthroughs:** [walkthroughs/](walkthroughs/) (WT-01…03 Synthetic Complete)

---

## 1. Purpose

Convert EDF Research Draft into a **schedulable White Paper freeze** by fixing:

1. What counts as evidence  
2. How claims map to evidence tiers (T0–T5)  
3. How ≥3 enterprise walkthroughs are structured (synthetic now; live later)  
4. What “evidence pack complete” means for Q4 White Paper gate  

This pack **defines** evidence; it does not yet claim T3 field completeness.

## 2. Evidence Pack Contents (Canonical Bundle)

| Slot | Artifact | Required for WP freeze | Notes |
|------|----------|------------------------|-------|
| E1 | Claim Register | Yes | §3 of this document |
| E2 | Domain Coverage Matrix | Yes | Maps EDF §3.1–3.11 → V-ED-01 |
| E3 | Falsifier Test Plan | Yes | Maps EDF §7 → observation protocol |
| E4 | Walkthrough Protocol (×3 minimum) | Yes (protocol); live T3 optional for freeze if synthetic T2 planned | §5 |
| E5 | Dossier Instance Schema Checklist | Yes | Aligns EDF §4 slots |
| E6 | Downstream Usability Notes (RP-005 / RP-007) | Yes (draft) | Consumability without auto-execution |
| E7 | Peer Review Record | Yes before WP Approval | Reviewer ≠ author |
| E8 | Deliverables Checklist | Yes | [DELIVERABLES-RP-001.md](DELIVERABLES-RP-001.md) |

**White Paper evidence floor (NRI-VAL):** T1 present + T2/T3 **planned** (live T3 may remain open if plan + synthetic walkthroughs exist).

## 3. Claim Register (EDF → Evidence Tier)

| Claim ID | Claim | Current Tier | Target for WP | Source |
|----------|-------|--------------|---------------|--------|
| C-ED-01 | Eleven discovery domains are necessary and jointly sufficient for advisory AI roadmaps | T1 | T1 + planned T2 | EDF §3, §9 |
| C-ED-02 | Capability Discovery ≠ Organization Discovery (must be separated in method) | T1 | T1 + planned T2/T3 | EDF §1.2, §3.3–3.4; V-ED-02 |
| C-ED-03 | Discovery outputs can feed Evolution Engine without implying auto-execution | T1 | T1 + planned T2 | EDF §1.5, §6; V-ED-03 |
| C-ED-04 | Growth Stage is evidence-linked, not vanity maturity theater | T1 | T1 + planned T2 | EDF §3.9; V-ED-04 |
| C-ED-05 | DNA axes are stable enough across two discovery cycles to constrain evolution advice | T0–T1 | planned T2/T3 | EDF §3.2, falsifier #3 |
| C-ED-06 | AI Readiness bands predict pilot success better than coin-flip heuristics | T0 | planned T3 | EDF §3.5, falsifier #2 |
| C-ED-07 | EDF roadmaps are distinguishable from generic vendor checklists | T1 | planned T2/T3 | EDF §3.11, falsifier #4 |
| C-ED-08 | Discovery effort can stay within decision-value bounds for target enterprise bands | T0–T1 | planned T2 | EDF falsifier #5 |
| C-ED-09 | Dossier schema is conceptually complete for Wave 1 advisory use | T1 | T1 | EDF §4 |
| C-ED-10 | Org≠Capability separation is teachable in workshops without collapse | T0–T1 | planned T2/T3 | EDF falsifier #1 |

## 4. Domain Coverage Matrix (V-ED-01)

| Domain | EDF Section | Required Inputs (min) | Required Outputs (min) | Evidence Log Fields |
|--------|-------------|-----------------------|------------------------|---------------------|
| Enterprise Profile | §3.1 | Legal identity, industry, scale band | Profile Record | source, as_of, confidence |
| Enterprise DNA | §3.2 | Constraint interviews | DNA Record | rater_id, axis scores |
| Capability Discovery | §3.3 | Capability workshops | Capability Graph | node_id, level, evidence_quality |
| Organization Discovery | §3.4 | Org / decision-rights session (separate) | Organization Map | role, decision_right |
| AI Readiness | §3.5 | People/process/data/tech probes | AI scorecard + band | dimension scores |
| Automation Readiness | §3.6 | Exception-density probes | Automation scorecard | exception_density |
| Infrastructure Discovery | §3.7 | Landing-zone inventory | Infra scorecard | asset_class |
| Knowledge Discovery | §3.8 | Authority interviews | Knowledge Map | authority_claim |
| Growth Stage | §3.9 | Evidence-linked stage criteria | Stage label + rationale | criterion_hits |
| Evolution Potential | §3.10 | Absorption / risk probes | Potential band | risk_flags |
| AI Roadmap | §3.11 | Synthesis workshop | Sequenced advisory plan | dependency_notes |

**Coverage rule:** Each domain must have ≥1 labeled evidence item in a walkthrough dossier instance (synthetic or live).

## 5. Walkthrough Protocol (≥3)

### 5.1 Purpose

Satisfy EDF Promotion Stance: *White Paper after ≥3 enterprise walkthroughs and evidence pack.*  
Wave 1 allows **synthetic / desk walkthroughs** (T1–T2 planning) before live enterprise T3.

### 5.2 Required Walkthrough Set

| ID | Enterprise Band (research) | Industry Flavor | Must Stress |
|----|----------------------------|-----------------|-------------|
| WT-01 | Mid-market manufacturing | Discrete / hybrid | Cap≠Org; OT/IT knowledge authority |
| WT-02 | Services / non-manufacturing | Knowledge-work heavy | AI Readiness vs license theater |
| WT-03 | Growth-stage contrast (S2 or S5) | Any | Growth Stage evidence-link; Evolution Potential |

### 5.3 Per-Walkthrough Minimum Record

Each walkthrough produces a **synthetic or live** dossier stub:

```text
walkthrough_id:
enterprise_band:
industry_flavor:
mode: synthetic | live
facilitator:
as_of:
dossier_version:
domains_completed: [list of 11]
cap_org_separated: yes | no | partial
evidence_items: [{domain, claim_ids[], tier, source_note}]
falsifier_observations: [{falsifier_id, result: open | not-triggered | triggered}]
downstream_notes:
  rp005_consumable: yes | no | partial
  rp007_consumable: yes | no | partial
  auto_execution_implied: never
open_risks: []
confidence_summary:
```

### 5.4 Synthetic Instances

| Walkthrough | Instance Path | Status |
|-------------|---------------|--------|
| WT-01 | [walkthroughs/WT-01-mid-mfg-synthetic.md](walkthroughs/WT-01-mid-mfg-synthetic.md) | **Synthetic Complete** |
| WT-02 | [walkthroughs/WT-02-services-synthetic.md](walkthroughs/WT-02-services-synthetic.md) | **Synthetic Complete** |
| WT-03 | [walkthroughs/WT-03-stage-contrast-synthetic.md](walkthroughs/WT-03-stage-contrast-synthetic.md) | **Synthetic Complete** |

Index: [walkthroughs/README.md](walkthroughs/README.md). Live T3 instances remain planned; synthetic set satisfies desk walkthrough requirement for scheduling White Paper draft (peer review still required).

## 6. Falsifier Test Plan

| Falsifier (EDF §7) | Observation Method | WP Freeze Expectation |
|--------------------|--------------------|----------------------|
| Cap/Org collapse in workshops | WT-01/02 Cap≠Org checklist | Documented separation method; collapse = Hold WP claims C-ED-02/10 |
| AI bands ≤ coin-flip | Compare band vs retrospective pilot outcomes when available | May remain planned T3; must not claim predictive validity |
| DNA instability across cycles | Two-pass scoring on same synthetic enterprise | Stability protocol defined; live replication planned |
| Roadmap ≈ vendor checklist | Blind distinguishability review (peer) | Peer note required |
| Effort > decision value | Time-to-dossier log vs decision usefulness score | Bound stated; exceedance → scope reduce |

## 7. Downstream Usability (RP-005 / RP-007)

| Consumer | Required Dossier Slots | Non-negotiable |
|----------|------------------------|----------------|
| RP-005 ANRF | Organization Map, Capability Graph, AI Readiness | Roles ≠ org boxes; no Runtime grant minting |
| RP-007 EEM | Stage, Evolution Potential, AI Roadmap, Open Risks | Recommendations advisory; `REC-HOLD` allowed; no Brain execute |

Usability draft criterion: each consumer author can cite which dossier fields feed which constructs **without** proposing Kernel/Runtime schema.

## 8. White Paper Freeze Gate (RP-001)

| Gate Item | Ready? |
|-----------|--------|
| Evidence pack defined (this document) | **Yes** |
| Deliverables checklist instantiated | **Yes** — DELIVERABLES-RP-001 |
| Claim register with tiers | **Yes** |
| ≥3 walkthrough instances completed | **Yes** — WT-01…03 synthetic complete (T1 desk) |
| Peer review | **Pass — 臻宇** (WP Draft Allowed; 2026-07-21) |
| White Paper draft | **Yes** — [WHITE_PAPER-RP-001.md](WHITE_PAPER-RP-001.md) （**Accepted**） |
| Architecture Review Candidate | **Opened** — [ARCHITECTURE_REVIEW_CANDIDATE-RP-001.md](ARCHITECTURE_REVIEW_CANDIDATE-RP-001.md)（NRI-ARC-RP-001；Awaiting Board） |
| T1 synthesis + T2/T3 plan explicit | **Yes** (T1 instances done); live T2/T3 still planned |
| V-ED-01…04 construct coverage in EDF | **Yes** (framework + synthetic walkthrough proof) |

**Decision:** Peer Pass + WP content Accepted recorded. Architecture Review Candidate Package opened（NRI-ARC-RP-001）— **Awaiting Board**；do **not** self-certify Board outcome；no Eng ingest.

## 9. Hard Boundaries

This evidence pack shall **not**:

- Modify Constitution, Blueprint, Kernel, Runtime, Database, or product source  
- Open Twin authorize / Brain execute / Marketplace payment clearing  
- Create Engineering Track PHX-G implementation tickets  
- Self-certify Architecture Review Board Promote/Hold/Reject  

## 10. Next Research Track Steps

1. ~~Author WT-01…03 synthetic walkthroughs~~ **Done.**  
2. ~~Deepen Industry / Risk to Draft~~ **Done.**  
3. ~~Assign human peer + Pass~~ **Done — 臻宇** ([PEER_REVIEW_PACKAGE.md](PEER_REVIEW_PACKAGE.md)).  
4. ~~Open White Paper draft + content Acceptance~~ **Done** — [WHITE_PAPER-RP-001.md](WHITE_PAPER-RP-001.md) Accepted.  
5. ~~Open Architecture Review Candidate Package~~ **Done** — [NRI-ARC-RP-001](ARCHITECTURE_REVIEW_CANDIDATE-RP-001.md)；Board decision pending.  
6. Optional：live T2/T3 evidence deepenings（honest tiers）— use [NRI-T2-T3-INTAKE](../../T2_T3_EVIDENCE_INTAKE.md) + [capture template](../../templates/LIVE_EVIDENCE_CAPTURE_TEMPLATE.md)；floor remains **T1** until verified live Complete.

## Related Documents

- [RP-001 Program Brief](README.md)  
- [Enterprise Discovery Framework](ENTERPRISE_DISCOVERY_FRAMEWORK.md)  
- [Architecture Review Candidate](ARCHITECTURE_REVIEW_CANDIDATE-RP-001.md)（NRI-ARC-RP-001）  
- [Industry Analysis](INDUSTRY_ANALYSIS.md)  
- [Risk Analysis](RISK_ANALYSIS.md)  
- [DELIVERABLES-RP-001](DELIVERABLES-RP-001.md)  
- [Walkthrough Index](walkthroughs/README.md)  
- [NRI Validation Rules](../../RESEARCH_VALIDATION_RULES.md)  
- [Phoenix Dual-Track Playbook](../../../project/DUAL_TRACK_GOVERNANCE.md)  
- [AED v1.1](../../../project/AUTONOMOUS_EXECUTION_DIRECTIVE.md)  
