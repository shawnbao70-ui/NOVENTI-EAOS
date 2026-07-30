# RISK-ANALYSIS-RP-004 — Organization Neutrality

**Research ID:** NRI-RP-004-RISK  
**Program:** RP-004  
**Version:** 1.0  
**Status:** Draft  
**Objective:** Register hierarchy chauvinism, grant leakage, adoption, and architectural risks for Organization Neutrality before any White Paper path  
**Scope:** In: risk register + hold triggers / Out: product SLOs; Const edits; Runtime privilege design  
**Author:** NRI  
**Reviewer:** 臻宇（PEER Assigned — decision Pending）  
**Approval:** Pending  
**Dependencies:** ONM §6; Evidence Pack; NA-01…02  
**Related ADR:** ADR-0162 Dual-Track; ADR-0019/0022 *(read-only)*  
**Promotion Status:** Research Library  
**Classification:** Research Only — Not Normative for Implementation  
**Evidence Tier:** T1  
**Last Updated:** 2026-07-21  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](../../RESEARCH_GOVERNANCE_CHARTER.md)

---

## 1. Posture Summary

Highest residual risks: (a) REC/UX remain manager-only despite checklist Pass, (b) Org-shape→grant leakage, (c) maturity ladders punishing plural forms, (d) Eng premature Organization schema tickets from neutrality research.

## 2. Risk Register

| Risk ID | Category | Description | L | I | Mitigation | Residual |
|---------|----------|-------------|---|---|------------|----------|
| R-ON-01 | Method | Checklist Pass but product copy still manager-only | H | High | N-05 advisory; Terminal language gate later | Med |
| R-ON-02 | Architectural | Org chart shape becomes Permission input | M | Crit | `org_shape_grant: never`; Dual-Track | Low |
| R-ON-03 | Integrity | Synthetic audits over-claimed as T3 live | M | High | Tier labels; live OF-03 planned | Low if honest |
| R-ON-04 | Method | Cap IDs renamed on every reorg | M | Med | N-08; Cap≠Org discipline | Med |
| R-ON-05 | Adoption | Maturity vendors rebrand hierarchy as “Level 5 org” | H | Med | P-ON-02 narrative | Med |
| R-ON-06 | Downstream | RP-007 templates ignore parameterized rights | M | High | NA-02 defect log | Med |
| R-ON-07 | Downstream | RP-005 title→grant via practice boxes | M | High | ANRF + N-07 | Med |
| R-ON-08 | Commercial | Packages hide mandatory hierarchy | L | Med | N-06 declarations | Low |
| R-ON-09 | Privacy | Org-rights workshops expose politics | M | High | Redaction; facilitator rules | Med |
| R-ON-10 | Governance | Eng soft-queue Org schema from ONM | L | Crit | No Eng ingest without Promote | Low |
| R-ON-11 | Const/BP | Silent BOOK org ideology | L | High | Promotion Rules only | Low |
| R-ON-12 | Brain | Neutrality used to justify execute | L | Crit | Fail-closed; advisory | Low |
| R-ON-13 | Federation | Multi-entity rights collapsed | M | High | N-04; deepen OF-03 | Med |
| R-ON-14 | Cultural | One-culture OS imposed globally | M | High | OF pluralism catalog | Med |

## 3. Falsifier ↔ Risk Map

| ONM Falsifier | Risks | Hold |
|---------------|-------|------|
| Instruments need Cap rename on matrix | R-ON-04 | Hold C-ON-02 |
| Advice always “ask your manager” | R-ON-01/06 | Hold C-ON-04 |
| OF-02…07 scored immature by definition | R-ON-05 | Hold C-ON-05 |
| Org shape → grant | R-ON-02/07/10 | Refuse productize |
| Hidden package hierarchy | R-ON-08 | Hold commercial claims |

## 4. WP Hold Triggers

1. Any artifact proposes Org-shape→grant.  
2. Neutrality checklist skipped or N-01/N-07 fail.  
3. Maturity ladder punishes plural forms as design.  
4. Evidence tiers mislabeled.

## 5. Hard Boundaries

No Const/BP/Kernel/Runtime/DB edits. No Twin authorize / Brain execute / Role→grant.

## Related Documents

- [ONM](ORGANIZATION_NEUTRALITY_MODEL.md)  
- [Industry Analysis](INDUSTRY_ANALYSIS.md)  
- [RP-003 Risk Analysis](../RP-003-capability-first/RISK_ANALYSIS.md)  
