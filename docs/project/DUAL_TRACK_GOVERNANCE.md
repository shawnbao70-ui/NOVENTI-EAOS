# Dual-Track Governance — Operating Playbook

**Program:** Project Phoenix  
**Document ID:** PHX-DUAL-TRACK  
**Version:** 1.0  
**Status:** Normative (Phoenix Governance)  
**Effective:** 2026-07-21  
**Governing ADR:** [ADR-0162](../decisions/ADR-0162-dual-track-governance.md)  
**Milestone:** PHX-G143

---

## 1. Implementation Strategy

| Track | Purpose | Cadence owner | Success measure |
|-------|---------|---------------|-----------------|
| **Engineering** | Keep Foundation production-truth stable and releasable | Release Train / Eng | Contracts green; Explicit Defer respected; fail-closed holds |
| **Research (NRI)** | Continuously produce validated enterprise-evolution knowledge | NRI / EERP | Library growth; stage discipline; zero bypass of promotion |

**Strategy principles**

1. One Constitution; two operating tracks under Phoenix Governance.  
2. Research proposes; Engineering implements only after promotion.  
3. Promotion is optional — Library permanence is success, not failure.  
4. Soft-queue exhaustion on Eng does **not** authorize speculative product openings.  
5. Domain rule: Eng truth order remains **Constitution First**; Research **promotion** order remains Blueprint → Constitution Review → Implementation (per NRI Charter).
6. Every promoted Business Package enters the sole ADR-0321 Decision Summary
   workflow; no track may create a Package-specific Gate process.

**Out of strategy (this playbook)**

- Opening Twin authorize / Brain execute / external PSP payment rails  
- Constitution BOOK or Blueprint content rewrites  
- Kernel / Runtime / Alembic changes

---

## 2. Migration Plan (implicit → explicit Dual-Track)

| Phase | Action | Exit |
|-------|--------|------|
| **M0 — Formalize** (PHX-G143) | ADR-0162 + this playbook + Gate/Acceptance + status/roadmap sync | Docs Accepted; contracts assert artifacts |
| **M1 — Language** | Tag Eng vs Research work in PROJECT_STATUS / ROADMAP / NRI Index | Readers can tell track without ambiguity |
| **M2 — Sync cadence** | Monthly Architecture Sync (Eng + NRI) | Minutes or status delta recorded |
| **M3 — Steady state** | Eng only numbered/approved slices; NRI advances Wave 1 programs | Soft invent-work banned |
| **M4 — First promotion (future)** | First RP reaches Architecture Review with full NRI-VAL package | Promote / Hold / Reject recorded — **not** part of G143 |

**Migration non-goals**

- No code migration  
- No research program content rewrite in G143  
- No forced promotion of RP-001…RP-010

---

## 3. Documentation Map

| Artifact | Role |
|----------|------|
| [ADR-0162](../decisions/ADR-0162-dual-track-governance.md) | Binding decision |
| [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md) | Sole Business Package Gate workflow |
| [AUTONOMOUS_EXECUTION_DIRECTIVE.md](AUTONOMOUS_EXECUTION_DIRECTIVE.md) | AED v1.1 — Dual-Track operating directive（PHX-G150 / ADR-0169） |
| This playbook | Strategy, migration, sync, execution order |
| [DELEGATED_AUTHORITY_LEDGER.md](DELEGATED_AUTHORITY_LEDGER.md) | CA/PO delegated grants + usage inventory |
| [MASTER_PLAN.md](MASTER_PLAN.md) | Dual-Track as standing governance principle |
| [ROADMAP.md](ROADMAP.md) | Dual-path delivery view |
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Current tip + track-aware 下一步 |
| [ENG_SOFT_QUEUE_TIP.md](ENG_SOFT_QUEUE_TIP.md) | Engineering soft-queue tip board |
| [../research/README.md](../research/README.md) | Research Track entry + Dual-Track pointer |
| [../research/RESEARCH_ROADMAP.md](../research/RESEARCH_ROADMAP.md) | Research waves (unchanged intent; sync row added) |
| [../research/RESEARCH_PROMOTION_RULES.md](../research/RESEARCH_PROMOTION_RULES.md) | Legal bridge (unchanged normative text) |

**Must not edit under Dual-Track formalization alone**

- `docs/constitution/**`  
- `docs/blueprint/**`  
- Kernel / Runtime / production source for “research completeness”

---

## 4. Roadmap Changes (normative intent)

```text
                    ┌─────────────────────────────┐
                    │     EAOS Constitution        │
                    └─────────────┬───────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │    Phoenix Governance       │
                    └──────┬──────────────┬───────┘
                           │              │
              ┌────────────▼──┐    ┌──────▼────────────┐
              │ Engineering   │    │ Research (NRI)    │
              │ Track         │    │ Track             │
              │ 0.2.x / G*    │    │ RP-001… / Library │
              │ ADR→Impl      │    │ validate→promote? │
              └────────┬──────┘    └─────────┬─────────┘
                       │                     │
                       │    Architecture     │
                       │    Review Board     │
                       └──────────┬──────────┘
                                  │
                    Blueprint → Constitution Review
                                  │
                           Implementation
```

**Engineering near-term backlog (unchanged Explicit Defer set)**

1. ~~Optional: Foundation `0.2.1` release train~~ → **done (thin)**（PHX-G144 / ADR-0163）；further deepenings per [AED v1.1](AUTONOMOUS_EXECUTION_DIRECTIVE.md)  
2. ~~Optional: WebAuthn / MFA product page~~ → **done (thin posture)**（PHX-G145 / ADR-0164）；~~ceremony stub deepen~~ → **done (503 stubs)**（PHX-G151 / ADR-0170 / DAL-U023）；~~stub observability~~ → **done**（PHX-G154 / ADR-0173 / DAL-U026）；live mint still deferred per AED  
3. ~~Optional: Role→grant auto-write~~ → **done (thin posture)**（PHX-G146 / ADR-0165）；~~auto-write stub deepen~~ → **done (503 stub)**（PHX-G156 / ADR-0175 / DAL-U028）；~~**live mint**~~ → **done (env-gated)**（PHX-G161 / ADR-0179 / DAL-G006 / DAL-U032；default OFF；Cap≠grant）  
4. Opened (PO)：Marketplace payment clearing **internal record**（Eng `4` / PHX-G162 / DAL-G007；external PSP / arbitration still deferred）  
5. Non-goal: multi-region production SaaS / failover  

**Related product surface (not Eng Explicit Defer `1`–`4`):** ~~T-0189 OIDC login page~~ → **done (thin product surface)**（PHX-G147 / ADR-0166；Auth Code CTAs only；no new protocol）；~~T-0188 全量 OpenAPI HTTP~~ → **partial deepen**（PHX-G148 inventory + **PHX-G164** mount parity complete / semantic still partial；ADR-0182；`full_openapi_http_complete=false`）  

**Engineering tip board：** [ENG_SOFT_QUEUE_TIP.md](ENG_SOFT_QUEUE_TIP.md)（PHX-G149 / ADR-0168；**Natural Pause PHX-G158** / ADR-0177；**AR Board Hold PHX-G159** / ADR-0178 ≠ Eng invent；**Role→grant mint PHX-G161** / ADR-0179；**Payment clearing PHX-G162** / ADR-0181；**OpenAPI semantic deepen PHX-G164** / ADR-0182；Held Brain/Twin/external PSP/WebAuthn attestation；Resume = live T2–T3 artifacts / WebAuthn mint-PO / further semantic；no invent）

**Research near-term backlog**

- Generation-1 complete；tip = [GENERATION2_TIP_BOARD.md](../research/GENERATION2_TIP_BOARD.md)  
- Default deepen outputs under AED：Architecture Review Candidate Packages + T2/T3 evidence（first opened：RP-001 NRI-ARC-RP-001）  
- Do not open Eng tickets from RP IDs until Promote + Phoenix ADR  

---

## 5. Execution Order (Chief Architect)

| Step | Work | Track |
|------|------|-------|
| 1 | Accept ADR-0162 + Gate/Acceptance (G143) | Eng governance |
| 2 | Publish this playbook; sync MASTER_PLAN / ROADMAP / PROJECT_STATUS / CHANGELOG | Eng governance |
| 3 | Cross-link NRI README + Research Roadmap Review Cadence | Research alignment |
| 4 | Contract test locking Dual-Track artifacts | Eng verification |
| 5 | Steady state: Eng waits numbered deferrals **or** advances release quality per AED；NRI continues optional deepenings | Both |
| 6 | (Future) First Architecture Review for a mature RP — Board only；Candidate Packages may be prepared under Research tip | Bridge |
| 7 | Accept ADR-0169 + AED v1.1（PHX-G150） | Eng governance |

**「继续」解释（post-G150 / AED v1.1）**

- 「继续」means: select the **highest-value** next task under [AUTONOMOUS_EXECUTION_DIRECTIVE.md](AUTONOMOUS_EXECUTION_DIRECTIVE.md) v1.1 **HARD HOLDS** — **not** invent product openings by sequence.  
- Inside DAL window through 2026-07-27: Eng `1`–`3` deepenings may proceed when charter-safe + Gate + DAL Usage Log；Eng `4` opened as PHX-G162 under DAL-G007（external PSP deepen still needs PO）.  
- Outside window: all Explicit Defer need PO.  
- Research default after G1: Architecture Review Candidate Packages + T2/T3 evidence — not new RP IDs.  
- Vision/governance/business-objective changes still require Product Owner.  
- Every milestone: report + DAL Usage Log.
---

## 6. Synchronization Rules

1. **Monthly Architecture Sync** — Eng tip + NRI Index stage deltas; blockers for promotion.  
2. **No auto-ingest** — Research IDs never enter Eng soft queue without Promote + new Phoenix ADR.  
3. **Status language** — Eng: Fully Accepted / Explicit Defer; NRI: Library / Hold / Promote.  
4. **Conflict** — Constitution overrides; production fail-closed wins over research narrative.  
5. **Delegation** — Implementation sequencing under approved Dual-Track may proceed without per-slice PO approval unless vision/governance/business objectives change. Time-bounded CA/PO approval grants and each exercise are recorded in [DELEGATED_AUTHORITY_LEDGER.md](DELEGATED_AUTHORITY_LEDGER.md).

---

## 7. Decision Authority (recap)

| Class | Authority |
|-------|-----------|
| Constitutional invariants | Constitutional editors |
| Promote / Hold / Reject | Architecture Review Board |
| Eng Explicit Defer open | Product Owner + Architecture (numbered) |
| Release train | Release Train owner |
| New RP programs | NRI under Charter |

---

**END OF PHX-DUAL-TRACK v1.0**
