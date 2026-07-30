# WP-RP-003 — Capability First Model White Paper

**Institute:** NOVENTI Research Institute  
**Research ID:** NRI-WP-RP-003  
**Program:** RP-003 Capability First  
**Version:** 0.1  
**Status:** Accepted White Paper  
**Objective:** Freeze the Capability First Model (CFM) as a peer-passed White Paper draft — capability graphs first; Cap≠Org; Capability ≠ Permission  
**Scope:** In: WP synthesis of CFM + CG-01…02 / Out: Const/BP/Kernel/Runtime edits; Eng ingest; Cap→grant; Twin authorize / Brain execute  
**Author:** NRI  
**Reviewer:** 臻宇（peer Pass recorded; WP content Accepted（CA delegated））  
**Approval:** Accepted — WP content Accepted（Chief Architect delegated authority 2026-07-21…2026-07-22；recorded 2026-07-21）  
**Dependencies:** [CFM](CAPABILITY_FIRST_MODEL.md); [Evidence Pack](EVIDENCE_PACK.md); [PEER](PEER_REVIEW_PACKAGE.md); RP-001 / RP-004  
**Related Capability:** Capability Model  
**Related Blueprint:** Package / Twin / Brain *(candidates)*  
**Related Constitution:** Capability / Org books *(candidates)*  
**Related ADR:** ADR-0162  
**Promotion Status:** Research Library  
**Evidence Floor:** T1 + planned T2/T3  
**Classification:** Research Only — Not Normative for Implementation  
**Governing Directive:** Research Governance Charter v1.0  
**Last Updated:** 2026-07-21  
**Peer gate:** Pass — WP Draft Allowed（臻宇；2026-07-21）  
**Content Acceptance:** Accepted（Chief Architect delegated；2026-07-21）

---

## Abstract

Enterprises plan AI and automation against org charts and then discover critical paths live elsewhere. The Capability First Model (CFM) treats enterprises as **capability graphs**—nodes with outcomes, maturity L0–L4, automation affinity A0–A4, and dependency edges—while organization remains descriptive anchors only. Cap≠Org and Capability ≠ Permission (`auto_grant_minted: never`) are hard invariants. Synthetic graphs CG-01…02 (T1) exercise Cap≠Org checklists and critical-path priority shifts vs department roadmaps. Peer 臻宇 passed PR-CAP-01…12. This White Paper Draft freezes CFM for later WP Acceptance; Architecture Review and Cap→grant remain closed.

## 1. Problem Statement

Dept-first AI roadmaps fund theater seats; capability gaps on the critical path stay invisible. Treating capability presence as Runtime authority collapses Permission discipline. EAOS needs a falsifiable, non-granting capability metamodel.

## 2. Research Questions

1. Is a capability graph a superior planning lens to org-chart-first for AI/evolution advice?  
2. Can Cap≠Org and Capability ≠ Permission be enforced in workshop instruments?  
3. What falsifiers (Cap≠Org collapse, affinity→execute, grant mint from Cap ID) Hold WP Acceptance?

## 3. Constructs and Definitions

| Construct | Definition | Measurement Approach |
|-----------|------------|----------------------|
| Capability node | Stable ID + outcome + level + affinity | CG protocol |
| Dependency edges | requires / amplifies / conflicts / feeds | Graph desk review |
| Cap≠Org | Dept name ≠ capability_id | Checklist on CG |
| auto_grant_minted | Must be never | Peer PR-CAP-07 |
| Automation affinity | A0–A4 advisory hint to RP-007 | Not execution |

## 4. Method

- Desk synthesis of CFM v1.0  
- Synthetic CG-01…02 from RP-001 WT dossiers  
- Industry P-CAP-01…10; Risk R-CAP-01…14  
- Peer PR-CAP-01…12 (Pass)  
- Limitations: no live T3 workshop yet  

## 5. Findings

### 5.1 Structural Findings

Cap≠Org teachable on CG-01…02; critical paths reorder priorities vs Quality/IT dept roadmaps; affinity remains advisory.

### 5.2 Enterprise Patterns

See [INDUSTRY_ANALYSIS.md](INDUSTRY_ANALYSIS.md) — org-label collapse, affinity theater, grant-pressure patterns.

### 5.3 Negative Evidence

Dept-as-capability, Cap ID → Permission mint, or affinity auto-execute fail PR-CAP and Hold WP Acceptance.

## 6. Proposed Framework / Model

Canonical model: [CAPABILITY_FIRST_MODEL.md](CAPABILITY_FIRST_MODEL.md) (NRI-RP-003-CFM).

## 7. Cross-Layer Impact Analysis

| Layer | Impact Class | Notes |
|-------|--------------|-------|
| Architecture | Observational | Cap registry candidates later |
| Kernel | None / Conflict if misused | Never grant from Cap |
| Runtime | None | Affinity ≠ execute |
| Smart Terminal | Observational | Facilitator Cap worksheets |
| Enterprise Brain | Observational | Cap features; no execute |
| Marketplace | Observational | Cap-indexed packs later |
| Constitution / Blueprint | Candidates | No edits now |

## 8. Risks and Constraints

| Risk | Severity | Mitigation |
|------|----------|------------|
| Cap→grant | Critical | auto_grant_minted: never |
| Cap≠Org collapse | High | CG checklists; falsifiers |
| Affinity misuse | Med–High | Advisory-only; RP-007 HOLD |

Full register: [RISK_ANALYSIS.md](RISK_ANALYSIS.md).

## 9. Falsifiers

1. Facilitators cannot state Cap without naming a department.  
2. Capability presence treated as Permission.  
3. Critical-path analysis does not change priorities vs dept roadmap.  
4. Affinity bands trigger Runtime mutation.  
5. Cap IDs unstable across reorg (fails RP-004 N-08 coupling).

## 10. Validation Status

Peer Pass — [PEER_REVIEW_PACKAGE.md](PEER_REVIEW_PACKAGE.md).  
Evidence pack: [EVIDENCE_PACK.md](EVIDENCE_PACK.md).

## 11. Pilot Recommendations

Reuse RP-001 dossiers; run Cap workshops before AI seat buys; condition RP-005/007 on Cap IDs; live T2/T3 planned.

## 12. Promotion Recommendation

After **WP Acceptance**: deepen Cap registry candidates; Architecture Review only via Dual-Track — not from this WP alone. Remain Asset OK.

## 13. Open Questions

- Cap ID governance across tenants  
- Affinity calibration thresholds  
- Interaction with RP-004 pluralism and RP-002 DNA stickiness  

## References

- [CFM](CAPABILITY_FIRST_MODEL.md)  
- [Evidence Pack](EVIDENCE_PACK.md)  
- [Graphs](graphs/README.md)  
- [Industry](INDUSTRY_ANALYSIS.md) · [Risk](RISK_ANALYSIS.md)  
- [WAVE2_PEER_ASSIGNMENT](../../WAVE2_PEER_ASSIGNMENT.md)  

## Appendix A — Evidence Log

| Claim ID | Claim | Evidence Tier | Source |
|----------|-------|---------------|--------|
| C-CAP-* | See Evidence Pack | T1 (+ planned T2/T3) | [EVIDENCE_PACK.md](EVIDENCE_PACK.md) |
