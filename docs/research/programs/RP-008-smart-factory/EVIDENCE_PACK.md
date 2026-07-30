# EVIDENCE-PACK-RP-008 — Smart Factory

**Research ID:** NRI-RP-008-EVID  
**Program:** RP-008  
**Version:** 1.2  
**Status:** Defined (Research) — Peer Pass; WP Accepted；AR Candidate Awaiting Board  
**Objective:** Define claims, plant-walkthrough overlay protocol, and WP gate for SFSM without MES Kernel fork or machine-control openings  
**Author:** NRI · **Reviewer:** 臻宇（Pass — WP Draft Allowed） · **Approval:** WP content Accepted；AR Candidate Awaiting Board  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-21  
**Deliverables:** [DELIVERABLES-RP-008.md](DELIVERABLES-RP-008.md)  
**Model:** [SMART_FACTORY_SPECIALIZATION_MODEL.md](SMART_FACTORY_SPECIALIZATION_MODEL.md)  
**White Paper:** [WHITE_PAPER-RP-008.md](WHITE_PAPER-RP-008.md)  
**Architecture Review Candidate:** [ARCHITECTURE_REVIEW_CANDIDATE-RP-008.md](ARCHITECTURE_REVIEW_CANDIDATE-RP-008.md)（NRI-ARC-RP-008）

---

## 1. Claim Register

| Claim ID | Claim | Tier Now | WP Target |
|----------|-------|----------|-----------|
| C-SF-01 | Factory specialization possible without forking EAOS core | T1 (PW-01/02) | T1 + planned T2 |
| C-SF-02 | Safety-before-smart is teachable (SF-03) | T1 (PW-01) | planned T2 |
| C-SF-03 | MES must not become Core Kernel | T1 | T1 |
| C-SF-04 | Brain never direct machine control | T1 (PW-01) | T1 |
| C-SF-05 | Robot paths need PR bands + EEM HOLD | T1 (PW-01) | T1 |
| C-SF-06 | Line-side Terminal differs from HQ UX | T1 (PW-02) | planned T2 |

## 2. Synthetic Plant Walkthrough Protocol

| ID | Path | Focus | Status |
|----|------|-------|--------|
| PW-01 | [walkthroughs/PW-01-discrete-cell.md](walkthroughs/PW-01-discrete-cell.md) | Discrete cell; SF-01/03/06 | **Synthetic Complete** |
| PW-02 | [walkthroughs/PW-02-line-terminal-ot.md](walkthroughs/PW-02-line-terminal-ot.md) | Line-side Terminal + OT island | **Synthetic Complete** |

Index: [walkthroughs/README.md](walkthroughs/README.md).  
Minimum before peer: **≥2 synthetic plant overlays** | **Yes** (`mes_kernelization: never`; `machine_control_from_brain: never`).

## 3. WP Freeze Gate

| Item | Ready? |
|------|--------|
| SFSM model draft | **Yes** |
| Deliverables tracking | **Yes** |
| ≥2 synthetic plant overlays | **Yes** (PW-01…02 T1) |
| Industry / Risk Draft | **Yes** — [IND](INDUSTRY_ANALYSIS.md) · [RISK](RISK_ANALYSIS.md) |
| Peer review (RP-008) | **Pass — 臻宇** (WP Draft Allowed; 2026-07-21) |
| White Paper draft | **Yes** — [WHITE_PAPER-RP-008.md](WHITE_PAPER-RP-008.md)（**Accepted**；DAL-G003） |
| Architecture Review Candidate | **Opened** — [ARCHITECTURE_REVIEW_CANDIDATE-RP-008.md](ARCHITECTURE_REVIEW_CANDIDATE-RP-008.md)（NRI-ARC-RP-008；Awaiting Board） |
| EEM / AIRM / ADR-0030 alignment | **Yes** (read-only) |

## 4. Hard Boundaries

No Const/BP/Kernel/Runtime/DB edits. No Brain execute / Twin authorize / Role→grant / payment clearing. No Eng MES-in-Kernel or machine-control tickets from this pack alone. Invariants: `mes_kernelization: never`; `machine_control_from_brain: never`. Twin authorize / Brain execute fail-closed.

**Decision:** Peer Pass + WP content Accepted recorded. Architecture Review Candidate Package opened（NRI-ARC-RP-008）— **Awaiting Board**；do **not** self-certify Board outcome；no Eng ingest.

## Related Documents

- [SFSM](SMART_FACTORY_SPECIALIZATION_MODEL.md)  
- [Architecture Review Candidate](ARCHITECTURE_REVIEW_CANDIDATE-RP-008.md)（NRI-ARC-RP-008）  
- [EEM Evidence](../RP-007-enterprise-evolution-engine/EVIDENCE_PACK.md)  
- [AIRM](../RP-006-ai-infrastructure-platform/AI_INFRASTRUCTURE_REFERENCE_MODEL.md)  
- [PEER](PEER_REVIEW_PACKAGE.md)  
- [WHITE_PAPER-RP-008.md](WHITE_PAPER-RP-008.md)  
