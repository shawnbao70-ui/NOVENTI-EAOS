# RISK-ANALYSIS-RP-008 — Smart Factory

**Research ID:** NRI-RP-008-RISK  
**Program:** RP-008  
**Version:** 1.0  
**Status:** Draft  
**Objective:** Register safety, MES-fork, machine-control, and Dual-Track risks for SFSM before any White Paper path  
**Scope:** In: risk register + hold triggers / Out: product SLOs; Const edits; Runtime privilege design  
**Author:** NRI  
**Reviewer:** 臻宇（Pass — WP Draft Allowed）  
**Approval:** Pending  
**Dependencies:** SFSM §5–6; Evidence Pack; PW-01…02  
**Related ADR:** ADR-0030; ADR-0027; ADR-0162 Dual-Track  
**Promotion Status:** Research Library  
**Classification:** Research Only — Not Normative for Implementation  
**Evidence Tier:** T1  
**Last Updated:** 2026-07-21  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](../../RESEARCH_GOVERNANCE_CHARTER.md)

---

## 1. Posture Summary

Highest residual risks: (a) smart-without-safety, (b) MES Kernel fork, (c) Brain/Twin machine control, (d) fail-open line Terminal, (e) Eng industry openings from Research urgency.

## 2. Risk Register

| Risk ID | Category | Description | L | I | Mitigation | Residual |
|---------|----------|-------------|---|---|------------|----------|
| R-SF-01 | Safety | Pilot robot without SF-03 case | H | Crit | PR bands; PW-01 | Med |
| R-SF-02 | Architectural | MES logic into Core Kernel | M | Crit | `mes_kernelization: never` | Low if enforced |
| R-SF-03 | Safety | Brain/Twin direct machine write | M | Crit | ADR-0030; C-SF-04 | Low |
| R-SF-04 | Method | REC-ROBOT without PR/HOLD | H | Crit | EEM coupling; C-SF-05 | Med |
| R-SF-05 | UX | HQ forms on line; missed exceptions | H | High | SF-04; PW-02 | Med |
| R-SF-06 | Integrity | Synthetic PW over-claimed as T3 | M | High | Tier labels | Low if honest |
| R-SF-07 | OT | Unrestricted MES mutate from edge | M | Crit | AIRM ID-07; PW-02 | Med |
| R-SF-08 | Degraded | Fail-open approvals offline | H | Crit | SF-07 | Med |
| R-SF-09 | Knowledge | Historian as Knowledge truth | H | High | SF-05 | Med |
| R-SF-10 | Governance | Eng soft-queue MES schema premature | L | Crit | Dual-Track | Low |
| R-SF-11 | Commercial | Industry packs without OT scope | M | Med | SF-08 | Med |
| R-SF-12 | Const/BP | Silent safety BOOK obligations | L | High | Promotion Rules only | Low |
| R-SF-13 | Cap | Dept-as-Cap on shop floor | M | High | Cap≠Org; SF-01 | Med |
| R-SF-14 | Adoption | “Smart” branding bypasses peer | H | High | PW suite mandatory for WP | Med |

## 3. Falsifier ↔ Risk Map

| SFSM Falsifier | Risks | Hold |
|----------------|-------|------|
| Smart without safety case | R-SF-01/14 | Hold C-SF-02 |
| MES Kernel fork | R-SF-02/10 | Refuse productize |
| Brain machine Act | R-SF-03 | Hold C-SF-04 |
| Robot without PR/HOLD | R-SF-04 | Hold C-SF-05 |
| Eng MES from Research | R-SF-10 | Dual-Track refuse |

## 4. WP Hold Triggers

1. Any artifact proposes MES-in-Kernel or Brain machine control.  
2. PW-01…02 missing or omit hard boundary fields.  
3. REC-ROBOT presented without PR band / HOLD.  
4. Evidence tiers mislabeled (synthetic as T3).  
5. Fail-open degraded mode treated as compliant.

## 5. Hard Boundaries

No Const/BP/Kernel/Runtime/DB edits. No Twin authorize / Role→grant / payment clearing.

## Related Documents

- [SFSM](SMART_FACTORY_SPECIALIZATION_MODEL.md)  
- [Evidence Pack](EVIDENCE_PACK.md)  
- [Industry Analysis](INDUSTRY_ANALYSIS.md)  
- [walkthroughs/](walkthroughs/)  
