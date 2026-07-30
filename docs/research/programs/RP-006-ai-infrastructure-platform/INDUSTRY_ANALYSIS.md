# INDUSTRY-ANALYSIS-RP-006 — AI Infrastructure Platform

**Research ID:** NRI-RP-006-IND  
**Program:** RP-006 AI Infrastructure Platform  
**Version:** 1.0  
**Status:** Draft  
**Objective:** Synthesize industry patterns that justify governance-before-GPU and eight-domain AIRM scoring  
**Scope:** In: shadow AI, approval gaps, OT islands, supply-chain trust / Out: vendor BOM; Const/BP/Kernel/Runtime edits  
**Author:** NRI  
**Reviewer:** 臻宇（Pass — WP Draft Allowed）  
**Approval:** Pending  
**Dependencies:** [AIRM](AI_INFRASTRUCTURE_REFERENCE_MODEL.md); GP-01…02; ADR-0027 (read-only)  
**Related Capability:** AI Infrastructure  
**Related Blueprint:** BP-RUNTIME / BP-AI *(candidates)*  
**Related Constitution:** Security/AI governance books *(candidates)*  
**Promotion Status:** Research Library  
**Classification:** Research Only — Not Normative for Implementation  
**Evidence Tier:** T1  
**Last Updated:** 2026-07-21  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](../../RESEARCH_GOVERNANCE_CHARTER.md)

---

## 1. Thesis

Enterprises buy **accelerators and seats** faster than they design **landing zones**. Industry needs eight-domain AIRM scoring so Evolution readiness and OT coupling hit approval/isolation gaps first — without Kernel bypass or Brain-execute from infra urgency.

## 2. Cross-Industry Patterns

| ID | Pattern | Symptom | AIRM Stress | Seen in |
|----|---------|---------|-------------|---------|
| P-INF-01 | GPU-as-readiness | Capacity roadmap = “AI ready” | C-INF-02 | GP-01 |
| P-INF-02 | Shadow SaaS | Keys in chat; no Identity landing | ID-01/02 | GP-01 |
| P-INF-03 | Unregistered tools | High-impact invoke without RegisterTool | ID-03 | GP-01/02 |
| P-INF-04 | Parallel approval | Slack bots outside Workflow | ID-04; V-INF-02 | GP-01 |
| P-INF-05 | Audit theater | Logs without correlation_id | ID-05 | GP-02 |
| P-INF-06 | Shared model pool | Weak tenant tags | ID-06 | GP-01 |
| P-INF-07 | Open OT mutate | Plant agents write MES freely | ID-07 | GP-02 |
| P-INF-08 | Unsigned artifacts | Models/tools without verify chain | ID-08 | GP-01/02 |
| P-INF-09 | Infra→grant leakage | Topology used to mint access | C-INF-03 | Dual-Track risk |
| P-INF-10 | Eng urgency | Research → Runtime schema tickets | Dual-Track | Soft-queue ban |

## 3. Sector Notes

### Cloud-native (GP-01)
Critical path through tool fabric, approval bridge, and tenant isolation before model scale.

### Hybrid OT (GP-02)
Safety islands and approval/observability before any plant Agentize; unrestricted MES write forbidden.

## 4. Hard Boundaries

No Const/BP/Kernel/Runtime/DB edits. No Brain execute / Twin authorize / Role→grant / payment clearing.

## Related Documents

- [AIRM](AI_INFRASTRUCTURE_REFERENCE_MODEL.md)  
- [gap-profiles/](gap-profiles/)  
- [EVIDENCE_PACK.md](EVIDENCE_PACK.md)  
