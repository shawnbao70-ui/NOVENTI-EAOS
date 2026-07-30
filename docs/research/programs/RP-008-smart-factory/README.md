# RP-008 — Smart Factory

**Institute:** NOVENTI Research Institute  
**Research ID:** NRI-RP-008  
**Version:** 1.0  
**Status:** Research  
**Objective:** Specialize EERP models for smart factory enterprises without forking EAOS core  
**Scope:** In: SFSM domains, physical risk bands, plant overlay protocol / Out: Runtime, Kernel, Source Code, Database, Constitution, Blueprint, Implementation modification  
**Author:** NRI  
**Reviewer:** 臻宇（Pass — WP Draft Allowed；WP content Accepted under DAL-G003）  
**Approval:** Pending — WP content Accepted；Architecture Review Candidate awaiting Board  
**Dependencies:** RP-001/003/005/006/007/009  
**Related Capability:** Industry / Smart Factory  
**Related Blueprint:** Package/Terminal/Event *(candidates)*  
**Related Constitution:** Industry/safety books *(candidates)*  
**Related ADR:** ADR-0030 / ADR-0027 / ADR-0008 *(read-only)* · ADR-0162 · ADR-0169 *(Dual-Track / AED)*  
**Promotion Status:** Research Library — AR Candidate opened（Awaiting Board）  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-21  
**Primary Deliverable:** [Smart Factory Specialization Model](SMART_FACTORY_SPECIALIZATION_MODEL.md)  
**Evidence Pack:** [EVIDENCE_PACK.md](EVIDENCE_PACK.md)  
**Deliverables:** [DELIVERABLES-RP-008.md](DELIVERABLES-RP-008.md)  
**Plant Overlays:** [walkthroughs/](walkthroughs/) (PW-01…02 Synthetic Complete)  
**Industry / Risk:** [INDUSTRY_ANALYSIS.md](INDUSTRY_ANALYSIS.md) · [RISK_ANALYSIS.md](RISK_ANALYSIS.md)  
**Peer Review:** [PEER_REVIEW_PACKAGE.md](PEER_REVIEW_PACKAGE.md) — **Pass — 臻宇**（WP Draft Allowed）  
**White Paper:** [WHITE_PAPER-RP-008.md](WHITE_PAPER-RP-008.md)（**Accepted**；content Accepted under DAL-G003）  
**Architecture Review Candidate:** [ARCHITECTURE_REVIEW_CANDIDATE-RP-008.md](ARCHITECTURE_REVIEW_CANDIDATE-RP-008.md)（**NRI-ARC-RP-008** — Candidate Package Awaiting Board；not Accepted）  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](../../RESEARCH_GOVERNANCE_CHARTER.md)

---

## 1. Research Objective

Apply discovery, AI/robot/device roles, terminals, and evolution triggers to plants; produce Smart Factory thesis as overlay — not MES fork.

## 2. Business Background

Manufacturing forces Human/AI/Robot/Device composition and robot triggers; must not collapse EAOS into MES.

## 3. Industry Problems

MES/ERP/AI poorly governed together; safety bypassed by “smart” pilots; shopfloor UX ignored; historians ≠ governed knowledge.

## 4. Future Trends

| Trend | Confidence | Horizon |
|-------|------------|---------|
| AI+robot certified cells | High | 2–4y |
| Line-side governed terminals | High | 1–3y |
| Factory capability graphs | Medium | 2–5y |
| Simulation-first line changes | Medium | 3–5y |

## 5. Enterprise Value

Safer automation; higher OEE with governance; clearer AI/robot sequencing; industry packages.

## 6. Capability Model

Domains SF-01…08 + physical risk PR0–PR4. See [SFSM](SMART_FACTORY_SPECIALIZATION_MODEL.md).

## 7. Architecture Impact

Industry overlay packages/integration patterns — not Core Kernel industry logic.

## 8. Kernel Impact

Uses sites/units and workflow approvals; no MES kernelization.

## 9. Runtime Impact

Edge constraints; degraded mode; OT event integration carefully bounded.

## 10. Smart Terminal Impact

High: line-side interaction, glanceable approvals, offline rules.

## 11. Enterprise Brain Impact

Advisory quality/OEE/risk insights; never direct machine control.

## 12. Marketplace Impact

Industry packages for quality/maintenance/scheduling with declared OT scopes.

## 13. Developer Platform Impact

OT connector/package authoring guidelines; safety declaration requirements — post-promotion.

## 14. Potential Blueprint Impact

Package/industry overlays; Terminal industrial UX; Event/Integration patterns (candidates).

## 15. Potential Constitutional Impact

Safety/industry obligations later — proposal only.

## 16. Validation Requirements

V-SF-01…05; plant walkthroughs; map to ANRF manufacturing + EEM robot triggers.

## 17. Enterprise Pilot Strategy

One discrete manufacturing pilot with safety stakeholder.

## 18. Success Criteria

Specialization without forking EAOS core models.

## 19. Promotion Criteria

White Paper after plant evidence + peer; Architecture Review after overlay ownership clarified; Remain Asset OK.

## 20. Migration Strategy

Pilot cell → governed terminal → scaled robotization under EEM HOLD rules; never skip safety case.

## 21. Long-term Evolution

Industry model family expansion; feeds RP-010; continuous plant learning loops.

---

## Charter Deliverables

See [DELIVERABLES-RP-008.md](DELIVERABLES-RP-008.md).

**Wave 3:** Peer **臻宇** Pass → WP content Accepted；AR Candidate **NRI-ARC-RP-008** opened — Awaiting Board；`mes_kernelization: never`；`machine_control_from_brain: never`；no Eng ingest.
