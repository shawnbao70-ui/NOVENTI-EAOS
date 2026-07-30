# RP-004 — Organization Neutrality

**Institute:** NOVENTI Research Institute  
**Research ID:** NRI-RP-004  
**Version:** 1.0  
**Status:** Research  
**Objective:** Ensure EAOS/EERP models do not hard-code a single organizational ideology  
**Scope:** In: Organization Neutrality Model & constraint checklist / Out: Runtime, Kernel, Source Code, Database, Constitution, Blueprint, Implementation modification  
**Author:** NRI  
**Reviewer:** 臻宇（Pass — WP Draft Allowed；WP content Accepted）  
**Approval:** Pending — WP content Accepted；Architecture Review Candidate awaiting Board  
**Dependencies:** Constrains RP-001/003/005/007/010  
**Related Capability:** Organization Models  
**Related Blueprint:** Org-facing BP language *(candidates)*  
**Related Constitution:** BOOK02 *(candidate)*  
**Related ADR:** ADR-0019 / ADR-0022 *(read-only constraints)* · ADR-0162 · ADR-0169 *(Dual-Track / AED)*  
**Promotion Status:** Research Library — AR Candidate opened（Awaiting Board）  
**Classification:** Research Only — Not Normative for Implementation  
**Last Updated:** 2026-07-21  
**Primary Deliverable:** [Organization Neutrality Model](ORGANIZATION_NEUTRALITY_MODEL.md)  
**Evidence Pack:** [EVIDENCE_PACK.md](EVIDENCE_PACK.md)  
**Deliverables:** [DELIVERABLES-RP-004.md](DELIVERABLES-RP-004.md)  
**Neutrality Audits:** [audits/](audits/) (NA-01…02 Synthetic Complete)  
**Industry / Risk:** [INDUSTRY_ANALYSIS.md](INDUSTRY_ANALYSIS.md) · [RISK_ANALYSIS.md](RISK_ANALYSIS.md)  
**Peer Review:** [PEER_REVIEW_PACKAGE.md](PEER_REVIEW_PACKAGE.md) — **Pass — 臻宇**（WP Draft Allowed）  
**White Paper:** [WHITE_PAPER-RP-004.md](WHITE_PAPER-RP-004.md)（**Accepted**）  
**Architecture Review Candidate:** [ARCHITECTURE_REVIEW_CANDIDATE-RP-004.md](ARCHITECTURE_REVIEW_CANDIDATE-RP-004.md)（**NRI-ARC-RP-004** — Candidate Package Awaiting Board；not Accepted）  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](../../RESEARCH_GOVERNANCE_CHARTER.md)

---

## 1. Research Objective

Define Organization Neutrality principles and a falsifiable checklist so discovery, capability, workforce, and evolution advice remain usable across plural org forms.

## 2. Business Background

Platforms assuming one org shape fail globally; EAOS already separates structure from permission—research extends neutrality across EERP-facing language and advice.

## 3. Industry Problems

Embedded corporate org assumptions; maturity models punish non-conforming structures; multi-entity enterprises poorly served; reorgs break brittle configs.

## 4. Future Trends

| Trend | Confidence | Horizon |
|-------|------------|---------|
| Plural org forms with shared capability cores | High | 2–5y |
| Decision-rights-driven config | High | 2–4y |
| Cross-cultural enterprise OS designs | Medium | 3–6y |

## 5. Enterprise Value

Global deployability; lower reorg breakage; fairer evolution advice; safer Cap≠Org discipline.

## 6. Capability Model

Neutrality as **constraint capability**: decision-rights and capability ownership parameterized by org form — see [ONM](ORGANIZATION_NEUTRALITY_MODEL.md).

## 7. Architecture Impact

Constraint thesis on enterprise-facing capabilities and package manifests.

## 8. Kernel Impact

Reinforces Organization/Permission separation; richer decision-rights descriptors without hierarchy dogma — no schema edits in this stage.

## 9. Runtime Impact

None direct.

## 10. Smart Terminal Impact

UX must support dual control/councils, not manager-only metaphors.

## 11. Enterprise Brain Impact

Advice templates parameterized by org form — advisory only.

## 12. Marketplace Impact

Packages declare org assumptions if any; prefer org-neutral manifests.

## 13. Developer Platform Impact

Package author guidelines for org-neutral manifests and approval metaphors — post-promotion.

## 14. Potential Blueprint Impact

Organization-facing blueprint language audits (candidates).

## 15. Potential Constitutional Impact

BOOK02 organizational pluralism clarifications — proposal only.

## 16. Validation Requirements

V-ON-01…05; neutrality checklist on RP-001/003/005/007; matrix/multi-entity/shopfloor cases.

## 17. Enterprise Pilot Strategy

Contrast two org forms with same instruments; measure forced-assumption defects.

## 18. Success Criteria

Checklist; defects remediated; Architecture Review accepts as constraint gate later.

## 19. Promotion Criteria

May promote as constraint White Paper without prototype if multi-case evidence sufficient; Remain Asset OK.

## 20. Migration Strategy

Audit existing research/product language for org chauvinism → remediate before Blueprint promotion of dependent programs.

## 21. Long-term Evolution

Standing neutrality gate for all new RPs; continuous language audits.

---

## Charter Deliverables

See [DELIVERABLES-RP-004.md](DELIVERABLES-RP-004.md).

**Wave 2:** Peer **臻宇** Pass → WP content Accepted；AR Candidate **NRI-ARC-RP-004** opened — Awaiting Board；Structure ≠ Permission；`org_shape_grant: never`；Cap≠Org；no Eng ingest.
