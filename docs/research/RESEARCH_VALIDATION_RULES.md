# NRI Research Validation Rules

**Institute:** NOVENTI Research Institute  
**Document ID:** NRI-VAL  
**Version:** 1.1  
**Status:** Normative gate rules  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](RESEARCH_GOVERNANCE_CHARTER.md)

---

## Purpose

Define mandatory validation before a research artifact may advance stages or remain as a permanent Research Asset with claimed completeness.

## Validation Principles

1. Evidence before eloquence.  
2. Falsifiability before promotion.  
3. Constitutional compatibility before architecture ambition.  
4. Enterprise relevance before platform elegance.  
5. No self-certification for White Paper or later stages.  
6. Charter deliverables completeness before Capability Model and beyond.

## Gate Matrix

| From → To | Minimum Evidence | Required Reviews | Blocking Defects |
|-----------|------------------|------------------|------------------|
| Idea → Research | Problem statement + constructs | Author | Missing objective / scope |
| Research → White Paper | T1 + planned T2/T3; 21 dimensions complete | Peer research review | Unmapped EAOS impact; missing falsifiers; missing library metadata |
| White Paper → Capability Model | Impact reports drafted; risk/ROI plan | Peer + deliverable check | No capability map / maturity models |
| Capability Model → Prototype | Capability constructs measurable | Methodology check | Prototype implies production schema |
| Prototype → Enterprise Pilot | Controlled results + risk register | Pilot readiness review | No human accountability; data leakage risk |
| Enterprise Pilot → Architecture Review | T3/T4; success criteria scored; migration draft | Architecture preview | Constitutional conflict unresolved |
| Architecture Review → Blueprint eligibility | Ownership classification ready | Architecture Review Board | Speculative core claims |
| Blueprint → Constitution Review | *(downstream)* Blueprint approved path | Constitutional editors | NRI must not edit Constitution |
| Any → Remain Research Asset | Explicit decision + library update | Peer for White Paper+ claims | Claiming product readiness while library-only |

Downstream Blueprint / Constitution / Implementation gates are **outside NRI** but require NRI stage completion as prerequisite. Promotion remains optional.

## Universal Checklist (All Stages)

| ID | Rule | Pass Criteria |
|----|------|---------------|
| V-01 | Identity complete | Research ID, version, status, library metadata present |
| V-02 | Scope honesty | In-scope / out-of-scope / non-goals explicit |
| V-03 | Boundary intact | No Runtime/Kernel/Source/DB/Constitution/Blueprint/Implementation modifications done by research |
| V-04 | Term fidelity | Uses EAOS canonical layer names |
| V-05 | Construct clarity | Key constructs defined and measurable |
| V-06 | Evidence labeled | Claims tagged T0–T5 |
| V-07 | Impact analyzed | Architecture → Marketplace + Developer Platform + Blueprint/Constitution potential impact |
| V-08 | Risks listed | Legal, operational, adoption, architectural risks |
| V-09 | Falsifiers present | At least 3 conditions that would invalidate major claims |
| V-10 | Next stage named | Explicit promotion target, Remain Asset, or missing work |
| V-11 | Dimensions complete | All 21 program dimensions addressed (from White Paper) |
| V-12 | Deliverables tracked | Charter 16 deliverables mapped (complete/waived) |

## Framework-Specific Validation

### Enterprise Discovery Framework (RP-001)

| ID | Rule |
|----|------|
| V-ED-01 | Covers Profile, DNA, Capability, Organization, AI Readiness, Automation Readiness, Infrastructure, Knowledge, Growth Stage, Evolution Potential, AI Roadmap |
| V-ED-02 | Distinguishes Organization Discovery from Capability Discovery |
| V-ED-03 | Outputs can feed Evolution Engine without implying auto-execution |
| V-ED-04 | Growth Stage model is evidence-linked, not vanity maturity theater |

### AI-Native Role Framework (RP-005)

| ID | Rule |
|----|------|
| V-AW-01 | Separates Human / AI / Robot / Device responsibilities |
| V-AW-02 | Preserves human legal and business responsibility |
| V-AW-03 | Aligns AI taxonomy with BOOK03 (Employee / Agent / Digital Human / Assistant) |
| V-AW-04 | Role fusion opportunities include risk separation and legal constraints |
| V-AW-05 | Capability mapping does not equate org title with permission |

### Enterprise Evolution Model (RP-007)

| ID | Rule |
|----|------|
| V-EE-01 | Defines recommendation triggers, not automatic mutations |
| V-EE-02 | Covers org / AI / automation / robot / capability / smart terminal evolution advice |
| V-EE-03 | Consumes Discovery and Workforce inputs explicitly |
| V-EE-04 | Enterprise Brain remains advisory; no execution authority |
| V-EE-05 | Includes hold/no-change recommendations as first-class outcomes |

## Scoring

Each checklist item: `Pass` / `Fail` / `N/A`.

| Result | Meaning |
|--------|---------|
| All required Pass | Eligible for requested stage vote |
| Any Fail on blocking rule | Hold |
| N/A overuse (>20% without justification) | Hold |

## Validation Record Format

```text
Artifact:
Version:
Requested Stage:
Validator:
Date:
Checklist Score: Pass / Fail / N/A counts
Blocking Findings:
Residual Risks:
Decision: Promote | Hold | Reject
```

## Independence Rule

Authors may draft validation self-checks.  
Stage promotion decisions require at least one non-author reviewer for White Paper and later.
