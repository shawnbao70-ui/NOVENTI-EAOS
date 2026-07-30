# GP-01 — Cloud-Native Landing Gap Profile

**Research ID:** NRI-RP-006-GP-01  
**Program:** RP-006  
**Version:** 1.0  
**Status:** Synthetic Complete  
**Mode:** synthetic · **Tier:** T1  
**Enterprise ref:** SynCloud-Gamma (synthetic SaaS-ish mid-market)  
**Parent:** [EVIDENCE_PACK.md](../EVIDENCE_PACK.md)  
**As Of:** 2026-07-21 · **Facilitator:** NRI-desk (synthetic)

---

## Record

```text
gap_profile_version: syn-gp01-1.0
enterprise_ref: SynCloud-Gamma
as_of: 2026-07-21
topology: cloud_native
kernel_bypass: never
grant_minted_from_infra: never
parallel_approval: never
gpu_without_governance: defect
```

## 1. Domain Scores (Research)

| Domain | Band | Confidence | Evidence sketch | Gap? |
|--------|------|------------|-----------------|------|
| ID-01 Identity Landing | I2 | medium | AI subjects exist in Identity; some orphan bots | Partial |
| ID-02 Model Hosting | I1 | medium | Mix of vendor SaaS + one VPC endpoint; key sprawl | **Yes** |
| ID-03 Tool Fabric | I1 | medium | Tools invoked ad hoc; few `RegisterTool` | **Yes — critical** |
| ID-04 Approval Bridge | I1 | high | Chat approvals bypass Workflow | **Yes — critical** |
| ID-05 Observability | I2 | medium | Logs exist; weak correlation_id discipline | Partial |
| ID-06 Tenant Isolation | I1 | medium | Shared model pool; weak tenant tags on tools | **Yes — critical** |
| ID-07 Edge / OT | I0 | high | N/A (no plant) | N/A |
| ID-08 Supply-Chain Trust | I0 | medium | Unsigned prompts/tools common | **Yes** |

**Portfolio read:** Do **not** claim I3+ from GPU purchase. Critical path: **ID-03 → ID-04 → ID-06** before model scale.

## 2. Anti-Patterns Observed

| Anti-pattern | Present? | AIRM response |
|--------------|----------|---------------|
| GPU roadmap as “AI-ready” | Yes | Fail C-INF-02 |
| Parallel Slack approval bot | Yes | Fail V-INF-02 |
| Unregistered high-impact tools | Yes | Fail ID-03 |
| Infra diagram with grant shortcut | No | Keep `kernel_bypass: never` |
| Shadow SaaS keys in chat | Yes | Cap ID-02 at I1 |

## 3. Readiness Implications (Advisory)

| Consumer | Hint | Bound |
|----------|------|-------|
| RP-007 | HOLD aggressive Agentize until ID-04 ≥ I2 | execution_authority=none |
| RP-001 | Infra Discovery must score all eight domains | no composite IQ |
| Eng / Runtime | — | **never** from this profile |

## 4. Hard Boundaries

`kernel_bypass: never`. No Brain execute / Twin authorize / Role→grant / payment clearing. Research Only — not Eng ticket.
