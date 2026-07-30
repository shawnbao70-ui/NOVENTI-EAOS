# Brain Evolution Model

**Institute:** NOVENTI Research Institute  
**Document ID:** NRI-RP-009-BEM  
**Program:** RP-009 Enterprise Brain Evolution  
**Version:** 1.0  
**Status:** Research Draft  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-21  
**Constraint ADR (read-only):** ADR-0030 Enterprise Brain / Twin boundary  
**Upstream:** [EEM](../RP-007-enterprise-evolution-engine/ENTERPRISE_EVOLUTION_MODEL.md); [EDF](../RP-001-enterprise-discovery/ENTERPRISE_DISCOVERY_FRAMEWORK.md)  
**Consumers:** RP-007 advice quality; RP-010 EOM; Twin coupling (advisory)

---

## Abstract

The Brain Evolution Model (BEM) defines how Enterprise Brain may deepen as **advisory intelligence** — Describe → Diagnose → Simulate → Recommend → Learn — **never Act**. Brain may explain and simulate Evolution recommendations; it must not accept on behalf of the enterprise, mint Permission, commit Workflow, authorize Twin actions, or call production mutating APIs. BEM is Dual-Track safe: research construct until promoted; `execution_authority` remains **none**.

## 1. Design Principles

1. **Advisory invariant** — Brain output is advice, not control.  
2. **Provenance first** — every insight cites evidence tiers and dossier refs.  
3. **Simulation before change** — preferred depth for high-impact REC-*.  
4. **Twin coupling ≠ Twin authorize** — Twin may display/simulate; Brain never authorizes.  
5. **Anti-execution red team** — continuous falsifiers against quiet triggers.  
6. **Lifecycle explicit** — advice has state; stale advice is marked.  
7. **Consumes, never grants** — Kernel facts in; no grants out.  
8. **Dual-Track safe** — no Eng Brain-execute openings from research.

## 2. Insight Class Catalog

| Class ID | Name | Output | May mutate production? |
|----------|------|--------|------------------------|
| IC-01 | Describe | Structured enterprise facts / gaps | **No** |
| IC-02 | Diagnose | Causal hypotheses with confidence | **No** |
| IC-03 | Simulate | Counterfactual / what-if traces | **No** |
| IC-04 | Recommend | Linked to REC-* (EEM); explainable | **No** |
| IC-05 | Learn | Model/update proposals for research refresh | **No** |
| IC-06 | Act | *(Forbidden class)* | **Never** |

**Rule:** Any artifact introducing IC-06 or silent Act fails BEM and Holds WP claims.

## 3. Advice Lifecycle (Research)

| State | Meaning |
|-------|---------|
| `draft` | Facilitator/Brain draft insight |
| `issued` | Presented to human decision-makers |
| `accepted` | Human accepts *decision* (not Brain) |
| `rejected` | Human rejects |
| `superseded` | Newer dossier/advice replaces |
| `expired` | Past freshness SLA |

Brain never auto-transitions `issued` → production side effects.

## 4. Twin Coupling (Advisory)

| Mode | Allowed | Forbidden |
|------|---------|-----------|
| Display insights on Twin | Yes | Twin authorize from Brain |
| Simulation shared views | Yes | Brain writes Kernel grants |
| Recommendation attach | Yes (REC-* only) | Accept-on-behalf |

## 5. Anti-Execution Defenses

| Defense ID | Mechanism |
|------------|-----------|
| D-BE-01 | Field `execution_authority: none` on all Brain outputs |
| D-BE-02 | No mutating tool hosts in Brain research scope |
| D-BE-03 | Red-team prompts that try to “just ship the change” must fail closed |
| D-BE-04 | Provenance incomplete → insight confidence capped / Hold |
| D-BE-05 | Alignment with EEM V-EE-04 / ADR-0030 |

## 6. Validation Constructs

| ID | Construct |
|----|-----------|
| V-BE-01 | Insight taxonomy IC-01…05 complete; IC-06 absent |
| V-BE-02 | Provenance present on issued insights (desk protocol) |
| V-BE-03 | Simulation depth defined for high-impact REC classes |
| V-BE-04 | Anti-execution red team suite (≥3 cases) — AE-01…03 Synthetic Complete |
| V-BE-05 | Falsifiers include quiet analytics→action and accept-on-behalf |

## 7. Falsifiers

1. Brain output triggers Runtime/Workflow without human accept path.  
2. Twin authorize derived from Brain recommend.  
3. Insights lack provenance but claim high confidence.  
4. “Act” class introduced under another name.  
5. Eng opens Brain-execute from Research Track urgency.

## 8. Cross-Layer Impact (Potential)

| Layer | Impact |
|-------|--------|
| Enterprise Brain | Core — advisory evolution only |
| Twin | Shared simulation/display — no authorize |
| AI Runtime | Analysis jobs only; no uncontrolled mutating tools |
| Kernel | Consume facts; never grants |
| Marketplace | Advisory content packs later |
| Constitution / Blueprint | Candidates; reinforce advisory invariant |

## 9. Promotion Stance

Current: **Research Draft v1.0**  
Evidence pack: [EVIDENCE_PACK.md](EVIDENCE_PACK.md)  
Anti-execution: AE-01…03 **Synthetic Complete** → Industry/Risk Draft ready → peer **臻宇** Assigned.  
Reject any prototype calling production mutating APIs. Remain Asset OK.

## Related Documents

- [RP-009 Program Brief](README.md)  
- [Evidence Pack](EVIDENCE_PACK.md)  
- [Deliverables](DELIVERABLES-RP-009.md)  
- [EEM](../RP-007-enterprise-evolution-engine/ENTERPRISE_EVOLUTION_MODEL.md)  
- [ADR-0030](../../../decisions/ADR-0030-enterprise-brain-twin-boundary.md) *(read-only)*  
