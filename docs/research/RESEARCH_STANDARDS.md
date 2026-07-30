# NRI Research Standards

**Institute:** NOVENTI Research Institute  
**Document ID:** NRI-STD  
**Version:** 1.1  
**Status:** Normative for all NRI research  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](RESEARCH_GOVERNANCE_CHARTER.md)

---

## Purpose

Define quality, structure, language, citation, metadata, deliverable, and boundary standards for all NRI research artifacts.

## 1. Document Identity & Library Metadata

Every research artifact MUST include Charter library fields:

| Field | Rule |
|-------|------|
| Research ID | `NRI-*` stable ID; register in [RESEARCH_LIBRARY.md](RESEARCH_LIBRARY.md) |
| Version | Research semantic version `MAJOR.MINOR` |
| Status | Idea / Research / White Paper / Capability Model / Prototype / Pilot / Architecture Review / Archived / Research Asset (Permanent) |
| Objective | One-paragraph purpose |
| Scope | In-scope and out-of-scope |
| Author | Primary author |
| Reviewer | Non-author required from White Paper onward |
| Approval | `Pending` / named approval record |
| Dependencies | Upstream research IDs / evidence deps |
| Related Capability | Capability targets if any |
| Related Blueprint | BP-* candidates only (read-only) |
| Related Constitution | BOOK candidates only (read-only) |
| Related ADR | ADR candidates / constraints |
| Promotion Status | Library-only / target stage / promoted ref |
| Classification | Research Only — Not Normative for Implementation |
| Institute | NOVENTI Research Institute |
| Last Updated | ISO date |

## 2. Required Program Dimensions (21)

Every Research Program MUST address:

1. Research Objective  
2. Business Background  
3. Industry Problems  
4. Future Trends  
5. Enterprise Value  
6. Capability Model  
7. Architecture Impact  
8. Kernel Impact  
9. Runtime Impact  
10. Smart Terminal Impact  
11. Enterprise Brain Impact  
12. Marketplace Impact  
13. Developer Platform Impact  
14. Potential Blueprint Impact  
15. Potential Constitutional Impact  
16. Validation Requirements  
17. Enterprise Pilot Strategy  
18. Success Criteria  
19. Promotion Criteria  
20. Migration Strategy  
21. Long-term Evolution  

Missing dimensions block White Paper promotion.

## 3. Mandatory Program Deliverables (16)

Per Governance Charter, programs shall produce:

| # | Deliverable | Earliest Expected Stage |
|---|-------------|-------------------------|
| 1 | Research Report | Research |
| 2 | Industry Analysis | Research |
| 3 | Future Trend Analysis | Research |
| 4 | Capability Map | Capability Model |
| 5 | Capability Maturity Model | Capability Model |
| 6 | Enterprise Maturity Model | Capability Model |
| 7 | AI Maturity Model | Capability Model |
| 8 | Architecture Impact Report | White Paper |
| 9 | Blueprint Impact Report | White Paper |
| 10 | Constitution Impact Report | White Paper |
| 11 | Migration Strategy | White Paper |
| 12 | Validation Strategy | Research |
| 13 | Enterprise Pilot Plan | Pre-Pilot |
| 14 | ROI Analysis | White Paper / Pilot |
| 15 | Risk Analysis | Research |
| 16 | Long-term Evolution Strategy | White Paper |

May be standalone files or labeled sections. Waivers require Validation Rules record.

## 4. Language and Style

- Preserve EAOS canonical terms: Kernel, Runtime, AI Runtime, Smart Terminal, Enterprise Brain, Twin, Marketplace, Constitution, Blueprint, Package, Shared Capability.
- New research constructs MUST be labeled **research constructs** until promoted.
- Do not draft Constitution or Blueprint normative text inside research (impact reports recommend only).

## 5. Boundary Standard

| Rule | Requirement |
|------|-------------|
| R-BOUND-01 | MUST NOT modify Constitution, Blueprint, Kernel, Runtime, Source Code, Database, or Implementation |
| R-BOUND-02 | Impact sections analyze *potential* effects only |
| R-BOUND-03 | Prototypes are research-scoped, disposable, non-production |
| R-BOUND-04 | Enterprise Brain research preserves advisory-only / no-execution |
| R-BOUND-05 | AI / Robot / Device workforce research preserves human legal/business responsibility (BOOK03) |
| R-BOUND-06 | Marketplace research does not reopen fail-closed commercial APIs without legal track |
| R-BOUND-07 | Promotion is optional; permanent Research Assets are valid end states |

## 6. Evidence Standard

| Tier | Label | Allowed Use |
|------|-------|-------------|
| T0 | Hypothesis | Idea stage only |
| T1 | Desk Research | Industry/literature synthesis |
| T2 | Structured Interview / Survey | Pattern formation |
| T3 | Enterprise Case Evidence | Framework refinement |
| T4 | Controlled Pilot | Architecture Review readiness |
| T5 | Multi-enterprise Replication | Strong promotion evidence |

White Papers: **T1 + planned T2/T3**.  
Architecture Review readiness: **T3 or T4**.

## 7. Traceability Standard

- Claim → evidence  
- Recommendation → EAOS layer potentially affected  
- Promotion request → Validation checklist  
- Deliverable → program dimension coverage  
- Explicit non-trace for out-of-scope items  

## 8. Naming Conventions

| Artifact | Pattern |
|----------|---------|
| Program folder | `RP-###-<kebab-title>/` |
| Program brief | `README.md` |
| Framework / Model | `UPPER_SNAKE_*.md` |
| White paper | `WP-RP-###-<kebab>.md` |
| Impact report | `IMPACT-RP-###-{ARCH\|BP\|CONST}.md` or labeled section |
| Pilot plan | `PILOT-RP-###-<kebab>.md` |
| Capability model | `CAPABILITY_MODEL-RP-###.md` or labeled section |

## 9. Review Standard

| Review Type | Required Before |
|-------------|-----------------|
| Author self-check | Sharing draft |
| Peer research review | White Paper |
| Deliverable completeness check | Capability Model stage |
| Constitutional compatibility (read-only) | Architecture Review package |
| Architecture ownership preview | Blueprint eligibility |

## 10. Conflict Handling

If research conflicts with Constitution:

1. Record conflict explicitly.  
2. Do not weaken Constitution in-repo.  
3. Route through Promotion Rules → Constitution Review.  
4. Prefer adapting research to invariants unless evidence demands a constitutional proposal.

## 11. Archival

Superseded research remains readable with status `Archived` and successor pointer. Deletion of promoted lineages is forbidden.
