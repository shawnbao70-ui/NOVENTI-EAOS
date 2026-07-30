# RISK-ANALYSIS-RP-002 — Enterprise DNA

**Research ID:** NRI-RP-002-RISK  
**Program:** RP-002  
**Version:** 1.0  
**Status:** Draft  
**Objective:** Register misuse, integrity, adoption, and architectural risks for Enterprise DNA before any White Paper path  
**Scope:** In: risk register + hold triggers / Out: product SLOs; Const edits; Runtime privilege design  
**Author:** NRI  
**Reviewer:** Pending  
**Approval:** Pending  
**Dependencies:** EDNA §7; Evidence Pack; SC-01…03  
**Related ADR:** ADR-0162 Dual-Track  
**Promotion Status:** Research Library  
**Classification:** Research Only — Not Normative for Implementation  
**Evidence Tier:** T1  
**Last Updated:** 2026-07-21  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](../../RESEARCH_GOVERNANCE_CHARTER.md)

---

## 1. Posture Summary

Highest residual risks: (a) DNA used for HR discrimination, (b) DNA fed into authorization, (c) synthetic scorecards over-claimed as T3 stability, (d) collapse to one maturity score that misleads RP-007.

## 2. Risk Register

| Risk ID | Category | Description | L | I | Mitigation | Residual |
|---------|----------|-------------|---|---|------------|----------|
| R-DNA-01 | Legal / Ethics | DNA used for hiring/firing discrimination | M | Crit | Explicit anti-HR use; pilot data rules | Med |
| R-DNA-02 | Architectural | DNA becomes Permission/Twin input | M | Crit | `authorization_input: never`; Dual-Track | Low |
| R-DNA-03 | Integrity | SC synthetic claimed as retest-stable T3 | M | High | Tier labels; retest plan open | Low if honest |
| R-DNA-04 | Method | Axes lockstep (no orthogonality) | M | Med | SC-01…03 contrast checks | Med |
| R-DNA-05 | Method | DNA confused with Growth Stage | H | Med | SC-03 explicit separation | Med |
| R-DNA-06 | Adoption | Culture-quiz vendors rebrand as “DNA” | H | Med | Industry P-DNA-01 narrative | Med |
| R-DNA-07 | Downstream | RP-007 ignores constraint hints | M | High | INPUT_FREEZE + TT linkage | Med |
| R-DNA-08 | Downstream | RP-005 scales AI despite DX-04 Extreme | M | High | SC-01 hints; RI stickiness | Med |
| R-DNA-09 | Privacy | DNA interviews expose sensitive org politics | M | High | Redaction; facilitator rules | Med |
| R-DNA-10 | Governance | Research urgency opens Eng schema for DNA | L | Crit | No Eng ingest without Promote | Low |
| R-DNA-11 | Safety | Low DX-02 ignored → unsafe robot advice | M | Crit | TT-03 / SC-01 Hold paths | Med |
| R-DNA-12 | Const/BP | Silent BOOK/BP DNA obligations | L | High | Promotion Rules only | Low |
| R-DNA-13 | Commercial | Marketplace “DNA packs” sold pre-validation | L | Med | Library-only until promote | Low |
| R-DNA-14 | Brain | Constraint features used to justify execute | L | Crit | Fail-closed Eng; advisory only | Low |

## 3. Falsifier ↔ Risk Map

| EDNA Falsifier | Risks | Hold |
|----------------|-------|------|
| Retest instability | R-DNA-03 | Hold predictive claims |
| Cannot distinguish from Stage theater | R-DNA-05 | Hold WP C-DNA-03 |
| No RP-007 HOLD improvement | R-DNA-07 | Hold C-DNA-05 |
| HR weaponization | R-DNA-01 | Refuse productization path |
| Lockstep axes | R-DNA-04 | Revise axis set |

## 4. WP Hold Triggers

1. Any artifact proposes DNA→grant/authorize.  
2. Evidence tiers mislabeled.  
3. Composite “DNA IQ” introduced as normative.  
4. HR use cases presented as in-scope.

## 5. Hard Boundaries

No Const/BP/Kernel/Runtime/DB edits. No Twin authorize / Brain execute / Role→grant.

## Related Documents

- [EDNA](ENTERPRISE_DNA_MODEL.md)  
- [Industry Analysis](INDUSTRY_ANALYSIS.md)  
- [RP-001 Risk Analysis](../RP-001-enterprise-discovery/RISK_ANALYSIS.md)  
