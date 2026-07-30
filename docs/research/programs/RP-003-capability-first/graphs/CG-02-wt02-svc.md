# CG-02 — Capability Graph · WT-02 SynSvc-Beta

**Research ID:** NRI-RP-003-CG-02  
**Program:** RP-003  
**Version:** 1.0  
**Status:** Synthetic Complete  
**Mode:** synthetic · **Tier:** T1  
**Dossier:** [WT-02](../../RP-001-enterprise-discovery/walkthroughs/WT-02-services-synthetic.md)  
**Parent:** [EVIDENCE_PACK.md](../EVIDENCE_PACK.md)  
**As Of:** 2026-07-21 · **Facilitator:** NRI-desk (synthetic)

---

```text
capability_graph_version: syn-cg02-1.0
enterprise_ref: WT-02 SynSvc-Beta
as_of: 2026-07-21
cap_org_separated: yes
auto_grant_minted: never
permission_input: never
license_theater_rejected: yes
```

## 1. Cap ≠ Org Checklist

| Check | Result |
|-------|--------|
| “Consulting Practice” ≠ CAP-DEL Delivery Governance | **Pass** |
| Partner titles ≠ capability owners-as-persons | **Pass** |
| Copilot seat inventory not treated as a capability | **Pass** — Infra/commercial only |
| Collapse observed? | **not-triggered** |

## 2. Capability Nodes

| capability_id | name | outcome | level | affinity | knowledge_authority | owner_role_class | org_anchors (descriptive) | confidence |
|---------------|------|---------|-------|----------|---------------------|------------------|---------------------------|------------|
| CAP-PUR | Client Pursuit | Qualified pursuits win rate within band | L3 | A1 | Pursuit collateral authority | Pursuit Lead class | Practices | medium |
| CAP-DEL | Delivery Governance | Engagements close within scope/risk | L3 | A1 | Engagement partner class | Delivery Lead class | Practices *(anchor)* | medium |
| CAP-SCO | Scoping & Estimation | Scope volatility within tolerance | L2 | A0 | Partner pricing exceptions | Engagement Partner class | Partners | medium |
| CAP-KRU | Knowledge Reuse | Cross-engagement reuse with cite rights | L1 | A1 | Unclear who may cite | Knowledge Lead class | HQ Knowledge | medium |
| CAP-RET | Retrieval Governance | Client-safe retrieval / redaction | L0–L1 | A1 | Missing stamps | InfoSec + Knowledge class | HQ | medium |
| CAP-PRP | Proposal Assembly | Proposals assembled with controlled reuse | L2 | A1 | Fragmented IP | Proposal Ops class | Ops | medium |
| CAP-ACC | AI Accountability Design | Named residual humans for AI drafts | L1 | A0 | RACI incomplete | Risk/Compliance class | HQ | medium |

## 3. Dependency Edges

| From | Type | To | Note |
|------|------|-----|------|
| CAP-RET | requires | CAP-KRU | Reuse without retrieval gov = leakage |
| CAP-KRU | feeds | CAP-PRP | Reuse fuels proposals |
| CAP-PRP | amplifies | CAP-PUR | Faster pursuits |
| CAP-SCO | requires | CAP-DEL | Bad scope breaks governance |
| CAP-ACC | requires | CAP-PRP | AI drafting without residual humans → Hold |
| CAP-RET | requires | CAP-ACC | Accountability before client-facing AI send |
| CAP-DEL | amplifies | CAP-PUR | Delivery reputation feeds pursuit |
| CAP-SCO | conflicts | CAP-KRU | Partner exceptions vs standardized reuse |

## 4. Critical Path & Gaps

| Path / Gap | Signal | Planning implication (advisory) |
|------------|--------|----------------------------------|
| Critical path | CAP-RET → CAP-KRU → CAP-PRP → CAP-PUR | Authority before licenses |
| Gap G1 | CAP-RET L0–L1 | Reject license-first AI roadmap (WT-02 probe) |
| Gap G2 | CAP-ACC L1 | Hold unsupervised client-facing send |
| Gap G3 | CAP-SCO A0 | Prefer Assist; Hold Agentize on pricing/scope |

**Dept-roadmap contrast:** Org-first buys “Practice Copilot”; graph funds CAP-RET + CAP-ACC before any Agentize.

## 5. Export Hints (RP-005 / RP-007)

| Consumer | Hint | Bound |
|----------|------|-------|
| RP-005 | Assistive drafting roles only after CAP-ACC ≥ L2 | no grant mint; no AI personhood |
| RP-007 | HOLD agentic client actions; Prefer Assist on CAP-PRP | execution_authority=none |
| Eng / Permission | — | **never** from this graph |

## 6. Hard Boundaries

Not Kernel schema; not Runtime grant; not Twin authorize / Brain execute. License theater explicitly rejected. Synthetic T1 only.
