# WP-RP-006 — AI Infrastructure Reference Model White Paper

**Institute:** NOVENTI Research Institute  
**Research ID:** NRI-WP-RP-006  
**Program:** RP-006 AI Infrastructure Platform  
**Version:** 0.1  
**Status:** Accepted White Paper  
**Objective:** Freeze the AI Infrastructure Reference Model (AIRM) as a peer-passed White Paper draft — governance-before-GPU; kernel_bypass never  
**Scope:** In: WP synthesis of AIRM + GP-01…02 / Out: Const/BP/Kernel/Runtime edits; Eng Runtime schema; Brain execute; Twin authorize  
**Author:** NRI  
**Reviewer:** 臻宇（peer Pass recorded; WP content Accepted（CA delegated））  
**Approval:** Accepted — WP content Accepted（Chief Architect delegated authority 2026-07-21…2026-07-22；recorded 2026-07-21）  
**Dependencies:** [AIRM](AI_INFRASTRUCTURE_REFERENCE_MODEL.md); [Evidence Pack](EVIDENCE_PACK.md); [PEER](PEER_REVIEW_PACKAGE.md); ADR-0027  
**Related Capability:** AI Infrastructure  
**Related Blueprint:** BP-RUNTIME / BP-AI *(candidates)*  
**Related Constitution:** Security/AI governance books *(candidates)*  
**Related ADR:** ADR-0027 / ADR-0008 / ADR-0007 *(read-only)*; ADR-0162  
**Promotion Status:** Research Library  
**Evidence Floor:** T1 + planned T2/T3  
**Classification:** Research Only — Not Normative for Implementation  
**Governing Directive:** Research Governance Charter v1.0  
**Last Updated:** 2026-07-21  
**Peer gate:** Pass — WP Draft Allowed（臻宇；2026-07-21）  
**Content Acceptance:** Accepted（Chief Architect delegated；2026-07-21）

---

## Abstract

Enterprises buy accelerators and seats faster than they design governed landing zones. The AI Infrastructure Reference Model (AIRM) defines eight domains (ID-01…08)—identity landing, model hosting, tool fabric, approval bridge, observability, tenant isolation, edge/OT coupling, supply-chain trust—with readiness bands I0–I4. GPU/capacity without governance is a defect. Infra must never bypass Kernel Permission/Workflow (`kernel_bypass: never`). Synthetic gap profiles GP-01 (cloud-native) and GP-02 (hybrid OT) exercise critical-path gaps before scale. Peer 臻宇 passed PR-INF-01…12. This White Paper Draft freezes AIRM for later WP Acceptance; Architecture Review and Runtime schema openings remain closed.

## 1. Problem Statement

Shadow SaaS, unregistered high-impact tools, parallel approval bots, and open OT mutate masquerade as “AI-ready infra.” EAOS needs a falsifiable, Dual-Track-safe readiness thesis aligned to ADR-0027.

## 2. Research Questions

1. Are eight domains jointly necessary without a single infra IQ?  
2. Can governance-before-GPU and approval-bridge critical path be enforced in desk instruments?  
3. What falsifiers (Kernel bypass, parallel approval, OT unrestricted mutate, Eng from Research) Hold WP Acceptance?

## 3. Constructs and Definitions

| Construct | Definition | Measurement Approach |
|-----------|------------|----------------------|
| ID-01…08 | Infra domains | GP scoring |
| I0–I4 | Readiness bands | Per-domain ordinal |
| kernel_bypass | Must be never | Peer PR-INF-07; GP field |
| Approval bridge | High-impact → Workflow | V-INF-02; ID-04 |
| OT safety island | Read advise OK; unrestricted write never | GP-02 / ID-07 |

## 4. Method

- Desk synthesis of AIRM v1.0  
- Synthetic GP-01…02 gap profiles  
- Industry P-INF-01…10; Risk R-INF-01…14  
- Peer PR-INF-01…12 (Pass)  
- Limitations: no live T3 deploy gap analysis yet  

## 5. Findings

### 5.1 Structural Findings

Eight domains teachable; critical path ID-03→04→06 (cloud) and ID-07+04/05 (OT) before scale; affinity to Runtime remains research readiness only.

### 5.2 Enterprise Patterns

See [INDUSTRY_ANALYSIS.md](INDUSTRY_ANALYSIS.md) — GPU-as-readiness, parallel approval, open OT mutate.

### 5.3 Negative Evidence

Kernel grant shortcut, parallel approval as compliant, or OT open-mutate as I3+ fail PR-INF and Hold WP Acceptance.

## 6. Proposed Framework / Model

Canonical model: [AI_INFRASTRUCTURE_REFERENCE_MODEL.md](AI_INFRASTRUCTURE_REFERENCE_MODEL.md) (NRI-RP-006-AIRM).

## 7. Cross-Layer Impact Analysis

| Layer | Impact Class | Notes |
|-------|--------------|-------|
| Architecture | Observational | Runtime/AI topology candidates |
| Kernel | Dependencies only | Never bypass |
| Runtime / AI Runtime | Core subject | Research readiness, not code rewrite |
| Smart Terminal | Observational | Hosting / degraded modes |
| Enterprise Brain | Capacity planning | Advisory only |
| Marketplace | Observational | Signed artifact chains later |
| Constitution / Blueprint | Candidates | No edits now |

## 8. Risks and Constraints

| Risk | Severity | Mitigation |
|------|----------|------------|
| Kernel bypass | Critical | kernel_bypass: never |
| Parallel approval | Critical | ID-04; ADR-0008 |
| OT unrestricted mutate | Critical | ID-07; GP-02 |

Full register: [RISK_ANALYSIS.md](RISK_ANALYSIS.md).

## 9. Falsifiers

1. GPU roadmap sold as AIRM-complete without ID-04/05/06.  
2. Infra diagram opens Kernel grant shortcut.  
3. Parallel approval system outside Workflow.  
4. OT agents with unrestricted mutating reach claimed I3+.  
5. Eng Runtime schema tickets from Research urgency alone.

## 10. Validation Status

Peer Pass — [PEER_REVIEW_PACKAGE.md](PEER_REVIEW_PACKAGE.md).  
Evidence pack: [EVIDENCE_PACK.md](EVIDENCE_PACK.md).  
Gap profiles: [gap-profiles/](gap-profiles/).

## 11. Pilot Recommendations

Cloud-native + hybrid OT deep-dives scored against AIRM; condition RP-007 Agentize on ID-04 ≥ I2; live T2/T3 planned.

## 12. Promotion Recommendation

After **WP Acceptance**: deepen topology candidates; Architecture Review only via Dual-Track — not from this WP alone. Remain Asset OK.

## 13. Open Questions

- Supply-chain verification cadence (ID-08)  
- FinOps coupling to readiness bands  
- Interaction with RP-008 OT island depth  

## References

- [AIRM](AI_INFRASTRUCTURE_REFERENCE_MODEL.md)  
- [Evidence Pack](EVIDENCE_PACK.md)  
- [gap-profiles/](gap-profiles/)  
- [Industry](INDUSTRY_ANALYSIS.md) · [Risk](RISK_ANALYSIS.md)  
- [WAVE3_PEER_ASSIGNMENT](../../WAVE3_PEER_ASSIGNMENT.md)  
- [ADR-0027](../../../decisions/ADR-0027-ai-runtime-boundary.md)  

## Appendix A — Evidence Log

| Claim ID | Claim | Evidence Tier | Source |
|----------|-------|---------------|--------|
| C-INF-* | See Evidence Pack | T1 (+ planned T2/T3) | [EVIDENCE_PACK.md](EVIDENCE_PACK.md) |
