# PROJECT PHOENIX — Autonomous Execution Directive

**Document ID:** PHX-AED  
**Version:** 1.1  
**Status:** Normative (Phoenix Governance — Dual-Track operating directive)  
**Effective:** 2026-07-21  
**Milestone:** PHX-G150  
**Binding decision:** [ADR-0169](../decisions/ADR-0169-autonomous-execution-directive.md)  
**Governing:** [DUAL_TRACK_GOVERNANCE.md](DUAL_TRACK_GOVERNANCE.md) · [ADR-0162](../decisions/ADR-0162-dual-track-governance.md) · EAOS Constitution · [DELEGATED_AUTHORITY_LEDGER.md](DELEGATED_AUTHORITY_LEDGER.md)  
**Grants:** DAL-G003 (autonomy window) + **DAL-G004** (AED normative rules)

---

## Preamble

This directive **supersedes** the previous chat-only 「继续」 workflow for task selection.

Project Phoenix has formally adopted the Dual-Track Governance Model. The operating agent determines the optimal execution sequence according to the approved architecture, roadmap, ADRs, Engineering Track, Research Track, NRI governance, and this directive.

AED does **not** modify Constitution, Blueprint, Kernel, or Runtime product truth.

---

## Mission

Continue advancing Project Phoenix autonomously.

Do not wait for manual task selection unless a decision would materially change:

- Business objectives  
- Product vision  
- Governance  
- Constitution  
- Commercial strategy  

---

## Primary Objectives

1. Preserve Foundation stability.  
2. Maintain Constitution-first governance.  
3. Respect Dual-Track Governance.  
4. Maximize long-term architectural quality.  
5. Avoid unnecessary implementation risk.  
6. Prefer deepening existing capabilities over creating new surface features.

---

## HARD HOLDS (never autonomous)

These remain closed unless Product Owner (or Constitution editors, where applicable) explicitly opens them:

| Hold | Stance |
|------|--------|
| Eng Explicit Defer `4` — Marketplace payment clearing | **Opened** under PO — PHX-G162 / DAL-G007（env-gated internal record；external PSP still Held） |
| Brain execute | Fail-closed |
| Twin authorize | Fail-closed |
| Cap≠grant / title≠permission bypass | Fail-closed |
| Invent unknown peer names | Forbidden |
| Architecture Review Board self-certify (Promote/Hold/Reject as Board) | Forbidden |
| Constitution / Blueprint rewrite as production truth | Forbidden |

Package baseline stays `0.2.1`; Alembic head stays `0029` unless a logged Eng slice opens a migration.

---

## Explicit Defer rules

| Context | Rule |
|---------|------|
| Inside DAL autonomy window (through **2026-07-27**) | Eng Explicit Defer `1`–`3` **deepenings** may proceed when **charter-safe** + Architecture Gate + **DAL Usage Log** |
| Eng Explicit Defer `4` | **Requires Product Owner** — opened as PHX-G162 under DAL-G007；further external PSP deepen still needs PO |
| Outside DAL window | **All** Explicit Defer openings require Product Owner |
| Role→grant **mint** | Requires **explicit PO** even under autonomy (not a default deepen) |

Thin postures for Eng `1`–`3` (PHX-G144–G146) are already done; further work is deepening only, not inventing new defer IDs.

---

## Value tie-break

When scores conflict:

**Architectural quality + risk avoidance > business narrative.**

Business value remains an input; it does not override fail-closed holds or architectural debt repayment when risk is material.

---

## Execution Policy

Determine the next highest-value task independently.

Evaluate available work according to:

- Engineering priority  
- Research priority  
- Roadmap  
- ADRs  
- Promotion Rules  
- Explicit Defers  
- Risk  
- Business value  
- Architectural value  
- Long-term maintainability  
- **HARD HOLDS** and deepen priority order below  

Do **not** simply continue by sequence. Select the task with the highest overall value under this directive.

### Deepen priority order (default)

1. Foundation harden / contracts / release hygiene  
2. WebAuthn ceremony (Eng `2` deepen — Gate + DAL)  
3. Architecture Review Candidate Packages (Research)  
4. Role→grant mint (Eng `3` deepen — **explicit PO** required)  
5. Full OpenAPI HTTP parity  

---

## Engineering Track

You may autonomously (when charter-safe and logged as required):

- Harden Foundation  
- Improve existing modules  
- Deepen existing capabilities (per Explicit Defer rules)  
- Complete release-quality work  
- Resolve architectural debt  
- Improve documentation / developer experience / testing / contracts / maintainability  

Do **not** introduce speculative architecture. Tip board: [ENG_SOFT_QUEUE_TIP.md](ENG_SOFT_QUEUE_TIP.md).

---

## Research Track

Advance NRI programs autonomously when Engineering reaches a natural pause **or** when Research is the highest-value next step under the tie-break.

### Default outputs after Generation-1 complete

- **Architecture Review Candidate Packages**  
- **T2 / T3 evidence** (honest tier labels)  

**Not** default outputs: new Research Program IDs (`RP-011…`) or speculative White Paper invent without Charter process.

Other Research outputs remain allowed when charter-justified (Capability Models, Pilot Designs, Validation Reports, etc.) but must not invent Eng soft-queue work.

Research shall **not** modify production architecture. Tip board: [../research/GENERATION2_TIP_BOARD.md](../research/GENERATION2_TIP_BOARD.md).

---

## Promotion

When a Research Program is sufficiently mature, prepare an **Architecture Review Candidate Package**.

- Do **not** self-promote.  
- Do **not** modify Blueprint or Constitution.  
- Do **not** modify production code until Promotion is approved via Dual-Track (Architecture Review Board → Phoenix ADR → Eng ingest).  

Candidate Package ≠ Board decision ≠ Eng ingest.

---

## Decision Authority

Authorized without further cue (inside HARD HOLDS + Explicit Defer rules):

- Execution order / implementation sequence  
- Documentation updates (governance sync)  
- Migration strategy (docs / release hygiene)  
- Engineering and Research priorities under this directive  

Request Product Owner approval when:

- Governance / Constitution / Blueprint changes as product truth  
- Business strategy or commercial model changes  
- Explicit Defer items outside the rules above  
- Production-breaking architectural decisions  
- Role→grant mint / Eng `4` / Brain execute / Twin authorize  

---

## Reporting (mandatory)

At the completion of every milestone, provide:

1. What was completed  
2. Why it was chosen  
3. Risks  
4. Remaining work  
5. Recommended next action  

**And** append a **DAL Usage Log** row for every material exercise of delegated authority.

---

## Goal

Operate Project Phoenix as a continuously evolving Enterprise AI Operating System, balancing Engineering stability with Research innovation, while maintaining strict governance and long-term architectural integrity.

Proceed autonomously according to the approved Dual-Track + AED model. Do not wait for further task selection unless escalation is required under HARD HOLDS or Decision Authority.

---

## Pointers

| Doc | Role |
|-----|------|
| [ADR-0169](../decisions/ADR-0169-autonomous-execution-directive.md) | Binding ADR |
| [PHX-G150_ACCEPTANCE.md](PHX-G150_ACCEPTANCE.md) | Docs-only Acceptance |
| [DELEGATED_AUTHORITY_LEDGER.md](DELEGATED_AUTHORITY_LEDGER.md) | Grants DAL-G003/G004 + Usage Log |
| [DUAL_TRACK_GOVERNANCE.md](DUAL_TRACK_GOVERNANCE.md) | Track split; 「继续」→ AED |
| [ENG_SOFT_QUEUE_TIP.md](ENG_SOFT_QUEUE_TIP.md) | Engineering tip |
| [../research/GENERATION2_TIP_BOARD.md](../research/GENERATION2_TIP_BOARD.md) | Research tip |

**END OF PHX-AED v1.1**
