# RISK-ANALYSIS-RP-010 — Future Enterprise Operating Model

**Research ID:** NRI-RP-010-RISK  
**Program:** RP-010  
**Version:** 1.0  
**Status:** Draft  
**Objective:** Register synthesis, promotion-skipping, and Dual-Track risks for FEOM before any White Paper path  
**Scope:** In: risk register + hold triggers / Out: product SLOs; Const edits; Runtime privilege design  
**Author:** NRI  
**Reviewer:** 臻宇（Pass — WP Draft Allowed）  
**Approval:** Pending（program RISK; WP Accepted separately）  
**Dependencies:** FEOM §5–6; Evidence Pack; SA-01…02  
**Related ADR:** ADR-0162; ADR-0030; ADR-0027  
**Promotion Status:** Research Library  
**Classification:** Research Only — Not Normative for Implementation  
**Evidence Tier:** T1  
**Last Updated:** 2026-07-21  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](../../RESEARCH_GOVERNANCE_CHARTER.md)

---

## 1. Posture Summary

Highest residual risks: (a) FEOM sold as Constitution/Blueprint, (b) vendor TOM equated to EOM, (c) Brain Act / Cap grant leakage in narrative, (d) Eng openings from “completeness,” (e) hierarchy-only spine.

## 2. Risk Register

| Risk ID | Category | Description | L | I | Mitigation | Residual |
|---------|----------|-------------|---|---|------------|----------|
| R-EOM-01 | Governance | Slide deck treated as Const/BP update | M | Crit | `constitution_rewrite: never`; Dual-Track | Low if enforced |
| R-EOM-02 | Method | Vendor suite sold as FEOM | H | High | Falsifier #3; SA-01 | Med |
| R-EOM-03 | Safety | Brain Act in EOM narrative | M | Crit | C-EOM-04; ADR-0030 | Low |
| R-EOM-04 | Authz | Cap/DNA/Org imply grants | M | Crit | Consistency matrix | Low |
| R-EOM-05 | Integrity | Synthetic SA over-claimed as T3 | M | High | Tier labels | Low if honest |
| R-EOM-06 | Neutrality | Hierarchy-only operating story | H | High | ONM; SA-02 | Med |
| R-EOM-07 | Method | Skip ES-01/02 into Operate | H | High | Spine gate | Med |
| R-EOM-08 | Infra | GPU-as-EOM | H | Med | AIRM coupling; SA-01 | Med |
| R-EOM-09 | Governance | Eng soft-queue from EOM urgency | L | Crit | ADR-0162 | Low |
| R-EOM-10 | Adoption | Residual human duty erased | M | High | R1/R2 in narrative | Med |
| R-EOM-11 | Plant | MES Kernel via EOM story | L | Crit | RP-008 invariants | Low |
| R-EOM-12 | Const/BP | Silent multi-BOOK obligations | L | High | Promotion Rules only | Low |
| R-EOM-13 | Commercial | EOM packs sold pre-validation | L | Med | Library-only | Low |
| R-EOM-14 | Synthesis | Contradicts peer-passed RP invariants | M | Crit | Consistency matrix; SA-02 | Med |

## 3. Falsifier ↔ Risk Map

| FEOM Falsifier | Risks | Hold |
|----------------|-------|------|
| Const/BP from FEOM alone | R-EOM-01/12 | Hold C-EOM-03 |
| Vendor TOM = EOM | R-EOM-02 | Hold C-EOM-01 |
| Brain Act / grant leak | R-EOM-03/04 | Refuse WP path |
| Eng from completeness | R-EOM-09 | Dual-Track refuse |
| Hierarchy-only spine | R-EOM-06 | Hold C-EOM-05 |

## 4. WP Hold Triggers

1. Any artifact proposes Const/BP/Kernel rewrite as done.  
2. SA-01…02 missing or omit hard boundary fields.  
3. Narrative drops HOLD / Cap≠Org / Brain never Act.  
4. Evidence tiers mislabeled (synthetic as T3).  
5. Eng openings requested from EOM completeness.

## 5. Hard Boundaries

No Const/BP/Kernel/Runtime/DB edits. No Twin authorize / Role→grant / payment clearing.

## Related Documents

- [FEOM](FUTURE_ENTERPRISE_OPERATING_MODEL.md)  
- [Evidence Pack](EVIDENCE_PACK.md)  
- [Industry Analysis](INDUSTRY_ANALYSIS.md)  
- [audits/](audits/)  
