# RISK-ANALYSIS-RP-006 — AI Infrastructure Platform

**Research ID:** NRI-RP-006-RISK  
**Program:** RP-006  
**Version:** 1.0  
**Status:** Draft  
**Objective:** Register governance, isolation, OT, and Dual-Track risks for AIRM before any White Paper path  
**Scope:** In: risk register + hold triggers / Out: product SLOs; Const edits; Runtime privilege design  
**Author:** NRI  
**Reviewer:** 臻宇（Pass — WP Draft Allowed）  
**Approval:** Pending  
**Dependencies:** AIRM §5–6; Evidence Pack; GP-01…02  
**Related ADR:** ADR-0027; ADR-0008; ADR-0162 Dual-Track  
**Promotion Status:** Research Library  
**Classification:** Research Only — Not Normative for Implementation  
**Evidence Tier:** T1  
**Last Updated:** 2026-07-21  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](../../RESEARCH_GOVERNANCE_CHARTER.md)

---

## 1. Posture Summary

Highest residual risks: (a) GPU-as-readiness theater, (b) Kernel bypass via infra shortcuts, (c) parallel approval outside Workflow, (d) unrestricted OT mutate, (e) Eng Runtime openings from Research urgency.

## 2. Risk Register

| Risk ID | Category | Description | L | I | Mitigation | Residual |
|---------|----------|-------------|---|---|------------|----------|
| R-INF-01 | Method | GPU roadmap sold as AIRM-complete | H | High | Eight-domain scoring; GP-01 | Med |
| R-INF-02 | Architectural | Infra topology bypasses Kernel | M | Crit | `kernel_bypass: never` | Low if enforced |
| R-INF-03 | Governance | Parallel approval outside Workflow | H | Crit | ID-04; ADR-0008 | Low if enforced |
| R-INF-04 | Safety | OT agents unrestricted MES write | M | Crit | ID-07 island; GP-02 | Med |
| R-INF-05 | Integrity | Synthetic GP over-claimed as T3 | M | High | Tier labels | Low if honest |
| R-INF-06 | Isolation | Cross-tenant model/tool leakage | H | Crit | ID-06; ADR-0007 | Med |
| R-INF-07 | Supply chain | Unsigned models/tools installed | H | High | ID-08 | Med |
| R-INF-08 | Downstream | RP-007 Agentize despite I1 ID-04 | M | High | Export hints; HOLD | Med |
| R-INF-09 | Brain | Infra capacity used to justify execute | L | Crit | ADR-0030; advisory | Low |
| R-INF-10 | Governance | Eng soft-queue Runtime schema premature | L | Crit | Dual-Track; no Eng ingest | Low |
| R-INF-11 | Observability | Uncorrelatable AI actions | H | High | ID-05 | Med |
| R-INF-12 | Const/BP | Silent infra BOOK obligations | L | High | Promotion Rules only | Low |
| R-INF-13 | Commercial | “AI landing zone” packs pre-validation | L | Med | Library-only | Low |
| R-INF-14 | Identity | Orphan agents without subject_id | M | High | ID-01 | Med |

## 3. Falsifier ↔ Risk Map

| AIRM Falsifier | Risks | Hold |
|----------------|-------|------|
| GPU without ID-04/05/06 | R-INF-01/03/06 | Hold C-INF-02 |
| Kernel grant shortcut | R-INF-02/10 | Refuse productize |
| Parallel approval | R-INF-03 | Hold V-INF-02 |
| OT unrestricted mutate as I3+ | R-INF-04 | Hold C-INF-05 |
| Eng Runtime from Research | R-INF-10 | Dual-Track refuse |

## 4. WP Hold Triggers

1. Any artifact proposes Kernel bypass / grant from infra.  
2. GP-01…02 missing, skipped, or omit `kernel_bypass: never`.  
3. Parallel approval presented as compliant.  
4. Evidence tiers mislabeled (synthetic as T3).  
5. OT open-mutate claimed managed readiness.

## 5. Hard Boundaries

No Const/BP/Kernel/Runtime/DB edits. No Brain execute / Twin authorize / Role→grant / payment clearing.

## Related Documents

- [AIRM](AI_INFRASTRUCTURE_REFERENCE_MODEL.md)  
- [Evidence Pack](EVIDENCE_PACK.md)  
- [Industry Analysis](INDUSTRY_ANALYSIS.md)  
- [gap-profiles/](gap-profiles/)  
