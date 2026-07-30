# GP-02 — Hybrid OT Gap Profile

**Research ID:** NRI-RP-006-GP-02  
**Program:** RP-006  
**Version:** 1.0  
**Status:** Synthetic Complete  
**Mode:** synthetic · **Tier:** T1  
**Enterprise ref:** SynMfg-Alpha / hybrid OT (aligned WT-01 class)  
**Parent:** [EVIDENCE_PACK.md](../EVIDENCE_PACK.md)  
**Dossier hint:** [WT-01](../../RP-001-enterprise-discovery/walkthroughs/WT-01-mid-mfg-synthetic.md)  
**As Of:** 2026-07-21 · **Facilitator:** NRI-desk (synthetic)

---

## Record

```text
gap_profile_version: syn-gp02-1.0
enterprise_ref: SynMfg-Alpha hybrid-OT
as_of: 2026-07-21
topology: hybrid_ot
kernel_bypass: never
grant_minted_from_infra: never
ot_unrestricted_mutate: never
parallel_approval: never
gpu_without_governance: defect
```

## 1. Domain Scores (Research)

| Domain | Band | Confidence | Evidence sketch | Gap? |
|--------|------|------------|-----------------|------|
| ID-01 Identity Landing | I2 | medium | Plant AI accounts exist; some shared OT logins | Partial |
| ID-02 Model Hosting | I1 | medium | Edge box + cloud fallback; prompt ownership unclear | **Yes** |
| ID-03 Tool Fabric | I1 | medium | MES/SCADA adapters not registered as tools | **Yes** |
| ID-04 Approval Bridge | I1 | high | Line leads approve in chat; no Workflow binding | **Yes — critical** |
| ID-05 Observability | I1 | medium | Plant logs siloed; weak correlation to HQ runs | **Yes — critical** |
| ID-06 Tenant Isolation | I2 | medium | Plant vs HQ bands partial | Partial |
| ID-07 Edge / OT Coupling | I0–I1 | high | Agents proposed with open MES write | **Yes — critical** |
| ID-08 Supply-Chain Trust | I0 | medium | Unsigned edge model images | **Yes** |

**Portfolio read:** Claiming I3+ with unrestricted plant agents fails falsifier #4. Critical path: **ID-07 safety island + ID-04/05** before any OT Agentize.

## 2. OT Safety Island Checklist

| Check | Result |
|-------|--------|
| Edge AI may read OT telemetry for advice | Allowed (advisory) |
| Edge AI may write MES/ERP without Workflow approval | **Forbidden** |
| OT tool `high_impact=true` requires approval bridge | Required |
| Plant agent without subject_id | **Defect** |
| “Self-heal line” branding as infra complete | **Reject** |

## 3. Anti-Patterns Observed

| Anti-pattern | Present? | AIRM response |
|--------------|----------|---------------|
| Open MES write from edge agent | Proposed | Fail ID-07; hold I3+ |
| GPU at plant without ID-04/05 | Yes | Fail governance-before-GPU |
| Twin authorize from plant insight | Pressure | Fail ADR-0030 coupling |
| Kernel bypass via OT VPN “shortcut” | Discussed | `kernel_bypass: never` |

## 4. Readiness Implications (Advisory)

| Consumer | Hint | Bound |
|----------|------|-------|
| RP-007 / RP-008 | HOLD robot/OT Agentize until ID-07 ≥ I2 + ID-04 ≥ I2 | execution_authority=none |
| RP-009 | Capacity planning only; no Brain execute from plant KPI | advisory |
| Eng / Runtime | — | **never** from this profile |

## 5. Hard Boundaries

`kernel_bypass: never`. `ot_unrestricted_mutate: never`. No Brain execute / Twin authorize / Role→grant. Research Only.
