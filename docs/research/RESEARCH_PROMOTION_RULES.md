# NRI Research Promotion Rules

**Institute:** NOVENTI Research Institute  
**Document ID:** NRI-PROMO  
**Version:** 1.1  
**Status:** Normative  
**Governing Directive:** [RESEARCH_GOVERNANCE_CHARTER.md](RESEARCH_GOVERNANCE_CHARTER.md)

---

## Purpose

Enforce the only legal path from research idea to EAOS product capability, and recognize permanent Research Library assets as valid end states.

## Canonical Lifecycle

```text
Idea
  ↓
Research
  ↓
White Paper
  ↓
Capability Model
  ↓
Prototype
  ↓
Enterprise Pilot
  ↓
Architecture Review
  ↓
Blueprint
  ↓
Constitution Review
  ↓
Implementation
  ↓
Product Release
  ↓
Continuous Evolution
```

**Hard rule:** No capability may directly enter Blueprint, Constitution, or Implementation without validation.

## Promotion Targets (Optional)

```text
Research Library  (default permanent home)
        ↓
Blueprint
        ↓
Architecture Decision
        ↓
Constitution
        ↓
Implementation
        ↓
EAOS Product
```

**Promotion is optional.** Research may remain permanently as Research Assets.

## Stage Definitions

| Stage | Owner | Allowed Outputs | Forbidden |
|-------|-------|-----------------|-----------|
| Idea | NRI | Problem brief | Settled-truth claims |
| Research | NRI | Draft frameworks/models/reports | Normative Constitution/Blueprint text |
| White Paper | NRI | Formal paper + impact reports plan | Committed engineering backlog |
| Capability Model | NRI | Capability map + maturity models | Runtime/Kernel schema changes |
| Prototype | NRI / Lab | Disposable sandbox prototype | Production Kernel/Runtime/DB changes |
| Enterprise Pilot | NRI + Enterprise | Observational/advisory results | Silent productization |
| Architecture Review | Architecture Review Board | Ownership classify; promote/hold/reject | Immediate Constitution/Blueprint edit by NRI |
| Blueprint | Architecture *(downstream)* | Blueprint draft under Phoenix rules | Skipping Architecture Review |
| Constitution Review | Constitutional editors *(downstream)* | BOOK proposal review | Implementation-first patches |
| Implementation | Engineering *(downstream)* | Code behind approved artifacts | Unvalidated research constructs as product APIs |
| Product Release | Release Train *(downstream)* | Versioned release | Research-stage features |
| Continuous Evolution | NRI + Product | Post-release research loops | Treating release as research end |

## Promotion Requests

Every promotion request MUST include:

1. Research ID + version  
2. Current stage and target (or `Remain as Research Asset`)  
3. Validation record ([NRI-VAL](RESEARCH_VALIDATION_RULES.md))  
4. Deliverable completeness map (16 Charter deliverables)  
5. Evidence tier map  
6. Cross-layer impact summary (incl. Developer Platform)  
7. Migration Strategy summary  
8. Constitutional compatibility notes  
9. Residual risks + ROI summary  
10. Rollback / hold conditions  

## Decision Outcomes

| Decision | Effect |
|----------|--------|
| Promote | Stage advanced; Library + Index updated |
| Hold | Stage unchanged; blockers remediable |
| Reject | May revert; rationale archived |
| Remain Asset | Explicit permanent Research Library end state |
| Split / Merge | Lineage updated in Library |

## Fast-Track Prohibition

No emergency fast track into Blueprint, Constitution, or Implementation from demo pressure or single-customer demand.

Customer urgency may accelerate pilots and review calendars only.

## Special Rules

### A. Advisory vs Execution

Action class must be stated: Observe / Advise / Recommend / Simulate / Execute.  
Execute is forbidden at NRI stages. Brain-related execution leakage → automatic Reject.

### B. AI / Robot / Device Responsibility

Transfer of legal or residual business responsibility away from humans → automatic Reject.

### C. Organization Neutrality

Hard-coding a single org-chart ideology requires RP-004 compatibility review.

### D. Marketplace Commercial

Commercial settlement paths remain on legal/commercial track; research may study, not authorize.

### E. Continuous Evolution

After Product Release, NRI opens a Continuous Evolution research loop; release does not freeze knowledge.

## Downstream Handoff Packet

When Architecture Review marks **Blueprint-eligible**, NRI hands off:

1. Frozen White Paper + Capability Model  
2. Impact reports (Architecture / Blueprint / Constitution)  
3. Pilot evidence + ROI/Risk summaries  
4. Migration Strategy  
5. Ownership classification proposal  
6. Open questions  

NRI does not itself edit Blueprint, Constitution, ADR, or Implementation.

## Index & Library Obligation

Promotions MUST update:

- [RESEARCH_LIBRARY.md](RESEARCH_LIBRARY.md)  
- [RESEARCH_INDEX.md](RESEARCH_INDEX.md) Promotion Registry  

in the same change set as stage status edits.

## Violation Handling

If Blueprint / Constitution / Implementation appears without NRI lineage:

1. Flag process defect under Phoenix Governance.  
2. Create retrospective research record or roll back per Architecture Review.  
3. Do not launder post-hoc research as if it preceded implementation.
