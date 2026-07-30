# EVIDENCE-PACK-RP-006 — AI Infrastructure Platform

**Research ID:** NRI-RP-006-EVID  
**Program:** RP-006  
**Version:** 1.2  
**Status:** Defined (Research) — Peer Pass; WP Accepted；AR Candidate Awaiting Board  
**Objective:** Define claims, synthetic gap-profile protocol, and WP gate for AIRM without Runtime/Kernel openings  
**Author:** NRI · **Reviewer:** 臻宇（Pass — WP Draft Allowed） · **Approval:** WP content Accepted；AR Candidate Awaiting Board  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-21  
**Deliverables:** [DELIVERABLES-RP-006.md](DELIVERABLES-RP-006.md)  
**Model:** [AI_INFRASTRUCTURE_REFERENCE_MODEL.md](AI_INFRASTRUCTURE_REFERENCE_MODEL.md)  
**White Paper:** [WHITE_PAPER-RP-006.md](WHITE_PAPER-RP-006.md)  
**Architecture Review Candidate:** [ARCHITECTURE_REVIEW_CANDIDATE-RP-006.md](ARCHITECTURE_REVIEW_CANDIDATE-RP-006.md)（NRI-ARC-RP-006）

---

## 1. Claim Register

| Claim ID | Claim | Tier Now | WP Target |
|----------|-------|----------|-----------|
| C-INF-01 | Eight domains ID-01…08 are jointly necessary | T1 (GP-01/02) | T1 + planned T2 |
| C-INF-02 | Governance-before-GPU is teachable | T1 (GP-01) | planned T2 |
| C-INF-03 | Infra must not bypass Kernel Permission/Workflow | T1 | T1 |
| C-INF-04 | Approval bridge is a critical-path domain | T1 (GP-01/02) | T1 |
| C-INF-05 | Hybrid OT needs safety-island scoring (ID-07) | T1 (GP-02) | planned T2 |
| C-INF-06 | Supply-chain trust (ID-08) gates Marketplace readiness | T1 (gap noted) | planned T2 |

## 2. Synthetic Gap Profile Protocol

| ID | Path | Focus | Status |
|----|------|-------|--------|
| GP-01 | [gap-profiles/GP-01-cloud-native.md](gap-profiles/GP-01-cloud-native.md) | Cloud landing; ID-02/03/04/06 gaps | **Synthetic Complete** |
| GP-02 | [gap-profiles/GP-02-hybrid-ot.md](gap-profiles/GP-02-hybrid-ot.md) | Hybrid OT; ID-07 critical; ID-04/05 | **Synthetic Complete** |

Index: [gap-profiles/README.md](gap-profiles/README.md).  
Minimum before peer: **≥2 synthetic gap profiles** | **Yes** (`kernel_bypass: never`).

## 3. WP Freeze Gate

| Item | Ready? |
|------|--------|
| AIRM model draft | **Yes** |
| Deliverables tracking | **Yes** |
| ≥2 synthetic gap profiles | **Yes** (GP-01…02 T1) |
| Industry / Risk Draft | **Yes** — [IND](INDUSTRY_ANALYSIS.md) · [RISK](RISK_ANALYSIS.md) |
| Peer review (RP-006) | **Pass — 臻宇** (WP Draft Allowed; 2026-07-21) |
| White Paper draft | **Yes** — [WHITE_PAPER-RP-006.md](WHITE_PAPER-RP-006.md)（**Accepted**） |
| Architecture Review Candidate | **Opened** — [ARCHITECTURE_REVIEW_CANDIDATE-RP-006.md](ARCHITECTURE_REVIEW_CANDIDATE-RP-006.md)（NRI-ARC-RP-006；Awaiting Board） |
| ADR-0027 / ADR-0008 alignment | **Yes** (read-only) |

## 4. Hard Boundaries

No Const/BP/Kernel/Runtime/DB edits. No Brain execute / Twin authorize / Role→grant / payment clearing. No Eng Runtime schema tickets from this pack alone.  
**`kernel_bypass: never`** · Twin authorize / Brain execute fail-closed.

**Decision:** Peer Pass + WP content Accepted recorded. Architecture Review Candidate Package opened（NRI-ARC-RP-006）— **Awaiting Board**；do **not** self-certify Board outcome；no Eng ingest.

## Related Documents

- [AIRM](AI_INFRASTRUCTURE_REFERENCE_MODEL.md)  
- [Architecture Review Candidate](ARCHITECTURE_REVIEW_CANDIDATE-RP-006.md)（NRI-ARC-RP-006）  
- [ADR-0027](../../../decisions/ADR-0027-ai-runtime-boundary.md)  
- [ADR-0008](../../../decisions/ADR-0008-ai-human-approval.md)  
- [PEER](PEER_REVIEW_PACKAGE.md)  
