# RISK-ANALYSIS-RP-005 — AI Workforce Transformation

**Research ID:** NRI-RP-005-RISK  
**Program:** RP-005  
**Version:** 1.0  
**Status:** Draft  
**Objective:** Register legal, safety, adoption, architectural, and research-integrity risks for ANRF before White Paper  
**Scope:** In: risk register + hold triggers / Out: product SLOs; Const edits; Runtime privilege design  
**Author:** NRI  
**Reviewer:** 包锦昱（via PEER package；decision Pending）  
**Approval:** Pending  
**Dependencies:** ANRF §7–8, §11; RI-01…02; Evidence Pack  
**Related Constitution:** BOOK03  
**Related ADR:** ADR-0021; ADR-0162  
**Promotion Status:** Research Library  
**Classification:** Research Only — Not Normative for Implementation  
**Evidence Tier:** T1  
**Last Updated:** 2026-07-21  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](../../RESEARCH_GOVERNANCE_CHARTER.md)

---

## 1. Posture Summary

Highest residual risks: (a) AI treated as legal person / residual duty erased, (b) title→grant leakage into Eng, (c) RC5 robot scale without certified path, (d) synthetic inventories over-claimed as T3.

## 2. Risk Register

| Risk ID | Category | Description | L | I | Mitigation | Residual |
|---------|----------|-------------|---|---|------------|----------|
| R-AW-01 | Legal | AI assigned liability / personhood | M | Crit | ANRF §8; legal peer; Refuse fusion | Low if peer holds |
| R-AW-02 | Architectural | ANRF mints Permission grants | M | Crit | `auto_grant_minted: never`; Dual-Track | Low |
| R-AW-03 | Safety | Unsupervised RC5 robotization | M | Crit | RI-02 vetoes; certified path only | Med |
| R-AW-04 | Operational | Cap/title collapse in inventories | M | Med | Cap≠title checks; RP-001 link | Med |
| R-AW-05 | Adoption | License theater reasserts | H | Med | Industry P-AW-04; readiness≠seats | Med |
| R-AW-06 | Integrity | Synthetic RI claimed as T3 | M | High | Explicit T1 labels | Low if honest |
| R-AW-07 | Legal | Labor/works-council bypass | M | High | Flag in pilots; jurisdiction overlays | Med |
| R-AW-08 | Privacy | Role inventory leaks PII | M | High | Synthetic codenames; pilot data rules | Med |
| R-AW-09 | Downstream | RP-007 Agentize from weak RI | M | High | TT-02 Assist≠Agentize | Med |
| R-AW-10 | Governance | Research urgency opens Role→grant Eng item | L | Crit | Explicit Defer numbered only | Low |
| R-AW-11 | Method | Families too abstract cross-industry | M | Med | RI-01/02 overlays; falsifier #2 | Med |
| R-AW-12 | Method | Fusion raises incidents | M | High | Do not claim safety gain yet | Med |
| R-AW-13 | Const | Silent BOOK03 rewrite | L | High | Promotion Rules; read-only BOOK03 | Low |
| R-AW-14 | Brain/Twin | Execute/authorize via “workforce urgency” | L | Crit | Fail-closed Eng invariants | Low |

## 3. Falsifier ↔ Risk Map

| ANRF Falsifier | Risks | Hold |
|----------------|-------|------|
| Demand AI legal ownership | R-AW-01 | Hold C-AW-02/10 |
| Families useless abstraction | R-AW-11 | Require industry overlays |
| Fusion raises incidents | R-AW-12 | No safety claims |
| Title≠grant breaks | R-AW-02/04 | Hold V-AW-05 claims |
| Irremediable BOOK03 conflict | R-AW-13 | Hold promotion path |

## 4. WP Hold Triggers

1. Legal peer rejects residual-human language.  
2. Any artifact proposes grant mint or execute open.  
3. Evidence tiers mislabeled.  
4. RC5 Refuse paths removed without certified alternative.

## 5. Hard Boundaries

No Const/BP/Kernel/Runtime/DB edits. No Role→grant / Brain execute / Twin authorize / payment clearing.

## Related Documents

- [ANRF](AI_NATIVE_ROLE_FRAMEWORK.md)  
- [Industry Analysis](INDUSTRY_ANALYSIS.md)  
- [Peer Review Package](PEER_REVIEW_PACKAGE.md)  
- [RP-001 Risk Analysis](../RP-001-enterprise-discovery/RISK_ANALYSIS.md)  
