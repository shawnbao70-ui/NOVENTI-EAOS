# AI-Native Role Framework

**Institute:** NOVENTI Research Institute  
**Document ID:** NRI-RP-005-ANRF  
**Program:** RP-005 AI Workforce Transformation  
**Version:** 1.0  
**Status:** Research Draft  
**Reviewer:** 包锦昱（legal peer Pass — WP Draft Allowed）  
**Approval:** Pending — WP content Acceptance separate  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-21  
**White Paper:** [WHITE_PAPER-RP-005.md](WHITE_PAPER-RP-005.md) （Draft）

---

## Abstract

The AI-Native Role Framework (ANRF) redesigns enterprise roles as compositions of Human, AI, Robot, and Device responsibilities. It preserves human legal and business accountability, aligns with EAOS BOOK03 taxonomy, separates risk-bearing duties from automatable duties, and defines safe role-fusion patterns for Evolution Engine advice.

## 1. Governing Invariants (Research-Enforced)

1. Human legal responsibility is non-transferable to AI, robots, or devices.  
2. Human business residual accountability remains explicit for every high-impact action class.  
3. AI execution occurs only through AI Runtime (constitutional constraint, read-only here).  
4. Org title ≠ permission grant.  
5. Digital Human is presentation, not a responsibility bearer.  
6. Smart Terminal is interaction surface, not workforce identity.  
7. Role fusion never erases risk separation.  
8. “Autonomous” means bounded autonomy under policy—not legal independence.

## 2. Actor Classes

| Actor Class | Definition | Can Bear Legal Duty? | Typical Strength |
|-------------|------------|----------------------|------------------|
| Human | Natural person in enterprise role | Yes | Judgment, accountability, exception ethics |
| AI Employee | Permanent governed AI workforce identity | No | Scale, consistency, tireless execution within grant |
| Agent | Technical planning/tool unit under AI Runtime | No | Multi-step work inside controls |
| AI Assistant | Collaboration role toward person/team | No | Local productivity support |
| Digital Human | Optional persona/multimodal skin | No | UX presence only |
| Robot | Embodied actuated machine | No (product liability paths exist separately) | Physical manipulation |
| Device / Edge Actor | Sensor/actuator/endpoint with narrow agency | No | Sensing, local control loops |
| Human+AI Cell | Composite operating unit | Human yes; AI no | Supervised high-throughput work |

## 3. Responsibility Categories

Every duty maps to exactly one primary category:

| Category | Meaning | Default Bearer |
|----------|---------|----------------|
| R1 Legal Accountability | Liability, regulated sign-off | Human |
| R2 Business Residual Duty | Outcome ownership | Human |
| R3 Decision Judgment | Irreducible discretion | Human (AI may advise) |
| R4 Approval Authority | High-impact authorize/deny | Human (workflow-bound) |
| R5 Exception Handling | Novel/unmodeled cases | Human-led; AI assist |
| R6 Standard Execution | Repeatable in-policy work | AI / Robot / Human |
| R7 Monitoring & Detection | Signal watch | AI / Device / Human |
| R8 Physical Actuation | Move matter/energy safely | Robot / Device (+ human supervise) |
| R9 Knowledge Capture | Preserve enterprise knowledge | AI assist + human validate |
| R10 Customer/Regulated Interaction | External commitments | Human primary; AI draft only unless policy allows |

## 4. Capability Mapping Method

```text
Enterprise Role Class
   → Mission Outcomes
   → Required Capabilities (from RP-001 Capability Graph)
   → Duty Decomposition (R1–R10)
   → Actor Assignment (Human / AI / Robot / Device)
   → Risk Class per Duty
   → Control Requirements (approval, audit, fallback)
   → Fusion Eligibility
```

Mapping rules:

- Each R1/R2 duty must name a human role class.  
- AI/Robot assignments require capability + readiness evidence from Discovery.  
- Device duties require infrastructure discovery evidence.  
- Permission implications are noted as *potential*; not granted by this framework.

## 5. Enterprise Role Families

ANRF analyzes role families, not every job title. Titles localize; families generalize.

### 5.1 Executive & Governance

| Duty Pattern | Human | AI | Robot | Device |
|--------------|-------|----|-------|--------|
| Strategy intent | Owns | Scenario simulation advise | — | — |
| Risk appetite | Owns | Risk sensing advise | — | — |
| Regulated attestations | Signs | Drafts evidence packs | — | — |
| Transformation sponsorship | Owns | Progress synthesis | — | — |

**Fusion note:** AI strategy co-pilot allowed; AI cannot hold fiduciary role.

### 5.2 Finance & Control

| Duty Pattern | Human | AI | Robot | Device |
|--------------|-------|----|-------|--------|
| Accounting judgment | Owns | Anomaly detection, reconciliations assist | — | — |
| Payment release (high impact) | Approves | Prepares, policy-checks | — | — |
| Fraud monitoring | Oversees | Continuous detection | — | Telemetry feeds |
| Close acceleration | Owns exceptions | Standard close tasks | — | — |

**Legal constraints:** Payment and attestations remain human-approved per policy impact class.

### 5.3 People & Organization

| Duty Pattern | Human | AI | Robot | Device |
|--------------|-------|----|-------|--------|
| Hiring decisions | Owns | Screening assist, scheduling | — | — |
| Performance judgment | Owns | Evidence assembly | — | — |
| Policy communication | Owns | Drafting/localization | — | — |
| AI workforce staffing request | Owns business need | Capacity forecasting | — | — |

**Risk separation:** AI must not unilaterally terminate humans or AI employees without human authority path.

### 5.4 Operations & Supply Chain

| Duty Pattern | Human | AI | Robot | Device |
|--------------|-------|----|-------|--------|
| Plan vs actual management | Owns exceptions | Forecasting, replan advise | Material move | Scanners/sensors |
| Supplier commitment | Owns | Draft/negotiate assist | — | — |
| Inventory accuracy | Oversees | Cycle-count prioritization | Pick/pack robots | RFID/IoT |
| Incident command | Owns | Signal correlation | Emergency stop capable | Safety interlocks |

### 5.5 Manufacturing / Quality (Smart Factory bridge)

| Duty Pattern | Human | AI | Robot | Device |
|--------------|-------|----|-------|--------|
| Process ownership | Owns | SPC/vision advise | Weld/assemble/inspect | PLCs, sensors |
| Quality release | Owns | Defect detection | Automated inspection | Metrology devices |
| Line balancing | Approves changes | Optimization advise | Collaborative robots | Line controllers |
| Safety intervention | Authority | Hazard prediction | Safety-rated stops | Hardwired safety |

**Legal constraints:** Safety-critical actuation requires certified control paths; AI advice is not a safety PLC.

### 5.6 Commercial & Customer

| Duty Pattern | Human | AI | Robot | Device |
|--------------|-------|----|-------|--------|
| Pricing authority | Owns bands | Recommend within policy | — | — |
| Customer commitments | Owns | Draft responses, triage | — | Channel endpoints |
| Opportunity scoring | Oversees | Rank/predict | — | — |
| Field service | Owns complex jobs | Diagnosis assist | Service robots (limited) | Installed equipment telemetry |

### 5.7 IT, Data & Platform

| Duty Pattern | Human | AI | Robot | Device |
|--------------|-------|----|-------|--------|
| Architecture authority | Owns | Design alternatives | — | — |
| Production change | Approves | Generate diffs/tests | — | — |
| Incident response | Owns Sev ownership | Triage/correlation | — | Observability agents |
| Access grant | Approves | Suggest least privilege | — | — |

### 5.8 Risk, Legal, Compliance

| Duty Pattern | Human | AI | Robot | Device |
|--------------|-------|----|-------|--------|
| Legal interpretation | Owns | Retrieval/draft assist | — | — |
| Compliance testing | Owns opinion | Continuous control testing | — | Log sources |
| Investigation decisions | Owns | Evidence clustering | — | — |
| Regulatory filing | Signs | Assemble packets | — | — |

### 5.9 Knowledge & Transformation Office

| Duty Pattern | Human | AI | Robot | Device |
|--------------|-------|----|-------|--------|
| Knowledge authority | Owns | Capture/summarize/classify | — | — |
| Discovery facilitation | Owns | Workshop assist | — | Terminal surfaces |
| Evolution recommendation acceptance | Owns | Generate options (Brain/Evolution) | — | — |

## 6. Role Fusion Opportunities

Fusion = intentional recomposition of duties across actors with explicit controls.

| Fusion Pattern | Description | Preconditions | Veto Conditions |
|----------------|-------------|---------------|-----------------|
| F1 Assistive Pair | Human + AI Assistant for drafting/analysis | AI Readiness ≥ Assistive-Ready | Regulated sole-human duty |
| F2 Supervised Cell | Human supervises multiple AI Employees | Agent-Ready; approval bridge live | Missing audit path |
| F3 Physical Loop | Human + Robot + Device under safety regime | Certified robotics controls | Safety case incomplete |
| F4 Sense-Decide-Act Split | Device senses, AI advises, Human/Robot acts | Clear actuation authority | AI directly drives unsafe actuator |
| F5 Knowledge Relay | AI captures; human validates; Knowledge system stores | Provenance required | Unsourced AI knowledge published as truth |
| F6 Exception Escalator | AI executes standard; human owns exceptions | Exception taxonomy exists | Exception rate too high |

## 7. Risk Separation Matrix

| Risk Class | Examples | Allowed Autonomy | Required Control |
|------------|----------|------------------|------------------|
| RC0 Informational | Summaries, search | High AI | Provenance |
| RC1 Reversible Ops | Draft tickets, suggest slots | High AI | Easy undo |
| RC2 Internal Commit | Update internal records | Medium | Policy check + audit |
| RC3 External Commit | Customer/supplier promises | Low | Human approval |
| RC4 Financial Move | Payments, credits | Low | Dual control as policy |
| RC5 Safety/Physical | Motion, energy isolation | Very low | Certified safety path |
| RC6 Legal/Regulated | Filings, attestations | None for AI final | Human sign-off |
| RC7 Identity/Permission | Access changes | Low | Governor/approval |

**Rule:** Fusion may raise throughput only within the same risk class controls—not by silently lowering risk class.

## 8. Legal Constraints (Research Baseline)

1. AI is not a legal person in this framework.  
2. Employment/labor law still governs human roles; AI staffing is service/capability deployment.  
3. Product liability for robots/devices remains with accountable enterprise functions and suppliers.  
4. Regulated professions may forbid AI final acts regardless of technical readiness.  
5. Cross-border data/AI rules may constrain assistant placement and knowledge access.  
6. Works-council / labor consultation may be required before role fusion at scale.  
7. Auditability is a legal-enabling property, not optional UX.

Jurisdiction overlays are required at pilot time; this baseline is not legal advice.

## 9. Alignment to EAOS BOOK03 Taxonomy

| BOOK03 Concept | ANRF Use |
|----------------|----------|
| AI Employee | Bearer of durable AI workforce role assignments (non-legal) |
| Agent | Execution instrument inside AI Runtime for a role’s R6/R7 duties |
| Digital Human | Optional presentation for human-facing fusion patterns |
| AI Assistant | Default pattern for F1 Assistive Pair |
| Smart Terminal | Interaction channel for supervision and approval—not a role bearer |
| Human responsibility non-transfer | Hard invariant for R1/R2 |

## 10. Outputs Consumed by Evolution Engine

ANRF emits:

- Role composition catalog  
- Fusion candidates with veto conditions  
- Risk class coverage gaps  
- Supervision load estimates  
- Legal constraint flags  
- Recommended next workforce evolution class: `Hold` / `Assist` / `Agentize` / `Robotize` / `Refuse`

## 11. Falsifiers

1. Enterprises reject human residual duty as impractical and demand AI legal ownership.  
2. Role families cannot generalize across industries without collapsing to useless abstraction.  
3. Fusion patterns increase incident rates vs baseline after controls.  
4. Mapping cannot stay consistent with Permission Kernel (title≠grant) in real pilots.  
5. Legal reviewers find systematic conflict with BOOK03 that cannot be remediated in research.

## 12. Validation Plan

- Peer review vs BOOK03 / AI Blueprint (read-only)  
- Counsel review of responsibility matrix language  
- Two-enterprise role inventory pilots  
- Inter-coder agreement on risk class assignment  
- Evolution Engine consumability check with RP-007

## 13. Promotion Stance

Current stage: **Research Draft v1.0**  
Evidence pack: **Defined** — [EVIDENCE_PACK.md](EVIDENCE_PACK.md) (NRI-RP-005-EVID)  
Deliverables tracking: [DELIVERABLES-RP-005.md](DELIVERABLES-RP-005.md)  
Inventories: **RI-01…02 Synthetic Complete** — [inventories/](inventories/)  
Industry/Risk: **Draft** — [INDUSTRY_ANALYSIS.md](INDUSTRY_ANALYSIS.md) · [RISK_ANALYSIS.md](RISK_ANALYSIS.md)  
Peer package: [PEER_REVIEW_PACKAGE.md](PEER_REVIEW_PACKAGE.md)  
Legal peer **包锦昱** Pass recorded; White Paper Draft open — [WHITE_PAPER-RP-005.md](WHITE_PAPER-RP-005.md).  
WP content Acceptance still Pending. Do **not** promote to Blueprint / Constitution / Implementation; **never** mint Permission grants from ANRF.

## Related Documents

- [RP-005 Program Brief](README.md)  
- [Evidence Pack](EVIDENCE_PACK.md)  
- [Deliverables Checklist](DELIVERABLES-RP-005.md)  
- [Industry Analysis](INDUSTRY_ANALYSIS.md)  
- [Risk Analysis](RISK_ANALYSIS.md)  
- [Peer Review Package](PEER_REVIEW_PACKAGE.md)  
- [Synthetic Inventories](inventories/README.md)  
- [Enterprise Discovery Framework](../RP-001-enterprise-discovery/ENTERPRISE_DISCOVERY_FRAMEWORK.md)  
- [Enterprise Evolution Model](../RP-007-enterprise-evolution-engine/ENTERPRISE_EVOLUTION_MODEL.md)  
- EAOS Constitution BOOK03 *(read-only)*  
