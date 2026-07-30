# Enterprise Discovery Framework

**Institute:** NOVENTI Research Institute  
**Document ID:** NRI-RP-001-EDF  
**Program:** RP-001 Enterprise Discovery  
**Version:** 1.0  
**Status:** Research Draft  
**Reviewer:** 臻宇（peer Pass — WP Draft Allowed）  
**Approval:** Pending — WP content Acceptance separate  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-21  
**White Paper:** [WHITE_PAPER-RP-001.md](WHITE_PAPER-RP-001.md) （Draft）

---

## Abstract

The Enterprise Discovery Framework (EDF) defines how EAOS should learn an enterprise before advising transformation. It separates durable identity (Profile, DNA), operating truth (Capabilities, Organization, Knowledge), readiness (AI, Automation, Infrastructure), and trajectory (Growth Stage, Evolution Potential, AI Roadmap). Discovery produces evidence for advisory evolution—not automatic execution.

## 1. Design Principles

1. **Discover before evolve.** No Evolution Engine recommendation without discovery evidence.  
2. **Capability ≠ Organization.** What the enterprise can do is not identical to who reports to whom.  
3. **Readiness is multi-dimensional.** Models, GPUs, and licenses are insufficient.  
4. **Knowledge has authority.** Undocumented tribal knowledge is a discovery finding, not an asset claim.  
5. **Advisory output only.** Discovery feeds Twin/Brain advice; humans retain decision authority.  
6. **Organization neutrality.** Framework must not force a single org-chart ideology.  
7. **Constitutional compatibility.** Aligns with BOOK03 responsibility rules and Brain no-execution invariant.  
8. **Continuous, not ceremonial.** Discovery is refreshable, versioned, and provenance-aware.

## 2. Framework Overview

```text
                    ┌─────────────────────────┐
                    │   Enterprise Profile    │
                    │   Enterprise DNA        │
                    └───────────┬─────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
 Capability Discovery   Organization Discovery   Knowledge Discovery
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                ▼
        AI Readiness · Automation Readiness · Infrastructure Discovery
                                │
                                ▼
        Growth Stage · Evolution Potential · AI Roadmap
                                │
                                ▼
                 Discovery Dossier (versioned evidence)
                                │
                                ▼
            RP-005 Workforce · RP-007 Evolution Engine
```

## 3. Discovery Domains

### 3.1 Enterprise Profile

**Purpose:** Establish the enterprise as a governed subject of discovery.

| Dimension | Questions | Example Signals |
|-----------|-----------|-----------------|
| Identity | Legal entities, brands, operating names | Registrations, tenant/enterprise mapping |
| Mission & Value Model | How value is created and captured | Revenue logic, customer segments |
| Industry Context | Primary/secondary industries | NAICS/ISIC-like coding, value chain position |
| Operating Footprint | Sites, regions, channels | Plants, offices, digital channels |
| Scale Band | People, revenue, transaction volume | Bands, not vanity precision |
| Regulatory Envelope | Mandatory regimes | Safety, privacy, financial, export |
| Strategic Intent | Stated 12–36 month transformation intent | Board/IT/OT strategy artifacts |

**Output:** `EnterpriseProfile` snapshot with provenance and confidence.

### 3.2 Enterprise DNA

**Purpose:** Capture stable traits that constrain plausible evolution paths.

Research construct (feeds RP-002). DNA is not a marketing personality quiz.

| DNA Axis | Meaning | Evolution Constraint Example |
|----------|---------|------------------------------|
| Decision Gravity | Where consequential decisions actually settle | Centralized DNA resists swarm autonomy |
| Exception Density | How often standard process fails | High density blocks naive automation |
| Formality Preference | Rules vs improvisation culture | Affects workflow rigidity tolerance |
| Knowledge Stickiness | Dependence on key persons | Blocks AI workforce scale-up |
| Asset Intensity | Capex / physical ops weight | Shapes robot/smart factory paths |
| Compliance Reflex | Default posture to controls | Affects AI approval design |
| Partner Embeddedness | Ecosystem dependence | Affects Marketplace package strategy |
| Change Absorption | Historical ability to absorb platform change | Caps Evolution Potential |

**Output:** `EnterpriseDNA` vector + narrative constraints + confidence.

### 3.3 Capability Discovery

**Purpose:** Map what the enterprise can do, independent of org chart.

| Element | Definition |
|---------|------------|
| Capability | Enduring ability to produce an outcome |
| Capability Level | Current performance band (Initial → Managed → Adaptive) |
| Dependency | Upstream capabilities or external partners |
| Evidence | Process, system, KPI, interview proof |
| Automation Affinity | Suitability for rules/AI/robot assist |
| Owner Role Class | Accountable human role class (not person name as truth) |

Method:

1. Seed from value stream workshops  
2. Decompose to capability catalog  
3. Score level + evidence quality  
4. Tag AI/automation affinity  
5. Export capability graph

**Anti-pattern:** Treating department names as capabilities.

### 3.4 Organization Discovery

**Purpose:** Understand structural reality without making it the capability model.

| Element | Definition |
|---------|------------|
| Structural Units | Enterprise → units → teams as operated |
| Role Inventory | Human role classes present |
| Decision Rights Map | Who may approve which impact classes |
| Span & Layers | Depth/width signals |
| Shadow Organization | Informal power paths |
| AI Placement Today | Where AI assistants/employees already sit |

Rules:

- Org discovery informs Permission/Workflow design later; it does not grant permissions.  
- Shadow organization findings are sensitive; handle under pilot data rules.

### 3.5 AI Readiness

**Purpose:** Evaluate preparedness for governed AI workforce and AI Runtime adoption.

| Pillar | Indicators |
|--------|------------|
| Data & Knowledge | Authority, quality, retrieval governance |
| Process Clarity | Documented happy path + exceptions |
| Governance | Approval culture, audit expectations |
| Workforce Literacy | Human ability to supervise AI |
| Technical Landing | Identity, permission, integration readiness |
| Risk Posture | Acceptable autonomy bands by action class |
| Accountability Design | Named human residual responsibility |

**Bands:** `Unready` · `Assistive-Ready` · `Agent-Ready` · `Workforce-Ready` · `Adaptive`

Bands are research constructs pending validation; they must not auto-enable Runtime privileges.

### 3.6 Automation Readiness

**Purpose:** Distinguish classical automation potential from AI potential.

| Factor | Signal |
|--------|--------|
| Rule stability | Low change rate of decision rules |
| Digital exhaust | Events/data already machine-readable |
| Exception rate | % cases requiring human improvisation |
| Latency tolerance | Real-time vs batch |
| Physical coupling | Needs robots/devices vs pure software |
| Control system maturity | OT/IT integration quality |

**Output:** Automation opportunity portfolio ranked by value × readiness × risk.

### 3.7 Infrastructure Discovery

**Purpose:** Inventory the landing zone for AI Runtime, integrations, and smart terminals.

| Domain | Discover |
|--------|----------|
| Identity & Access | IdP, SSO, least privilege maturity |
| Integration Fabric | APIs, events, files, EDI, OT buses |
| Compute & Model Hosting | Cloud/on-prem/edge options |
| Observability | Logs, traces, audit sinks |
| Terminal Surfaces | Desktops, mobile, shopfloor, kiosks |
| Resilience | HA, DR, offline plant realities |
| Security Envelope | Zones, secrets, signing, supply chain |

Infrastructure discovery must capture **approval-path infrastructure**, not only GPUs.

### 3.8 Knowledge Discovery

**Purpose:** Locate enterprise knowledge, authority, and gaps.

| Class | Examples |
|-------|----------|
| System of Record | ERP, MES, CRM master data |
| System of Engagement | Email, chat, tickets |
| Embodied Knowledge | SOPs performed but undocumented |
| Expert Knowledge | Specialist judgment |
| External Knowledge | Regulations, supplier docs |
| AI-derived Knowledge | Prior model outputs (trust carefully) |

For each knowledge domain score: coverage, authority, freshness, provenance, retrieval safety.

### 3.9 Growth Stage

**Purpose:** Situate the enterprise on an evolution-relevant stage model.

| Stage | Characteristics | Typical Discovery Emphasis |
|-------|-----------------|---------------------------|
| S1 Foundational | Core processes unstable; data unreliable | Profile, process hygiene |
| S2 Digitized | Systems present; integration weak | Infrastructure, knowledge authority |
| S3 Integrated | Cross-domain flows work | Capability graph, automation |
| S4 Assistive AI | AI assistants in pockets | AI readiness, role boundaries |
| S5 AI Workforce | Governed AI employees/agents in ops | Workforce framework, approvals |
| S6 Adaptive Enterprise | Continuous evolution with advisory engine | Evolution potential optimization |

Stage is a **lens**, not a score to shame customers.

### 3.10 Evolution Potential

**Purpose:** Estimate capacity to absorb recommended change safely.

| Factor | Positive Signal | Negative Signal |
|--------|-----------------|-----------------|
| Leadership sponsorship | Named executive owner | Initiative orphan |
| Change absorption DNA | Prior successful platform shifts | Repeated transformation fatigue |
| Constraint slack | Budget/time/talent buffer | All capacity firefighting |
| Governance fitness | Clear approval paths | Unowned high-impact actions |
| Technical debt drag | Managed debt | Opaque legacy critical path |
| Workforce adaptability | Learning culture | Role fear / rigid demarcation |

**Output:** `EvolutionPotential` band + limiting constraints + earliest safe recommendation classes.

### 3.11 AI Roadmap

**Purpose:** Translate discovery into a sequenced, evidence-backed AI journey.

Roadmap is **not** a feature backlog. It is a staged advice structure:

1. Stabilize discovery dossier  
2. Close readiness blockers  
3. Deploy assistive use cases  
4. Introduce governed agents for bounded actions  
5. Expand AI workforce roles per RP-005  
6. Enable Evolution Engine advisory loops per RP-007  

Each roadmap item requires: capability target, readiness gate, human accountability, risk class, success metric, kill criteria.

## 4. Discovery Dossier

Canonical research output bundle:

| Artifact | Contents |
|----------|----------|
| Profile Record | Identity and context |
| DNA Record | Stable constraints |
| Capability Graph | Nodes, levels, affinities |
| Organization Map | Structure + decision rights |
| Knowledge Map | Domains + authority |
| Readiness Scorecards | AI / Automation / Infrastructure |
| Stage & Potential | Growth stage + evolution potential |
| AI Roadmap Draft | Sequenced advisory plan |
| Evidence Log | Sources, tiers, confidence |
| Open Risks | Legal, safety, adoption |

Dossier versioning: `dossier_version`, `as_of`, `facilitator`, `confidence_summary`.

## 5. Method Playbook (Wave 1)

| Phase | Duration Guide | Activities |
|-------|----------------|------------|
| Prep | 1–2 weeks | Scope, data rules, stakeholder map |
| Profile & DNA | 1 workshop + interviews | Structured intake |
| Capability & Org | 2 workshops | Separate sessions mandatory |
| Knowledge & Infra | Interviews + inventory | Evidence capture |
| Readiness Synthesis | Analysis sprint | Scorecards + falsifiers |
| Roadmap Co-creation | 1 workshop | Advisory only |
| Validation | Peer + enterprise review | Update dossier |

## 6. Cross-Layer Impact (Potential)

| Layer | Impact Class | Notes |
|-------|--------------|-------|
| Architecture | Additive later | Possible discovery shared capability |
| Kernel | Observational / additive | Enterprise metadata enrichment only |
| Runtime | Additive later | Assessment workflows via AI Runtime |
| Smart Terminal | Additive | Guided discovery UX |
| Enterprise Brain | Additive | Consumes dossier for advice |
| Marketplace | Additive later | Assessment packages |
| Constitution | Potential | Enterprise/knowledge/AI readiness obligations |
| Blueprint | Potential | Data shapes + Terminal/Brain inputs |

## 7. Falsifiers

1. Enterprises cannot separate capability from organization in workshops without collapse.  
2. AI Readiness bands fail to predict pilot success better than coin-flip heuristics.  
3. DNA axes show no stability across two discovery cycles.  
4. Roadmaps produced by EDF are indistinguishable from generic vendor checklists.  
5. Discovery effort consistently exceeds decision value for target enterprise bands.

## 8. Required Validation

See NRI-VAL V-ED-01…04 plus:

- Inter-rater reliability on DNA and readiness scoring  
- Time-to-dossier measurement  
- Downstream usability check by RP-005 and RP-007 authors

## 9. Success Criteria

1. Eleven domains covered with definitions, inputs, outputs.  
2. Dossier schema conceptual completeness.  
3. Clear non-execution guarantee.  
4. Consumable by Evolution Engine recommendation triggers.  
5. Peer-reviewed construct glossary accepted.

## 10. Promotion Stance

Current stage: **Research Draft v1.0**  
Evidence pack: **Defined** — [EVIDENCE_PACK.md](EVIDENCE_PACK.md) (NRI-RP-001-EVID)  
Deliverables tracking: [DELIVERABLES-RP-001.md](DELIVERABLES-RP-001.md)  
Walkthroughs: **WT-01…03 Synthetic Complete** — [walkthroughs/](walkthroughs/)  
Industry / Risk: **Draft** — [INDUSTRY_ANALYSIS.md](INDUSTRY_ANALYSIS.md) · [RISK_ANALYSIS.md](RISK_ANALYSIS.md)  
Peer **臻宇** Pass recorded; White Paper Draft open — [WHITE_PAPER-RP-001.md](WHITE_PAPER-RP-001.md).  
WP content Acceptance still Pending. Do **not** promote to Blueprint / Constitution / Implementation from this stage.

## 11. Glossary (Research Constructs)

| Term | Meaning |
|------|---------|
| Discovery Dossier | Versioned evidence pack produced by EDF |
| Enterprise DNA | Stable constraint vector for evolution |
| Capability Graph | Outcome-oriented ability map |
| Readiness Band | Ordinal preparedness class |
| Evolution Potential | Capacity to absorb change safely |
| AI Roadmap | Sequenced advisory transformation plan |

## Related Documents

- [RP-001 Program Brief](README.md)  
- [Evidence Pack](EVIDENCE_PACK.md)  
- [Deliverables Checklist](DELIVERABLES-RP-001.md)  
- [Industry Analysis](INDUSTRY_ANALYSIS.md)  
- [Risk Analysis](RISK_ANALYSIS.md)  
- [Synthetic Walkthroughs](walkthroughs/README.md)  
- [RP-005 AI-Native Role Framework](../RP-005-ai-workforce-transformation/AI_NATIVE_ROLE_FRAMEWORK.md)  
- [RP-007 Enterprise Evolution Model](../RP-007-enterprise-evolution-engine/ENTERPRISE_EVOLUTION_MODEL.md)  
- [NRI Methodology](../../RESEARCH_METHODOLOGY.md)  
