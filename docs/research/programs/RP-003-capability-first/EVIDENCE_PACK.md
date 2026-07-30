# EVIDENCE-PACK-RP-003 — Capability First

**Research ID:** NRI-RP-003-EVID  
**Program:** RP-003  
**Version:** 1.3  
**Status:** Defined (Research) — Peer Pass; WP Accepted; AR Candidate opened  
**Objective:** Define claims, synthetic graph protocol, and WP gate for CFM without Permission leakage  
**Author:** NRI · **Reviewer:** 臻宇（Pass — WP Draft Allowed） · **Approval:** WP content Accepted；AR Candidate Awaiting Board  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-21  
**Deliverables:** [DELIVERABLES-RP-003.md](DELIVERABLES-RP-003.md)  
**Model:** [CAPABILITY_FIRST_MODEL.md](CAPABILITY_FIRST_MODEL.md)  
**White Paper:** [WHITE_PAPER-RP-003.md](WHITE_PAPER-RP-003.md)  
**Architecture Review Candidate:** [ARCHITECTURE_REVIEW_CANDIDATE-RP-003.md](ARCHITECTURE_REVIEW_CANDIDATE-RP-003.md)（NRI-ARC-RP-003）

---

## 1. Claim Register

| Claim ID | Claim | Tier Now | WP Target |
|----------|-------|----------|-----------|
| C-CAP-01 | Capability graph is a superior planning lens to org-chart-first | T1 (desk contrast in CG-01/02) | T1 + planned T2 |
| C-CAP-02 | Cap≠Org is teachable and enforceable in workshops | T1 (via RP-001 + CG checklists) | planned T2 |
| C-CAP-03 | Capability ≠ Permission / grant | T1 | T1 |
| C-CAP-04 | Dependency edges change build/buy/AI priorities | T1 (critical-path vs dept roadmap) | planned T2 |
| C-CAP-05 | Automation affinity is advisory-only | T1 | T1 |
| C-CAP-06 | RP-005/007 can consume capability IDs without org lock-in | T1 (export hints) | planned T2 |

## 2. Synthetic Graph Protocol

| ID | Path | Source Dossier | Status |
|----|------|----------------|--------|
| CG-01 | [graphs/CG-01-wt01-mfg.md](graphs/CG-01-wt01-mfg.md) | WT-01 | **Synthetic Complete** |
| CG-02 | [graphs/CG-02-wt02-svc.md](graphs/CG-02-wt02-svc.md) | WT-02 | **Synthetic Complete** |

Index: [graphs/README.md](graphs/README.md).  
Minimum before peer: **≥2 synthetic capability graphs** | **Yes** (CG-01…02; Cap≠Org + critical-path gaps).

## 3. WP Freeze Gate

| Item | Ready? |
|------|--------|
| CFM model draft | **Yes** |
| Deliverables tracking | **Yes** |
| ≥2 synthetic graphs | **Yes** (T1) |
| Industry / Risk Draft | **Yes** — [IND](INDUSTRY_ANALYSIS.md) · [RISK](RISK_ANALYSIS.md) |
| Peer review (RP-003) | **Pass — 臻宇** (WP Draft Allowed; 2026-07-21) |
| White Paper draft | **Yes** — [WHITE_PAPER-RP-003.md](WHITE_PAPER-RP-003.md) （**Accepted**） |
| Architecture Review Candidate | **Opened** — [ARCHITECTURE_REVIEW_CANDIDATE-RP-003.md](ARCHITECTURE_REVIEW_CANDIDATE-RP-003.md)（NRI-ARC-RP-003；Awaiting Board） |
| Wave 1 / RP-002 peers | **Pass** — WP Drafts open (separate programs) |

## 4. Hard Boundaries

No Const/BP/Kernel/Runtime/DB edits. Capability IDs must not open Twin authorize / Brain execute / Role→grant / payment clearing.  
**Cap ≠ Org** · **Capability ≠ Permission** · **`auto_grant_minted: never`**.

**Decision:** Peer Pass + WP content Accepted recorded. Architecture Review Candidate Package opened（NRI-ARC-RP-003）— **Awaiting Board**；do **not** self-certify Board outcome；no Eng ingest.

## Related Documents

- [CFM](CAPABILITY_FIRST_MODEL.md)  
- [Architecture Review Candidate](ARCHITECTURE_REVIEW_CANDIDATE-RP-003.md)（NRI-ARC-RP-003）  
- [RP-001 Evidence Pack](../RP-001-enterprise-discovery/EVIDENCE_PACK.md)  
