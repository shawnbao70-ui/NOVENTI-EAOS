# WP-RP-008 — Smart Factory Specialization Model White Paper

**Institute:** NOVENTI Research Institute  
**Research ID:** NRI-WP-RP-008  
**Program:** RP-008 Smart Factory  
**Version:** 0.1  
**Status:** Accepted White Paper  
**Objective:** Freeze the Smart Factory Specialization Model (SFSM) as a peer-passed White Paper — overlay not fork; mes_kernelization never; machine_control_from_brain never  
**Scope:** In: WP synthesis of SFSM + PW-01…02 / Out: Const/BP/Kernel/Runtime edits; Eng MES schema; Brain execute; Twin authorize  
**Author:** NRI  
**Reviewer:** 臻宇（peer Pass recorded; WP content Accepted（CA delegated DAL-G003））  
**Approval:** Accepted — WP content Accepted（Chief Architect delegated authority DAL-G003 through 2026-07-27；recorded 2026-07-21）  
**Dependencies:** [SFSM](SMART_FACTORY_SPECIALIZATION_MODEL.md); [Evidence Pack](EVIDENCE_PACK.md); [PEER](PEER_REVIEW_PACKAGE.md); ADR-0030  
**Related Capability:** Industry / Smart Factory  
**Related Blueprint:** Package/Terminal/Event *(candidates)*  
**Related Constitution:** Industry/safety books *(candidates)*  
**Related ADR:** ADR-0030 / ADR-0027 / ADR-0008 *(read-only)*; ADR-0162  
**Promotion Status:** Research Library  
**Evidence Floor:** T1 + planned T2/T3  
**Classification:** Research Only — Not Normative for Implementation  
**Governing Directive:** Research Governance Charter v1.0  
**Last Updated:** 2026-07-21  
**Peer gate:** Pass — WP Draft Allowed（臻宇；2026-07-21）  
**Content Acceptance:** Accepted（Chief Architect delegated DAL-G003；2026-07-21）

---

## Abstract

Enterprises chase “smart factory” pilots faster than they design safety cases and governed plant overlays. The Smart Factory Specialization Model (SFSM) defines eight domains (SF-01…08)—plant capability overlay, Human/AI/Robot/Device mix, physical risk & safety case, line-side Terminal UX, OT event/historian coupling, robot/cell readiness, degraded/offline mode, industry package scope—with physical risk bands PR0–PR4. Smart-without-safety is a defect. Plants specialize EERP as an **overlay**, never an MES Kernel fork (`mes_kernelization: never`). Brain remains advisory—never direct machine control (`machine_control_from_brain: never`). Synthetic plant walkthroughs PW-01 (discrete cell) and PW-02 (line Terminal + OT) exercise critical-path gaps before scale. Peer 臻宇 passed PR-SF-01…12. This White Paper freezes SFSM under CA Content Acceptance (DAL-G003); Architecture Review and Eng MES/machine-control openings remain closed.

## 1. Problem Statement

MES/ERP/AI poorly governed together, safety bypassed by “smart” pilots, HQ UX forced on the line, and Brain/Twin sold as machine controllers masquerade as plant readiness. EAOS needs a falsifiable, Dual-Track-safe specialization thesis aligned to ADR-0030 / ADR-0027.

## 2. Research Questions

1. Are eight domains jointly necessary without a single factory IQ?  
2. Can safety-before-smart and overlay-not-fork be enforced in desk instruments?  
3. What falsifiers (MES Kernel fork, Brain machine control, REC-ROBOT without PR case, Eng from Research) Hold WP Acceptance?

## 3. Constructs and Definitions

| Construct | Definition | Measurement Approach |
|-----------|------------|----------------------|
| SF-01…08 | Plant specialization domains | PW scoring |
| PR0–PR4 | Physical risk bands | Per-path ordinal |
| mes_kernelization | Must be never | Peer PR-SF-07; PW field |
| machine_control_from_brain | Must be never | Peer PR-SF-07; PW field |
| OT safety island | Read advise OK; unrestricted MES write never | PW-02 / SF-05; AIRM ID-07 |

## 4. Method

- Desk synthesis of SFSM v1.0  
- Synthetic PW-01…02 plant walkthrough overlays  
- Industry P-SF-01…10; Risk R-SF-01…14  
- Peer PR-SF-01…12 (Pass)  
- Limitations: no live T3 plant evidence yet  

## 5. Findings

### 5.1 Structural Findings

Eight domains teachable; critical path SF-03→06 (safety before robot claims) and SF-04/07 (line Terminal + degraded) before scale; affinity to industry packages remains research overlay only.

### 5.2 Enterprise Patterns

See [INDUSTRY_ANALYSIS.md](INDUSTRY_ANALYSIS.md) — smart-without-safety, MES-as-Kernel pressure, Brain-as-controller theater.

### 5.3 Negative Evidence

MES logic in Core Kernel, Brain/Twin machine write, or REC-ROBOT without PR/RC case fail PR-SF and Hold WP Acceptance.

## 6. Proposed Framework / Model

Canonical model: [SMART_FACTORY_SPECIALIZATION_MODEL.md](SMART_FACTORY_SPECIALIZATION_MODEL.md) (NRI-RP-008-SFSM).

## 7. Cross-Layer Impact Analysis

| Layer | Impact Class | Notes |
|-------|--------------|-------|
| Architecture | Observational | Industry overlay / OT integration candidates |
| Kernel | Dependencies only | Sites/units; never MES kernelization |
| Runtime / AI Runtime | Observational | Edge constraints; OT tools high_impact |
| Smart Terminal | Core subject | Line-side UX; offline rules — research only |
| Enterprise Brain | Advisory only | OEE/quality; never machine Act |
| Marketplace | Observational | Industry packs with declared OT scopes later |
| Constitution / Blueprint | Candidates | No edits now |

## 8. Risks and Constraints

| Risk | Severity | Mitigation |
|------|----------|------------|
| MES Kernel fork | Critical | mes_kernelization: never |
| Brain machine control | Critical | machine_control_from_brain: never |
| Smart-without-safety | Critical | SF-03; PR bands; PW-01 |

Full register: [RISK_ANALYSIS.md](RISK_ANALYSIS.md).

## 9. Falsifiers

1. Smart pilot sold as SFSM-complete without SF-03/06.  
2. MES logic moved into Core Kernel.  
3. Brain/Twin authorize machine write.  
4. REC-ROBOT without PR band / RC case.  
5. Eng MES/industry schema tickets from Research urgency alone.

## 10. Validation Status

Peer Pass — [PEER_REVIEW_PACKAGE.md](PEER_REVIEW_PACKAGE.md).  
Evidence pack: [EVIDENCE_PACK.md](EVIDENCE_PACK.md).  
Plant walkthroughs: [walkthroughs/](walkthroughs/).

## 11. Pilot Recommendations

Discrete-cell + line-Terminal/OT deep-dives scored against SFSM; condition robot paths on PR ≥ PR2 with RC case; live T2/T3 planned.

## 12. Promotion Recommendation

After **WP Acceptance**: deepen industry package candidates; Architecture Review only via Dual-Track — not from this WP alone. Remain Asset OK.

## 13. Open Questions

- Historian → governed knowledge cadence (SF-05)  
- Collaborative (PR3) approval UX on line Terminal  
- Interaction with RP-006 OT island depth and RP-010 plant EOM stories  

## References

- [SFSM](SMART_FACTORY_SPECIALIZATION_MODEL.md)  
- [Evidence Pack](EVIDENCE_PACK.md)  
- [walkthroughs/](walkthroughs/)  
- [Industry](INDUSTRY_ANALYSIS.md) · [Risk](RISK_ANALYSIS.md)  
- [WAVE3_PEER_ASSIGNMENT](../../WAVE3_PEER_ASSIGNMENT.md)  
- [ADR-0030](../../../decisions/ADR-0030-enterprise-brain-twin-boundary.md)  
- [ADR-0027](../../../decisions/ADR-0027-ai-runtime-boundary.md)  

## Appendix A — Evidence Log

| Claim ID | Claim | Evidence Tier | Source |
|----------|-------|---------------|--------|
| C-SF-* | See Evidence Pack | T1 (+ planned T2/T3) | [EVIDENCE_PACK.md](EVIDENCE_PACK.md) |
