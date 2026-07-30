# PW-02 — Line-side Terminal + OT Island Overlay

**Research ID:** NRI-RP-008-PW-02  
**Program:** RP-008  
**Version:** 1.0  
**Status:** Synthetic Complete  
**Mode:** synthetic · **Tier:** T1  
**Enterprise ref:** SynMfg-Alpha line-side + hybrid OT  
**Parent:** [EVIDENCE_PACK.md](../EVIDENCE_PACK.md)  
**Coupling:** [GP-02](../../RP-006-ai-infrastructure-platform/gap-profiles/GP-02-hybrid-ot.md)  
**As Of:** 2026-07-21 · **Facilitator:** NRI-desk (synthetic)

---

## Record

```text
plant_overlay_version: syn-pw02-1.0
enterprise_ref: SynMfg-Alpha line-terminal-ot
as_of: 2026-07-21
topology: line_side_plus_ot_island
mes_kernelization: never
machine_control_from_brain: never
ot_unrestricted_mutate: never
hq_ux_forced_on_line: defect
execution_authority: none
```

## 1. Domain Scores (Research)

| Domain | Band / Note | Confidence | Gap? |
|--------|-------------|------------|------|
| SF-01 Plant Cap Overlay | Cap IDs stable across reorg | medium | Partial |
| SF-02 H/AI/R/D Mix | Line lead + AI assist; device adapters unclear | medium | Partial |
| SF-03 Physical Risk | PR1 desk tools only on this line | medium | OK for Assist |
| SF-04 Line-side Terminal | Need glanceable approve; offline rules missing | high | **Yes — critical** |
| SF-05 OT/Historian | Telemetry readable; Knowledge write gated | medium | Partial |
| SF-06 Robot Readiness | No robot on this line | high | N/A |
| SF-07 Degraded Mode | Fail-open chat approve when OT down | high | **Yes — critical** |
| SF-08 Package Scope | Line pack must declare OT read-only vs write | medium | **Yes** |

**Portfolio read:** Critical path **SF-04 + SF-07** before claiming line-side “AI ready.” Aligns AIRM ID-07 island: read OK; unrestricted MES write never.

## 2. Line-side Terminal Checklist

| Check | Result |
|-------|--------|
| Approvals glanceable in <3s glance | Fail (HQ form dense) |
| Offline / degraded mode defined | **Missing** — fail-open risk |
| Permission + Workflow still bind when online | Required |
| Twin authorize from plant KPI card | **Forbidden** |
| Historian promoted to Knowledge without governance | **Defect** |

## 3. OT Island Coupling (AIRM)

| Check | Result |
|-------|--------|
| Edge AI may advise from telemetry | Allowed |
| Edge AI may write MES without Workflow | **Forbidden** |
| OT tools high_impact require approval bridge | Required (GP-02) |

## 4. Hard Boundaries

`mes_kernelization: never`. `machine_control_from_brain: never`. `ot_unrestricted_mutate: never`. Research Only.
