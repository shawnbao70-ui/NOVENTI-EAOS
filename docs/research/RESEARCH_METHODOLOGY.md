# NRI Research Methodology

**Institute:** NOVENTI Research Institute  
**Document ID:** NRI-MET  
**Version:** 1.1  
**Status:** Normative method guide  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](RESEARCH_GOVERNANCE_CHARTER.md)

---

## Purpose

Define how NRI produces reliable enterprise research suitable for eventual EAOS architecture evolution, in accordance with the Research Governance Charter (21 program dimensions, 16 deliverables, optional promotion).

## Method Stack

```text
1. Problem Framing
2. Construct Definition
3. Desk Synthesis
4. Field Discovery
5. Model Construction
6. Cross-Layer Impact Analysis
7. Validation Design
8. Pilot Design
9. Promotion Package
```

## 1. Problem Framing

Inputs:

- Enterprise pain observed in AI transformation
- EAOS architectural maturity gaps
- Industry structural shifts

Outputs:

- Research Objective
- In-scope / out-of-scope
- Non-goals (especially: no implementation)

## 2. Construct Definition

Define research constructs before measuring them.

Example constructs for Generation-1:

| Construct | Program | Definition Intent |
|-----------|---------|-------------------|
| Enterprise Profile | RP-001 | Structured snapshot of enterprise identity and operating context |
| Enterprise DNA | RP-001 / RP-002 | Stable traits that constrain evolution paths |
| Capability Map | RP-001 / RP-003 | What the enterprise can do, independent of org chart |
| AI Readiness | RP-001 | Preparedness for AI workforce and AI Runtime adoption |
| Role Fusion | RP-005 | Safe recombination of human/AI/robot/device responsibilities |
| Evolution Potential | RP-001 / RP-007 | Capacity and readiness to absorb recommended change |
| Recommendation Trigger | RP-007 | Condition under which EAOS should advise a specific evolution |

Rules:

- Constructs are research objects, not Constitution objects.
- Constructs must be measurable or evaluable.
- Constructs must map to one or more EAOS layers for impact analysis.

## 3. Desk Synthesis

Sources:

- Industry reports and standards (cite tier T1)
- Existing EAOS Constitution / Blueprint (read-only constraints)
- Comparative enterprise OS / ERP / MES / AI platform patterns
- Legal and labor constraints relevant to AI workforce

Method:

- Extract recurring problems
- Separate durable structural problems from tooling fashion
- Produce Future Trends with confidence labels (High / Medium / Exploratory)

## 4. Field Discovery

Preferred instruments:

| Instrument | Use |
|------------|-----|
| Structured enterprise interview | Profile, DNA, readiness |
| Process / capability workshop | Capability discovery |
| Org / role inventory | Workforce transformation |
| Infrastructure inventory | Automation and AI infra readiness |
| Knowledge inventory | Knowledge discovery |
| Decision diary | Evolution trigger validation |

Sampling guidance:

- At least 3 enterprises across different growth stages before White Paper freeze for core frameworks.
- Include manufacturing and non-manufacturing where claims are industry-general.
- Record negative evidence (what does **not** fit the model).

## 5. Model Construction

Models must specify:

1. Entities  
2. Relationships  
3. States / stages  
4. Evaluation dimensions  
5. Outputs / recommendations  
6. Failure modes  
7. Constitutional compatibility notes  

Forbidden:

- Hidden execution authority in advisory models
- Org-chart lock-in presented as capability truth
- Treating AI as legal person

## 6. Cross-Layer Impact Analysis

For every major recommendation, analyze:

| Layer | Question |
|-------|----------|
| Architecture | Does layer ownership change? |
| Kernel | New invariant or entity? |
| Runtime | New enforcement or execution path? |
| Smart Terminal | New human interaction surface? |
| Enterprise Brain | New advisory insight class? |
| Marketplace | New package / capability distribution surface? |
| Constitution | New obligation or taxonomy? |
| Blueprint | New BP document or BP section? |

Impact is classified:

- **None**
- **Observational only**
- **Potential additive**
- **Potential restructuring**
- **Constitutional conflict** *(must escalate)*

## 7. Validation Design

See [RESEARCH_VALIDATION_RULES.md](RESEARCH_VALIDATION_RULES.md).

Minimum method for first-wave frameworks:

1. Internal consistency review  
2. Constitutional compatibility read-only check  
3. Expert peer review  
4. At least one enterprise walkthrough using the framework as a lens  
5. Explicit falsifiers (what would disprove the model)

## 8. Pilot Design

See Enterprise Pilot Template.

Pilot principles:

- Advisory or observational first
- No production Kernel/Runtime mutation from research pilots
- Clear human accountability
- Measurable success criteria tied to research questions, not feature shipping

## 9. Promotion Package

When requesting stage advancement, include:

1. Artifact + version  
2. Evidence tier map  
3. Validation checklist score  
4. Remaining risks  
5. Downstream impact summary  
6. Explicit ask: promote to which stage  

## Research Ethics

- Protect enterprise confidential data; store only approved anonymized extracts in repo.
- Do not collect personal data beyond research need.
- Distinguish vendor claims from observed enterprise outcomes.
- Never present research prototypes as product features.

## Method Anti-Patterns

| Anti-Pattern | Why Forbidden |
|--------------|---------------|
| Solution-first research | Bypasses discovery |
| Constitution drafting inside research | Violates promotion chain |
| Single-vendor case generalized | Weak evidence |
| Org chart as capability model | Breaks organization neutrality |
| AI given residual legal duty | Conflicts BOOK03 |
| Brain given execution path | Conflicts advisory invariant |
