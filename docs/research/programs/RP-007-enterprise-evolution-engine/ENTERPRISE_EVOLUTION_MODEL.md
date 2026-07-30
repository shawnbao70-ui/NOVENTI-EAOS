# Enterprise Evolution Model

**Institute:** NOVENTI Research Institute  
**Document ID:** NRI-RP-007-EEM  
**Program:** RP-007 Enterprise Evolution Engine  
**Version:** 1.0  
**Status:** Research Draft  
**Reviewer:** 牟蓉（peer Pass — WP Draft Allowed）  
**Approval:** Pending — WP content Acceptance separate  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-21  
**White Paper:** [WHITE_PAPER-RP-007.md](WHITE_PAPER-RP-007.md) （Draft）

---

## Abstract

The Enterprise Evolution Model (EEM) defines how EAOS continuously evaluates enterprise growth and emits governed recommendations for organizational, AI, automation, robot, capability, and smart terminal evolution. EEM is an advisory model: it recommends, explains, and simulates; it does not execute. It consumes Enterprise Discovery dossiers and AI-Native Role compositions, and respects Evolution Potential constraints.

## 1. Model Purpose

Answer, continuously:

> Given this enterprise’s evidence, what should change next—if anything—and why?

Non-purpose:

- Auto-reorganize companies  
- Auto-deploy robots or AI employees  
- Bypass Permission / Workflow / approval bridges  
- Replace executive judgment

## 2. Core Loop

```text
Discover (RP-001)
   ↓
Compose Roles (RP-005)
   ↓
Evaluate Signals (EEM)
   ↓
Generate Recommendations (Advise / Simulate)
   ↓
Human Decision (Accept / Defer / Reject / Hold Confirm)
   ↓
Capture Outcome Evidence
   ↓
Refresh Discovery & Roles
```

All arrows above recommendation are observational/advisory. Execution, if any, occurs only after full NRI promotion and constitutional authority—outside this research model’s power.

## 3. Inputs

| Input Pack | Source | Required Fields |
|------------|--------|-----------------|
| Discovery Dossier | RP-001 | Profile, DNA, capabilities, org, readiness, stage, potential, knowledge, infra |
| Role Composition Catalog | RP-005 | Duties, actor splits, fusion candidates, risk classes, legal flags |
| Operating Signals | Enterprise systems (future) | KPI deltas, incident rates, exception rates, adoption metrics |
| Constraint Register | Legal/safety/compliance | Hard vetoes |
| Prior Recommendation Ledger | EEM history | Accept/defer/reject outcomes |

## 4. Recommendation Classes

| Code | Class | Question EEM Answers |
|------|-------|----------------------|
| REC-ORG | Organizational evolution | Should structure/decision rights/spans change? |
| REC-AI | AI upgrades | Should AI assistance/agents/workforce expand or upgrade? |
| REC-AUTO | Automation upgrades | Should rule/RPA/workflow automation expand? |
| REC-ROBOT | Robot deployment | Should embodied automation be introduced/scaled? |
| REC-CAP | Capability evolution | Which capabilities should level up or be newly built? |
| REC-TERM | Smart terminal deployment | Where should governed interaction surfaces be deployed/extended? |
| REC-HOLD | Hold / no change | What should explicitly not change now? |

`REC-HOLD` is mandatory in every evaluation cycle.

## 5. Evaluation Dimensions

| Dimension | Derived From | Use |
|-----------|--------------|-----|
| Growth Stage Fit | RP-001 stage | Blocks stage-skipping advice |
| Evolution Potential | RP-001 potential | Caps recommendation aggressiveness |
| DNA Constraints | RP-001 DNA | Filters culturally/structurally impossible moves |
| Readiness Gates | AI/Automation/Infra readiness | Enables or blocks classes |
| Capability Gaps | Capability graph | Targets REC-CAP |
| Role Stress | ANRF supervision load / risk gaps | Targets REC-AI / REC-ORG |
| Exception Pressure | Ops signals + DNA exception density | Targets REC-AUTO vs human investment |
| Physical Opportunity | Infra + manufacturing signals | Targets REC-ROBOT |
| Interaction Friction | Terminal/worksurface gaps | Targets REC-TERM |
| Constraint Vetoes | Legal/safety register | Hard blocks |

## 6. Trigger Library

Triggers fire recommendations only when evidence thresholds are met **and** vetoes are clear.

### 6.1 Organizational Evolution (REC-ORG)

| Trigger ID | Condition (research draft) | Recommend |
|------------|----------------------------|-----------|
| T-ORG-01 | Decision rights map shows chronic bottleneck at single node + Evolution Potential ≥ medium | Redistribute decision rights for named action classes |
| T-ORG-02 | Shadow organization dominates >N critical capabilities | Formalize ownership for those capabilities |
| T-ORG-03 | Span/layer shape blocks AI supervision cells | Create human supervision roles for F2 cells |
| T-ORG-04 | Role fusion vetoes mostly organizational (unclear owner) | Clarify accountable human role classes |

**Hold if:** transformation fatigue high; leadership sponsor absent.

### 6.2 AI Upgrades (REC-AI)

| Trigger ID | Condition | Recommend |
|------------|-----------|-----------|
| T-AI-01 | AI Readiness = Assistive-Ready; many RC0–RC1 duties still manual | Deploy Assistive Pair (F1) on top duty clusters |
| T-AI-02 | AI Readiness ≥ Agent-Ready; standard execution duties stable; approval bridge ready | Agentize bounded R6 duties |
| T-AI-03 | Workforce-Ready; supervision model exists; knowledge authority adequate | Introduce AI Employee assignments for named capability clusters |
| T-AI-04 | Incident pattern shows AI overreach attempts | Downgrade autonomy / reinforce approvals |
| T-AI-05 | Knowledge stickiness high + expert flight risk | AI capture assist + human validation program |

**Hold if:** readiness band unmet; legal flags on duty class; audit path missing.

### 6.3 Automation Upgrades (REC-AUTO)

| Trigger ID | Condition | Recommend |
|------------|-----------|-----------|
| T-AUTO-01 | Rule stability high + exception rate below threshold | Workflow/RPA expansion on named processes |
| T-AUTO-02 | Exception rate high despite automation attempts | Invest in process redesign before more bots |
| T-AUTO-03 | Digital exhaust sufficient; latency tolerance fits | Event-driven automation for specific flows |
| T-AUTO-04 | Automation without permission explainability | Pause; remediate governance first |

### 6.4 Robot Deployment (REC-ROBOT)

| Trigger ID | Condition | Recommend |
|------------|-----------|-----------|
| T-ROB-01 | Physical tasks high volume + safety case feasible + infra ready | Pilot collaborative robot cell |
| T-ROB-02 | Quality inspection variance high + vision feasibility shown | Automated inspection pilot |
| T-ROB-03 | Safety incident near-miss cluster on manual handling | Safety-first robotization assessment |
| T-ROB-04 | AI model proposes direct unsafe actuation path | Reject; enforce sense-advise-act split (F4) |

**Hold if:** safety case incomplete; OT isolation unclear; no human emergency authority.

### 6.5 Capability Evolution (REC-CAP)

| Trigger ID | Condition | Recommend |
|------------|-----------|-----------|
| T-CAP-01 | Capability level blocks stage-appropriate AI/automation | Capability uplift plan before tech upgrade |
| T-CAP-02 | Strategic intent depends on missing capability | Build-or-partner recommendation |
| T-CAP-03 | Capability owned only as tribal knowledge | Knowledge solidification before scale |
| T-CAP-04 | Marketplace package could accelerate capability | Evaluate certified package options *(advisory)* |

### 6.6 Smart Terminal Deployment (REC-TERM)

| Trigger ID | Condition | Recommend |
|------------|-----------|-----------|
| T-TERM-01 | High-impact approvals still occur in unmanaged channels | Deploy governed Terminal approval surfaces |
| T-TERM-02 | Shopfloor/field roles lack safe AI interaction surface | Role-appropriate terminal deployment |
| T-TERM-03 | Extension sprawl / ungoverned UI tools | Consolidate into signed extension host model |
| T-TERM-04 | Discovery/evolution reviews lack interactive workspace | Assessment & recommendation review workspace |

### 6.7 Hold (REC-HOLD)

| Trigger ID | Condition | Recommend |
|------------|-----------|-----------|
| T-HOLD-01 | Evolution Potential low | Freeze non-critical changes; stabilize fundamentals |
| T-HOLD-02 | Competing transformations exceed absorption capacity | Sequence; defer lower-value recs |
| T-HOLD-03 | Evidence confidence below threshold | Gather discovery evidence; do not advise major moves |
| T-HOLD-04 | Recent major change still in soak period | Soak; measure; then re-evaluate |

## 7. Recommendation Object (Conceptual)

Every recommendation instance includes:

| Field | Meaning |
|-------|---------|
| `rec_id` | Stable identifier |
| `class` | REC-* code |
| `trigger_ids` | Firing triggers |
| `statement` | Plain-language advice |
| `evidence_refs` | Dossier/signal/role evidence |
| `confidence` | Low / Medium / High |
| `expected_value` | Qualitative/quant bands |
| `risk_class` | Highest touched RC* |
| `vetoes` | Hard blocks remaining |
| `preconditions` | Readiness/org/safety gates |
| `human_owner_role` | Accountable acceptor |
| `simulation_suggested` | Yes/No |
| `execution_authority` | Always `none` at EEM layer |
| `kill_criteria` | When to abandon after accept |
| `expiry` | When advice goes stale |

## 8. Decision Lifecycle

```text
Drafted → Explained → Simulated? → Human Accept|Defer|Reject|HoldConfirm
                ↓
         Outcome Logged → Dossier Refresh Cue
```

Enterprise Brain may help explain/simulate. It may not accept on behalf of the enterprise.

## 9. Continuous Evaluation Cadence

| Cadence | Evaluation Depth |
|---------|------------------|
| Event-driven | Incidents, readiness band changes, major org changes |
| Monthly | Signal deltas vs open recommendations |
| Quarterly | Full dossier refresh + trigger sweep |
| Post-pilot | Outcome learning for trigger calibration |

## 10. Cross-Layer Impact (Potential)

| Layer | Impact Class | Notes |
|-------|--------------|-------|
| Architecture | Additive / restructuring candidate | Evolution advisory semantics near Brain/Twin |
| Kernel | Observational / additive | Consume facts; optional advice audit records later |
| Runtime | Additive | Simulation/analysis runs only |
| Smart Terminal | Additive | Recommendation review UX |
| Enterprise Brain | Additive (core) | Insight classes for evolution; no execution |
| Marketplace | Additive later | Trigger/playbook packages |
| Constitution | Potential | Advisory evolution obligations |
| Blueprint | Potential | Brain/Twin/AI/Terminal extensions |

## 11. Failure Modes

| Failure Mode | Mitigation |
|--------------|------------|
| Recommendation spam | Cap concurrent open recs; prefer HOLD |
| Stage skipping | Stage-fit gate |
| Execution leakage | Hard field `execution_authority=none` |
| Vendor-driven triggers | Evidence-tier requirement |
| Org-chart chauvinism | Capability-first inputs from RP-001/003 |
| Safety blindness | Robot triggers require safety case |

## 12. Falsifiers

1. Human decision-makers find recommendations less useful than static maturity checklists.  
2. Hold recommendations are never selected (model always pushes change).  
3. Trigger firings cannot be explained from dossier evidence.  
4. Model repeatedly suggests robot/AI moves that fail safety or legal review.  
5. Continuous loop increases thrash rather than absorption-quality outcomes.

## 13. Validation Plan

- Reconcile inputs with RP-001 and RP-005 drafts  
- Expert review of trigger thresholds (calibrate in pilots)  
- Synthetic dossier test suite including mandatory HOLD cases  
- Blind usefulness scoring with enterprise sponsors  
- Constitutional compatibility check on advisory boundary

## 14. Success Criteria

1. Six evolution classes + HOLD defined with triggers.  
2. Recommendation object complete and non-executing.  
3. Cadence and lifecycle specified.  
4. Consumes Discovery + Role frameworks without semantic gaps.  
5. Ready for White Paper evidence plan.

## 15. Promotion Stance

Current stage: **Research Draft v1.0**  
Evidence pack: **Defined** — [EVIDENCE_PACK.md](EVIDENCE_PACK.md)  
Input freeze: [INPUT_FREEZE.md](INPUT_FREEZE.md)  
Trigger tests: **TT-01…03 Synthetic Complete** — [trigger-tests/](trigger-tests/)  
Peer package: [PEER_REVIEW_PACKAGE.md](PEER_REVIEW_PACKAGE.md)  
Peer **牟蓉** Pass recorded; White Paper Draft open — [WHITE_PAPER-RP-007.md](WHITE_PAPER-RP-007.md).  
WP content Acceptance still Pending. Do **not** promote to Blueprint / Constitution / Implementation; `execution_authority` remains **none**.

## Related Documents

- [RP-007 Program Brief](README.md)  
- [Evidence Pack](EVIDENCE_PACK.md)  
- [Deliverables Checklist](DELIVERABLES-RP-007.md)  
- [Input Freeze](INPUT_FREEZE.md)  
- [Trigger Tests](trigger-tests/README.md)  
- [Peer Review Package](PEER_REVIEW_PACKAGE.md)  
- [Enterprise Discovery Framework](../RP-001-enterprise-discovery/ENTERPRISE_DISCOVERY_FRAMEWORK.md)  
- [AI-Native Role Framework](../RP-005-ai-workforce-transformation/AI_NATIVE_ROLE_FRAMEWORK.md)  
- [NRI Promotion Rules](../../RESEARCH_PROMOTION_RULES.md)  
